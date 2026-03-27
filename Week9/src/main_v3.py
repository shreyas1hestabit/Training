import asyncio
import csv
import io
import json
import os
import sys
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination

from src.utils.config import client as model_client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from src.tools.code_executor import local_python_executor
from src.tools.db_agent       import query_database, get_schema, clean_sql, DB_AGENT_SYSTEM_PROMPT
from src.tools.file_agent     import file_manager, save_analysis_report

LOG_FILE = "log_day3.json"

def save_log(user_query: str, execution_steps: list) -> None:
    entry = {
        "timestamp":       datetime.now().isoformat(),
        "user_query":      user_query,
        "execution_steps": execution_steps,
    }
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
    print(f"[Logger] Saved → {LOG_FILE}")

async def tool_list_files() -> str:
    """List all .csv and .txt files in the data/ directory."""
    _ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(_ROOT, "data")
    if not os.path.exists(data_dir):
        return "data/ directory does not exist yet."
    files = [f for f in os.listdir(data_dir) if f.endswith((".csv", ".txt"))]
    if not files:
        return "No .csv or .txt files found in data/."
    return "Files in data/:\n" + "\n".join(f"  • {f}" for f in sorted(files))


async def tool_read_file(file_name: str) -> str:
    """
    Read a .csv or .txt file from the data/ directory.
    Args:
        file_name: exact file name, e.g. 'clothes.csv'
    """
    return file_manager("read", file_name)


async def tool_write_txt(file_name: str, lines: list) -> str:
    """
    Create or overwrite a .txt file. Each item in lines becomes one line.
    Use this for plain text files — NOT for code or CSV.
    Args:
        file_name : e.g. 'notes.txt'
        lines     : list of strings, e.g. ["Hello", "World"]
    """
    content = "\n".join(lines) + "\n"
    return file_manager("write", file_name, content)


async def tool_append_txt(file_name: str, lines: list) -> str:
    """
    Append lines to an existing .txt file.
    Args:
        file_name : e.g. 'notes.txt'
        lines     : list of strings to append
    """
    content = "\n".join(lines) + "\n"
    return file_manager("append", file_name, content)


async def tool_write_csv(file_name: str, headers: list, rows: list) -> str:
    """
    Create a new CSV file. Max 10 rows per call — use tool_append_csv for more.
    Args:
        file_name : e.g. 'data.csv'
        headers   : list of column names, e.g. ["name", "age", "city"]
        rows      : list of rows (max 10), each a list of string values
                    e.g. [["Alice", "30", "Delhi"], ["Bob", "25", "Mumbai"]]
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return file_manager("write", file_name, buf.getvalue())


async def tool_append_csv(file_name: str, rows: list) -> str:
    """
    Append rows to an existing CSV file. Max 10 rows per call.
    Args:
        file_name : existing CSV in data/
        rows      : list of rows (max 10), each a list of string values
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return file_manager("append", file_name, buf.getvalue())

async def tool_run_python(code: str) -> str:
    """
    Execute Python code and return its printed output.
    Only stdlib allowed: csv, json, math, statistics, collections, io, datetime.
    Do NOT import os, subprocess, sys, shutil.
    All output must use print(). Wrap risky code in try/except.
    Args:
        code: complete Python source code to execute
    """
    return local_python_executor(code)


async def tool_save_code(file_name: str, description: str) -> str:
    """
    Generate Python code based on description and save it to a .txt file in data/.
    Use this when the user asks to generate code AND save it to a file.
    The code is generated fresh from the description — do NOT pass raw code here.
    Args:
        file_name   : output file name, e.g. 'calculator.txt' or 'fibonacci.txt'
        description : plain English description of what the code should do,
                      e.g. 'a calculator with add, subtract, multiply, divide'
    """
    from autogen_core.models import UserMessage, SystemMessage

    prompt = (
        f"Write clean Python code for: {description}\n\n"
        "Rules:\n"
        "- Write complete, runnable Python code.\n"
        "- Include a main() function and if __name__ == '__main__': main() block.\n"
        "- Add clear comments.\n"
        "- Output ONLY the Python code, no markdown fences, no explanation."
    )
    result = await model_client.create(messages=[
        SystemMessage(content="You are an expert Python programmer. Output only raw Python code.", source="system"),
        UserMessage(content=prompt, source="user"),
    ])

    import re
    code = result.content
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip()).strip()

    save_result = file_manager("write", file_name, code + "\n")
    return f"Code generated and saved.\n{save_result}\n\nCode preview (first 300 chars):\n{code[:300]}"


