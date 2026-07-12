import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models" / "resume_scorer"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
FEATURES = ["skills_count", "has_email", "has_phone", "has_name", "word_count", "education_count", "experience_years", "project_count", "cert_count", "section_count"]


def load_data() -> pd.DataFrame:
    path = PROCESSED / "resume_training_data.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run training/preprocess.py first.")
    df = pd.read_csv(path).dropna()
    return df


def train(force_retrain: bool = False):
    model_path = MODEL_DIR / "rf_model.pkl"
    if model_path.exists() and not force_retrain:
        print(f"[SKIP] {model_path} exists. Use --force-retrain to retrain.")
        return
    df = load_data()
    missing_columns = [col for col in FEATURES + ["ats_label"] if col not in df.columns]
    if missing_columns:
        raise RuntimeError(f"resume_training_data.csv is missing columns: {missing_columns}")
    df = df.dropna(subset=FEATURES + ["ats_label"])
    if df.empty:
        raise RuntimeError("resume_training_data.csv has no usable training rows")
    class_counts = df["ats_label"].astype(int).value_counts().sort_index()
    missing_labels = sorted(set(range(3)) - set(class_counts.index))
    if missing_labels:
        raise RuntimeError(f"resume_training_data.csv is missing ats_label classes: {missing_labels}")
    min_class_count = int(class_counts.min())
    if min_class_count < 2:
        raise RuntimeError("Each ats_label class needs at least 2 rows for stratified training")
    x = df[FEATURES]
    y = df["ats_label"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)
    rf = RandomForestClassifier(n_estimators=140, random_state=42, class_weight="balanced", max_depth=12)
    rf.fit(x_train, y_train)
    pred = rf.predict(x_test)
    acc = accuracy_score(y_test, pred)
    labels_present = sorted(set(y_test) | set(pred))
    target_names = ["low", "medium", "high"]
    cv_folds = min(5, min_class_count)
    cv = cross_val_score(rf, x, y, cv=StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42), scoring="accuracy")
    print(f"Resume scorer accuracy: {acc:.4f}")
    print(classification_report(y_test, pred, labels=labels_present, target_names=[target_names[i] for i in labels_present], zero_division=0))
    print(f"{cv_folds}-Fold CV Accuracy: {cv.mean():.4f} ± {cv.std():.4f}")
    importances = dict(zip(FEATURES, [float(v) for v in rf.feature_importances_]))
    for key, value in sorted(importances.items(), key=lambda x: -x[1]):
        print(f"  {key}: {value:.4f}")
    joblib.dump({"model": rf, "features": FEATURES, "labels": {0: "low", 1: "medium", 2: "high"}, "feature_importances": importances}, model_path)
    metrics = {"accuracy": float(acc), "cv_mean": float(cv.mean()), "cv_std": float(cv.std()), "rows": int(len(df)), "feature_importances": importances}
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Saved {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-retrain", action="store_true")
    args = parser.parse_args()
    train(args.force_retrain)
