from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Resume, ParsedResumeData, Candidate, User, Job, Company
from services.resume_service import upload_resume, match_resume
import json

resume_bp = Blueprint("resume", __name__)

def get_candidate_id(user_id):
    user = User.query.get(user_id)
    if user and user.candidate:
        return user.candidate.id
    return None

def get_company_id(user_id):
    user = User.query.get(user_id)
    if user and user.company:
        return user.company.id
    return None

@resume_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    job_id = request.form.get("job_id", type=int)
    result, code = upload_resume(candidate_id, file, job_id)
    return jsonify(result), code

@resume_bp.route("/match/<int:job_id>", methods=["POST"])
@jwt_required()
def match(job_id):
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403
    resume = Resume.query.filter_by(candidate_id=candidate_id).order_by(Resume.created_at.desc()).first()
    if not resume:
        return jsonify({"error": "No resume found. Upload one first."}), 404
    result, code = match_resume(resume.id, job_id)
    return jsonify(result), code

@resume_bp.route("/mine", methods=["GET"])
@jwt_required()
def mine():
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403
    resumes = Resume.query.filter_by(candidate_id=candidate_id).order_by(Resume.created_at.desc()).all()
    result = []
    for r in resumes:
        job_title = ""
        if r.job_id:
            job = Job.query.get(r.job_id)
            job_title = job.title if job else ""
        result.append({
            "id": r.id, "original_filename": r.original_filename, "status": r.status,
            "ats_score": r.ats_score or 0, "job_title": job_title,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })
    return jsonify(result), 200

@resume_bp.route("/<int:resume_id>", methods=["GET"])
@jwt_required()
def get_resume(resume_id):
    r = Resume.query.get(resume_id)
    if not r:
        return jsonify({"error": "Resume not found"}), 404
    p = r.parsed_data
    return jsonify({
        "id": r.id, "original_filename": r.original_filename, "status": r.status,
        "ats_score": r.ats_score, "skill_match_score": r.skill_match_score,
        "experience_match_score": r.experience_match_score,
        "project_match_score": r.project_match_score,
        "certification_match_score": r.certification_match_score,
        "keyword_match_score": r.keyword_match_score,
        "matched_skills": (r.matched_skills or "").split(",") if r.matched_skills else [],
        "missing_skills": (r.missing_skills or "").split(",") if r.missing_skills else [],
        "recommendations": r.recommendations,
        "parsed_data": {
            "name": p.name if p else "", "email": p.email if p else "",
            "phone": p.phone if p else "", "location": p.location if p else "",
            "linkedin": p.linkedin if p else "", "github": p.github if p else "",
            "portfolio": p.portfolio if p else "", "summary": p.summary if p else "",
            "skills": json.loads(p.skills) if p and p.skills else [],
            "experience": json.loads(p.experience) if p and p.experience else [],
            "education": json.loads(p.education) if p and p.education else [],
            "projects": json.loads(p.projects) if p and p.projects else [],
            "certifications": json.loads(p.certifications) if p and p.certifications else [],
            "languages": json.loads(p.languages) if p and p.languages else [],
            "resume_strength_score": p.resume_strength_score if p else 0,
            "action_word_count": p.action_word_count if p else 0,
        } if p else None,
    }), 200

@resume_bp.route("/<int:resume_id>", methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    r = Resume.query.get(resume_id)
    if not r:
        return jsonify({"error": "Resume not found"}), 404
    p = r.parsed_data
    if p:
        db.session.delete(p)
    db.session.delete(r)
    db.session.commit()
    return jsonify({"message": "Resume deleted"}), 200

@resume_bp.route("/job/<int:job_id>", methods=["GET"])
@jwt_required()
def job_resumes(job_id):
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    job = Job.query.get(job_id)
    if not job or job.company_id != company_id:
        return jsonify({"error": "Unauthorized"}), 403
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.ats_score.desc()).all()
    result = []
    for r in resumes:
        c = Candidate.query.get(r.candidate_id)
        result.append({
            "resume_id": r.id, "candidate_id": r.candidate_id,
            "candidate_name": c.full_name if c else "Unknown",
            "ats_score": r.ats_score or 0, "status": r.status,
            "matched_skills": (r.matched_skills or "").split(",") if r.matched_skills else [],
            "missing_skills": (r.missing_skills or "").split(",") if r.missing_skills else [],
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })
    return jsonify(result), 200

@resume_bp.route("/qualification/<int:job_id>", methods=["GET"])
@jwt_required()
def qualification(job_id):
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    resume = Resume.query.filter_by(candidate_id=candidate_id, job_id=job_id).order_by(Resume.created_at.desc()).first()
    if not resume:
        return jsonify({"qualified": False, "ats_score": 0, "threshold": job.ats_pass_threshold}), 200
    return jsonify({
        "qualified": (resume.ats_score or 0) >= (job.ats_pass_threshold or 70),
        "ats_score": resume.ats_score or 0,
        "threshold": job.ats_pass_threshold,
    }), 200
