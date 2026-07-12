from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity  # type: ignore[import]
from models import User, Candidate, Company
from services.dashboard_service import get_company_dashboard, get_candidate_dashboard, get_hiring_funnel

dashboard_bp = Blueprint("dashboard", __name__)

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

@dashboard_bp.route("/company", methods=["GET"])
@jwt_required()
def company_dashboard():
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    if not company_id:
        return jsonify({"error": "Company access required"}), 403
    result, code = get_company_dashboard(company_id)
    return jsonify(result), code

@dashboard_bp.route("/candidate", methods=["GET"])
@jwt_required()
def candidate_dashboard():
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403
    result, code = get_candidate_dashboard(candidate_id)
    return jsonify(result), code

@dashboard_bp.route("/report/funnel", methods=["GET"])
@jwt_required()
def funnel():
    user_id = int(get_jwt_identity())
    company_id = get_company_id(user_id)
    if not company_id:
        return jsonify({"error": "Company access required"}), 403
    result, code = get_hiring_funnel(company_id)
    return jsonify(result), code