async def tool_analyze_csv(file_name: str, question: str) -> str:
    """
    Read a CSV file and answer a question about it using Python.
    Use this when the user asks to analyze, filter, or compute something from a CSV.
    Args:
        file_name : CSV file in data/, e.g. 'fruits.csv'
        question  : what to find, e.g. 'list fruits with quantity > 3'
    """
    content = file_manager("read", file_name)
    if content.startswith("Error"):
        return content

    from autogen_core.models import UserMessage, SystemMessage

    prompt = (
        f"Given this CSV data:\n{content}\n\n"
        f"Task: {question}\n\n"
        "Write Python code to answer this. Rules:\n"
        "- Parse with: import io, csv; reader = csv.DictReader(io.StringIO(data))\n"
        "- where data = '''paste csv here''' at the top of the code.\n"
        "- Print results clearly with labels.\n"
        "- Only stdlib. No imports of os/sys/subprocess.\n"
        "- Output ONLY raw Python code, no markdown."
    )
    r = await model_client.create(messages=[
        SystemMessage(content="You are an expert Python data analyst. Output only raw Python code.", source="system"),
        UserMessage(content=prompt, source="user"),
    ])

    import re
    code = r.content
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip()).strip()

    result = local_python_executor(code)
    return f"Analysis of '{file_name}' — {question}:\n\n{result}"

async def tool_list_db_tables() -> str:
    """List all tables in the SQLite database with their row counts."""
    import sqlite3
    _ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH = os.path.join(_ROOT, "data", "business.db")
    if not os.path.exists(DB_PATH):
        return "No database found. Load a CSV first using tool_load_csv_to_db."
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in cur.fetchall()]
        if not tables:
            return "Database exists but has no tables yet."
        lines = ["Tables in business.db:"]
        with sqlite3.connect(DB_PATH) as conn:
            for t in tables:
                cur = conn.cursor()
                cur.execute(f'SELECT COUNT(*) FROM "{t}";')
                count = cur.fetchone()[0]
                lines.append(f"  • {t}  ({count} rows)")
        return "\n".join(lines)
    except Exception as exc:
        return f"DB Error: {exc}"


async def tool_load_csv_to_db(csv_file_name: str, table_name: str) -> str:
    """
    Load a CSV from data/ into a SQLite table in data/business.db.
    Args:
        csv_file_name: exact CSV file name, e.g. 'clothes.csv'
        table_name:    name for the table, e.g. 'clothes'
    """
    import sqlite3
    _ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DB_PATH  = os.path.join(_ROOT, "data", "business.db")
    DATA_DIR = os.path.join(_ROOT, "data")
    csv_path = os.path.join(DATA_DIR, csv_file_name)
    if not os.path.exists(csv_path):
        return f"Error: '{csv_file_name}' not found in data/."
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader  = csv.reader(f)
            headers = next(reader)
            rows    = list(reader)
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cur      = conn.cursor()
            cols_def = ", ".join(f'"{h.strip()}" TEXT' for h in headers)
            cur.execute(f'DROP TABLE IF EXISTS "{table_name}";')
            cur.execute(f'CREATE TABLE "{table_name}" ({cols_def});')
            placeholders = ", ".join("?" * len(headers))
            cur.executemany(f'INSERT INTO "{table_name}" VALUES ({placeholders});', rows)
            conn.commit()
        return (
            f"Success: {len(rows)} rows loaded into table '{table_name}' "
            f"from '{csv_file_name}'.\nColumns: {', '.join(headers)}"
        )
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


