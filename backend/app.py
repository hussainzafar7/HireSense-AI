from flask import Flask, jsonify
from extensions import db, jwt, bcrypt, cors
from config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        from models import (User, Candidate, Company, Job, Resume,
                            ParsedResumeData, Interview, InterviewQuestion)
        db.create_all()

    from routes.auth           import auth_bp
    from routes.jobs           import jobs_bp
    from routes.resume         import resume_bp
    from routes.interview      import interview_bp
    from routes.interview_room import interview_room_bp
    from routes.dashboard      import dashboard_bp
    from routes.ai             import ai_bp

    app.register_blueprint(auth_bp,           url_prefix="/api/auth")
    app.register_blueprint(jobs_bp,           url_prefix="/api/jobs")
    app.register_blueprint(resume_bp,         url_prefix="/api/resume")
    app.register_blueprint(interview_bp,      url_prefix="/api/interview")
    app.register_blueprint(interview_room_bp, url_prefix="/api/interview-room")
    app.register_blueprint(dashboard_bp,      url_prefix="/api/dashboard")
    app.register_blueprint(ai_bp,             url_prefix="/api/ai")

    @jwt.unauthorized_loader
    def unauthorized(reason):
        return jsonify({"error": "Missing or invalid token"}), 401

    @jwt.expired_token_loader
    def expired(header, payload):
        return jsonify({"error": "Token expired"}), 401

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large. Max 16MB."}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
