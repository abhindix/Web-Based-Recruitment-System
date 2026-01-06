from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)

    phone: Mapped[str] = mapped_column(String(64))
    cover_letter: Mapped[str] = mapped_column(Text)

    # Store the CV as an uploaded file record
    cv_file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    applicant = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    cv_file = relationship("StoredFile", foreign_keys=[cv_file_id])
