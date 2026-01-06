from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db, require_roles
from ...crud import job as job_crud
from ...models.user import UserRole, User
from ...schemas.job import JobCreate, JobOut

router = APIRouter(tags=["jobs"])


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
