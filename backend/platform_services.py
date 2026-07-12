import json
import os
import re
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from .ats_engine import run_ats_analysis, split_csv
    from .config import Config
    from .db import Candidate, Company, Interview, InterviewQuestion, Job, ParsedResumeData, Resume, User, db
    from .question_generator import generate_questions
    from .report_generator import generate_pdf_report
    from .resume_parser import extract_years, parse_resume, parse_resume_text, text_from_upload
except ImportError:
    from ats_engine import run_ats_analysis, split_csv
    from config import Config
    from db import Candidate, Company, Interview, InterviewQuestion, Job, ParsedResumeData, Resume, User, db
    from question_generator import generate_questions
    from report_generator import generate_pdf_report
    from resume_parser import extract_years, parse_resume, parse_resume_text, text_from_upload


def json_dumps(value) -> str:
    return json.dumps(value or [], ensure_ascii=False)


def json_loads(value, default=None):
    try:
        return json.loads(value or "")
    except Exception:
        return [] if default is None else default


def user_payload(user: User) -> dict:
    profile = None
    if user.role == "candidate" and user.candidate:
        c = user.candidate
        profile = {"id": c.id, "full_name": c.full_name, "phone": c.phone, "location": c.location, "headline": c.headline, "skills": split_csv(c.skills)}
    if user.role == "company" and user.company:
        co = user.company
        profile = {"id": co.id, "company_name": co.company_name, "industry": co.industry, "location": co.location, "website": co.website}
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role, "is_active": user.is_active, "profile": profile}


def make_token(user: User) -> str:
    return create_access_token(identity=str(user.id), additional_claims={"role": user.role})


def register_candidate(data: dict) -> dict:
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or data.get("name") or email.split("@")[0]).strip()
    if not email or not password:
        raise ValueError("Email and password are required.")
    if User.query.filter_by(email=email).first():
        raise ValueError("A user with this email already exists.")
    user = User(email=email, name=full_name, password_hash=generate_password_hash(password), role="candidate")
    db.session.add(user)
    db.session.flush()
    candidate = Candidate(
        user_id=user.id,
        full_name=full_name,
        phone=data.get("phone", ""),
        location=data.get("location", ""),
        headline=data.get("headline", ""),
        years_of_experience=float(data.get("years_of_experience") or 0),
        current_role=data.get("current_role", ""),
        current_company=data.get("current_company", ""),
        skills=data.get("skills", ""),
        linkedin_url=data.get("linkedin_url", ""),
        portfolio_url=data.get("portfolio_url", ""),
        bio=data.get("bio", ""),
    )
    db.session.add(candidate)
    db.session.commit()
    return {"access_token": make_token(user), "user": user_payload(user)}


def register_company(data: dict) -> dict:
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    company_name = (data.get("company_name") or data.get("name") or "Company").strip()
    if not email or not password:
        raise ValueError("Email and password are required.")
    if User.query.filter_by(email=email).first():
        raise ValueError("A user with this email already exists.")
    user = User(email=email, name=company_name, password_hash=generate_password_hash(password), role="company")
    db.session.add(user)
    db.session.flush()
    company = Company(
        user_id=user.id,
        company_name=company_name,
        industry=data.get("industry", ""),
        website=data.get("website", ""),
        location=data.get("location", ""),
        company_size=data.get("company_size", ""),
        description=data.get("description", ""),
        logo_url=data.get("logo_url", ""),
        contact_person=data.get("contact_person", ""),
        contact_phone=data.get("contact_phone", ""),
    )
    db.session.add(company)
    db.session.commit()
    return {"access_token": make_token(user), "user": user_payload(user)}


def login(data: dict) -> dict:
    email = (data.get("email") or "").strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.is_active or not check_password_hash(user.password_hash, data.get("password") or ""):
        raise PermissionError("Invalid email or password.")
    return {"access_token": make_token(user), "user": user_payload(user)}


def require_role(user: User, role: str):
    if not user or user.role != role:
        raise PermissionError(f"This action requires a {role} account.")


def job_payload(job: Job) -> dict:
    return {
        "id": job.id,
        "company_id": job.company_id,
        "company_name": job.company.company_name if job.company else "",
        "title": job.title,
        "description": job.description,
        "responsibilities": job.responsibilities,
        "qualifications": job.qualifications,
        "required_skills": split_csv(job.required_skills),
        "preferred_skills": split_csv(job.preferred_skills),
        "location": job.location,
        "employment_type": job.employment_type,
        "experience_level": job.experience_level,
        "min_experience_years": job.min_experience_years,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "remote_allowed": job.remote_allowed,
        "status": job.status,
        "ats_pass_threshold": job.ats_pass_threshold,
        "interview_pass_threshold": job.interview_pass_threshold,
        "final_hiring_threshold": job.final_hiring_threshold,
        "created_at": job.created_at.isoformat() if job.created_at else None,
    }


