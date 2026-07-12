import os
import uuid
import json
from pathlib import Path
from extensions import db
from models import Resume, ParsedResumeData, Candidate
from werkzeug.utils import secure_filename
from services.text_extractor import extract_text
from services.local_resume_parser import parse_resume, calculate_resume_strength
from services.ats_engine import run_ats_analysis

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def upload_resume(candidate_id, file, job_id=None):
    if not file or not allowed_file(file.filename):
        return {"error": "Invalid file. Allowed: PDF, DOCX, TXT"}, 400

    ext = os.path.splitext(file.filename)[1].lower()
    stored_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = Path(__file__).parent.parent / "uploads" / "resumes"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / stored_name
    file.save(str(file_path))

    raw_text = extract_text(str(file_path))
    if not raw_text:
        return {"error": "Could not extract text from file"}, 400

    parsed = parse_resume(raw_text)
    strength = calculate_resume_strength(parsed)

    resume = Resume(
        candidate_id=candidate_id,
        job_id=job_id,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=str(file_path),
        file_size=os.path.getsize(file_path),
        mime_type=f"application/{ext[1:]}",
        raw_text=raw_text[:50000],
        extracted_skills=",".join(parsed.get("skills", [])),
        extracted_experience_years=len(parsed.get("experience", [])),
        extracted_education=json.dumps(parsed.get("education", [])),
        extracted_email=parsed.get("email", ""),
        extracted_phone=parsed.get("phone", ""),
        status="parsed",
    )
    db.session.add(resume)
    db.session.flush()

    parsed_data = ParsedResumeData(
        resume_id=resume.id,
        name=parsed.get("name", ""),
        email=parsed.get("email", ""),
        phone=parsed.get("phone", ""),
        location=parsed.get("location", ""),
        linkedin=parsed.get("linkedin", ""),
        github=parsed.get("github", ""),
        portfolio=parsed.get("portfolio", ""),
        summary=parsed.get("summary", ""),
        skills=json.dumps(parsed.get("skills", [])),
        languages=json.dumps(parsed.get("languages", [])),
        experience=json.dumps(parsed.get("experience", [])),
        education=json.dumps(parsed.get("education", [])),
        projects=json.dumps(parsed.get("projects", [])),
        certifications=json.dumps(parsed.get("certifications", [])),
        action_word_count=parsed.get("action_word_count", 0),
        resume_strength_score=strength,
    )
    db.session.add(parsed_data)

    if job_id:
        from models import Job
        job = Job.query.get(job_id)
        if job:
            ats = run_ats_analysis(raw_text, parsed, job)
            resume.ats_score = ats["ats_score"]
            resume.skill_match_score = ats["skill_match_score"]
            resume.experience_match_score = ats["experience_match_score"]
            resume.project_match_score = ats["project_match_score"]
            resume.certification_match_score = ats["certification_match_score"]
            resume.keyword_match_score = ats["keyword_match_score"]
            resume.matched_skills = ",".join(ats["matched_skills"])
            resume.missing_skills = ",".join(ats["missing_skills"])
            resume.recommendations = ats["recommendations"]
            resume.status = "matched"

    db.session.commit()
    return {"resume_id": resume.id, "status": resume.status, "ats_score": resume.ats_score or 0}, 201

def match_resume(resume_id, job_id):
    from models import Job
    resume = Resume.query.get(resume_id)
    job = Job.query.get(job_id)
    if not resume or not job:
        return {"error": "Resume or job not found"}, 404
    if resume.status == "uploaded":
        resume.status = "parsed"
    parsed_data = resume.parsed_data
    parsed = {
        "skills": json.loads(parsed_data.skills) if parsed_data and parsed_data.skills else [],
        "projects": json.loads(parsed_data.projects) if parsed_data and parsed_data.projects else [],
        "certifications": json.loads(parsed_data.certifications) if parsed_data and parsed_data.certifications else [],
        "extracted_experience_years": resume.extracted_experience_years or 0,
    }
    ats = run_ats_analysis(resume.raw_text or "", parsed, job)
    resume.ats_score = ats["ats_score"]
    resume.skill_match_score = ats["skill_match_score"]
    resume.experience_match_score = ats["experience_match_score"]
    resume.project_match_score = ats["project_match_score"]
    resume.certification_match_score = ats["certification_match_score"]
    resume.keyword_match_score = ats["keyword_match_score"]
    resume.matched_skills = ",".join(ats["matched_skills"])
    resume.missing_skills = ",".join(ats["missing_skills"])
    resume.recommendations = ats["recommendations"]
    resume.status = "matched"
    resume.job_id = job_id
    db.session.commit()
    return ats, 200
