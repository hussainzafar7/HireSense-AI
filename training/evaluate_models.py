import json
from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"


def main():
    answer_model = PROJECT_ROOT / "models" / "answer_evaluator" / "tfidf_lr_model.pkl"
    resume_model = PROJECT_ROOT / "models" / "resume_scorer" / "rf_model.pkl"
    qbank = PROCESSED / "question_bank.json"
    refs = PROCESSED / "reference_answers.json"
    training = PROCESSED / "training_data.csv"
    missing = [p for p in [answer_model, resume_model, qbank, refs, training] if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required artifacts: " + ", ".join(str(p) for p in missing))
    df = pd.read_csv(training)
    q = json.loads(qbank.read_text(encoding="utf-8"))
    r = json.loads(refs.read_text(encoding="utf-8"))
    am = joblib.load(answer_model)
    rm = joblib.load(resume_model)
    print("=== HireSense AI Model Evaluation ===")
    print(f"Training rows: {len(df)}")
    print(f"Question bank questions: {len(q)}")
    print(f"Reference answers: {len(r)}")
    print(f"Answer evaluator labels: {am.get('labels')}")
    print(f"Resume scorer labels: {rm.get('labels')}")
    for metrics_path in [answer_model.parent / "metrics.json", resume_model.parent / "metrics.json"]:
        if metrics_path.exists():
            print(f"\n{metrics_path}:")
            print(metrics_path.read_text(encoding="utf-8"))
    answer_metrics = json.loads((answer_model.parent / "metrics.json").read_text(encoding="utf-8"))
    resume_metrics = json.loads((resume_model.parent / "metrics.json").read_text(encoding="utf-8"))
    cv = answer_metrics.get("cv_mean", 0)
    if cv < 0.70:
        print(f"[WARN] Evaluator CV accuracy is below target: {cv:.3f}")
    else:
        print(f"Evaluator CV accuracy target met: {cv:.3f}")
    resume_acc = resume_metrics.get("accuracy", 0)
    if resume_acc < 0.70:
        print(f"[WARN] Resume scorer accuracy is below target: {resume_acc:.3f}")
    else:
        print(f"Resume scorer accuracy target met: {resume_acc:.3f}")


if __name__ == "__main__":
    main()