def create_job(company: Company, data: dict) -> Job:
    if not data.get("title"):
        raise ValueError("Job title is required.")
    job = Job(
        company_id=company.id,
        title=data.get("title"),
        description=data.get("description", ""),
        responsibilities=data.get("responsibilities", ""),
        qualifications=data.get("qualifications", ""),
        required_skills=",".join(split_csv(data.get("required_skills"))),
        preferred_skills=",".join(split_csv(data.get("preferred_skills"))),
        location=data.get("location", ""),
        employment_type=data.get("employment_type", "full-time"),
        experience_level=data.get("experience_level", "mid"),
        min_experience_years=float(data.get("min_experience_years") or 0),
        salary_min=float(data["salary_min"]) if data.get("salary_min") not in [None, ""] else None,
        salary_max=float(data["salary_max"]) if data.get("salary_max") not in [None, ""] else None,
        remote_allowed=bool(data.get("remote_allowed", False)),
        status=data.get("status", "open"),
        ats_weight_skills=float(data.get("ats_weight_skills") or 40),
        ats_weight_experience=float(data.get("ats_weight_experience") or 25),
        ats_weight_projects=float(data.get("ats_weight_projects") or 15),
        ats_weight_certifications=float(data.get("ats_weight_certifications") or 10),
        ats_weight_keywords=float(data.get("ats_weight_keywords") or 10),
        ats_pass_threshold=float(data.get("ats_pass_threshold") or 70),
        interview_pass_threshold=float(data.get("interview_pass_threshold") or 70),
        final_hiring_threshold=float(data.get("final_hiring_threshold") or 80),
    )
    db.session.add(job)
    db.session.commit()
    return job


def save_resume_upload(file, candidate: Candidate, job: Job | None = None) -> tuple[Resume, dict, dict]:
    filename = file.filename or "resume.pdf"
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in Config.ALLOWED_RESUME_EXTENSIONS:
        raise ValueError("Upload a PDF, DOCX, DOC, or TXT resume file.")
    Config.RESUME_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = Config.RESUME_UPLOAD_DIR / stored
    file.save(path)
    if ext == "txt":
        raw_text = path.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_resume_text(raw_text)
    else:
        with path.open("rb") as fh:
            parsed = parse_resume(fh, filename)
        raw_text = parsed.get("raw_text", "")
    parsed["experience_years"] = max([extract_years(raw_text)] + [float(x.get("years", 0) or 0) for x in parsed.get("experience", [])])
    ats = run_ats_analysis(parsed, job) if job else {"ats_score": 0, "skill_match_score": 0, "experience_match_score": 0, "keyword_match_score": 0, "project_match_score": 0, "certification_match_score": 0, "matched_skills": [], "missing_skills": [], "recommendations": []}
    resume = Resume(
        candidate_id=candidate.id,
        job_id=job.id if job else None,
        original_filename=filename,
        stored_filename=stored,
        file_path=str(path),
        file_size=path.stat().st_size,
        mime_type=file.mimetype or "application/octet-stream",
        raw_text=raw_text,
        extracted_skills=",".join(parsed.get("skills", [])),
        extracted_experience_years=parsed.get("experience_years", 0),
        extracted_education=json_dumps(parsed.get("education", [])),
        extracted_email=parsed.get("email", ""),
        extracted_phone=parsed.get("phone", ""),
        ats_score=ats.get("ats_score", 0),
        skill_match_score=ats.get("skill_match_score", 0),
        experience_match_score=ats.get("experience_match_score", 0),
        keyword_match_score=ats.get("keyword_match_score", 0),
        project_match_score=ats.get("project_match_score", 0),
        certification_match_score=ats.get("certification_match_score", 0),
        matched_skills=",".join(ats.get("matched_skills", [])),
        missing_skills=",".join(ats.get("missing_skills", [])),
        recommendations="\n".join(ats.get("recommendations", [])),
        status="matched" if job else "parsed",
    )
    db.session.add(resume)
    db.session.flush()
    parsed_data = ParsedResumeData(
        resume_id=resume.id,
        name=parsed.get("name", ""),
        email=parsed.get("email", ""),
        phone=parsed.get("phone", ""),
        summary=parsed.get("summary", ""),
        skills=json_dumps(parsed.get("skills", [])),
        experience=json_dumps(parsed.get("experience", [])),
        education=json_dumps(parsed.get("education", [])),
        projects=json_dumps(parsed.get("projects", [])),
        certifications=json_dumps(parsed.get("certifications", [])),
        ats_score=ats.get("ats_score", 0),
        resume_strength_score=min(100, len(parsed.get("skills", [])) * 4 + len(parsed.get("projects", [])) * 10 + len(parsed.get("education", [])) * 8),
    )
    db.session.add(parsed_data)
    db.session.commit()
    return resume, parsed, ats


