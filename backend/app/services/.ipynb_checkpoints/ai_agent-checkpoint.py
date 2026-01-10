from sqlalchemy.orm import Session

from app.crud.agent_memory import add_memory, get_recent_memory
from app.services.agents.coordinator_agent import coordinator_agent


async def run_manager_agent(
    db: Session,
    hiring_manager_id: int,
    chat_messages: list[dict],
):
    """
    Entry point for manager chat.
    Handles memory and delegates to coordinator.
    """

    # Load memory
    memory_rows = get_recent_memory(db, hiring_manager_id, limit=10)
    memory = [{"role": m.role, "content": m.content} for m in memory_rows]

    # Store user messages
    for m in chat_messages:
        if m["role"] == "user":
            add_memory(db, hiring_manager_id, "user", m["content"])

    # ✅ FIX: pass hiring_manager_id explicitly
    reply, data = await coordinator_agent(
        db=db,
        hiring_manager_id=hiring_manager_id,
        memory=memory,
        chat_messages=chat_messages,
    )

    # Store assistant reply
    add_memory(db, hiring_manager_id, "assistant", reply)

    return reply, data