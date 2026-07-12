from datetime import datetime
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "hiresense_ai.sqlite"
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="candidate")
    is_active = db.Column(db.Boolean, default=True)
    name = db.Column(db.String(255), nullable=False, default="User")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Candidate(db.Model):
    __tablename__ = "candidates"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(80), default="")
    location = db.Column(db.String(255), default="")
    headline = db.Column(db.String(255), default="")
    years_of_experience = db.Column(db.Float, default=0.0)
    current_role = db.Column(db.String(255), default="")
    current_company = db.Column(db.String(255), default="")
    education = db.Column(Text, default="[]")
    skills = db.Column(Text, default="")
    linkedin_url = db.Column(db.String(500), default="")
    portfolio_url = db.Column(db.String(500), default="")
    avatar_url = db.Column(db.String(500), default="")
    bio = db.Column(Text, default="")
    user = db.relationship("User", backref=db.backref("candidate", uselist=False))


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    company_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255), default="")
    website = db.Column(db.String(500), default="")
    location = db.Column(db.String(255), default="")
    company_size = db.Column(db.String(120), default="")
    description = db.Column(Text, default="")
    logo_url = db.Column(db.String(500), default="")
    contact_person = db.Column(db.String(255), default="")
    contact_phone = db.Column(db.String(80), default="")
    user = db.relationship("User", backref=db.backref("company", uselist=False))


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(Text, nullable=False, default="")
    responsibilities = db.Column(Text, default="")
    qualifications = db.Column(Text, default="")
    required_skills = db.Column(Text, default="")
    preferred_skills = db.Column(Text, default="")
    location = db.Column(db.String(255), default="")
    employment_type = db.Column(db.String(120), default="full-time")
    experience_level = db.Column(db.String(120), default="mid")
    min_experience_years = db.Column(db.Float, default=0.0)
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    remote_allowed = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(30), default="open")
    ats_weight_skills = db.Column(db.Float, default=40.0)
    ats_weight_experience = db.Column(db.Float, default=25.0)
    ats_weight_projects = db.Column(db.Float, default=15.0)
    ats_weight_certifications = db.Column(db.Float, default=10.0)
    ats_weight_keywords = db.Column(db.Float, default=10.0)
    ats_pass_threshold = db.Column(db.Float, default=70.0)
    interview_pass_threshold = db.Column(db.Float, default=70.0)
    final_hiring_threshold = db.Column(db.Float, default=80.0)
    application_deadline = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship("Company", backref="jobs")


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(800), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(160), default="")
    raw_text = db.Column(Text, default="")
    extracted_skills = db.Column(Text, default="")
    extracted_experience_years = db.Column(db.Float, default=0.0)
    extracted_education = db.Column(Text, default="[]")
    extracted_email = db.Column(db.String(255), default="")
    extracted_phone = db.Column(db.String(80), default="")
    ats_score = db.Column(db.Float, default=0.0)
    skill_match_score = db.Column(db.Float, default=0.0)
    experience_match_score = db.Column(db.Float, default=0.0)
    keyword_match_score = db.Column(db.Float, default=0.0)
    project_match_score = db.Column(db.Float, default=0.0)
    certification_match_score = db.Column(db.Float, default=0.0)
    matched_skills = db.Column(Text, default="")
    missing_skills = db.Column(Text, default="")
    recommendations = db.Column(Text, default="")
    status = db.Column(db.String(30), default="uploaded")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidate = db.relationship("Candidate", backref="resumes")
    job = db.relationship("Job", backref="resumes")


class ParsedResumeData(db.Model):
    __tablename__ = "parsed_resume_data"
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False, unique=True)
    name = db.Column(db.String(255), default="")
    email = db.Column(db.String(255), default="")
    phone = db.Column(db.String(80), default="")
    date_of_birth = db.Column(db.String(80), default="")
    location = db.Column(db.String(255), default="")
    nationality = db.Column(db.String(120), default="")
    linkedin = db.Column(db.String(500), default="")
    github = db.Column(db.String(500), default="")
    portfolio = db.Column(db.String(500), default="")
    kaggle = db.Column(db.String(500), default="")
    stackoverflow = db.Column(db.String(500), default="")
    summary = db.Column(Text, default="")
    skills = db.Column(Text, default="[]")
    languages = db.Column(Text, default="[]")
    awards = db.Column(Text, default="[]")
    good_words = db.Column(Text, default="[]")
    experience = db.Column(Text, default="[]")
    education = db.Column(Text, default="[]")
    projects = db.Column(Text, default="[]")
    certifications = db.Column(Text, default="[]")
    action_word_count = db.Column(db.Integer, default=0)
    ats_score = db.Column(db.Float, default=0.0)
    resume_strength_score = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(120), default="software")
    parsing_error = db.Column(Text, default="")
    resume = db.relationship("Resume", backref=db.backref("parsed_data", uselist=False))