def resume_payload(resume: Resume, include_raw: bool = False) -> dict:
    payload = {
        "id": resume.id,
        "candidate_id": resume.candidate_id,
        "job_id": resume.job_id,
        "original_filename": resume.original_filename,
        "ats_score": resume.ats_score,
        "skill_match_score": resume.skill_match_score,
        "experience_match_score": resume.experience_match_score,
        "keyword_match_score": resume.keyword_match_score,
        "project_match_score": resume.project_match_score,
        "certification_match_score": resume.certification_match_score,
        "matched_skills": split_csv(resume.matched_skills),
        "missing_skills": split_csv(resume.missing_skills),
        "recommendations": [x for x in resume.recommendations.split("\n") if x],
        "status": resume.status,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
        "parsed": parsed_payload(resume.parsed_data) if resume.parsed_data else None,
    }
    if include_raw:
        payload["raw_text"] = resume.raw_text
    return payload


def parsed_payload(parsed: ParsedResumeData) -> dict:
    return {
        "name": parsed.name,
        "email": parsed.email,
        "phone": parsed.phone,
        "summary": parsed.summary,
        "skills": json_loads(parsed.skills),
        "experience": json_loads(parsed.experience),
        "education": json_loads(parsed.education),
        "projects": json_loads(parsed.projects),
        "certifications": json_loads(parsed.certifications),
        "ats_score": parsed.ats_score,
        "resume_strength_score": parsed.resume_strength_score,
        "category": parsed.category,
    }


def start_interview(candidate: Candidate, job: Job | None, resume: Resume | None, answer_evaluator=None, total: int = 10) -> Interview:
    parsed = parsed_payload(resume.parsed_data) if resume and resume.parsed_data else {"skills": [], "projects": [], "experience": [], "education": []}
    role = job.title if job else "software engineer"
    questions = generate_questions({**parsed, "raw_text": resume.raw_text if resume else ""}, role, n=total)
    interview = Interview(candidate_id=candidate.id, job_id=job.id if job else None, resume_id=resume.id if resume else None, total_questions=len(questions), status="in_progress")
    db.session.add(interview)
    db.session.flush()
    for index, q in enumerate(questions, start=1):
        domain = q.get("domain", "software_engineering")
        qtype = "project" if domain == "software_engineering" and "project" in q.get("question", "").lower() else "skill"
        db.session.add(InterviewQuestion(
            interview_id=interview.id,
            order_index=index,
            question_type=qtype,
            difficulty=q.get("difficulty", "intermediate"),
            question_text=q.get("question") or q.get("question_text"),
            expected_keywords=",".join(q.get("keywords", [])),
            expected_concepts=json_dumps(q.get("keywords", [])),
            reference=q.get("reference_answer", ""),
        ))
    db.session.commit()
    return interview


def evaluate_interview_answer(question: InterviewQuestion, answer_text: str, answer_evaluator) -> dict:
    keywords = split_csv(question.expected_keywords)
    if answer_evaluator and answer_evaluator.loaded:
        result = answer_evaluator.evaluate(question.question_text, answer_text, question.reference, keywords)
        score = round(result["score"] * 100, 1)
        semantic = result.get("semantic_score", 0)
        keyword_fraction = result.get("keyword_coverage", "0/1")
        try:
            a, b = keyword_fraction.split("/")
            keyword_score = int(a) / max(int(b), 1)
        except Exception:
            keyword_score = 0
    else:
        words = len(answer_text.split())
        keyword_score = sum(1 for k in keywords if k.lower() in answer_text.lower()) / max(len(keywords), 1)
        semantic = min(1, words / 80)
        score = round((keyword_score * 0.55 + semantic * 0.45) * 100, 1)
        result = {"feedback": "Evaluated with the local fallback scorer.", "missing_keywords": [k for k in keywords if k.lower() not in answer_text.lower()]}
    technical = min(10, score / 10)
    completeness = min(10, len(answer_text.split()) / 12)
    depth = min(10, len(set(answer_text.lower().split())) / 10)
    communication = min(10, max(2, len(answer_text.split()) / 14))
    confidence = min(10, max(2, 10 - answer_text.lower().count("maybe") - answer_text.lower().count("not sure")))
    relevance = min(10, max(1, (semantic * 5) + (keyword_score * 5)))
    strengths = []
    weaknesses = []
    if score >= 75:
        strengths.append("Strong technical alignment and clear explanation.")
    if keyword_score >= 0.5:
        strengths.append("Covered expected keywords or concepts.")
    if completeness < 5:
        weaknesses.append("Answer needs more completeness and examples.")
    if keyword_score < 0.4:
        weaknesses.append("Important expected concepts were missing.")
    question.answer_text = answer_text
    question.answered_at = datetime.utcnow()
    question.score = score
    question.technical_accuracy = round(technical, 1)
    question.completeness = round(completeness, 1)
    question.depth = round(depth, 1)
    question.communication = round(communication, 1)
    question.confidence = round(confidence, 1)
    question.relevance = round(relevance, 1)
    question.semantic_score = round(semantic, 3)
    question.keyword_score = round(keyword_score, 3)
    question.feedback = result.get("feedback", "")
    question.strengths = json_dumps(strengths)
    question.weaknesses = json_dumps(weaknesses)
    db.session.commit()
    return question_payload(question)


