from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..deps import get_db, require_roles
from ...crud import application as application_crud
from ...crud import job as job_crud
from ...models.user import User, UserRole
from ...schemas.application import ApplicationOut
from ...services.email_service import send_email
from ...services.storage_service import save_upload

router = APIRouter(tags=["applications"])


@router.post("/applications", response_model=ApplicationOut, status_code=201)
async def submit_application(
    job_id: int = Form(...),
    phone: str = Form(...),
    cover_letter: str = Form(...),
    cv: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: User = Depends(require_roles(UserRole.APPLICANT)),
):
    job = job_crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    stored = await save_upload(db, cv)

    application = application_crud.create_application(
        db=db,
        job_id=job_id,
        applicant_id=current.id,
        phone=phone,
        cover_letter=cover_letter,
        cv_file_id=stored.id,
    )

    # best-effort email confirmation
    subject = f"Application received: {job.role_title}"
    body = (
        f"Hi {current.full_name or current.email},\n\n"
        f"Thanks for applying for '{job.role_title}'. We've received your application.\n\n"
        f"Job ID: {job.id}\n"
        f"We'll be in touch if there's a match.\n\n"
        f"— Recruitment Team"
    )
    await send_email(to_email=current.email, subject=subject, body=body)

    return application
