from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.base import Base


class AgentMemory(Base):
    __tablename__ = "agent_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    role = Column(Text, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())