from extensions import db, bcrypt
from models import User, Candidate, Company
from flask_jwt_extended import create_access_token

def register_candidate(data):
    if User.query.filter_by(email=data["email"]).first():
        return {"error": "Email already registered"}, 409
    pw_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(email=data["email"], password_hash=pw_hash, role="candidate")
    db.session.add(user)
    db.session.flush()
    candidate = Candidate(
        user_id=user.id,
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
        location=data.get("location", ""),
        headline=data.get("headline", ""),
        years_of_experience=float(data.get("years_of_experience", 0)),
        current_role=data.get("current_role", ""),
        current_company=data.get("current_company", ""),
        education=data.get("education", ""),
        skills=data.get("skills", ""),
        linkedin_url=data.get("linkedin_url", ""),
        portfolio_url=data.get("portfolio_url", ""),
        bio=data.get("bio", ""),
    )
    db.session.add(candidate)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": "candidate", "profile_id": candidate.id, "full_name": candidate.full_name}}, 201

def register_company(data):
    if User.query.filter_by(email=data["email"]).first():
        return {"error": "Email already registered"}, 409
    pw_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(email=data["email"], password_hash=pw_hash, role="company")
    db.session.add(user)
    db.session.flush()
    company = Company(
        user_id=user.id,
        company_name=data.get("company_name", ""),
        industry=data.get("industry", ""),
        website=data.get("website", ""),
        location=data.get("location", ""),
        company_size=data.get("company_size", ""),
        description=data.get("description", ""),
        contact_person=data.get("contact_person", ""),
        contact_phone=data.get("contact_phone", ""),
    )
    db.session.add(company)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": "company", "profile_id": company.id, "company_name": company.company_name}}, 201

def login(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return {"error": "Invalid email or password"}, 401
    token = create_access_token(identity=str(user.id))
    profile = None
    if user.role == "candidate" and user.candidate:
        c = user.candidate
        profile = {"id": c.id, "full_name": c.full_name, "headline": c.headline, "skills": c.skills}
    elif user.role == "company" and user.company:
        c = user.company
        profile = {"id": c.id, "company_name": c.company_name, "industry": c.industry, "location": c.location}
    return {"token": token, "user": {"id": user.id, "email": user.email, "role": user.role, "profile": profile}}, 200

def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404
    if user.role == "candidate":
        c = user.candidate
        return {"user": {"id": user.id, "email": user.email, "role": "candidate", "profile": {"id": c.id, "full_name": c.full_name, "phone": c.phone, "location": c.location, "headline": c.headline, "years_of_experience": c.years_of_experience, "current_role": c.current_role, "current_company": c.current_company, "education": c.education, "skills": c.skills, "linkedin_url": c.linkedin_url, "portfolio_url": c.portfolio_url, "bio": c.bio}}}, 200
    else:
        c = user.company
        return {"user": {"id": user.id, "email": user.email, "role": "company", "profile": {"id": c.id, "company_name": c.company_name, "industry": c.industry, "website": c.website, "location": c.location, "company_size": c.company_size, "description": c.description, "contact_person": c.contact_person, "contact_phone": c.contact_phone}}}, 200
