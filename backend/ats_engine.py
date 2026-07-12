import re
from collections import Counter

try:
    from rapidfuzz import fuzz
except Exception:  # pragma: no cover - optional dependency fallback
    fuzz = None


def split_csv(value: str | list | None) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", str(text).lower()) if len(t) > 2}


def fuzzy_contains(needle: str, haystack: list[str]) -> bool:
    n = needle.lower().strip()
    for item in haystack:
        i = item.lower().strip()
        if n == i or n in i or i in n:
            return True
        if fuzz and fuzz.partial_ratio(n, i) >= 88:
            return True
    return False


def score_skill_match(resume_skills: list[str], required: list[str], preferred: list[str] | None = None) -> tuple[float, list[str], list[str]]:
    required = required or []
    preferred = preferred or []
    if not required and not preferred:
        return 100.0 if resume_skills else 0.0, [], []
    weighted = [(s, 1.0) for s in required] + [(s, 0.4) for s in preferred]
    total = sum(w for _, w in weighted) or 1.0
    matched = []
    missing = []
    earned = 0.0
    for skill, weight in weighted:
        if fuzzy_contains(skill, resume_skills):
            matched.append(skill)
            earned += weight
        elif weight >= 1.0:
            missing.append(skill)
    return round(min(100.0, earned / total * 100), 1), list(dict.fromkeys(matched)), list(dict.fromkeys(missing))


def score_experience(candidate_years: float, required_years: float) -> float:
    if required_years <= 0:
        return 100.0
    return round(min(100.0, max(0.0, candidate_years) / required_years * 100), 1)


def score_projects(projects: list | int) -> float:
    count = projects if isinstance(projects, int) else len(projects or [])
    if count >= 5:
        return 100.0
    if count >= 3:
        return 80.0
    if count == 2:
        return 60.0
    if count == 1:
        return 40.0
    return 0.0


def score_certifications(certs: list | int) -> float:
    count = certs if isinstance(certs, int) else len(certs or [])
    if count >= 3:
        return 100.0
    if count == 2:
        return 80.0
    if count == 1:
        return 60.0
    return 50.0


def score_keywords(raw_text: str, job_text: str) -> float:
    resume_tokens = token_set(raw_text)
    job_tokens = token_set(job_text)
    stop = {"and", "the", "with", "for", "you", "our", "will", "are", "from", "this", "that", "have", "has", "job", "role"}
    job_tokens -= stop
    if not job_tokens:
        return 100.0
    common = resume_tokens & job_tokens
    return round(min(100.0, len(common) / max(12, min(len(job_tokens), 60)) * 100), 1)


def recommendation(score: float) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Partial"
    return "Weak"


def run_ats_analysis(parsed_resume: dict, job) -> dict:
    resume_skills = parsed_resume.get("skills", []) or split_csv(parsed_resume.get("extracted_skills"))
    required = split_csv(getattr(job, "required_skills", "")) if job else []
    preferred = split_csv(getattr(job, "preferred_skills", "")) if job else []
    skill_score, matched, missing = score_skill_match(resume_skills, required, preferred)
    exp_score = score_experience(float(parsed_resume.get("experience_years", 0) or parsed_resume.get("extracted_experience_years", 0) or 0), float(getattr(job, "min_experience_years", 0) or 0))
    project_score = score_projects(parsed_resume.get("projects", []))
    cert_score = score_certifications(parsed_resume.get("certifications", []))
    job_text = " ".join(str(getattr(job, f, "") or "") for f in ["title", "description", "responsibilities", "qualifications", "required_skills", "preferred_skills"]) if job else ""
    keyword_score = score_keywords(parsed_resume.get("raw_text", ""), job_text)
    weights = {
        "skills": float(getattr(job, "ats_weight_skills", 40) or 40),
        "experience": float(getattr(job, "ats_weight_experience", 25) or 25),
        "projects": float(getattr(job, "ats_weight_projects", 15) or 15),
        "certifications": float(getattr(job, "ats_weight_certifications", 10) or 10),
        "keywords": float(getattr(job, "ats_weight_keywords", 10) or 10),
    }
    total_weight = sum(weights.values()) or 100.0
    overall = (
        skill_score * weights["skills"]
        + exp_score * weights["experience"]
        + project_score * weights["projects"]
        + cert_score * weights["certifications"]
        + keyword_score * weights["keywords"]
    ) / total_weight
    recommendations = []
    if missing:
        recommendations.append("Add or highlight required skills: " + ", ".join(missing[:6]))
    if exp_score < 70:
        recommendations.append("Clarify years of experience and outcomes that match the role requirement.")
    if project_score < 60:
        recommendations.append("Include more project evidence with architecture, impact, and technologies.")
    return {
        "ats_score": round(overall, 1),
        "skill_match_score": skill_score,
        "experience_match_score": exp_score,
        "project_match_score": project_score,
        "certification_match_score": cert_score,
        "keyword_match_score": keyword_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendation": recommendation(overall),
        "recommendations": recommendations or ["Resume is aligned enough to proceed to interview review."],
    }
