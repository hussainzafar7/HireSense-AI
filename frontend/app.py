import html
import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_BASE = os.environ.get("HIRESENSE_API", "http://localhost:5000")

st.set_page_config(page_title="HireSense AI", page_icon="HS", layout="wide")

st.markdown(
    """
<style>
:root {
  --hs-primary: #0369A1;
  --hs-secondary: #0EA5E9;
  --hs-accent: #16A34A;
  --hs-bg: #F0F9FF;
  --hs-surface: #FFFFFF;
  --hs-surface-strong: #E7EFF5;
  --hs-text: #0C4A6E;
  --hs-text-muted: #47657A;
  --hs-border: #BAE6FD;
  --hs-danger: #DC2626;
  --hs-warning: #B45309;
  --hs-ring: #0369A1;
  --hs-shadow: 0 18px 45px rgba(12, 74, 110, 0.12);
  --hs-radius: 22px;
}

.stApp {
  background:
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.18), transparent 34rem),
    linear-gradient(180deg, #F0F9FF 0%, #FFFFFF 46%, #F8FBFD 100%);
  color: var(--hs-text);
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0C4A6E 0%, #075985 100%);
}

[data-testid="stSidebar"] * {
  color: #FFFFFF !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 14px;
  padding: 0.5rem 0.75rem;
  margin: 0.35rem 0;
  background: rgba(255, 255, 255, 0.08);
  min-height: 44px;
  transition: background 180ms ease, border-color 180ms ease, transform 180ms ease;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: rgba(255, 255, 255, 0.16);
  border-color: rgba(255, 255, 255, 0.36);
}

.block-container {
  max-width: 1240px;
  padding-top: 2.2rem;
  padding-bottom: 4rem;
}

h1, h2, h3 {
  color: var(--hs-text);
  letter-spacing: -0.035em;
}

p, li, label, .stMarkdown, .stCaption, [data-testid="stMetricLabel"] {
  color: var(--hs-text-muted);
}

.hs-hero {
  background:
    linear-gradient(135deg, rgba(3, 105, 161, 0.96), rgba(14, 165, 233, 0.88)),
    linear-gradient(45deg, #075985, #0369A1);
  border-radius: 28px;
  padding: clamp(1.5rem, 4vw, 3.5rem);
  color: #FFFFFF;
  box-shadow: var(--hs-shadow);
  border: 1px solid rgba(255, 255, 255, 0.22);
  margin-bottom: 1.25rem;
}

.hs-hero h1 {
  color: #FFFFFF;
  font-size: clamp(2.2rem, 5vw, 4.7rem);
  line-height: 0.98;
  margin: 0 0 1rem 0;
}

.hs-hero p {
  color: rgba(255, 255, 255, 0.88);
  font-size: clamp(1rem, 2vw, 1.18rem);
  line-height: 1.65;
  max-width: 740px;
}

.hs-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 34px;
  padding: 0.35rem 0.75rem;
  margin-bottom: 1rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.24);
  color: #FFFFFF;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  font-size: 0.78rem;
}

.hs-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid var(--hs-border);
  border-radius: var(--hs-radius);
  box-shadow: var(--hs-shadow);
  padding: 1.25rem;
  margin: 0.6rem 0 1rem 0;
}

.hs-card-compact {
  background: rgba(255, 255, 255, 0.90);
  border: 1px solid var(--hs-border);
  border-radius: 18px;
  padding: 1rem;
  margin: 0.5rem 0;
}

.hs-kpi {
  background: linear-gradient(180deg, #FFFFFF, #F7FCFF);
  border: 1px solid var(--hs-border);
  border-radius: 20px;
  padding: 1rem;
  min-height: 118px;
  box-shadow: 0 12px 30px rgba(12, 74, 110, 0.08);
}

.hs-kpi span {
  color: var(--hs-text-muted);
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.hs-kpi strong {
  color: var(--hs-text);
  display: block;
  font-size: 2rem;
  line-height: 1.15;
  margin-top: 0.45rem;
}

.hs-badge, .hs-badge-success, .hs-badge-muted, .hs-badge-warning {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0.28rem 0.68rem;
  margin: 0.18rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  border: 1px solid transparent;
}

.hs-badge { background: #E0F2FE; color: #075985; border-color: #BAE6FD; }
.hs-badge-success { background: #DCFCE7; color: #166534; border-color: #BBF7D0; }
.hs-badge-muted { background: #F1F5F9; color: #334155; border-color: #E2E8F0; }
.hs-badge-warning { background: #FEF3C7; color: #92400E; border-color: #FDE68A; }

.hs-step {
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: 18px;
  background: #FFFFFF;
  border: 1px solid var(--hs-border);
  height: 100%;
}

.hs-step-index {
  width: 2rem;
  min-width: 2rem;
  height: 2rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--hs-primary);
  color: #FFFFFF;
  font-weight: 800;
}

.hs-question {
  border-left: 5px solid var(--hs-primary);
  background: #FFFFFF;
  border-radius: 18px;
  padding: 1.25rem;
  box-shadow: var(--hs-shadow);
  border-top: 1px solid var(--hs-border);
  border-right: 1px solid var(--hs-border);
  border-bottom: 1px solid var(--hs-border);
}

.hs-muted { color: var(--hs-text-muted); }
.hs-divider { height: 1px; background: var(--hs-border); margin: 1rem 0; }

.stButton > button,
.stDownloadButton > button {
  min-height: 44px;
  border-radius: 14px !important;
  font-weight: 800 !important;
  border: 1px solid var(--hs-border) !important;
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(3, 105, 161, 0.16) !important;
  border-color: var(--hs-primary) !important;
}

.stButton > button:focus,
.stDownloadButton > button:focus,
input:focus,
textarea:focus {
  outline: 3px solid rgba(3, 105, 161, 0.28) !important;
  outline-offset: 2px !important;
}

[data-testid="stFileUploader"] section {
  border-radius: 18px;
  border-color: var(--hs-border);
  background: #FFFFFF;
}

[data-testid="stDataFrame"] {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid var(--hs-border);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
""",
    unsafe_allow_html=True,
)