def complete_interview(interview: Interview) -> dict:
    answered = [q for q in interview.questions if q.answer_text]
    interview.answered_questions = len(answered)
    if answered:
        interview.technical_score = round(sum(q.technical_accuracy for q in answered) / len(answered) * 10, 1)
        interview.communication_score = round(sum(q.communication for q in answered) / len(answered) * 10, 1)
        interview.confidence_score = round(sum(q.confidence for q in answered) / len(answered) * 10, 1)
        interview.overall_score = round(interview.technical_score * 0.4 + interview.communication_score * 0.3 + interview.confidence_score * 0.3, 1)
    if interview.overall_score >= 90:
        interview.recommendation = "highly_recommended"
    elif interview.overall_score >= 75:
        interview.recommendation = "recommended"
    elif interview.overall_score >= 60:
        interview.recommendation = "consider_review"
    else:
        interview.recommendation = "not_recommended"
    strengths = []
    weaknesses = []
    for q in answered:
        strengths.extend(json_loads(q.strengths))
        weaknesses.extend(json_loads(q.weaknesses))
    interview.strengths = json_dumps(list(dict.fromkeys(strengths))[:6] or ["Completed the interview process."])
    interview.weaknesses = json_dumps(list(dict.fromkeys(weaknesses))[:6] or ["Continue adding specific examples and measurable results."])
    interview.feedback = f"Interview completed with {interview.overall_score:.1f}% overall score and {interview.recommendation.replace('_', ' ')} recommendation."
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    db.session.commit()
    return interview_payload(interview)


def question_payload(q: InterviewQuestion) -> dict:
    return {
        "id": q.id,
        "order_index": q.order_index,
        "question_type": q.question_type,
        "difficulty": q.difficulty,
        "question_text": q.question_text,
        "follow_up": q.follow_up,
        "expected_keywords": split_csv(q.expected_keywords),
        "expected_concepts": json_loads(q.expected_concepts),
        "reference": q.reference,
        "answer_text": q.answer_text,
        "score": q.score,
        "technical_accuracy": q.technical_accuracy,
        "completeness": q.completeness,
        "depth": q.depth,
        "communication": q.communication,
        "confidence": q.confidence,
        "relevance": q.relevance,
        "semantic_score": q.semantic_score,
        "keyword_score": q.keyword_score,
        "feedback": q.feedback,
        "strengths": json_loads(q.strengths),
        "weaknesses": json_loads(q.weaknesses),
        "answered_at": q.answered_at.isoformat() if q.answered_at else None,
    }


def interview_payload(interview: Interview) -> dict:
    return {
        "id": interview.id,
        "candidate_id": interview.candidate_id,
        "job_id": interview.job_id,
        "resume_id": interview.resume_id,
        "total_questions": interview.total_questions,
        "answered_questions": interview.answered_questions,
        "skipped_questions": interview.skipped_questions,
        "overall_score": interview.overall_score,
        "technical_score": interview.technical_score,
        "communication_score": interview.communication_score,
        "confidence_score": interview.confidence_score,
        "feedback": interview.feedback,
        "strengths": json_loads(interview.strengths),
        "weaknesses": json_loads(interview.weaknesses),
        "recommendation": interview.recommendation,
        "status": interview.status,
        "started_at": interview.started_at.isoformat() if interview.started_at else None,
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
        "questions": [question_payload(q) for q in sorted(interview.questions, key=lambda x: x.order_index)],
    }
