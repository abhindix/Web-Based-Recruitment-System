from sqlalchemy.orm import Session
from app.agents.tools import tool_list_jobs, tool_count_applications_by_job

def run_agent(db: Session, message: str) -> str:
    m = message.lower().strip()

    # Simple deterministic intents (works immediately)
    if "latest jobs" in m or "show jobs" in m or "list jobs" in m:
        jobs = tool_list_jobs(db, limit=10)
        if not jobs:
            return "There are no jobs yet."
        lines = [f"- #{j['id']}: {j['title']} ({j.get('salary') or 'salary n/a'})" for j in jobs]
        return "Here are the latest jobs:\n" + "\n".join(lines)

    if "applications" in m and ("count" in m or "how many" in m):
        counts = tool_count_applications_by_job(db)
        if not counts:
            return "No applications found yet."
        lines = [f"- Job {job_id}: {cnt} application(s)" for job_id, cnt in counts.items()]
        return "Applications per job:\n" + "\n".join(lines)

    return "I can help with jobs and applications. Try: “Show latest jobs” or “How many applications per job?”"
