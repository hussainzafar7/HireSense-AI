import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = PROJECT_ROOT / "models" / "answer_evaluator"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "training_data.csv"


def keyword_overlap(reference: str, answer: str) -> float:
    ref_words = set(str(reference).lower().split())
    ans_words = set(str(answer).lower().split())
    if not ref_words:
        return 0.0
    return len(ref_words & ans_words) / len(ref_words)


def build_matrix(df: pd.DataFrame, tfidf: TfidfVectorizer | None = None, fit: bool = True):
    text = (df["question"].fillna("") + " " + df["candidate_answer"].fillna("")).astype(str)
    if fit:
        tfidf = TfidfVectorizer(max_features=6000, ngram_range=(1, 2), min_df=1)
        x_text = tfidf.fit_transform(text)
    else:
        x_text = tfidf.transform(text)
    lengths = (df["candidate_answer"].fillna("").str.split().str.len().clip(0, 160) / 160).values.reshape(-1, 1)
    overlaps = df.apply(lambda row: keyword_overlap(row.get("reference_answer", ""), row.get("candidate_answer", "")), axis=1).values.reshape(-1, 1)
    return hstack([x_text, lengths, overlaps]), tfidf


def cache_sentence_transformer() -> dict:
    target = MODEL_DIR / "sentence_transformer"
    try:
        from sentence_transformers import SentenceTransformer

        fallback_marker = target / "FALLBACK.json"
        model_ready = (target / "config.json").exists() or (target / "modules.json").exists()
        if fallback_marker.exists() or not model_ready:
            if fallback_marker.exists():
                fallback_marker.unlink()
            target.mkdir(parents=True, exist_ok=True)
            print("Downloading sentence-transformers model all-MiniLM-L6-v2...")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            model.save(str(target))
        return {"available": True, "path": str(target), "backend": "sentence-transformers"}
    except Exception as exc:
        target.mkdir(parents=True, exist_ok=True)
        info = {"available": False, "path": str(target), "backend": "tfidf_fallback", "error": str(exc)}
        (target / "FALLBACK.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        print(f"[WARN] Sentence transformer unavailable; TF-IDF fallback will be used: {exc}")
        return info


def train(force_retrain: bool = False):
    model_path = MODEL_DIR / "tfidf_lr_model.pkl"
    metrics_path = MODEL_DIR / "metrics.json"
    if model_path.exists() and not force_retrain:
        print(f"[SKIP] {model_path} exists. Use --force-retrain to retrain.")
        cache_sentence_transformer()
        return
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}. Run training/preprocess.py first.")
    df = pd.read_csv(DATA_PATH).dropna(subset=["question", "candidate_answer", "reference_answer", "score_label"])
    if df.empty:
        raise RuntimeError(f"{DATA_PATH} has no usable training rows")
    class_counts = df["score_label"].astype(int).value_counts().sort_index()
    missing_labels = sorted(set(range(4)) - set(class_counts.index))
    if missing_labels:
        raise RuntimeError(f"training_data.csv is missing score_label classes: {missing_labels}")
    min_class_count = int(class_counts.min())
    if min_class_count < 2:
        raise RuntimeError("Each score_label class needs at least 2 rows for stratified training")
    print(f"Dataset size: {len(df)} samples")
    print(class_counts)
    x, tfidf = build_matrix(df, fit=True)
    y = df["score_label"].astype(int).values
    stratify = y if min_class_count >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=stratify)
    lr = LogisticRegression(max_iter=1000, C=2.0, multi_class="auto", class_weight="balanced")
    lr.fit(x_train, y_train)
    pred = lr.predict(x_test)
    acc = accuracy_score(y_test, pred)
    print(f"Accuracy: {acc:.4f}")
    labels_present = sorted(set(y_test) | set(pred))
    target_names = ["poor", "average", "good", "excellent"]
    print(classification_report(y_test, pred, labels=labels_present, target_names=[target_names[i] for i in labels_present], zero_division=0))
    cv_folds = min(5, min_class_count)
    if cv_folds >= 2:
        cv = cross_val_score(lr, x, y, cv=StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42), scoring="accuracy")
        print(f"{cv_folds}-Fold CV Accuracy: {cv.mean():.4f} ± {cv.std():.4f}")
    else:
        cv = np.array([acc])
        print("Cross-validation skipped: not enough rows per class")
    artifact = {
        "tfidf": tfidf,
        "lr": lr,
        "labels": {0: "poor", 1: "average", 2: "good", 3: "excellent"},
        "feature_order": ["tfidf(question+answer)", "length_norm", "reference_overlap"],
        "training_rows": len(df),
    }
    joblib.dump(artifact, model_path)
    metrics = {"accuracy": float(acc), "cv_mean": float(cv.mean()), "cv_std": float(cv.std()), "rows": int(len(df))}
    metrics["sentence_transformer"] = cache_sentence_transformer()
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Saved {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-retrain", action="store_true")
    args = parser.parse_args()
    train(args.force_retrain)
