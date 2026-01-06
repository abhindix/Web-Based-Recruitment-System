from enum import Enum

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRole(str, Enum):
    MANAGER = "manager"
    APPLICANT = "applicant"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default=UserRole.APPLICANT.value)

    applications = relationship(
        "Application",
        back_populates="applicant",
        cascade="all, delete-orphan",
    )
