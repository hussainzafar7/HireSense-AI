import re

try:
    from rapidfuzz import fuzz
except Exception:
    fuzz = None


def split_csv(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def token_set(text):
    return {t for t in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", str(text).lower()) if len(t) > 2}


def fuzzy_contains(needle, haystack):
    n = needle.lower().strip()
    for item in haystack:
        i = item.lower().strip()
        if n == i or n in i or i in n:
            return True
        if fuzz and fuzz.partial_ratio(n, i) >= 88:
            return True
    return False


def score_skill_match(resume_skills, required, preferred=None):
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


def score_experience(candidate_years, required_years):
    if required_years <= 0:
        return 100.0
    return round(min(100.0, max(0.0, candidate_years) / required_years * 100), 1)


def score_projects(projects):
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


def score_certifications(certs):
    count = certs if isinstance(certs, int) else len(certs or [])
    if count >= 3:
        return 100.0
    if count == 2:
        return 80.0
    if count == 1:
        return 60.0
    return 50.0


def score_keywords(raw_text, job_text):
    resume_tokens = token_set(raw_text)
    job_tokens = token_set(job_text)
    stop = {"and", "the", "with", "for", "you", "our", "will", "are", "from", "this", "that", "have", "has", "job", "role"}
    job_tokens -= stop
    if not job_tokens:
        return 100.0
    common = resume_tokens & job_tokens
    return round(min(100.0, len(common) / max(12, min(len(job_tokens), 60)) * 100), 1)


def recommendation(score):
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Partial"
    return "Weak"


def run_ats_analysis(raw_text, parsed, job):
    resume_skills = parsed.get("skills", [])
    required = split_csv(getattr(job, "required_skills", "")) if job else []
    preferred = split_csv(getattr(job, "preferred_skills", "")) if job else []
    skill_score, matched, missing = score_skill_match(resume_skills, required, preferred)
    exp_years = parsed.get("extracted_experience_years", 0) or 0
    if isinstance(exp_years, list):
        exp_years = len(exp_years)
    exp_score = score_experience(float(exp_years), float(getattr(job, "min_experience_years", 0) or 0))
    project_score = score_projects(parsed.get("projects", []))
    cert_score = score_certifications(parsed.get("certifications", []))
    job_text = " ".join(str(getattr(job, f, "") or "") for f in ["title", "description", "responsibilities", "qualifications", "required_skills", "preferred_skills"]) if job else ""
    keyword_score = score_keywords(raw_text or "", job_text)
    weights = {
        "skills": 40,
        "experience": 25,
        "projects": 15,
        "certifications": 10,
        "keywords": 10,
    }
    total_weight = sum(weights.values()) or 100.0
    overall = (
        skill_score * weights["skills"]
        + exp_score * weights["experience"]
        + project_score * weights["projects"]
        + cert_score * weights["certifications"]
        + keyword_score * weights["keywords"]
    ) / total_weight
    recommendations_list = []
    if missing:
        recommendations_list.append("Add or highlight required skills: " + ", ".join(missing[:6]))
    if exp_score < 70:
        recommendations_list.append("Clarify years of experience and outcomes that match the role requirement.")
    if project_score < 60:
        recommendations_list.append("Include more project evidence with architecture, impact, and technologies.")
    if cert_score < 60:
        recommendations_list.append("Consider adding relevant certifications to strengthen your profile.")
    if keyword_score < 60:
        recommendations_list.append("Tailor your resume with more keywords from the job description.")
    if not recommendations_list:
        recommendations_list.append("Resume is aligned well with the job requirements. Proceed to interview.")
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
        "recommendations": "\n".join(recommendations_list),
    }
