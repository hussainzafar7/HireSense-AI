from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Interview, InterviewQuestion, Candidate, Job, User

interview_bp = Blueprint("interview", __name__)

def get_candidate_id(user_id):
    user = User.query.get(user_id)
    if user and user.candidate:
        return user.candidate.id
    return None

@interview_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403
    interviews = Interview.query.filter_by(candidate_id=candidate_id).order_by(Interview.started_at.desc()).all()
    result = []
    for i in interviews:
        job_title = ""
        if i.job_id:
            job = Job.query.get(i.job_id)
            job_title = job.title if job else ""
        result.append({
            "id": i.id, "job_title": job_title,
            "overall_score": i.overall_score or 0,
            "status": i.status, "recommendation": i.recommendation or "",
            "total_questions": i.total_questions, "answered_questions": i.answered_questions,
            "started_at": i.started_at.isoformat() if i.started_at else "",
            "completed_at": i.completed_at.isoformat() if i.completed_at else "",
        })
    return jsonify(result), 200