async def tool_query_db(natural_language_request: str, table_name: str) -> str:
    """
    Answer a question about data in SQLite using auto-generated SQL.
    Args:
        natural_language_request: user's question in plain English
        table_name:               the table to query (must exist in DB)
    """
    from autogen_core.models import UserMessage, SystemMessage
    schema = get_schema(table_name)
    if not schema["columns"]:
        return f"Table '{table_name}' not found. Load a CSV first with tool_load_csv_to_db."
    schema_hint = (
        f"Table: {table_name}\nColumns: {', '.join(schema['columns'])}\n"
        "Sample values:\n" +
        "\n".join(f"  {c}: {v[:3]}" for c, v in schema["sample_values"].items())
    )
    async def _gen_sql(extra: str = "") -> str:
        prompt = f"{schema_hint}\n\nUser request: {natural_language_request}"
        if extra:
            prompt += f"\n\n{extra}"
        r = await model_client.create(messages=[
            SystemMessage(content=DB_AGENT_SYSTEM_PROMPT, source="system"),
            UserMessage(content=prompt, source="user"),
        ])
        return clean_sql(r.content)
    sql    = await _gen_sql()
    result = query_database(sql)
    if "No rows matched" in result and "WHERE" in sql.upper():
        sql    = await _gen_sql("Previous query returned no rows. Use LIKE '%value%' COLLATE NOCASE.")
        result = query_database(sql)
    return f"SQL:\n{sql}\n\nResults:\n{result}"


async def tool_save_report(original_query: str, report: str, file_name: str) -> str:
    """
    Save an analysis report as a .txt file in data/.
    Args:
        original_query: the user's question
        report:         full report text
        file_name:      e.g. 'report.txt'
    """
    return save_analysis_report(original_query, report, file_name)

def build_agents():

    file_agent = AssistantAgent(
        name="FileAgent",
        model_client=model_client,
        tools=[tool_list_files, tool_read_file,
               tool_write_txt, tool_append_txt,
               tool_write_csv, tool_append_csv],
        system_message="""
You are the File Agent. You ONLY manage files — no code, no analysis, no database.

Your tools:
- tool_list_files()                        → list available files
- tool_read_file(file_name)                → read a file
- tool_write_txt(file_name, lines)         → create/overwrite a .txt file
- tool_append_txt(file_name, lines)        → append lines to a .txt file
- tool_write_csv(file_name, headers, rows) → create a CSV (max 10 rows per call)
- tool_append_csv(file_name, rows)         → append to CSV (max 10 rows per call)

When to act:
- User wants to create, read, update, or list a .txt or .csv file

When NOT to act — say "This is not a file task":
- Code generation requests
- Data analysis or computation requests
- Database queries

End every response with: TERMINATE
""",
    )

    code_agent = AssistantAgent(
        name="CodeAgent",
        model_client=model_client,
        tools=[tool_run_python, tool_analyze_csv, tool_save_code],
        system_message="""
You are the Code Agent. You write, run, and save Python code, and analyze CSV data.

Your tools:
- tool_run_python(code)                      → execute Python and return output
- tool_analyze_csv(file_name, question)      → read CSV and answer a question about it
- tool_save_code(file_name, description)     → generate Python code and save to a file

When to act:
- User asks to generate code (fibonacci, calculator, sorting, etc.)
- User asks to analyze or compute from a CSV file
- User asks to run Python code

When the user says "generate code for X and save to Y.txt":
→ use tool_save_code("Y.txt", "X")

When the user says "analyze X.csv and find Y":
→ use tool_analyze_csv("X.csv", "Y")

Do NOT: query the database, read/write files directly (use your tools).
End every response with: TERMINATE
""",
    )

    db_agent = AssistantAgent(
        name="DBAgent",
        model_client=model_client,
        tools=[tool_list_db_tables, tool_load_csv_to_db, tool_query_db, tool_save_report],
        system_message="""
You are the Database Agent. You ONLY interact with the SQLite database.

Your tools:
- tool_list_db_tables()                          → list all tables and row counts
- tool_load_csv_to_db(csv_file_name, table_name) → load CSV into DB
- tool_query_db(question, table_name)            → query a table in plain English
- tool_save_report(query, report, file_name)     → save analysis to a .txt file

When to act:
- User asks about database tables, row counts, or DB contents
- User asks to load a CSV into the database
- User asks to query or filter data from a DB table

Do NOT: read CSV files directly, run Python, or write files.
End every response with: TERMINATE
""",
    )

    summariser = AssistantAgent(
        name="Summariser",
        model_client=model_client,
        tools=[],
        system_message="""
You are the Summariser. You write the final human-readable answer after a task completes.

When to act: after FileAgent, CodeAgent, or DBAgent says TERMINATE.

Write a clear, concise summary of what was done and what the result was.
Do NOT call any tools.
End your message with: TERMINATE
""",
    )

    return file_agent, code_agent, db_agent, summariser

