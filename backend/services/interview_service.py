import json
from datetime import datetime, timezone
from extensions import db
from models import Interview, InterviewQuestion


def calculate_overall_score(interview_id):
    interview = Interview.query.get(interview_id)
    if not interview:
        return {"error": "Interview not found"}, 404
    questions = InterviewQuestion.query.filter_by(interview_id=interview_id).all()
    answered = [q for q in questions if q.answer_text]
    if not answered:
        return {"overall_score": 0, "technical_score": 0, "communication_score": 0, "confidence_score": 0}
    interview.answered_questions = len(answered)
    total_scores = [q.score or 0 for q in answered]
    avg_score = sum(total_scores) / len(total_scores)
    technical = sum(getattr(q, "technical_accuracy", 0) or 0 for q in answered) / len(answered)
    communication = sum(getattr(q, "communication", 0) or 0 for q in answered) / len(answered)
    confidence = sum(getattr(q, "confidence", 0) or 0 for q in answered) / len(answered)
    overall = technical * 0.4 + communication * 0.3 + confidence * 0.3
    interview.technical_score = round(technical * 10, 1)
    interview.communication_score = round(communication * 10, 1)
    interview.confidence_score = round(confidence * 10, 1)
    interview.overall_score = round(overall * 10, 1)
    if interview.overall_score >= 90:
        interview.recommendation = "highly_recommended"
    elif interview.overall_score >= 75:
        interview.recommendation = "recommended"
    elif interview.overall_score >= 60:
        interview.recommendation = "consider_review"
    else:
        interview.recommendation = "not_recommended"
    strengths = []
    weaknesses = []
    for q in answered:
        if q.strengths:
            try:
                strengths.extend(json.loads(q.strengths) if isinstance(q.strengths, str) else q.strengths)
            except Exception:
                pass
        if q.weaknesses:
            try:
                weaknesses.extend(json.loads(q.weaknesses) if isinstance(q.weaknesses, str) else q.weaknesses)
            except Exception:
                pass
    interview.strengths = json.dumps(list(dict.fromkeys(strengths))[:6] or ["Completed the interview process."])
    interview.weaknesses = json.dumps(list(dict.fromkeys(weaknesses))[:6] or ["Continue adding specific examples and measurable results."])
    interview.status = "completed"
    interview.completed_at = datetime.now(timezone.utc)
    interview.feedback = f"Interview completed with {interview.overall_score:.1f}% overall score and {interview.recommendation.replace('_', ' ')} recommendation."
    db.session.commit()
    return {
        "overall_score": interview.overall_score,
        "technical_score": interview.technical_score,
        "communication_score": interview.communication_score,
        "confidence_score": interview.confidence_score,
        "recommendation": interview.recommendation,
        "strengths": json.loads(interview.strengths),
        "weaknesses": json.loads(interview.weaknesses),
        "feedback": interview.feedback,
    }, 200


def generate_report_local(interview_id):
    interview = Interview.query.get(interview_id)
    if not interview:
        return {"error": "Interview not found"}, 404
    questions = InterviewQuestion.query.filter_by(interview_id=interview_id).order_by(InterviewQuestion.order_index).all()
    if interview.status != "completed":
        calc_result, _ = calculate_overall_score(interview_id)
        if isinstance(calc_result, dict) and "error" in calc_result:
            return calc_result, 404
    question_data = []
    for q in questions:
        answer = {}
        if q.answer_text:
            answer = {
                "candidate_answer": q.answer_text,
                "score": (q.score or 0) / 100.0 if (q.score or 0) > 1 else (q.score or 0),
                "feedback": q.feedback or "",
            }
        question_data.append({
            "id": q.id,
            "order_index": q.order_index,
            "question_text": q.question_text,
            "domain": q.question_type or "technical",
            "difficulty": q.difficulty or "intermediate",
            "answer": answer,
        })
    strengths = []
    weaknesses = []
    if interview.strengths:
        try:
            strengths = json.loads(interview.strengths) if isinstance(interview.strengths, str) else interview.strengths
        except Exception:
            strengths = []
    if interview.weaknesses:
        try:
            weaknesses = json.loads(interview.weaknesses) if isinstance(interview.weaknesses, str) else interview.weaknesses
        except Exception:
            weaknesses = []
    return {
        "interview_id": interview.id,
        "candidate_id": interview.candidate_id,
        "job_id": interview.job_id,
        "overall_score": interview.overall_score or 0,
        "technical_score": interview.technical_score or 0,
        "communication_score": interview.communication_score or 0,
        "confidence_score": interview.confidence_score or 0,
        "recommendation": interview.recommendation or "",
        "strengths": strengths or ["Completed the interview process."],
        "weaknesses": weaknesses or ["Continue adding specific examples and measurable results."],
        "feedback": interview.feedback or "",
        "questions": question_data,
        "status": interview.status,
        "started_at": interview.started_at.isoformat() if interview.started_at else "",
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else "",
    }, 200
