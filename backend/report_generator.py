from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def recommendation_from_score(score: float) -> str:
    if score >= 85:
        return "STRONG HIRE"
    if score >= 70:
        return "HIRE"
    if score >= 50:
        return "MAYBE"
    return "PASS"


def summarize_answers(questions: list[dict]) -> tuple[list[str], list[str], float]:
    scores = []
    strengths = []
    weaknesses = []
    for q in questions:
        ans = q.get("answer") or {}
        if ans:
            scores.append(float(ans.get("score", 0)) * 100)
            if ans.get("score", 0) >= 0.7:
                strengths.append(f"Strong answer in {q.get('domain', 'technical')} topics")
            elif ans.get("score", 0) < 0.45:
                weaknesses.append(f"Improve {q.get('domain', 'technical')} explanations and keyword coverage")
    avg = sum(scores) / len(scores) if scores else 0.0
    strengths = list(dict.fromkeys(strengths))[:5] or ["Completed the interview workflow"]
    weaknesses = list(dict.fromkeys(weaknesses))[:5] or ["Add more concrete examples and measurable outcomes"]
    return strengths, weaknesses, avg


def build_report_payload(session: dict, questions: list[dict]) -> dict:
    strengths, weaknesses, technical_score = summarize_answers(questions)
    ats = float(session.get("ats_score", 0))
    overall = round((technical_score * 0.65) + (ats * 0.35), 1) if questions else round(ats, 1)
    communication = round(min(100, technical_score * 0.8 + 20), 1) if questions else 0
    return {
        "overall_score": overall,
        "technical_score": round(technical_score, 1),
        "communication_score": communication,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": recommendation_from_score(overall),
    }


def generate_pdf_report(session: dict, questions: list[dict], payload: dict | None = None) -> bytes:
    payload = payload or build_report_payload(session, questions)
    resume = session.get("resume", {})
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=48, leftMargin=48, topMargin=48, bottomMargin=48)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], textColor=colors.HexColor("#e94560"), fontSize=22)
    heading = ParagraphStyle("Heading", parent=styles["Heading2"], textColor=colors.HexColor("#16213e"))
    story = [Paragraph("HireSense AI Interview Report", title), Spacer(1, 0.15 * inch)]
    story.append(Paragraph(f"Candidate: {resume.get('name', 'Candidate')}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    summary = [["Overall", "Technical", "Communication", "Recommendation"], [f"{payload['overall_score']}%", f"{payload['technical_score']}%", f"{payload['communication_score']}%", payload["recommendation"]]]
    table = Table(summary, colWidths=[1.3 * inch, 1.3 * inch, 1.6 * inch, 1.8 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Skills Detected", heading))
    story.append(Paragraph(", ".join(resume.get("skills", [])[:40]) or "No skills detected", styles["Normal"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Strengths", heading))
    for item in payload["strengths"]:
        story.append(Paragraph(f"✓ {item}", styles["Normal"]))
    story.append(Paragraph("Weaknesses", heading))
    for item in payload["weaknesses"]:
        story.append(Paragraph(f"• {item}", styles["Normal"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Q&A Breakdown", heading))
    for idx, q in enumerate(questions, start=1):
        ans = q.get("answer") or {}
        story.append(Paragraph(f"{idx}. {q.get('question_text') or q.get('question')}", styles["Heading4"]))
        story.append(Paragraph(f"Domain: {q.get('domain')} | Difficulty: {q.get('difficulty')} | Score: {round(float(ans.get('score', 0))*100, 1)}%", styles["Normal"]))
        story.append(Paragraph(f"Answer: {(ans.get('candidate_answer') or '')[:900]}", styles["Normal"]))
        story.append(Paragraph(f"Feedback: {ans.get('feedback', 'No feedback submitted.')}", styles["Normal"]))
        story.append(Spacer(1, 0.08 * inch))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Disclaimer: HireSense AI provides decision support only. Human review and fair hiring practices remain required.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()
