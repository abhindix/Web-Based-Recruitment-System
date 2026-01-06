import httpx
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.services.sql_safety import validate_sql
from app.crud import job as job_crud

SYSTEM = """You are an assistant for hiring managers inside a recruitment system.
You can:
1) Create jobs when the user provides role_title, requirements, and optionally indicative_salary.
2) Answer questions about jobs/applications by querying the database using the SQL tool (SELECT-only).
When unsure, ask a short clarifying question.
"""

def _openai_headers():
    return {"Authorization": f"Bearer {settings.LLM_API_KEY}", "Content-Type": "application/json"}

async def llm_chat(messages: list[dict]) -> dict:
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "create_job",
                    "description": "Create a new job posting.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "role_title": {"type": "string"},
                            "requirements": {"type": "string"},
                            "indicative_salary": {"type": ["integer", "null"]},
                        },
                        "required": ["role_title", "requirements"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "query_db",
                    "description": "Run a read-only SQL SELECT query to answer questions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {"type": "string"},
                        },
                        "required": ["sql"],
                    },
                },
            },
        ],
        "tool_choice": "auto",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=_openai_headers(), json=payload)
        r.raise_for_status()
        return r.json()

async def run_manager_agent(db: Session, hiring_manager_id: int, chat_messages: list[dict]) -> tuple[str, dict | None]:
    msgs = [{"role": "system", "content": SYSTEM}] + chat_messages
    if not settings.LLM_API_KEY:
        # demo fallback when no key is set
        return "LLM not configured. Set LLM_API_KEY to enable AI chat.", None

    first = await llm_chat(msgs)
    choice = first["choices"][0]["message"]

    # Tool call?
    tool_calls = choice.get("tool_calls") or []
    if not tool_calls:
        return choice.get("content", ""), None

    tool = tool_calls[0]
    name = tool["function"]["name"]
    args = tool["function"]["arguments"]

    import json
    parsed = json.loads(args)

    if name == "create_job":
        job = job_crud.create_job(
            db=db,
            hiring_manager_id=hiring_manager_id,
            role_title=parsed["role_title"],
            requirements=parsed["requirements"],
            indicative_salary=parsed.get("indicative_salary"),
        )
        # send tool result back to model to craft friendly response
        msgs2 = msgs + [
            choice,
            {
                "role": "tool",
                "tool_call_id": tool["id"],
                "name": "create_job",
                "content": json.dumps({"job_id": job.id, "role_title": job.role_title}),
            },
        ]
        second = await llm_chat(msgs2)
        reply = second["choices"][0]["message"].get("content", "Created job.")
        return reply, {"job_id": job.id}

    if name == "query_db":
        sql = validate_sql(parsed["sql"])
        rows = db.execute(text(sql)).mappings().all()
        msgs2 = msgs + [
            choice,
            {"role": "tool", "tool_call_id": tool["id"], "name": "query_db", "content": json.dumps({"sql": sql, "rows": rows[:50]})},
        ]
        second = await llm_chat(msgs2)
        reply = second["choices"][0]["message"].get("content", "Here are the results.")
        return reply, {"sql": sql, "rows": rows[:50]}

    return "Tool not supported.", None
