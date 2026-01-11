import httpx
import json
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

from app.core.config import settings
from app.services.sql_safety import validate_sql
from app.crud import job as job_crud
from app.models.job import Job  # ✅ direct model access


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
# PROMPT
# ==========================================================

def build_system_prompt(schema: str, memory: list[dict], role_hint: str) -> str:
    memory_block = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in memory])

    return f"""
You are an autonomous {role_hint} assistant.

PAST MEMORY:
{memory_block or "No prior memory."}

DATABASE SCHEMA (AUTHORITATIVE):
{schema}

CRITICAL RULES:
- NEVER use INSERT/UPDATE/DELETE/DDL in SQL.
- query_db tool MUST be SELECT-only.
- For writes, use tools: create_job / update_job / delete_job.
- Always enforce manager ownership when changing jobs.
- If a query is rejected, fix it and retry.

Respond clearly and helpfully (no raw JSON blocks).
""".strip()


# ==========================================================
# LLM CLIENT
# ==========================================================

def _headers():
    return {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }


async def llm_call(messages: list[dict], tools: list[dict]):
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.post(url, headers=_headers(), json=payload)
        r.raise_for_status()
        return r.json()


# ==========================================================
# TOOLS
# ==========================================================

TOOL_CREATE_JOB = {
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
}

TOOL_UPDATE_JOB = {
    "type": "function",
    "function": {
        "name": "update_job",
        "description": "Update an existing job by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "integer"},
                "role_title": {"type": ["string", "null"]},
                "requirements": {"type": ["string", "null"]},
                "indicative_salary": {"type": ["integer", "null"]},
            },
            "required": ["job_id"],
        },
    },
}

TOOL_DELETE_JOB = {
    "type": "function",
    "function": {
        "name": "delete_job",
        "description": "Delete a job by ID (manager only).",
        "parameters": {
            "type": "object",
            "properties": {"job_id": {"type": "integer"}},
            "required": ["job_id"],
        },
    },
}

TOOL_QUERY_DB = {
    "type": "function",
    "function": {
        "name": "query_db",
        "description": "Run a SELECT-only SQL query.",
        "parameters": {
            "type": "object",
            "properties": {"sql": {"type": "string"}},
            "required": ["sql"],
        },
    },
}


# ==========================================================
# HELPERS: SAFE JOB LOOKUP / OWNERSHIP
# ==========================================================

def _get_job_owned_by_manager(db: Session, job_id: int, hiring_manager_id: int) -> Job | None:
    return (
        db.query(Job)
        .filter(Job.id == job_id, Job.hiring_manager_id == hiring_manager_id)
        .first()
    )


# ==========================================================
# CORE AGENT LOOP
# ==========================================================

async def run_llm_agent(
    db: Session,
    hiring_manager_id: int,
    memory: list[dict],
    chat_messages: list[dict],
    role_hint: str,
    tools: list[dict],
):
    schema = load_db_schema(db)
    system_prompt = build_system_prompt(schema, memory, role_hint)
    messages = [{"role": "system", "content": system_prompt}] + chat_messages

    for _ in range(6):
        response = await llm_call(messages, tools)
        msg = response["choices"][0]["message"]

        # Done
        if not msg.get("tool_calls"):
            return msg.get("content", ""), None

        tool_call = msg["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])

        messages.append(msg)

        # --------------------------
        # CREATE JOB
        # --------------------------
        if tool_name == "create_job":
            job = job_crud.create_job(
                db=db,
                hiring_manager_id=hiring_manager_id,
                role_title=args["role_title"],
                requirements=args["requirements"],
                indicative_salary=args.get("indicative_salary"),
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": "create_job",
                "content": json.dumps({"job_id": job.id}, default=str),
            })
            continue

        # --------------------------
        # UPDATE JOB (FIXED: no job_crud.get)
        # --------------------------
        if tool_name == "update_job":
            job_id = int(args["job_id"])
            job = _get_job_owned_by_manager(db, job_id, hiring_manager_id)

            if not job:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": "update_job",
                    "content": json.dumps({"error": "Job not found or not authorized"}, default=str),
                })
                continue

            # update fields if provided
            if args.get("role_title") is not None:
                job.role_title = args["role_title"]
            if args.get("requirements") is not None:
                job.requirements = args["requirements"]
            if args.get("indicative_salary") is not None:
                job.indicative_salary = args["indicative_salary"]

            db.add(job)
            db.commit()
            db.refresh(job)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": "update_job",
                "content": json.dumps({"status": "updated", "job_id": job.id}, default=str),
            })
            continue

        # --------------------------
        # DELETE JOB (FIXED: no job_crud.remove)
        # --------------------------
        if tool_name == "delete_job":
            job_id = int(args["job_id"])
            job = _get_job_owned_by_manager(db, job_id, hiring_manager_id)

            if not job:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": "delete_job",
                    "content": json.dumps({"error": "Job not found or not authorized"}, default=str),
                })
                continue

            db.delete(job)
            db.commit()

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": "delete_job",
                "content": json.dumps({"status": "deleted", "job_id": job_id}, default=str),
            })
            continue

        # --------------------------
        # QUERY DB (self-heal on blocked SQL)
        # --------------------------
        if tool_name == "query_db":
            sql_raw = args.get("sql", "")

            try:
                sql = validate_sql(sql_raw)
            except ValueError as e:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": "query_db",
                    "content": json.dumps(
                        {
                            "error": str(e),
                            "hint": "Use SELECT only. Do not use UPDATE/DELETE/INSERT/DDL.",
                            "original_sql": sql_raw,
                        },
                        default=str,
                    ),
                })
                continue

            rows = db.execute(text(sql)).mappings().all()
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": "query_db",
                "content": json.dumps({"sql": sql, "rows": [dict(r) for r in rows[:50]]}, default=str),
            })
            continue

        # Unknown tool
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": tool_name,
            "content": json.dumps({"error": f"Unknown tool: {tool_name}"}),
        })

    return "I need a simpler or clearer request.", None