import json
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity as sk_cos

MODEL_DIR = Path(__file__).parent.parent / "ml" / "models_cache"

class LocalAnswerEvaluator:
    def __init__(self):
        self.st_model = None
        self._load()

    def _load(self):
        try:
            from sentence_transformers import SentenceTransformer
            st_path = MODEL_DIR / "sentence_transformer"
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            if st_path.exists():
                self.st_model = SentenceTransformer(str(st_path))
            else:
                self.st_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.st_model.save(str(st_path))
        except Exception as e:
            print(f"[WARN] sentence-transformers unavailable: {e}. Using TF-IDF fallback.")

    def evaluate(self, question: str, answer: str, reference: str,
                 expected_keywords: list, expected_concepts: list) -> dict:
        answer = (answer or "").strip()
        if not answer or len(answer) < 5:
            return self._zero("No answer provided.")

        if self.st_model and reference:
            emb_r = self.st_model.encode([reference])
            emb_a = self.st_model.encode([answer])
            semantic = float(sk_cos(emb_r, emb_a)[0][0])
        else:
            semantic = self._tfidf_sim(reference or question, answer)

        al = answer.lower()
        covered = [k for k in expected_keywords if k.lower() in al]
        kw_score = len(covered) / max(len(expected_keywords), 1)

        con_score = sum(1 for c in expected_concepts if c.lower() in al) / max(len(expected_concepts), 1)

        wc = len(answer.split())
        len_score = min(wc / 60, 1.0)

        tech  = round((semantic*0.6 + kw_score*0.4) * 10, 1)
        comp  = round((kw_score*0.5 + con_score*0.5) * 10, 1)
        depth = round((len_score*0.4 + semantic*0.6) * 10, 1)
        comm  = round(min(len_score*1.2, 1.0) * 10, 1)
        conf  = round((len_score*0.5 + kw_score*0.5) * 10, 1)
        relev = round((semantic*0.7 + con_score*0.3) * 10, 1)

        overall = round(((tech+comp+depth+comm+conf+relev) / 60) * 100, 1)

        label = ("Excellent" if overall >= 80 else "Good" if overall >= 65
                 else "Average" if overall >= 45 else "Needs Improvement")

        missing = [k for k in expected_keywords if k.lower() not in al]
        feedback = self._feedback(label, missing, wc)
        return {
            "score": overall,
            "technical_accuracy": tech, "completeness": comp, "depth": depth,
            "communication": comm, "confidence": conf, "relevance": relev,
            "semantic_score": round(semantic, 3), "keyword_score": round(kw_score, 3),
            "label": label, "feedback": feedback,
            "strengths": self._strengths(tech, comm, depth, kw_score),
            "weaknesses": self._weaknesses(tech, comm, depth, missing),
            "missing_keywords": missing[:5],
        }

    def _tfidf_sim(self, ref, cand):
        from sklearn.feature_extraction.text import TfidfVectorizer
        try:
            v = TfidfVectorizer()
            m = v.fit_transform([ref, cand])
            return float(sk_cos(m[0], m[1])[0][0])
        except:
            return 0.3

    def _feedback(self, label, missing, wc):
        tip = f" Consider covering: {', '.join(missing[:3])}." if missing else ""
        if label == "Excellent":
            return "Outstanding response. Strong technical knowledge and clear communication."
        elif label == "Good":
            return f"Good answer showing solid understanding.{tip}"
        elif label == "Average":
            short = " Try to expand — aim for 50+ words." if wc < 30 else ""
            return f"Partial understanding shown.{tip}{short}"
        else:
            return f"Answer needs improvement.{tip} Aim for at least 3-4 clear sentences."

    def _strengths(self, tech, comm, depth, kw):
        s = []
        if tech >= 7: s.append("Strong technical accuracy")
        if comm >= 7: s.append("Clear communication")
        if depth >= 7: s.append("Good depth and detail")
        if kw >= 0.6: s.append("Good use of technical terminology")
        return s or ["Attempted the question"]

    def _weaknesses(self, tech, comm, depth, missing):
        w = []
        if tech < 5: w.append("Technical accuracy needs improvement")
        if comm < 5: w.append("Communication could be clearer")
        if depth < 5: w.append("Answer lacks depth")
        if missing: w.append(f"Missing key terms: {', '.join(missing[:3])}")
        return w

    def _zero(self, reason):
        return {
            "score": 0, "technical_accuracy": 0, "completeness": 0, "depth": 0,
            "communication": 0, "confidence": 0, "relevance": 0,
            "semantic_score": 0, "keyword_score": 0, "label": "No Answer",
            "feedback": reason, "strengths": [], "weaknesses": ["No answer provided"],
            "missing_keywords": [],
        }

evaluator = LocalAnswerEvaluator()