PAGES = ["Home", "Upload Resume", "Interview", "Final Report", "History"]


def safe(value: Any) -> str:
    return html.escape(str(value or ""))


def init_state():
    defaults = {
        "token": None,
        "user": None,
        "page": "Home",
        "session_id": None,
        "questions": [],
        "current_idx": 0,
        "answers": [],
        "resume": None,
        "ats": None,
        "api_online": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}


def show_notice(message: str, level: str = "info"):
    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)


def api(method, path, **kwargs):
    try:
        merged_headers = {**headers(), **kwargs.pop("headers", {})}
        response = requests.request(method, f"{API_BASE}{path}", headers=merged_headers, timeout=60, **kwargs)
        content_type = response.headers.get("content-type", "")
        data = response.json() if "application/json" in content_type else response.content
        if response.status_code >= 400:
            if isinstance(data, dict):
                msg = data.get("error") or data.get("message") or "The request could not be completed."
            else:
                msg = "The request could not be completed. Please check the backend logs."
            show_notice(msg, "error")
            return None
        return data
    except requests.exceptions.ConnectionError:
        show_notice("Backend is not reachable. Start the Flask API, then try again.", "error")
    except requests.exceptions.Timeout:
        show_notice("The request timed out. Please retry in a moment.", "error")
    except requests.exceptions.RequestException:
        show_notice("A network error occurred. Please verify the API URL and retry.", "error")
    return None


def check_health():
    data = api("GET", "/api/health")
    st.session_state.api_online = bool(data and data.get("status") == "ok")
    return data


