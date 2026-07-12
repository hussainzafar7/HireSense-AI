from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Interview, InterviewQuestion, Candidate, Job, Resume, User
from services.question_service import generate_questions
from services.answer_evaluator import evaluator
from services.interview_service import calculate_overall_score, generate_report_local
from services.report_service import generate_pdf_report
import json
import io
from datetime import datetime, timezone

interview_room_bp = Blueprint("interview_room", __name__)

def get_candidate_id(user_id):
    user = User.query.get(user_id)
    if user and user.candidate:
        return user.candidate.id
    return None

@interview_room_bp.route("/start", methods=["POST"])
@jwt_required()
def start_interview():
    user_id = int(get_jwt_identity())
    candidate_id = get_candidate_id(user_id)
    if not candidate_id:
        return jsonify({"error": "Candidate access required"}), 403

    data = request.get_json() or {}
    job_id = data.get("job_id")
    resume_id = data.get("resume_id")

    candidate = Candidate.query.get(candidate_id)
    job = Job.query.get(job_id) if job_id else None
    resume = Resume.query.get(resume_id) if resume_id else None

    parsed_resume = {}
    if resume and resume.parsed_data:
        p = resume.parsed_data
        parsed_resume = {
            "skills": json.loads(p.skills) if p.skills else [],
            "projects": json.loads(p.projects) if p.projects else [],
            "experience": json.loads(p.experience) if p.experience else [],
            "extracted_experience_years": resume.extracted_experience_years or 0,
        }

    questions = generate_questions(parsed_resume, job.title if job else "", num_questions=10)

    interview = Interview(
        candidate_id=candidate_id,
        job_id=job_id,
        resume_id=resume_id,
        total_questions=len(questions),
        status="in_progress",
    )
    db.session.add(interview)
    db.session.flush()

    for i, q in enumerate(questions):
        iq = InterviewQuestion(
            interview_id=interview.id,
            order_index=i + 1,
            question_type=q.get("question_type", "skill"),
            difficulty=q.get("difficulty", "intermediate"),
            question_text=q.get("question_text", ""),
            follow_up=q.get("follow_up", ""),
            expected_keywords=q.get("expected_keywords", ""),
            expected_concepts=q.get("expected_concepts", "[]"),
            reference=q.get("reference", ""),
        )
        db.session.add(iq)

    db.session.commit()

    first = interview.questions[0] if interview.questions else None
    return jsonify({
        "interview_id": interview.id,
        "total_questions": interview.total_questions,
        "current_question": {
            "id": first.id,
            "order_index": first.order_index,
            "question_type": first.question_type,
            "difficulty": first.difficulty,
            "question_text": first.question_text,
            "follow_up": first.follow_up,
        } if first else None,
    }), 201

