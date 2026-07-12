import io
import subprocess
import sys

from reportlab.pdfgen import canvas

from backend.app import create_app
from backend.db import db


def ensure_artifacts():
    subprocess.run([sys.executable, "training/preprocess.py"], check=True)
    subprocess.run([sys.executable, "training/train_evaluator.py"], check=True)
    subprocess.run([sys.executable, "training/train_resume_scorer.py"], check=True)


def resume_bytes():
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    lines = [
        "John Candidate",
        "john@example.com | 555-987-6543",
        "Skills: Python, SQL, Docker, Kubernetes, React, Git, AWS, testing",
        "Education: Master of Science in Computer Science, Demo University",
        "Experience: Backend Engineer with 4 years building REST APIs and cloud services.",
        "Projects: Interview platform using Flask, SQLite, Docker, and React.",
    ]
    y = 760
    for line in lines:
        c.drawString(72, y, line)
        y -= 22
    c.save()
    buf.seek(0)
    return buf


def client():
    ensure_artifacts()
    app = create_app(testing=True)
    return app.test_client()


def test_health_register_and_full_flow():
    c = client()
    health = c.get("/api/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"
    reg = c.post("/api/register", json={"email": "john@example.com", "password": "secret123", "name": "John Candidate"})
    assert reg.status_code == 200
    login = c.post("/api/login", json={"email": "john@example.com", "password": "secret123"})
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    upload = c.post(
        "/api/upload-resume",
        headers={"Authorization": f"Bearer {token}"},
        data={"job_role": "backend engineer", "resume": (resume_bytes(), "resume.pdf")},
        content_type="multipart/form-data",
    )
    assert upload.status_code == 200, upload.get_data(as_text=True)
    sid = upload.get_json()["session_id"]
    qs = c.get(f"/api/questions/{sid}")
    assert qs.status_code == 200
    questions = qs.get_json()["questions"]
    assert len(questions) >= 10
    answer = c.post("/api/submit-answer", json={"question_id": questions[0]["id"], "candidate_answer": "This concept matters because it improves design, testing, scalability, and maintainability in practical systems."})
    assert answer.status_code == 200, answer.get_data(as_text=True)
    report = c.get(f"/api/report/{sid}")
    assert report.status_code == 200
    pdf = c.get(f"/api/report/{sid}?format=pdf")
    assert pdf.status_code == 200
    assert len(pdf.data) > 1000