SELECTOR_PROMPT = """You are routing each message to the correct agent.

Available agents:
- FileAgent   → ONLY for: create/read/write/list .txt or .csv files
- CodeAgent   → ONLY for: generate code, run Python, analyze CSV data with computation
- DBAgent     → ONLY for: query SQLite database, load tables, list DB contents
- Summariser  → ONLY after a specialist finishes (their message contains TERMINATE)

Routing rules — read carefully:

1. "generate code for X" or "write a program for X" → CodeAgent
2. "generate code for X and save to file Y" → CodeAgent (it handles both)
3. "analyze X.csv" or "from X.csv list/filter/compute" → CodeAgent
4. "create a file" / "read a file" / "write to file" / "update a file" → FileAgent
5. "from table X" / "query the database" / "list DB tables" / "load into DB" → DBAgent
6. A specialist just said TERMINATE → Summariser
7. Summariser just responded → conversation is over

CRITICAL:
- Code generation always goes to CodeAgent, even if it mentions saving to a file
- CSV analysis/filtering goes to CodeAgent, not FileAgent
- FileAgent only creates/reads/updates raw file content — it does NOT analyze

Return ONLY the agent name. Nothing else.
"""
async def main():
    print("\n" + "═" * 62)
    print("  Day 3 — AutoGen Multi-Agent Orchestrator")
    print("  Agents : FileAgent | CodeAgent | DBAgent | Summariser")
    print("  Logs   : log_day3.json")
    print()
    print("  Example prompts:")
    print("    • Create clothes.csv with 10 rows of product data")
    print("    • Generate code for fibonacci series")
    print("    • Generate calculator code and save to calculator.txt")
    print("    • Analyze fruits.csv and list fruits with quantity > 3")
    print("    • Load clothes.csv into a table called clothes")
    print("    • From clothes table show the most expensive product")
    print("    • List the content of the database")
    print()
    print("  Type 'exit' to quit.")
    print("═" * 62 + "\n")

    file_agent, code_agent, db_agent, summariser = build_agents()

    termination = TextMentionTermination("TERMINATE")

    team = SelectorGroupChat(
        participants=[file_agent, code_agent, db_agent, summariser],
        model_client=model_client,
        termination_condition=termination,
        max_turns=20,
        selector_prompt=SELECTOR_PROMPT,
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break

        print()
        execution_steps = []
        try:
            async for msg in team.run_stream(task=user_input):
                if hasattr(msg, "source") and hasattr(msg, "content"):
                    source  = msg.source
                    content = msg.content
                    if isinstance(content, str) and content.strip():
                        print(f"---------- {source} ----------")
                        print(content)
                        execution_steps.append({"agent": source, "result": content})
        except Exception as e:
            print(f"\n[Error] {e}")
            print("[Info] Query failed. Please try again.\n")

        save_log(user_input, execution_steps)
        await team.reset()
        print()

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())