import httpx
import json
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from sqlalchemy.exc import ProgrammingError

from app.core.config import settings
from app.services.sql_safety import validate_sql
from app.crud import job as job_crud


# ==========================================================
# SCHEMA INTROSPECTION (CORRECT + SAFE)
# ==========================================================

def load_db_schema(db: Session) -> str:
    engine = db.get_bind()  # IMPORTANT: inspect ENGINE, not Session
    inspector = inspect(engine)

    lines = []
    for table in sorted(inspector.get_table_names()):
        lines.append(f"TABLE: {table}")
        for col in inspector.get_columns(table):
            lines.append(f"- {col['name']} ({col['type']})")
        lines.append("")

    return "\n".join(lines).strip()


# ==========================================================
# SYSTEM PROMPT (AGENTIC + SCHEMA LOCKED)
# ==========================================================

def build_system_prompt(schema: str) -> str:
    return f"""
You are an autonomous hiring-manager assistant.

You are an AGENT, not a chatbot.

DATABASE SCHEMA (single source of truth):
{schema}

RULES:
- Never guess table or column names
- Use ONLY the schema above
- Use SELECT-only SQL
- Prefer COUNT before listing rows
- If data does not exist, explain clearly
- If information is missing, ask a follow-up question

Always think step-by-step and return structured data internally.
""".strip()


# ==========================================================
# HUMAN OUTPUT RENDERER (NO JSON IN UI)
# ==========================================================

def render_manager_response(obj: dict) -> str:
    lines = []

    # Latest jobs
    if "latest_jobs" in obj:
        jobs = obj.get("latest_jobs", [])
        if not jobs:
            return "There are no job postings yet."

        lines.append("Latest Job Openings:\n")

        for job in jobs:
            lines.append(f"Role: {job.get('role_title')}")
            lines.append(f"Requirements: {job.get('requirements')}")

            salary = job.get("indicative_salary")
            lines.append(
                f"Salary: ₹{salary}" if salary else "Salary: Not specified"
            )

            applicants = job.get("applicants")
            if not applicants:
                lines.append("Applicants: No applications yet")
            else:
                lines.append(f"Applicants: {', '.join(applicants)}")

            lines.append("")

        return "\n".join(lines)

    # Generic summary
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
# AGENT LOOP (MULTI-STEP + SELF-HEALING)
# ==========================================================

async def run_manager_agent(
    db: Session,
    hiring_manager_id: int,
    chat_messages: list[dict],
) -> tuple[str, dict | None]:

    if not settings.LLM_API_KEY:
        return "LLM not configured.", None

    schema = load_db_schema(db)
    system_prompt = build_system_prompt(schema)

    messages = [{"role": "system", "content": system_prompt}] + chat_messages
    collected_rows = []

    for _ in range(5):
        response = await llm_call(messages, TOOLS)
        msg = response["choices"][0]["message"]

        # ======================
        # FINAL ANSWER
        # ======================
        if not msg.get("tool_calls"):
            content = msg.get("content", "")
            try:
                structured = json.loads(content)
                pretty = render_manager_response(structured)
                return pretty, structured
            except Exception:
                return content, {"rows": collected_rows}

        tool = msg["tool_calls"][0]
        name = tool["function"]["name"]
        args = json.loads(tool["function"]["arguments"])

        # ======================
        # CREATE JOB
        # ======================
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

        # ======================
        # QUERY DB (SELF-HEALING)
        # ======================
        if name == "query_db":
            sql = validate_sql(args["sql"])

            try:
                result = db.execute(text(sql)).mappings().all()
                rows = [dict(r) for r in result]
            except ProgrammingError:
                messages.append(msg)
                messages.append({
                    "role": "system",
                    "content": (
                        "The previous SQL failed. "
                        "Fix it using ONLY the schema. "
                        "If impossible, ask a follow-up question."
                    ),
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