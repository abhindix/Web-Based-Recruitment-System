from app.services.agents.llm_agent_core import (
    run_llm_agent,
    TOOL_CREATE_JOB,
    TOOL_UPDATE_JOB,
    TOOL_DELETE_JOB,
    TOOL_QUERY_DB,
)


async def recruiter_agent(db, hiring_manager_id, memory, chat_messages):
    return await run_llm_agent(
        db=db,
        hiring_manager_id=hiring_manager_id,
        memory=memory,
        chat_messages=chat_messages,
        role_hint="recruiter (jobs & hiring)",
        tools=[
            TOOL_CREATE_JOB,
            TOOL_UPDATE_JOB,
            TOOL_DELETE_JOB,
            TOOL_QUERY_DB,
        ],
    )