import importlib
import importlib.util
import json
from pathlib import Path

joblib = None
if importlib.util.find_spec("joblib") is not None:
    joblib = importlib.import_module("joblib")
elif importlib.util.find_spec("sklearn.externals.joblib") is not None:
    joblib = importlib.import_module("sklearn.externals.joblib")
try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None
from scipy.sparse import hstack
from sklearn.metrics.pairwise import cosine_similarity

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "answer_evaluator" / "tfidf_lr_model.pkl"
ST_PATH = PROJECT_ROOT / "models" / "answer_evaluator" / "sentence_transformer"


class AnswerEvaluator:
    def __init__(self):
        self.model_path = MODEL_PATH
        self.artifact = joblib.load(self.model_path) if self.model_path.exists() else None
        self.tfidf = self.artifact.get("tfidf") if self.artifact else None
        self.lr = self.artifact.get("lr") if self.artifact else None
        self.labels = self.artifact.get("labels", {0: "poor", 1: "average", 2: "good", 3: "excellent"}) if self.artifact else {0: "poor", 1: "average", 2: "good", 3: "excellent"}
        self.sentence_model = None
        self.semantic_backend = "tfidf_fallback"
        if ST_PATH.exists() and not (ST_PATH / "FALLBACK.json").exists():
            try:
                from sentence_transformers import SentenceTransformer
                self.sentence_model = SentenceTransformer(str(ST_PATH))
                self.semantic_backend = "sentence-transformers"
            except Exception:
                self.sentence_model = None

    @property
    def loaded(self) -> bool:
        return np is not None and self.lr is not None and self.tfidf is not None

    def _keyword_overlap(self, reference: str, answer: str) -> float:
        ref_words = set(str(reference).lower().split())
        ans_words = set(str(answer).lower().split())
        if not ref_words:
            return 0.0
        return len(ref_words & ans_words) / len(ref_words)

    def _feature_matrix(self, question: str, answer: str, reference: str):
        text = [f"{question} {answer}"]
        x_text = self.tfidf.transform(text)
        length = np.array([[min(len(answer.split()) / 160, 1.0)]])
        overlap = np.array([[self._keyword_overlap(reference, answer)]])
        return hstack([x_text, length, overlap])

    def _semantic_score(self, candidate_answer: str, reference_answer: str) -> float:
        if not candidate_answer.strip() or not reference_answer.strip():
            return 0.0
        if self.sentence_model is not None:
            emb = self.sentence_model.encode([reference_answer, candidate_answer])
            return float(cosine_similarity([emb[0]], [emb[1]])[0][0])
        if self.tfidf is not None:
            vec = self.tfidf.transform([reference_answer, candidate_answer])
            return float(cosine_similarity(vec[0], vec[1])[0][0])
        return 0.0

    def evaluate(self, question, candidate_answer, reference_answer, keywords):
        if not self.loaded:
            raise RuntimeError(f"Answer evaluator model missing at {self.model_path}. Run training/train_evaluator.py")
        candidate_answer = candidate_answer or ""
        keywords = keywords or []
        x = self._feature_matrix(question, candidate_answer, reference_answer)
        probs = self.lr.predict_proba(x)[0]
        expected = float(np.dot(probs, [0.05, 0.35, 0.65, 0.9]))
        semantic_score = max(0.0, min(1.0, self._semantic_score(candidate_answer, reference_answer)))
        answer_lower = candidate_answer.lower()
        covered = [k for k in keywords if k.lower() in answer_lower]
        keyword_score = len(covered) / max(len(keywords), 1)
        length_score = min(len(candidate_answer.split()) / 50, 1.0)
        final_score = 0.35 * expected + 0.35 * semantic_score + 0.20 * keyword_score + 0.10 * length_score
        if candidate_answer.strip().lower() in {"i don't know", "idk", "no idea", ""}:
            final_score = min(final_score, 0.15)
        if final_score >= 0.75:
            label = "excellent"
        elif final_score >= 0.55:
            label = "good"
        elif final_score >= 0.35:
            label = "average"
        else:
            label = "poor"
        missing = [k for k in keywords if k.lower() not in answer_lower]
        return {
            "score": round(float(final_score), 3),
            "label": label,
            "feedback": self._generate_feedback(label, missing, semantic_score),
            "missing_keywords": missing,
            "semantic_score": round(float(semantic_score), 3),
            "keyword_coverage": f"{len(covered)}/{len(keywords)}",
            "semantic_backend": self.semantic_backend,
            "model_probabilities": {str(i): round(float(v), 3) for i, v in enumerate(probs)},
        }

    def _generate_feedback(self, label, missing, sem_score):
        if label == "excellent":
            return "Outstanding answer. Covered key concepts with clear explanation and strong semantic match."
        if label == "good":
            tips = f" Consider mentioning: {', '.join(missing[:3])}." if missing else ""
            return f"Good answer with solid understanding.{tips}"
        if label == "average":
            return f"Partial understanding shown. Key concepts missing: {', '.join(missing[:5])}. Expand the answer with examples and trade-offs."
        return f"Answer needs significant improvement. Focus on: {', '.join(missing[:5])}. Minimum 3-4 technical sentences expected."