def metric_card(label: str, value: str, helper: str = ""):
    st.markdown(
        f"""
<div class="hs-kpi">
  <span>{safe(label)}</span>
  <strong>{safe(value)}</strong>
  <p class="hs-muted">{safe(helper)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = ""):
    st.markdown(f"### {safe(title)}")
    if subtitle:
        st.caption(subtitle)


def gauge(value, title):
    numeric = max(0.0, min(100.0, float(value or 0)))
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=numeric,
            number={"suffix": "%", "font": {"size": 34, "color": "#0C4A6E"}},
            title={"text": title, "font": {"size": 17, "color": "#0C4A6E"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#47657A"},
                "bar": {"color": "#0369A1", "thickness": 0.22},
                "bgcolor": "#FFFFFF",
                "borderwidth": 1,
                "bordercolor": "#BAE6FD",
                "steps": [
                    {"range": [0, 50], "color": "#FEE2E2"},
                    {"range": [50, 75], "color": "#FEF3C7"},
                    {"range": [75, 100], "color": "#DCFCE7"},
                ],
                "threshold": {"line": {"color": "#16A34A", "width": 4}, "thickness": 0.8, "value": numeric},
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=18, r=18, t=52, b=18), paper_bgcolor="rgba(0,0,0,0)", font={"color": "#0C4A6E"})
    return fig


def hero():
    st.markdown(
        """
<div class="hs-hero">
  <div class="hs-eyebrow">AI recruitment intelligence</div>
  <h1>Evaluate resumes and interviews with clear, defensible signals.</h1>
  <p>HireSense AI combines trained resume scoring, adaptive technical questions, answer evaluation, and downloadable reports in one offline-ready hiring workflow.</p>
</div>
""",
        unsafe_allow_html=True,
    )


def login_page():
    hero()
    health = check_health()
    cols = st.columns(3)
    with cols[0]:
        metric_card("API status", "Online" if st.session_state.api_online else "Offline", API_BASE)
    with cols[1]:
        metric_card("Models", "Ready" if health and health.get("models_loaded") else "Check", "Resume scorer and answer evaluator")
    with cols[2]:
        metric_card("Workflow", "4 steps", "Upload, interview, score, report")

    st.markdown("<div class='hs-divider'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='hs-step'><div class='hs-step-index'>1</div><div><strong>Parse resume</strong><br><span class='hs-muted'>Extract contact details, skills, education, projects, and experience.</span></div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='hs-step'><div class='hs-step-index'>2</div><div><strong>Run interview</strong><br><span class='hs-muted'>Generate targeted questions from the candidate profile and role.</span></div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='hs-step'><div class='hs-step-index'>3</div><div><strong>Export report</strong><br><span class='hs-muted'>Review strengths, gaps, scores, and a PDF summary.</span></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='hs-card'>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["Login", "Create account"])
    with tab_login:
        email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        if st.button("Login and continue", type="primary", use_container_width=True, disabled=not email or not password):
            with st.spinner("Signing you in..."):
                data = api("POST", "/api/login", json={"email": email, "password": password})
            if data:
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.session_state.page = "Upload Resume"
                st.rerun()
    with tab_register:
        name = st.text_input("Full name", key="reg_name", placeholder="Jane Candidate")
        email = st.text_input("Work email", key="reg_email", placeholder="jane@example.com")
        password = st.text_input("Create password", type="password", key="reg_password", placeholder="Use a strong password")
        if st.button("Create account", use_container_width=True, disabled=not name or not email or not password):
            with st.spinner("Creating your account..."):
                data = api("POST", "/api/register", json={"name": name, "email": email, "password": password})
            if data:
                show_notice("Registration complete. You can log in now.", "success")
    st.markdown("</div>", unsafe_allow_html=True)


def upload_page():
    section_header("Upload and score a resume", "Use a PDF or DOCX resume. The system extracts profile signals and scores ATS readiness with the trained model.")
    with st.container():
        left, right = st.columns([1.05, 0.95])
        with left:
            st.markdown("<div class='hs-card'>", unsafe_allow_html=True)
            job_role = st.text_input("Target job role", "software engineer", help="Questions and scoring are tailored to this role.")
            file = st.file_uploader("Upload PDF or DOCX resume", type=["pdf", "docx"], help="Scanned image-only resumes are not supported.")
            ready = bool(file and job_role.strip())
            if st.button("Parse and score resume", type="primary", use_container_width=True, disabled=not ready):
                files = {"resume": (file.name, file.getvalue(), file.type or "application/octet-stream")}
                with st.status("Analyzing resume...", expanded=True) as status:
                    st.write("Extracting text and candidate signals")
                    data = api("POST", "/api/upload-resume", files=files, data={"job_role": job_role})
                    if data:
                        st.write("Loading generated interview questions")
                        st.session_state.session_id = data["session_id"]
                        st.session_state.resume = data["parsed_resume"]
                        st.session_state.ats = data["ats_score"]
                        qdata = api("GET", f"/api/questions/{data['session_id']}")
                        st.session_state.questions = qdata.get("questions", []) if qdata else []
                        st.session_state.current_idx = 0
                        st.session_state.answers = []
                        status.update(label="Resume analysis complete", state="complete", expanded=False)
                    else:
                        status.update(label="Resume analysis could not be completed", state="error")
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown(
                """
<div class="hs-card">
  <h3>What HireSense evaluates</h3>
  <p>Contact completeness, skill density, education, project depth, experience relevance, ATS-friendly structure, and answer quality during the interview.</p>
  <div><span class="hs-badge">Trained ML scorer</span><span class="hs-badge-success">Offline ready</span><span class="hs-badge-muted">PDF report</span></div>
</div>
""",
                unsafe_allow_html=True,
            )

    if st.session_state.resume and st.session_state.ats:
        parsed, ats = st.session_state.resume, st.session_state.ats
        st.markdown("<div class='hs-divider'></div>", unsafe_allow_html=True)
        score_col, profile_col = st.columns([0.9, 1.4])
        with score_col:
            st.plotly_chart(gauge(ats.get("overall_score", 0), "ATS Score"), use_container_width=True)
        with profile_col:
            st.markdown(
                f"""
<div class="hs-card">
  <span class="hs-badge-success">Candidate profile</span>
  <h2>{safe(parsed.get('name') or 'Unknown Candidate')}</h2>
  <p>{safe(parsed.get('email'))} &nbsp; {safe(parsed.get('phone'))}</p>
  <p><strong>{safe(parsed.get('word_count'))}</strong> words parsed from the resume.</p>
</div>
""",
                unsafe_allow_html=True,
            )
            skills = parsed.get("skills", [])[:44]
            if skills:
                st.markdown(" ".join(f"<span class='hs-badge'>{safe(skill)}</span>" for skill in skills), unsafe_allow_html=True)
            else:
                show_notice("No skills were detected. Consider checking whether the resume text is extractable.", "warning")

        section_header("Score breakdown", "Each dimension contributes to the blended rule-based and ML ATS readiness score.")
        breakdown = pd.DataFrame([ats.get("breakdown", {})]).T.rename(columns={0: "Score"})
        st.dataframe(breakdown, use_container_width=True)
        if st.button("Start interview", type="primary", use_container_width=True):
            st.session_state.page = "Interview"
            st.rerun()


def interview_page():
    questions = st.session_state.questions
    if not questions:
        show_notice("Upload and score a resume first. Then the interview questions will appear here.", "warning")
        if st.button("Go to upload", use_container_width=True):
            st.session_state.page = "Upload Resume"
            st.rerun()
        return

    idx = st.session_state.current_idx
    if idx >= len(questions):
        st.markdown(
            """
<div class="hs-card">
  <span class="hs-badge-success">Interview complete</span>
  <h2>Your candidate evaluation is ready.</h2>
  <p>Open the final report to review technical score, communication score, recommendation, strengths, weaknesses, and question-level details.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button("View final report", type="primary", use_container_width=True):
            st.session_state.page = "Final Report"
            st.rerun()
        return

    answered_count = len(st.session_state.answers)
    avg = sum(a["score"] for a in st.session_state.answers) / answered_count * 100 if answered_count else 0
    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("Progress", f"{idx + 1}/{len(questions)}", "Current question")
    with m2:
        metric_card("Answered", str(answered_count), "Saved responses")
    with m3:
        metric_card("Average", f"{avg:.1f}%" if answered_count else "Pending", "Interview score")

    q = questions[idx]
    st.progress((idx + 1) / len(questions), text=f"Question {idx + 1} of {len(questions)}")
    st.markdown(
        f"""
<div class="hs-question">
  <span class="hs-badge">{safe(q.get('domain'))}</span>
  <span class="hs-badge-muted">{safe(q.get('difficulty'))}</span>
  <h2>{safe(q.get('question_text'))}</h2>
</div>
""",
        unsafe_allow_html=True,
    )
    answer = st.text_area(
        "Your answer",
        height=190,
        key=f"answer_{q['id']}",
        placeholder="Explain your reasoning, trade-offs, edge cases, and a practical example where possible.",
        help="A stronger answer usually includes concrete terms, examples, and limitations.",
    )

    submitted = q.get("answer")
    action_col, next_col = st.columns([1, 1])
    with action_col:
        if st.button("Submit answer", type="primary", use_container_width=True, disabled=not answer.strip() or bool(submitted)):
            with st.spinner("Evaluating answer..."):
                data = api("POST", "/api/submit-answer", json={"question_id": q["id"], "candidate_answer": answer})
            if data:
                q["answer"] = data | {"candidate_answer": answer}
                st.session_state.answers.append(data)
                st.rerun()

    if q.get("answer"):
        result = q["answer"]
        result_col, feedback_col = st.columns([0.85, 1.15])
        with result_col:
            st.plotly_chart(gauge(result.get("score", 0) * 100, safe(result.get("label", "Score")).upper()), use_container_width=True)
        with feedback_col:
            st.markdown(
                f"""
<div class="hs-card">
  <span class="hs-badge-success">Feedback</span>
  <p>{safe(result.get('feedback'))}</p>
</div>
""",
                unsafe_allow_html=True,
            )
        with next_col:
            if st.button("Next question", use_container_width=True):
                st.session_state.current_idx += 1
                st.rerun()


def report_page():
    session_id = st.session_state.session_id
    if not session_id:
        show_notice("No active session. Complete a resume upload and interview first.", "warning")
        return

    with st.spinner("Preparing final report..."):
        data = api("GET", f"/api/report/{session_id}")
    if not data:
        return

    report = data["report"]
    section_header("Final evaluation report", "Review the hiring recommendation and export a PDF for the hiring packet.")
    top1, top2, top3 = st.columns(3)
    with top1:
        metric_card("Recommendation", report.get("recommendation", "Review"), "Decision guidance")
    with top2:
        metric_card("Technical", f"{report.get('technical_score', 0):.1f}%", "Answer evaluation")
    with top3:
        metric_card("Communication", f"{report.get('communication_score', 0):.1f}%", "Clarity and completeness")

    c1, c2 = st.columns([0.9, 1.1])
    with c1:
        st.plotly_chart(gauge(report.get("overall_score", 0), "Overall Score"), use_container_width=True)
    with c2:
        categories = ["Technical", "Communication", "ATS"]
        values = [report.get("technical_score", 0), report.get("communication_score", 0), st.session_state.ats.get("overall_score", 0) if st.session_state.ats else 0]
        fig = go.Figure(data=go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", line={"color": "#0369A1"}, fillcolor="rgba(14, 165, 233, 0.22)"))
        fig.update_layout(height=330, margin=dict(l=28, r=28, t=42, b=28), paper_bgcolor="rgba(0,0,0,0)", polar={"bgcolor": "#FFFFFF", "radialaxis": {"range": [0, 100], "gridcolor": "#BAE6FD"}, "angularaxis": {"gridcolor": "#E7EFF5"}}, font={"color": "#0C4A6E"})
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='hs-card'><h3>Strengths</h3>", unsafe_allow_html=True)
        for item in report.get("strengths", []):
            st.success(item)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='hs-card'><h3>Areas to validate</h3>", unsafe_allow_html=True)
        for item in report.get("weaknesses", []):
            st.warning(item)
        st.markdown("</div>", unsafe_allow_html=True)

    rows = []
    for q in data.get("questions", []):
        answer = q.get("answer", {})
        rows.append(
            {
                "Question": q.get("question_text"),
                "Domain": q.get("domain"),
                "Difficulty": q.get("difficulty"),
                "Score": round(answer.get("score", 0) * 100, 1),
                "Label": answer.get("label", ""),
            }
        )
    section_header("Question-level evidence", "Use this table to audit individual signals behind the final score.")
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    try:
        pdf = requests.get(f"{API_BASE}/api/report/{session_id}?format=pdf", headers=headers(), timeout=60)
        if pdf.ok:
            st.download_button("Download PDF report", pdf.content, file_name=f"hiresense_report_{session_id}.pdf", mime="application/pdf", use_container_width=True)
        else:
            show_notice("PDF report is not available yet. Please retry after the report finishes generating.", "warning")
    except requests.exceptions.RequestException:
        show_notice("Could not download the PDF report. Please verify the backend is running.", "error")


def history_page():
    user = st.session_state.user
    if not user:
        show_notice("Please log in to view previous sessions.", "warning")
        return
    section_header("Evaluation history", "Review prior resume and interview scoring sessions for this user.")
    data = api("GET", f"/api/history/{user['id']}")
    if data and data.get("sessions"):
        st.dataframe(pd.DataFrame(data["sessions"]), use_container_width=True)
    else:
        st.markdown(
            """
<div class="hs-card">
  <span class="hs-badge-muted">No sessions yet</span>
  <p>Upload a resume and complete an interview to create your first evaluation record.</p>
</div>
""",
            unsafe_allow_html=True,
        )


def sidebar():
    with st.sidebar:
        st.markdown("## HireSense AI")
        st.caption("Recruitment intelligence workspace")
        current = st.session_state.page if st.session_state.page in PAGES else "Home"
        st.session_state.page = st.radio("Navigate", PAGES, index=PAGES.index(current), label_visibility="collapsed")
        st.markdown("---")
        if st.session_state.user:
            st.caption("Signed in")
            st.markdown(f"**{safe(st.session_state.user.get('email'))}**")
            if st.button("Logout", use_container_width=True):
                for key in ["token", "user", "session_id", "questions", "resume", "ats", "answers"]:
                    st.session_state[key] = None if key not in ["questions", "answers"] else []
                st.session_state.current_idx = 0
                st.session_state.page = "Home"
                st.rerun()
        else:
            st.caption("Sign in to save history and reports.")
        st.markdown("---")
        st.caption("Design system: Swiss minimal, high contrast, accessible controls, clear feedback.")


init_state()
sidebar()

if st.session_state.page == "Home":
    login_page()
elif st.session_state.page == "Upload Resume":
    upload_page()
elif st.session_state.page == "Interview":
    interview_page()
elif st.session_state.page == "Final Report":
    report_page()
elif st.session_state.page == "History":
    history_page()