class Interview(db.Model):
    __tablename__ = "interviews"
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    total_questions = db.Column(db.Integer, default=10)
    answered_questions = db.Column(db.Integer, default=0)
    skipped_questions = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Float, default=0.0)
    communication_score = db.Column(db.Float, default=0.0)
    technical_score = db.Column(db.Float, default=0.0)
    confidence_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(Text, default="")
    strengths = db.Column(Text, default="[]")
    weaknesses = db.Column(Text, default="[]")
    recommendation = db.Column(db.String(80), default="consider_review")
    recording_path = db.Column(db.String(800), default="")
    transcript_path = db.Column(db.String(800), default="")
    status = db.Column(db.String(30), default="in_progress")
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    candidate = db.relationship("Candidate", backref="interviews")
    job = db.relationship("Job", backref="interviews")
    resume = db.relationship("Resume", backref="interviews")


class InterviewQuestion(db.Model):
    __tablename__ = "interview_questions"
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id"), nullable=False)
    order_index = db.Column(db.Integer, default=0)
    question_type = db.Column(db.String(80), default="skill")
    difficulty = db.Column(db.String(50), default="intermediate")
    question_text = db.Column(Text, nullable=False)
    follow_up = db.Column(Text, default="")
    expected_keywords = db.Column(Text, default="")
    expected_concepts = db.Column(Text, default="[]")
    reference = db.Column(Text, default="")
    answer_text = db.Column(Text, default="")
    answer_audio_path = db.Column(db.String(800), default="")
    answered_at = db.Column(db.DateTime, nullable=True)
    answer_duration = db.Column(db.Float, default=0.0)
    score = db.Column(db.Float, default=0.0)
    technical_accuracy = db.Column(db.Float, default=0.0)
    completeness = db.Column(db.Float, default=0.0)
    depth = db.Column(db.Float, default=0.0)
    communication = db.Column(db.Float, default=0.0)
    confidence = db.Column(db.Float, default=0.0)
    relevance = db.Column(db.Float, default=0.0)
    semantic_score = db.Column(db.Float, default=0.0)
    keyword_score = db.Column(db.Float, default=0.0)
    feedback = db.Column(Text, default="")
    strengths = db.Column(Text, default="[]")
    weaknesses = db.Column(Text, default="[]")
    interview = db.relationship("Interview", backref="questions")


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resume_data_json = db.Column(Text, nullable=False)
    ats_score = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    user = db.relationship("User", backref="sessions")


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    question_text = db.Column(Text, nullable=False)
    domain = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    reference_answer = db.Column(Text, nullable=False)
    keywords_json = db.Column(Text, nullable=False, default="[]")
    session = db.relationship("Session", backref="questions")


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    candidate_answer = db.Column(Text, nullable=False)
    score = db.Column(db.Float, default=0.0)
    label = db.Column(db.String(50), nullable=False)
    feedback = db.Column(Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    question = db.relationship("Question", backref="answers")


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    overall_score = db.Column(db.Float, default=0.0)
    technical_score = db.Column(db.Float, default=0.0)
    communication_score = db.Column(db.Float, default=0.0)
    strengths_json = db.Column(Text, nullable=False, default="[]")
    weaknesses_json = db.Column(Text, nullable=False, default="[]")
    recommendation = db.Column(db.String(80), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    session = db.relationship("Session", backref="reports")


def auto_migrate_sqlite():
    inspector = db.inspect(db.engine)
    migrations = {
        "users": {"role": "VARCHAR(30) DEFAULT 'candidate' NOT NULL", "is_active": "BOOLEAN DEFAULT 1", "name": "VARCHAR(255) DEFAULT 'User' NOT NULL"},
        "jobs": {"ats_weight_projects": "FLOAT DEFAULT 15", "ats_weight_keywords": "FLOAT DEFAULT 10", "final_hiring_threshold": "FLOAT DEFAULT 80"},
        "resumes": {"project_match_score": "FLOAT DEFAULT 0", "certification_match_score": "FLOAT DEFAULT 0", "recommendations": "TEXT DEFAULT ''"},
        "interviews": {"confidence_score": "FLOAT DEFAULT 0", "recording_path": "VARCHAR(800) DEFAULT ''", "transcript_path": "VARCHAR(800) DEFAULT ''"},
        "interview_questions": {"confidence": "FLOAT DEFAULT 0", "relevance": "FLOAT DEFAULT 0", "semantic_score": "FLOAT DEFAULT 0", "keyword_score": "FLOAT DEFAULT 0"},
    }
    existing_tables = set(inspector.get_table_names())
    with db.engine.begin() as conn:
        for table, columns in migrations.items():
            if table not in existing_tables:
                continue
            existing_columns = {col["name"] for col in inspector.get_columns(table)}
            for column, ddl in columns.items():
                if column not in existing_columns:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("SQLALCHEMY_DATABASE_URI") or f"sqlite:///{DB_PATH.as_posix()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if str(app.config["SQLALCHEMY_DATABASE_URI"]).startswith("sqlite"):
            auto_migrate_sqlite()
