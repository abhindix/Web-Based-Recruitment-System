import httpx
import json
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from sqlalchemy.exc import ProgrammingError

from app.core.config import settings
from app.services.sql_safety import validate_sql
from app.crud import job as job_crud
from app.crud.agent_memory import add_memory, get_recent_memory


# ==========================================================
# SCHEMA INTROSPECTION
# ==========================================================

def load_db_schema(db: Session) -> str:
    engine = db.get_bind()
    inspector = inspect(engine)

    lines = []
    for table in sorted(inspector.get_table_names()):
        lines.append(f"TABLE: {table}")
        for col in inspector.get_columns(table):
            lines.append(f"- {col['name']} ({col['type']})")
        lines.append("")

    return "\n".join(lines).strip()


# ==========================================================
# SYSTEM PROMPT (WITH MEMORY)
# ==========================================================

def build_system_prompt(schema: str, memory: list[dict]) -> str:
    memory_block = "\n".join(
        [f"{m['role'].upper()}: {m['content']}" for m in memory]
    )

    return f"""
You are an autonomous hiring-manager assistant with MEMORY.

====================
PAST CONVERSATION MEMORY
====================
{memory_block or "No prior memory."}

====================
DATABASE SCHEMA
====================
{schema}

RULES:
- Never guess tables or columns
- Use ONLY the schema above
- Use SELECT-only SQL
- Prefer COUNT before listing rows
- Use memory to provide contextual follow-ups
- If the user refers to "last time" or "previous job", use memory

Respond clearly and helpfully.
""".strip()


# ==========================================================
# HUMAN OUTPUT RENDERER
# ==========================================================

def render_manager_response(obj: dict) -> str:
    lines = []

    if "latest_jobs" in obj:
        jobs = obj.get("latest_jobs", [])
        if not jobs:
            return "There are no job postings yet."

        lines.append("Latest Job Openings:\n")

        for job in jobs:
            lines.append(f"Role: {job.get('role_title')}")
            lines.append(f"Requirements: {job.get('requirements')}")
            salary = job.get("indicative_salary")
            lines.append(f"Salary: ₹{salary}" if salary else "Salary: Not specified")

            applicants = job.get("applicants")
            if not applicants:
                lines.append("Applicants: No applications yet")
            else:
                lines.append(f"Applicants: {', '.join(applicants)}")

            lines.append("")

        return "\n".join(lines)

    if "summary" in obj:
        return obj["summary"]

    return "Here is the information you requested."


# ==========================================================
# LLM CLIENT
# ==========================================================

def _headers():
    return {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }


async def llm_call(messages: list[dict], tools: list[dict] | None = None) -> dict:
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "temperature": 0.2,
        "tools": tools,
        "tool_choice": "auto" if tools else None,
    }

    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url, headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json()


# ==========================================================
# TOOLS
# ==========================================================

TOOLS = [
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
            "description": "Run SELECT-only SQL using ONLY the provided schema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string"},
                },
                "required": ["sql"],
            },
        },
    },
]


# ==========================================================
# AGENT LOOP WITH MEMORY
# ==========================================================

async def run_manager_agent(
    db: Session,
    hiring_manager_id: int,
    chat_messages: list[dict],
) -> tuple[str, dict | None]:

    # 🔹 Load memory
    memory_rows = get_recent_memory(db, hiring_manager_id, limit=10)
    memory = [{"role": m.role, "content": m.content} for m in memory_rows]

    schema = load_db_schema(db)
    system_prompt = build_system_prompt(schema, memory)

    messages = [{"role": "system", "content": system_prompt}] + chat_messages
    collected_rows = []

    # 🔹 Store user message in memory
    for m in chat_messages:
        if m["role"] == "user":
            add_memory(db, hiring_manager_id, "user", m["content"])

    for _ in range(5):
        response = await llm_call(messages, TOOLS)
        msg = response["choices"][0]["message"]

        # FINAL ANSWER
        if not msg.get("tool_calls"):
            content = msg.get("content", "")

            # 🔹 Store assistant response
            add_memory(db, hiring_manager_id, "assistant", content)

            try:
                structured = json.loads(content)
                pretty = render_manager_response(structured)
                return pretty, structured
            except Exception:
                return content, {"rows": collected_rows}

        tool = msg["tool_calls"][0]
        name = tool["function"]["name"]
        args = json.loads(tool["function"]["arguments"])

        if name == "create_job":
            job = job_crud.create_job(
                db=db,
                hiring_manager_id=hiring_manager_id,
                role_title=args["role_title"],
                requirements=args["requirements"],
                indicative_salary=args.get("indicative_salary"),
            )

            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool["id"],
                "name": name,
                "content": json.dumps(
                    {"job_id": job.id, "role_title": job.role_title},
                    default=str,
                ),
            })
            continue

        if name == "query_db":
            sql = validate_sql(args["sql"])

            try:
                result = db.execute(text(sql)).mappings().all()
                rows = [dict(r) for r in result]
            except ProgrammingError:
                messages.append(msg)
                messages.append({
                    "role": "system",
                    "content": "Fix the SQL using ONLY the schema or ask a follow-up question.",
                })
                continue

            collected_rows.extend(rows)

            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool["id"],
                "name": name,
                "content": json.dumps(
                    {"rows": rows[:50]},
                    default=str,
                ),
            })
            continue

    return "I need more information to answer accurately.", {"rows": collected_rows}