import httpx
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.core.config import settings
from app.services.sql_safety import validate_sql
from app.crud import job as job_crud


SYSTEM = """You are an assistant for hiring managers inside a recruitment system.

CRITICAL DATABASE RULES (must follow exactly):

The database schema is FIXED and you must NEVER guess column names.

Tables and columns you are allowed to use:

TABLE: jobs
- id (int)
- role_title (text)
- requirements (text)
- indicative_salary (int, nullable)
- hiring_manager_id (int, foreign key to users.id)
- created_at (datetime)

TABLE: applications
- id (int)
- applicant_id (int, foreign key to users.id)
- job_id (int, foreign key to jobs.id)
- phone (string)
- cover_letter (text)
- cv_file_id (int, foreign key to files.id)
- created_at (datetime)

TABLE: users
- id (int)
- email (string)
- full_name (string, nullable)
- role (string)

TABLE: files
- id (int)
- filename (string)
- content_type (string)
- path (string)
- size_bytes (int)
- created_at (datetime)

IMPORTANT:
- There is NO applicant_name column.
- Applicant names may be NULL (users.full_name can be null).
- Do NOT invent columns.
- If a value does not exist in the schema, do not query it.

When answering questions:
- If no rows exist, say: "There are currently no applications for this job."
- If the requested data is not stored, explain that clearly instead of guessing.

You may:
1) Create jobs when role_title and requirements are provided (optionally indicative_salary).
2) Answer questions using SELECT-only SQL queries via the query_db tool.

You must NEVER:
- Assume column names
- Guess schema
- Query non-existent fields
- Use INSERT, UPDATE, DELETE, DROP, or ALTER
"""


def _openai_headers():
    return {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }


async def llm_chat(messages: list[dict]) -> dict:
    """Calls an OpenAI-compatible /chat/completions endpoint."""
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
                    "description": (
                        "Run a read-only SQL SELECT query to answer questions. "
                        "You MUST only use columns explicitly listed in the schema. "
                        "If data does not exist, do not guess."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {"sql": {"type": "string"}},
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


async def run_manager_agent(
    db: Session,
    hiring_manager_id: int,
    chat_messages: list[dict],
) -> tuple[str, dict | None]:
    """Manager agent with DB tool access.

    Minimal "agentic" loop:
    - Call LLM
    - Execute any tool calls returned
    - Call LLM again with tool outputs
    - Repeat for a small number of iterations to avoid infinite loops
    """
    msgs: list[dict] = [{"role": "system", "content": SYSTEM}] + chat_messages

    if not settings.LLM_API_KEY:
        return "LLM not configured. Set LLM_API_KEY to enable AI chat.", None

    last_data: dict | None = None
    max_iters = 3

    for _ in range(max_iters):
        first = await llm_chat(msgs)
        choice = first["choices"][0]["message"]

        tool_calls = choice.get("tool_calls") or []
        if not tool_calls:
            return choice.get("content", ""), last_data

        # Include the assistant message that requested tools
        msgs.append(choice)

        for tool in tool_calls:
            name = tool["function"]["name"]
            parsed = json.loads(tool["function"]["arguments"] or "{}")

            if name == "create_job":
                job = job_crud.create_job(
                    db=db,
                    hiring_manager_id=hiring_manager_id,
                    role_title=parsed.get("role_title"),
                    requirements=parsed.get("requirements"),
                    indicative_salary=parsed.get("indicative_salary"),
                )
                last_data = {"job_id": job.id}

                msgs.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool["id"],
                        "name": "create_job",
                        "content": json.dumps(
                            {"job_id": job.id, "role_title": job.role_title},
                            default=str,
                        ),
                    }
                )
                continue

            if name == "query_db":
                try:
                    sql = validate_sql(parsed.get("sql", ""))
                except Exception as e:
                    rows: list[dict] = []
                    last_data = {"sql": parsed.get("sql", ""), "rows": rows, "error": str(e)}
                    msgs.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool["id"],
                            "name": "query_db",
                            "content": json.dumps(last_data, default=str),
                        }
                    )
                    continue

                try:
                    result = db.execute(text(sql)).mappings().all()
                    rows = [dict(r) for r in result]
                except ProgrammingError:
                    rows = []

                last_data = {"sql": sql, "rows": rows[:50]}

                msgs.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool["id"],
                        "name": "query_db",
                        "content": json.dumps(last_data, default=str),
                    }
                )
                continue

            # Unknown tool
            msgs.append(
                {
                    "role": "tool",
                    "tool_call_id": tool["id"],
                    "name": name,
                    "content": json.dumps({"error": "Tool not supported."}),
                }
            )

        # Loop continues: call model again with tool outputs in msgs

    return "I couldn't complete that request right now. Please try rephrasing.", last_data