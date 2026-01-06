from sqlalchemy.orm import Session
from app.models.job import Job
from app.models.application import Application

def tool_list_jobs(db: Session, limit: int = 10):
    q = db.query(Job).order_by(Job.id.desc()).limit(limit).all()
    return [{"id": j.id, "title": j.title, "salary": j.salary} for j in q]

def tool_count_applications_by_job(db: Session):
    # simple safe aggregation (adjust to your schema)
    rows = db.query(Application.job_id).all()
    counts = {}
    for (job_id,) in rows:
        counts[job_id] = counts.get(job_id, 0) + 1
    return counts
