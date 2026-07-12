from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import register_candidate, register_company, login, get_profile

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register/candidate", methods=["POST"])
def reg_candidate():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    result, code = register_candidate(data)
    return jsonify(result), code

@auth_bp.route("/register/company", methods=["POST"])
def reg_company():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password") or not data.get("company_name"):
        return jsonify({"error": "Email, password, and company_name required"}), 400
    result, code = register_company(data)
    return jsonify(result), code

@auth_bp.route("/login", methods=["POST"])
def login_route():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    result, code = login(data["email"], data["password"])
    return jsonify(result), code

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    result, code = get_profile(user_id)
    return jsonify(result), code
