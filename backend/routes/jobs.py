from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Job, Company, User
from sqlalchemy import or_

jobs_bp = Blueprint("jobs", __name__)

def get_company_id(user_id):
    user = User.query.get(user_id)
    if user and user.company:
        return user.company.id
    return None

@jobs_bp.route("", methods=["GET"])
def list_jobs():
    query = Job.query.filter_by(status="open")
    if request.args.get("company_id"):
        query = query.filter_by(company_id=int(request.args["company_id"]))
    if request.args.get("location"):
        query = query.filter(Job.location.ilike(f"%{request.args['location']}%"))
    if request.args.get("employment_type"):
        query = query.filter_by(employment_type=request.args["employment_type"])
    if request.args.get("experience_level"):
        query = query.filter_by(experience_level=request.args["experience_level"])
    if request.args.get("remote_only") == "true":
        query = query.filter_by(remote_allowed=True)
    if request.args.get("search"):
        s = request.args["search"]
        query = query.filter(or_(Job.title.ilike(f"%{s}%"), Job.description.ilike(f"%{s}%")))
    query = query.order_by(Job.created_at.desc())
    jobs = query.all()
    result = []
    for j in jobs:
        company = j.company
        result.append({
            "id": j.id, "title": j.title, "company_name": company.company_name if company else "",
            "location": j.location, "employment_type": j.employment_type,
            "experience_level": j.experience_level, "salary_min": j.salary_min,
            "salary_max": j.salary_max, "remote_allowed": j.remote_allowed,
            "status": j.status, "created_at": j.created_at.isoformat() if j.created_at else "",
            "company_id": j.company_id,
        })
    return jsonify(result), 200

@jobs_bp.route("/mine", methods=["GET"])
@jwt_required()
def my_jobs():
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    if not company_id:
        return jsonify({"error": "Company access required"}), 403
    jobs = Job.query.filter_by(company_id=company_id).order_by(Job.created_at.desc()).all()
    result = []
    for j in jobs:
        result.append({
            "id": j.id, "title": j.title, "status": j.status, "location": j.location,
            "employment_type": j.employment_type, "experience_level": j.experience_level,
            "applications": len(j.resumes) if j.resumes else 0,
            "created_at": j.created_at.isoformat() if j.created_at else "",
        })
    return jsonify(result), 200

@jobs_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id):
    j = Job.query.get(job_id)
    if not j:
        return jsonify({"error": "Job not found"}), 404
    company = j.company
    return jsonify({
        "id": j.id, "title": j.title, "description": j.description,
        "responsibilities": j.responsibilities, "qualifications": j.qualifications,
        "required_skills": j.required_skills, "preferred_skills": j.preferred_skills,
        "location": j.location, "employment_type": j.employment_type,
        "experience_level": j.experience_level, "min_experience_years": j.min_experience_years,
        "salary_min": j.salary_min, "salary_max": j.salary_max,
        "remote_allowed": j.remote_allowed, "status": j.status,
        "ats_weight_skills": j.ats_weight_skills, "ats_weight_experience": j.ats_weight_experience,
        "ats_weight_projects": j.ats_weight_projects,
        "ats_weight_certifications": j.ats_weight_certifications,
        "ats_weight_keywords": j.ats_weight_keywords,
        "ats_pass_threshold": j.ats_pass_threshold,
        "interview_pass_threshold": j.interview_pass_threshold,
        "final_hiring_threshold": j.final_hiring_threshold,
        "application_deadline": j.application_deadline.isoformat() if j.application_deadline else "",
        "company_name": company.company_name if company else "",
        "company": {"id": company.id, "company_name": company.company_name, "industry": company.industry,
                     "location": company.location, "description": company.description,
                     "website": company.website, "logo_url": company.logo_url} if company else None,
    }), 200

@jobs_bp.route("", methods=["POST"])
@jwt_required()
def create_job():
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    if not company_id:
        return jsonify({"error": "Company access required"}), 403
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Job title is required"}), 400
    job = Job(
        company_id=company_id, title=data["title"],
        description=data.get("description", ""),
        responsibilities=data.get("responsibilities", ""),
        qualifications=data.get("qualifications", ""),
        required_skills=data.get("required_skills", ""),
        preferred_skills=data.get("preferred_skills", ""),
        location=data.get("location", ""),
        employment_type=data.get("employment_type", ""),
        experience_level=data.get("experience_level", ""),
        min_experience_years=float(data.get("min_experience_years", 0)),
        salary_min=float(data.get("salary_min", 0)) if data.get("salary_min") else None,
        salary_max=float(data.get("salary_max", 0)) if data.get("salary_max") else None,
        remote_allowed=data.get("remote_allowed", False),
        status=data.get("status", "open"),
        ats_weight_skills=int(data.get("ats_weight_skills", 40)),
        ats_weight_experience=int(data.get("ats_weight_experience", 25)),
        ats_weight_projects=int(data.get("ats_weight_projects", 15)),
        ats_weight_certifications=int(data.get("ats_weight_certifications", 10)),
        ats_weight_keywords=int(data.get("ats_weight_keywords", 10)),
        ats_pass_threshold=int(data.get("ats_pass_threshold", 70)),
        interview_pass_threshold=int(data.get("interview_pass_threshold", 70)),
        final_hiring_threshold=int(data.get("final_hiring_threshold", 80)),
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"id": job.id, "title": job.title, "status": job.status}), 201

@jobs_bp.route("/<int:job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    job = Job.query.get(job_id)
    if not job or job.company_id != company_id:
        return jsonify({"error": "Job not found or unauthorized"}), 404
    data = request.get_json()
    for field in ["title", "description", "responsibilities", "qualifications",
                  "required_skills", "preferred_skills", "location", "employment_type",
                  "experience_level", "status"]:
        if field in data:
            setattr(job, field, data[field])
    for num_field in ["min_experience_years", "salary_min", "salary_max",
                      "ats_weight_skills", "ats_weight_experience", "ats_weight_projects",
                      "ats_weight_certifications", "ats_weight_keywords",
                      "ats_pass_threshold", "interview_pass_threshold", "final_hiring_threshold"]:
        if num_field in data:
            setattr(job, num_field, float(data[num_field]) if "." in num_field else int(data[num_field]))
    if "remote_allowed" in data:
        job.remote_allowed = data["remote_allowed"]
    db.session.commit()
    return jsonify({"id": job.id, "title": job.title, "status": job.status}), 200

@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    job = Job.query.get(job_id)
    if not job or job.company_id != company_id:
        return jsonify({"error": "Job not found or unauthorized"}), 404
    job.status = "closed"
    db.session.commit()
    return jsonify({"message": "Job closed"}), 200
