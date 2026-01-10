from app.services.agents.llm_agent_core import run_llm_agent, TOOL_QUERY_DB


async def analyst_agent(db, hiring_manager_id, memory, chat_messages):
    return await run_llm_agent(
        db=db,
        hiring_manager_id=hiring_manager_id,
        memory=memory,
        chat_messages=chat_messages,
        role_hint="analyst (metrics & trends)",
        tools=[TOOL_QUERY_DB],
    )