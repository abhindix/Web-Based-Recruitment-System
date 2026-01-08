import re

DISALLOWED = re.compile(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b", re.IGNORECASE)

ALLOWED_TABLES = {"jobs", "applications", "users", "files", "applicants",}

def _normalize_identifier(token: str) -> str:
    """
    Normalize SQL identifiers:
    - remove quotes
    - remove trailing punctuation
    - lowercase
    """
    return token.strip().strip("\"'`;").lower()

def validate_sql(sql: str) -> str:
    s = sql.strip().rstrip(";")

    # Block dangerous operations
    if DISALLOWED.search(s):
        raise ValueError("Disallowed SQL operation.")

    # SELECT-only
    if not s.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    lower = s.lower()

    # Find identifiers after FROM or JOIN
    tokens = re.findall(
        r"\b(from|join)\s+([a-zA-Z0-9_\"'`\.]+)",
        lower,
    )

    for _, raw in tokens:
        table = _normalize_identifier(raw)

        # Handle schema-qualified names (e.g. public.applicants)
        if "." in table:
            table = table.split(".")[-1]

        if table not in ALLOWED_TABLES:
            raise ValueError(f"Table not allowed: {table}")

    # Enforce a LIMIT if missing
    if " limit " not in lower:
        s += " LIMIT 50"

    return s
