import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

try:
    from .resume_parser import MASTER_SKILLS, extract_years
except ImportError:
    from resume_parser import MASTER_SKILLS, extract_years

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "resume_scorer" / "rf_model.pkl"


class ResumeScorer:
    def __init__(self, model_path: Path = MODEL_PATH):
        self.model_path = Path(model_path)
        self.artifact = None
        self.model = None
        self.features = []
        if self.model_path.exists():
            self.artifact = joblib.load(self.model_path)
            self.model = self.artifact["model"]
            self.features = self.artifact["features"]

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def extract_features(self, parsed: dict) -> dict:
        raw = parsed.get("raw_text", "")
        exp_years = max([extract_years(raw)] + [float(x.get("years", 0) or 0) for x in parsed.get("experience", [])])
        return {
            "skills_count": len(parsed.get("skills", [])),
            "has_email": int(bool(parsed.get("email"))),
            "has_phone": int(bool(parsed.get("phone"))),
            "has_name": int(bool(parsed.get("name")) and parsed.get("name") != "Unknown Candidate"),
            "word_count": int(parsed.get("word_count", 0)),
            "education_count": len(parsed.get("education", [])),
            "experience_years": exp_years,
            "project_count": len(parsed.get("projects", [])),
            "cert_count": len(parsed.get("certifications", [])),
            "section_count": sum(1 for section in ["education", "experience", "projects", "skills", "certifications", "summary"] if re.search(section, raw, re.I)),
        }

    def score(self, parsed: dict, job_role: str = "software engineer") -> dict:
        features = self.extract_features(parsed)
        contact = round((features["has_email"] + features["has_phone"] + features["has_name"]) / 3 * 100, 1)
        skills_density = round(min(features["skills_count"] / 20, 1) * 100, 1)
        education_quality = round(min(features["education_count"] / 2, 1) * 100, 1)
        experience_relevance = round(min((features["experience_years"] / 5) * 0.7 + (features["project_count"] / 4) * 0.3, 1) * 100, 1)
        wc = features["word_count"]
        format_ats = 100 if 400 <= wc <= 800 else 75 if 250 <= wc <= 1000 else 45
        rule_score = 0.15 * contact + 0.25 * skills_density + 0.20 * education_quality + 0.25 * experience_relevance + 0.15 * format_ats
        ml_label = 1
        ml_score = rule_score
        ml_proba = None
        if self.model is not None:
            x = pd.DataFrame([[features.get(f, 0) for f in self.features]], columns=self.features)
            ml_label = int(self.model.predict(x)[0])
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(x)[0]
                ml_proba = {str(i): round(float(v), 3) for i, v in enumerate(probs)}
                ml_score = float(np.dot(probs, [25, 60, 88]))
            else:
                ml_score = [25, 60, 88][ml_label]
        overall = round(0.65 * rule_score + 0.35 * ml_score, 1)
        recommendation = "STRONG" if overall >= 82 else "GOOD" if overall >= 68 else "FAIR" if overall >= 50 else "WEAK"
        missing_skills = [s for s in ["Python", "SQL", "Git", "Docker", "REST API", "testing", "AWS"] if s not in parsed.get("skills", [])]
        return {
            "overall_score": overall,
            "recommendation": recommendation,
            "breakdown": {
                "contact_completeness": contact,
                "skills_density": skills_density,
                "education_quality": education_quality,
                "experience_relevance": experience_relevance,
                "format_ats": float(format_ats),
            },
            "features": features,
            "ml_label": ml_label,
            "ml_probability": ml_proba,
            "matched_skills": parsed.get("skills", []),
            "missing_suggestions": missing_skills[:5],
        }
