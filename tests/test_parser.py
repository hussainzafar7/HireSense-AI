from pathlib import Path

from reportlab.pdfgen import canvas

from backend.resume_parser import parse_resume


def make_resume_pdf(path: Path):
    c = canvas.Canvas(str(path))
    lines = [
        "Jane Developer",
        "jane@example.com | 555-123-4567",
        "Skills: Python, SQL, Docker, React, Git, AWS, pandas",
        "Education: Bachelor of Science in Computer Science, Example University, 2021",
        "Experience: Software Engineer at Acme Corp, 3 years building APIs and data pipelines.",
        "Projects: Resume Analyzer using Python, Flask, SQL, Docker, and React.",
        "Certifications: AWS Cloud Practitioner",
    ]
    y = 760
    for line in lines:
        c.drawString(72, y, line)
        y -= 22
    c.save()


def test_pdf_resume_parser_extracts_core_fields(tmp_path):
    path = tmp_path / "resume.pdf"
    make_resume_pdf(path)
    parsed = parse_resume(path)
    assert parsed["name"]
    assert parsed["email"] == "jane@example.com"
    assert parsed["phone"]
    assert "Python" in parsed["skills"]
    assert "SQL" in parsed["skills"]
    assert parsed["word_count"] > 20
