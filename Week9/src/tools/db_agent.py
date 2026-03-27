import os
import re
import sqlite3
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────────────────
_ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_LOG_DIR  = os.path.join(_ROOT, "logs")
_OUT_FILE = os.path.join(_LOG_DIR, "db_output.txt")
DB_PATH   = os.path.join(_ROOT, "data", "business.db")

os.makedirs(_LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ── System prompt ─────────────────────────────────────────────────────────
DB_AGENT_SYSTEM_PROMPT = """
You are the Database Agent — a SQLite specialist.

YOUR JOB:
1. Receive a natural-language request about data in a SQLite database.
2. Translate it into ONE valid SQLite SQL statement.
3. Output ONLY the raw SQL — no markdown, no explanation, no preface.

STRICT RULES:
- Output ONLY the SQL statement. Nothing else.
- Always wrap column names in double quotes: "Column Name".
- Use LIKE with % wildcards for all text searches (e.g. WHERE "Job Title" LIKE '%Lawyer%').
- Add COLLATE NOCASE to text comparisons for case-insensitive matching.
- Never use DROP, DELETE, TRUNCATE, UPDATE, or ALTER — read-only queries only.
- Use LIMIT 50 on SELECT * queries unless the user asks for all rows.
- For aggregation (count, sum, avg), always alias the result column (e.g. COUNT(*) AS total).
- For "top N" requests, use ORDER BY … DESC LIMIT N.
- If multiple conditions exist, combine with AND inside a single WHERE clause.
- The main table is always called: data_import
- Price/cost/amount columns may contain currency symbols like "$". For any numeric sort or comparison ALWAYS use:
  CAST(REPLACE(REPLACE("column_name","$",""),",","") AS REAL)
  Example: ORDER BY CAST(REPLACE(REPLACE("price","$",""),",","") AS REAL) DESC LIMIT 1
- NEVER sort a currency/price column as plain text — the result will be wrong.
"""

# ── Blocked SQL keywords (destructive operations) ─────────────────────────
_BLOCKED_SQL = ["drop", "delete", "truncate", "update", "alter"]

def is_safe_sql(sql: str) -> bool:
    lower = sql.lower()
    return not any(word in lower for word in _BLOCKED_SQL)


# ── Logging helper ─────────────────────────────────────────────────────────
def _log_query(sql: str, result: str) -> None:
    with open(_OUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"SQL       :\n{sql.strip()}\n")
        f.write(f"{'─'*60}\n")
        f.write(f"RESULT    :\n{result.strip()}\n")


# ── Core execution ─────────────────────────────────────────────────────────
def query_database(sql_query: str) -> str:
    """
    Execute a SQL query against business.db.
    Returns result rows as a formatted string, or an error message.
    """
    sql_query = sql_query.strip().rstrip(";") + ";"

    if not is_safe_sql(sql_query):
        result = "[SECURITY BLOCKED] Destructive SQL detected (DROP/DELETE/TRUNCATE/UPDATE/ALTER)."
        _log_query(sql_query, result)
        return result

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql_query)

            upper = sql_query.strip().upper()
            if upper.startswith("SELECT") or upper.startswith("WITH") or upper.startswith("PRAGMA"):
                rows = cursor.fetchall()
                if not rows:
                    result = "Query executed successfully. No rows matched."
                else:
                    # Pretty-print with column headers
                    cols = [d[0] for d in cursor.description]
                    lines = [" | ".join(cols)]
                    lines.append("-" * len(lines[0]))
                    for row in rows:
                        lines.append(" | ".join(str(row[c]) if row[c] is not None else "NULL"
                                                for c in cols))
                    result = "\n".join(lines)
            else:
                conn.commit()
                result = f"Statement executed. Rows affected: {cursor.rowcount}"

        _log_query(sql_query, result)
        return result

    except sqlite3.OperationalError as exc:
        result = f"SQL Error: {exc}"
        _log_query(sql_query, result)
        return result
    except Exception as exc:
        result = f"DB Error: {type(exc).__name__}: {exc}"
        _log_query(sql_query, result)
        return result


# ── Schema helper (used by orchestrator to build prompts) ─────────────────
def get_schema(table: str = "data_import") -> dict:
    """
    Return {'columns': [...], 'sample_values': {col: [...]}} for a table.
    Used by the orchestrator to build schema-aware SQL prompts.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Column names + types
            cur.execute(f"PRAGMA table_info({table});")
            cols = [r["name"] for r in cur.fetchall()]

            # Up to 5 distinct non-empty sample values per column
            samples: dict[str, list] = {}
            for col in cols:
                cur.execute(
                    f'SELECT DISTINCT "{col}" FROM {table} '
                    f'WHERE "{col}" IS NOT NULL AND "{col}" != "" LIMIT 5;'
                )
                samples[col] = [str(r[0]) for r in cur.fetchall()]

            return {"columns": cols, "sample_values": samples}
    except Exception:
        return {"columns": [], "sample_values": {}}


# ── SQL cleaning helper (used by orchestrator) ─────────────────────────────
def clean_sql(raw: str) -> str:
    """
    Strip markdown fences and non-SQL lines from LLM output.
    Keeps lines that start with a SQL keyword or are continuation lines.
    """
    # Remove markdown fences
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
    cleaned = re.sub(r"\n?```$",           "", cleaned.strip()).strip()

    # Keep only SQL-looking lines
    sql_keywords = ("SELECT", "WITH", "INSERT", "CREATE", "PRAGMA",
                    "FROM", "WHERE", "GROUP", "ORDER", "HAVING",
                    "LIMIT", "JOIN", "LEFT", "INNER", "AND", "OR")

    kept = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(stripped.upper().startswith(kw) for kw in sql_keywords):
            kept.append(stripped)
        elif kept:
            # Continuation of previous SQL line
            kept.append(stripped)

    result = " ".join(kept)

    # Ensure semicolon
    if result and not result.endswith(";"):
        result += ";"

    return result


# ── Tool descriptor ───────────────────────────────────────────────────────
db_tool = {
    "name":          "db_querier",
    "description":   "Run SQL queries against business.db (SQLite). Read-only.",
    "func":          query_database,
    "get_schema":    get_schema,
    "clean_sql":     clean_sql,
    "system_prompt": DB_AGENT_SYSTEM_PROMPT,
}
