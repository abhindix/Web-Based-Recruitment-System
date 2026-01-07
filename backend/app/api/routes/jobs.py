
from sqlalchemy import select, join
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...models.application import Application
from ...models.user import User
from ..deps import get_db, require_roles
from ...crud import job as job_crud
from ...models.user import UserRole, User
from ...schemas.job import JobCreate, JobOut

router = APIRouter(tags=["jobs"])

@router.get("/jobs/applicants", response_model=list[dict])
def jobs_with_applicants(db: Session = Depends(get_db)):
    results = db.execute(
        select(
            job_crud.Job.id,
            job_crud.Job.role_title,
            User.email
        ).select_from(
            join(job_crud.Job, Application, job_crud.Job.id == Application.job_id)
            .join(User, Application.applicant_id == User.id)
        )
    ).all()
    jobs = {}
    for job_id, role_title, email in results:
        if job_id not in jobs:
            jobs[job_id] = {"job_id": job_id, "role_title": role_title, "applicants": []}
        jobs[job_id]["applicants"].append(email)
    return list(jobs.values())


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return job_crud.list_jobs(db)


@router.post("/jobs", response_model=JobOut, status_code=201)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(UserRole.MANAGER)),
):
    job = job_crud.create_job(
        db=db,
        hiring_manager_id=current.id,
        role_title=payload.role_title,
        requirements=payload.requirements,
        indicative_salary=payload.indicative_salary,
    )
    return job


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
