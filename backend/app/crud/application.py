from sqlalchemy.orm import Session
from app.models.application import Application

def create_application(db: Session, job_id: int, applicant_id: int, phone: str, cover_letter: str, cv_file_id: int):
    app = Application(
        job_id=job_id,
        applicant_id=applicant_id,
        phone=phone,
        cover_letter=cover_letter,
        cv_file_id=cv_file_id,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app
