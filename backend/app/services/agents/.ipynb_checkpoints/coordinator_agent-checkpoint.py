from app.services.agents.recruiter_agent import recruiter_agent
from app.services.agents.analyst_agent import analyst_agent


async def coordinator_agent(db, hiring_manager_id, memory, chat_messages):
    msg = chat_messages[-1]["content"].lower()

    if any(k in msg for k in ["job", "hire", "applicant", "delete", "update"]):
        return await recruiter_agent(db, hiring_manager_id, memory, chat_messages)

    return await analyst_agent(db, hiring_manager_id, memory, chat_messages)