@interview_room_bp.route("/submit-answer", methods=["POST"])
@jwt_required()
def submit_answer():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    interview_id = data.get("interview_id")
    question_id = data.get("question_id")
    answer_text = data.get("answer_text", "")

    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview.candidate_id != get_candidate_id(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    question = InterviewQuestion.query.get(question_id)
    if not question or question.interview_id != interview_id:
        return jsonify({"error": "Question not found"}), 404

    expected_kw = [k.strip() for k in (question.expected_keywords or "").split(",") if k.strip()]
    expected_concepts = json.loads(question.expected_concepts or "[]")

    result = evaluator.evaluate(
        question=question.question_text,
        answer=answer_text,
        reference=question.reference or "",
        expected_keywords=expected_kw,
        expected_concepts=expected_concepts,
    )

    question.answer_text = answer_text
    question.score = result["score"]
    question.technical_accuracy = result["technical_accuracy"]
    question.completeness = result["completeness"]
    question.depth = result["depth"]
    question.communication = result["communication"]
    question.confidence = result["confidence"]
    question.relevance = result["relevance"]
    question.semantic_score = result["semantic_score"]
    question.keyword_score = result["keyword_score"]
    question.feedback = result["feedback"]
    question.strengths = json.dumps(result["strengths"])
    question.weaknesses = json.dumps(result["weaknesses"])
    question.answered_at = datetime.now(timezone.utc)

    interview.answered_questions = (interview.answered_questions or 0) + 1
    db.session.commit()

    remaining = [q for q in interview.questions if q.score is None or q.score == 0]
    next_q = None
    total_score = None
    for q in remaining:
        if q.id != question_id:
            next_q = {
                "id": q.id, "order_index": q.order_index,
                "question_type": q.question_type, "difficulty": q.difficulty,
                "question_text": q.question_text, "follow_up": q.follow_up,
            }
            break

    if not remaining:
        scores = calculate_overall_score(interview.questions)
        interview.overall_score = scores["overall_score"]
        interview.technical_score = scores["technical_score"]
        interview.communication_score = scores["communication_score"]
        interview.confidence_score = scores["confidence_score"]
        interview.recommendation = scores["recommendation"]
        interview.status = "completed"
        interview.completed_at = datetime.now(timezone.utc)
        report = generate_report_local(interview, interview.questions, "", "")
        interview.feedback = report.get("summary", "")
        interview.strengths = json.dumps(report.get("strengths", []))
        interview.weaknesses = json.dumps(report.get("weaknesses", []))
        db.session.commit()
        total_score = scores

    return jsonify({
        "evaluation": result,
        "next_question": next_q,
        "interview_complete": next_q is None,
        "total_score": total_score,
        "answered": interview.answered_questions,
        "total": interview.total_questions,
    }), 200

@interview_room_bp.route("/skip", methods=["POST"])
@jwt_required()
def skip_question():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    interview_id = data.get("interview_id")
    question_id = data.get("question_id")

    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    if interview.candidate_id != get_candidate_id(user_id):
        return jsonify({"error": "Unauthorized"}), 403

    if (interview.skipped_questions or 0) >= 1:
        return jsonify({"error": "Maximum 1 skip allowed"}), 400

    question = InterviewQuestion.query.get(question_id)
    if not question or question.interview_id != interview_id:
        return jsonify({"error": "Question not found"}), 404

    question.score = 0
    question.technical_accuracy = 0
    question.completeness = 0
    question.depth = 0
    question.communication = 0
    question.confidence = 0
    question.relevance = 0
    question.semantic_score = 0
    question.keyword_score = 0
    question.feedback = "Skipped"
    question.answer_text = "[Skipped]"
    interview.skipped_questions = (interview.skipped_questions or 0) + 1
    interview.answered_questions = (interview.answered_questions or 0) + 1
    db.session.commit()

    remaining = [q for q in interview.questions if q.score is None or q.score == 0]
    next_q = None
    for q in remaining:
        if q.id != question_id:
            next_q = {
                "id": q.id, "order_index": q.order_index,
                "question_type": q.question_type, "difficulty": q.difficulty,
                "question_text": q.question_text, "follow_up": q.follow_up,
            }
            break

    if not remaining:
        scores = calculate_overall_score(interview.questions)
        interview.overall_score = scores["overall_score"]
        interview.technical_score = scores["technical_score"]
        interview.communication_score = scores["communication_score"]
        interview.confidence_score = scores["confidence_score"]
        interview.recommendation = scores["recommendation"]
        interview.status = "completed"
        interview.completed_at = datetime.now(timezone.utc)
        report = generate_report_local(interview, interview.questions, "", "")
        interview.feedback = report.get("summary", "")
        interview.strengths = json.dumps(report.get("strengths", []))
        interview.weaknesses = json.dumps(report.get("weaknesses", []))
        db.session.commit()

    return jsonify({
        "next_question": next_q,
        "interview_complete": next_q is None,
        "skipped": interview.skipped_questions,
        "answered": interview.answered_questions,
        "total": interview.total_questions,
    }), 200

@interview_room_bp.route("/complete", methods=["POST"])
@jwt_required()
def complete():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    interview_id = data.get("interview_id")
    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    scores = calculate_overall_score(interview.questions)
    interview.overall_score = scores["overall_score"]
    interview.technical_score = scores["technical_score"]
    interview.communication_score = scores["communication_score"]
    interview.confidence_score = scores["confidence_score"]
    interview.recommendation = scores["recommendation"]
    interview.status = "completed"
    interview.completed_at = datetime.now(timezone.utc)
    cand = Candidate.query.get(interview.candidate_id)
    job = Job.query.get(interview.job_id) if interview.job_id else None
    report = generate_report_local(interview, interview.questions,
                                    cand.full_name if cand else "",
                                    job.title if job else "")
    interview.feedback = report.get("summary", "")
    interview.strengths = json.dumps(report.get("strengths", []))
    interview.weaknesses = json.dumps(report.get("weaknesses", []))
    db.session.commit()
    return jsonify({"report": report, "interview_id": interview.id}), 200

@interview_room_bp.route("/state/<int:interview_id>", methods=["GET"])
@jwt_required()
def state(interview_id):
    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    questions = interview.questions
    answered = [q for q in questions if q.score is not None and q.score > 0]
    return jsonify({
        "status": interview.status,
        "answered": len(answered),
        "total": len(questions),
        "skipped": interview.skipped_questions or 0,
        "overall_score": interview.overall_score,
        "scores_so_far": [{"q_id": q.id, "score": q.score, "type": q.question_type} for q in answered],
    }), 200

@interview_room_bp.route("/tts", methods=["POST"])
def tts():
    data = request.get_json()
    text = data.get("text", "") if data else ""
    return jsonify({"text": text, "use_browser_tts": True}), 200

@interview_room_bp.route("/transcribe", methods=["POST"])
def transcribe():
    transcript = ""
    if request.is_json:
        transcript = (request.get_json() or {}).get("transcript", "")
    else:
        transcript = request.form.get("transcript", "")
    return jsonify({"transcript": transcript, "language": "en", "duration": 0}), 200

@interview_room_bp.route("/transcript/<int:interview_id>", methods=["GET"])
@jwt_required()
def transcript(interview_id):
    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    result = []
    for q in sorted(interview.questions, key=lambda x: x.order_index):
        result.append({
            "order": q.order_index, "question": q.question_text,
            "answer": q.answer_text or "", "score": q.score or 0,
            "type": q.question_type, "feedback": q.feedback or "",
        })
    return jsonify({"transcript": result}), 200

@interview_room_bp.route("/report/<int:interview_id>", methods=["GET"])
@jwt_required()
def report(interview_id):
    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    cand = Candidate.query.get(interview.candidate_id)
    job = Job.query.get(interview.job_id) if interview.job_id else None
    report_data = generate_report_local(interview, interview.questions,
                                         cand.full_name if cand else "",
                                         job.title if job else "")
    return jsonify(report_data), 200

@interview_room_bp.route("/export-pdf/<int:interview_id>", methods=["POST"])
@jwt_required()
def export_pdf(interview_id):
    interview = Interview.query.get(interview_id)
    if not interview:
        return jsonify({"error": "Interview not found"}), 404
    cand = Candidate.query.get(interview.candidate_id)
    job = Job.query.get(interview.job_id) if interview.job_id else None
    pdf_bytes = generate_pdf_report(interview, interview.questions,
                                     cand.full_name if cand else "",
                                     job.title if job else "")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"hiresense_report_{interview.id}.pdf",
    )
