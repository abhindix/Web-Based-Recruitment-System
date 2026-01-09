from sqlalchemy.orm import Session
from typing import List

from app.models.agent_memory import AgentMemory


def add_memory(db: Session, user_id: int, role: str, content: str) -> None:
    db.add(
        AgentMemory(
            user_id=user_id,
            role=role,
            content=content,
        )
    )
    db.commit()


def get_recent_memory(
    db: Session,
    user_id: int,
    limit: int = 10,
) -> List[AgentMemory]:
    return (
        db.query(AgentMemory)
        .filter(AgentMemory.user_id == user_id)
        .order_by(AgentMemory.created_at.desc())
        .limit(limit)
        .all()[::-1]  # chronological order
    )