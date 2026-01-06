import re

DISALLOWED = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b", re.IGNORECASE)

ALLOWED_TABLES = {"jobs", "applications", "users", "files"}

def validate_sql(sql: str) -> str:
    s = sql.strip().rstrip(";")
    if DISALLOWED.search(s):
        raise ValueError("Disallowed SQL operation.")
    if not s.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    # naive table allowlist check (demo)
    lower = s.lower()
    if " from " in lower:
        # find identifiers after FROM / JOIN
        tokens = re.findall(r"\b(from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)", lower)
        for _, t in tokens:
            if t not in ALLOWED_TABLES:
                raise ValueError(f"Table not allowed: {t}")
    # enforce a LIMIT if missing
    if " limit " not in lower:
        s += " LIMIT 50"
    return s
