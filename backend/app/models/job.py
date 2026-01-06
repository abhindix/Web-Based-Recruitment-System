from datetime import datetime

from sqlalchemy import DateTime, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_title: Mapped[str] = mapped_column(String(255), index=True)
    requirements: Mapped[str] = mapped_column(Text)
    indicative_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)

    hiring_manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    hiring_manager = relationship("User")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    applications = relationship("Application", back_populates="job")
