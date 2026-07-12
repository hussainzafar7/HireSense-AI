from models import db, Job, Resume, Interview, Candidate, Company, InterviewQuestion
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta, timezone
import json

def get_company_dashboard(company_id):
    company = Company.query.get(company_id)
    if not company:
        return {"error": "Company not found"}, 404

    jobs = Job.query.filter_by(company_id=company_id).all()
    job_ids = [j.id for j in jobs]
    total_jobs = len(jobs)
    open_jobs = sum(1 for j in jobs if j.status == "open")

    resumes = Resume.query.filter(Resume.job_id.in_(job_ids)).all() if job_ids else []
    total_applications = len(resumes)
    matched = [r for r in resumes if r.status == "matched"]
    avg_ats = sum(r.ats_score or 0 for r in matched) / max(len(matched), 1)

    interviews = Interview.query.filter(Interview.job_id.in_(job_ids)).all() if job_ids else []
    total_interviews = len(interviews)
    completed_iv = [i for i in interviews if i.status == "completed"]
    avg_iv_score = sum(i.overall_score or 0 for i in completed_iv) / max(len(completed_iv), 1)

    top_candidates = []
    seen = set()
    for r in sorted(matched, key=lambda x: x.ats_score or 0, reverse=True)[:5]:
        if r.candidate_id not in seen:
            seen.add(r.candidate_id)
            c = Candidate.query.get(r.candidate_id)
            top_candidates.append({
                "resume_id": r.id, "candidate_id": r.candidate_id,
                "name": c.full_name if c else "",
                "ats_score": r.ats_score or 0,
                "matched_skills": (r.matched_skills or "").split(",")[:5],
                "missing_skills": (r.missing_skills or "").split(",")[:5],
            })

    per_job = []
    for j in jobs:
        j_resumes = [r for r in resumes if r.job_id == j.id]
        j_interviews = [i for i in interviews if i.job_id == j.id]
        j_matched = [r for r in j_resumes if r.status == "matched"]
        per_job.append({
            "job_id": j.id, "title": j.title, "status": j.status,
            "applications": len(j_resumes),
            "interviews": len(j_interviews),
            "avg_ats": round(sum(r.ats_score or 0 for r in j_matched) / max(len(j_matched), 1), 1),
        })

    return {
        "total_jobs": total_jobs, "open_jobs": open_jobs,
        "total_applications": total_applications, "total_interviews": total_interviews,
        "avg_ats_score": round(avg_ats, 1), "avg_interview_score": round(avg_iv_score, 1),
        "top_candidates": top_candidates, "per_job_breakdown": per_job,
    }, 200

def get_candidate_dashboard(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return {"error": "Candidate not found"}, 404

    resumes = Resume.query.filter_by(candidate_id=candidate_id).all()
    total_resumes = len(resumes)
    total_applications = sum(1 for r in resumes if r.job_id is not None)
    matched_resumes = [r for r in resumes if r.status == "matched"]
    best_ats = max((r.ats_score or 0) for r in matched_resumes) if matched_resumes else 0
    avg_ats = sum(r.ats_score or 0 for r in matched_resumes) / max(len(matched_resumes), 1)

    interviews = Interview.query.filter_by(candidate_id=candidate_id).all()
    total_interviews = len(interviews)
    completed = [i for i in interviews if i.status == "completed"]
    best_iv = max((i.overall_score or 0) for i in completed) if completed else 0
    avg_iv = sum(i.overall_score or 0 for i in completed) / max(len(completed), 1)

    recent_apps = []
    for r in sorted(resumes, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]:
        job_title = ""
        if r.job_id:
            job = Job.query.get(r.job_id)
            job_title = job.title if job else ""
        recent_apps.append({
            "resume_id": r.id, "job_title": job_title,
            "ats_score": r.ats_score or 0, "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        })

    recent_iv = []
    for i in sorted(interviews, key=lambda x: x.started_at or datetime.min, reverse=True)[:5]:
        job_title = ""
        if i.job_id:
            job = Job.query.get(i.job_id)
            job_title = job.title if job else ""
        recent_iv.append({
            "interview_id": i.id, "job_title": job_title,
            "overall_score": i.overall_score or 0, "status": i.status,
            "recommendation": i.recommendation or "",
            "started_at": i.started_at.isoformat() if i.started_at else "",
        })

    return {
        "total_resumes": total_resumes, "total_applications": total_applications,
        "total_interviews": total_interviews, "best_ats_score": best_ats,
        "avg_ats_score": round(avg_ats, 1), "best_interview_score": best_iv,
        "avg_interview_score": round(avg_iv, 1),
        "recent_applications": recent_apps, "recent_interviews": recent_iv,
    }, 200

def get_hiring_funnel(company_id):
    company = Company.query.get(company_id)
    if not company:
        return {"error": "Company not found"}, 404
    jobs = Job.query.filter_by(company_id=company_id).all()
    job_ids = [j.id for j in jobs]
    if not job_ids:
        return {"funnel": {"applied": 0, "interviewed": 0, "score_ge_60": 0, "score_ge_80": 0}}

    applied = Resume.query.filter(Resume.job_id.in_(job_ids)).count()
    interviewed_raw = Interview.query.filter(Interview.job_id.in_(job_ids)).all()
    interviewed = len(interviewed_raw)
    score_ge_60 = sum(1 for i in interviewed_raw if i.overall_score and i.overall_score >= 60)
    score_ge_80 = sum(1 for i in interviewed_raw if i.overall_score and i.overall_score >= 80)

    return {"applied": applied, "interviewed": interviewed, "score_ge_60": score_ge_60, "score_ge_80": score_ge_80}, 200
