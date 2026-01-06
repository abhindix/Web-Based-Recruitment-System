from sqlalchemy.orm import Session
from app.models.job import Job

def create_job(db: Session, hiring_manager_id: int, role_title: str, requirements: str, indicative_salary: int | None):
    job = Job(
        hiring_manager_id=hiring_manager_id,
        role_title=role_title,
        requirements=requirements,
        indicative_salary=indicative_salary,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def list_jobs(db: Session):
    return db.query(Job).order_by(Job.id.desc()).all()

def get_job(db: Session, job_id: int) -> Job | None:
    return db.get(Job, job_id)
