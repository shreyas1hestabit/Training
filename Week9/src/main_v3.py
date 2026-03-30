# """
# main.py — Day 3 Orchestrator (AutoGen, fully dynamic)
# Model backend: .env via config.py (Groq or Ollama)

# Solution to Groq tool-call syntax bug:
#   DBAgent has NO tools. All DB work is done in pure Python inside
#   a custom on_messages_stream override — the LLM never generates
#   a tool call for DB operations, eliminating all syntax errors.

# Install: pip install -U "autogen-agentchat" "autogen-ext[openai]" python-dotenv
# Run:     python main.py
# """

# import asyncio
# import csv
# import io
# import json
# import os
# import re
# import sqlite3
# import sys
# from datetime import datetime
# from typing import AsyncGenerator, Sequence

# from autogen_agentchat.agents import AssistantAgent
# from autogen_agentchat.base import Response
# from autogen_agentchat.messages import (
#     BaseAgentEvent, BaseChatMessage, TextMessage, AgentEvent
# )
# from autogen_agentchat.teams import SelectorGroupChat
# from autogen_agentchat.conditions import TextMentionTermination

# from src.utils.config import client as model_client

# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# from src.tools.code_executor import local_python_executor
# from src.tools.db_agent       import query_database, get_schema, clean_sql, DB_AGENT_SYSTEM_PROMPT
# from src.tools.file_agent     import file_manager


# # ── Paths & helpers ───────────────────────────────────────────────────────

# def _data_dir():
#     return os.path.join(
#         os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data"
#     )

# def _db_path():
#     return os.path.join(_data_dir(), "business.db")

# def _strip_fences(text):
#     text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
#     return re.sub(r"\n?```$", "", text.strip()).strip()

# async def _llm(system: str, user: str) -> str:
#     from autogen_core.models import SystemMessage, UserMessage
#     r = await model_client.create(messages=[
#         SystemMessage(content=system, source="system"),
#         UserMessage(content=user, source="user"),
#     ])
#     return r.content


# # ── Logger ────────────────────────────────────────────────────────────────

# LOG_FILE = "log_day3.json"

# def save_log(user_query: str, execution_steps: list) -> None:
#     entry = {
#         "timestamp": datetime.now().isoformat(),
#         "user_query": user_query,
#         "execution_steps": execution_steps,
#     }
#     logs = []
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, "r") as f:
#                 logs = json.load(f)
#         except Exception:
#             logs = []
#     logs.append(entry)
#     with open(LOG_FILE, "w") as f:
#         json.dump(logs, f, indent=4)
#     print(f"[Logger] Saved → {LOG_FILE}")


# # ── Pure-Python Router ────────────────────────────────────────────────────

# _DB_KEYWORDS = [
#     "database", "data_import", "sql", "sqlite", "_table",
#     "from the database", "extract all", "load into", "load csv",
#     "rows in", "how many rows", "rows of", "count rows",
#     "list tables", "show tables", "check the db",
#     "first 3 rows", "first three rows", "first 5 rows", "first five rows",
#     "all rows", "all data from",
#     "from clothes table", "from data_import", "from name_table",
#     "from laptops", "from the clothes", "from the data",
#     "clothes table", "data_import table", "name_table",
# ]

# _CODE_KEYWORDS = [
#     "generate code", "generate a code", "write code", "write a code",
#     "python code for", "create a program", "write a program",
#     "save it in", "save the code", "store the code",
#     "generate a python", "write python",
# ]

# def _classify(text: str) -> str:
#     t = text.lower()
#     # Static keyword match
#     if any(kw in t for kw in _DB_KEYWORDS):
#         return "db"
#     # Dynamic pattern: "in X table" / "from X table" / "of X table"
#     # catches any table name even if not in the static keyword list
#     if re.search(r"(?:in|from|of|into)\s+(?:the\s+)?(\w+)\s+table", t):
#         return "db"
#     # "X table show/list/find/count/rows" pattern
#     if re.search(r"(\w+)\s+table", t) and any(
#         kw in t for kw in ["show", "list", "find", "count", "rows", "cheapest",
#                             "expensive", "total", "first", "all", "extract"]):
#         return "db"
#     if any(kw in t for kw in _CODE_KEYWORDS):
#         return "code"
#     return "file"

# def make_selector():
#     def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
#         if len(messages) == 1:
#             return {"db": "DBAgent", "code": "CodeAgent", "file": "FileAgent"}[
#                 _classify(messages[0].content)]

#         last_source  = getattr(messages[-1], "source", "")
#         last_content = getattr(messages[-1], "content", "") or ""
#         if not isinstance(last_content, str):
#             last_content = ""

#         if "TERMINATE" in last_content and last_source in ("FileAgent", "CodeAgent", "DBAgent"):
#             return "Summariser"
#         if last_source == "Summariser":
#             return None
#         if last_source in ("FileAgent", "CodeAgent", "DBAgent"):
#             return last_source

#         return {"db": "DBAgent", "code": "CodeAgent", "file": "FileAgent"}[
#             _classify(messages[0].content if messages else "")]

#     return selector_func


# # ═════════════════════════════════════════════════════════════════════════
# # DB ENGINE — pure Python, no tool calls, no LLM-generated syntax
# # ═════════════════════════════════════════════════════════════════════════

# async def _db_get_schema_text() -> str:
#     """Read live schema from SQLite and return as text."""
#     db = _db_path()
#     if not os.path.exists(db):
#         return "No database found."
#     try:
#         lines = []
#         with sqlite3.connect(db) as conn:
#             tables = [r[0] for r in conn.execute(
#                 "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
#         if not tables:
#             return "Database exists but has no tables yet."
#         with sqlite3.connect(db) as conn:
#             for t in tables:
#                 count = conn.execute(f'SELECT COUNT(*) FROM "{t}";').fetchone()[0]
#                 cur   = conn.execute(f'SELECT * FROM "{t}" LIMIT 3;')
#                 cols  = [d[0] for d in cur.description] if cur.description else []
#                 rows  = cur.fetchall()
#                 lines.append(f"\nTable: {t}  ({count} rows)")
#                 lines.append(f"  Columns: {', '.join(cols)}")
#                 if rows:
#                     lines.append("  Sample rows:")
#                     for row in rows:
#                         lines.append("    " + " | ".join(str(v) for v in row))
#         return "\n".join(lines)
#     except Exception as e:
#         return f"DB read error: {e}"


# async def _db_answer(user_question: str) -> str:
#     """
#     Answer any DB question in pure Python:
#     1. Read live schema
#     2. Generate SQL via LLM (internal call, never a tool call)
#     3. Execute SQL
#     4. Return formatted result
#     """
#     schema_text = await _db_get_schema_text()

#     if "No database" in schema_text or "no tables" in schema_text:
#         return schema_text

#     # Generate SQL
#     sql_raw = await _llm(
#         DB_AGENT_SYSTEM_PROMPT,
#         f"Database schema:\n{schema_text}\n\nUser question: {user_question}\n\n"
#         "Write ONE valid SQLite SELECT statement. Output ONLY the raw SQL."
#     )
#     sql = clean_sql(sql_raw)
#     result = query_database(sql)

#     # Auto-retry with LIKE fallback
#     if "No rows matched" in result and "WHERE" in sql.upper():
#         sql_raw = await _llm(
#             DB_AGENT_SYSTEM_PROMPT,
#             f"Database schema:\n{schema_text}\n\nUser question: {user_question}\n\n"
#             "Previous query returned no rows. Rewrite using LIKE '%value%' COLLATE NOCASE. "
#             "Output ONLY the raw SQL."
#         )
#         sql = clean_sql(sql_raw)
#         result = query_database(sql)

#     return f"SQL: {sql}\n\nResults:\n{result}"


# async def _db_load_csv(csv_file: str, table_name: str) -> str:
#     """Load a CSV file into SQLite. Pure Python, no tool calls."""
#     db       = _db_path()
#     csv_path = os.path.join(_data_dir(), csv_file)
#     if not os.path.exists(csv_path):
#         return f"Error: '{csv_file}' not found in data/."
#     try:
#         with open(csv_path, newline="", encoding="utf-8") as f:
#             reader  = csv.reader(f)
#             headers = next(reader)
#             rows    = list(reader)
#         os.makedirs(os.path.dirname(db), exist_ok=True)
#         with sqlite3.connect(db) as conn:
#             cols = ", ".join(f'"{h.strip()}" TEXT' for h in headers)
#             conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
#             conn.execute(f'CREATE TABLE "{table_name}" ({cols});')
#             conn.executemany(
#                 f'INSERT INTO "{table_name}" VALUES ({",".join(["?"]*len(headers))});', rows)
#             conn.commit()
#         return (f"Loaded {len(rows)} rows into table '{table_name}' from '{csv_file}'.\n"
#                 f"Columns: {', '.join(headers)}")
#     except Exception as e:
#         return f"Error: {e}"


# # ═════════════════════════════════════════════════════════════════════════
# # CUSTOM DB AGENT — no tools, all logic in Python
# # ═════════════════════════════════════════════════════════════════════════

# async def _db_all_tables() -> str:
#     """Query every table in the DB and return all results."""
#     db = _db_path()
#     if not os.path.exists(db):
#         return "No database found."
#     try:
#         with sqlite3.connect(db) as conn:
#             tables = [r[0] for r in conn.execute(
#                 "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
#         if not tables:
#             return "Database has no tables yet."
#         parts = []
#         for t in tables:
#             result = query_database(f'SELECT * FROM "{t}" LIMIT 50;')
#             parts.append(f"=== Table: {t} ===\n{result}")
#         return "\n\n".join(parts)
#     except Exception as e:
#         return f"DB Error: {e}"


# class DBAgent(AssistantAgent):
#     """
#     DBAgent handles all database operations entirely in Python.
#     It has NO tools, so the LLM never generates a tool call.
#     All SQL generation and execution happens in _db_answer().
#     """

#     def __init__(self):
#         super().__init__(
#             name="DBAgent",
#             model_client=model_client,
#             tools=[],
#             system_message=(
#                 "You are DBAgent. You have already executed the database query "
#                 "and the result is shown in the conversation. "
#                 "Summarise the result clearly for the user and end with TERMINATE."
#             ),
#         )

#     async def on_messages_stream(
#         self,
#         messages: Sequence[BaseChatMessage],
#         cancellation_token,
#     ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
#         """Override: intercept, run DB logic in Python, yield result as text."""

#         # Find the original user question from message history
#         user_question = ""
#         for msg in messages:
#             if getattr(msg, "source", "") == "user":
#                 user_question = msg.content
#                 break
#         if not user_question:
#             user_question = messages[-1].content if messages else ""

#         # Detect intent and run appropriate DB operation
#         q = user_question.lower()

#         # Only trigger CSV load when the message explicitly says
#         # "load X.csv into table Y" or "import X.csv as Y"
#         load_match = re.search(
#             r'([\w\-]+\.csv)\s+(?:into|as|to)\s+(?:a\s+)?(?:the\s+)?(?:database|table|db|my\s+database|(?:table\s+)?)([\w]*)',
#             q
#         )
#         if load_match and any(kw in q for kw in ["load", "import", "convert", "add", "insert", "move"]):
#             csv_file   = load_match.group(1)
#             table_name = load_match.group(2).strip() or csv_file.replace(".csv", "").replace("-", "_")
#             result = await _db_load_csv(csv_file, table_name)
#         elif any(kw in q for kw in ["list tables", "show tables", "what tables", "available tables"]):
#             result = await _db_get_schema_text()
#         elif any(kw in q for kw in ["all the data", "extract all", "all data"]) and "table" not in q:
#             # "extract all data" with no specific table → query every table
#             result = await _db_all_tables()
#         else:
#             result = await _db_answer(user_question)

#         # Yield ONLY the Response — yielding TextMessage separately causes duplicate output
#         reply = f"{result}\n\nTERMINATE"
#         yield Response(
#             chat_message=TextMessage(content=reply, source=self.name)
#         )


# # ═════════════════════════════════════════════════════════════════════════
# # FILE ENGINE — pure Python helpers, used by FileAgent internally
# # ═════════════════════════════════════════════════════════════════════════

# def _file_list() -> str:
#     data_dir = _data_dir()
#     if not os.path.exists(data_dir):
#         return "data/ directory does not exist yet."
#     files = [f for f in os.listdir(data_dir) if f.endswith((".csv", ".txt"))]
#     return ("Files in data/:\n" + "\n".join(f"  • {f}" for f in sorted(files))
#             if files else "No files found in data/.")

# def _file_read(file_name: str) -> str:
#     return file_manager("read", file_name)

# def _file_write_csv(file_name: str, headers: list, rows: list) -> str:
#     buf = io.StringIO()
#     writer = csv.writer(buf)
#     writer.writerow(headers)
#     writer.writerows(rows)
#     return file_manager("write", file_name, buf.getvalue())

# def _file_append_csv(file_name: str, rows: list) -> str:
#     buf = io.StringIO()
#     writer = csv.writer(buf)
#     writer.writerows(rows)
#     return file_manager("append", file_name, buf.getvalue())

# async def _file_create_txt(file_name: str, description: str, num_lines: int = 10) -> str:
#     content = await _llm(
#         "Generate plain text file content. Output ONLY the raw text lines, no markdown.",
#         f"Generate exactly {num_lines} lines. Description: {description}\nOutput only the lines."
#     )
#     result = file_manager("write", file_name, _strip_fences(content) + "\n")
#     return f"Created '{file_name}'.\n{result}"

# async def _file_update_txt(file_name: str, instruction: str) -> str:
#     current = file_manager("read", file_name)
#     if current.startswith("Error"):
#         return current
#     updated = await _llm(
#         "Edit file content as instructed. Output ONLY the complete updated content.",
#         f"Current content:\n{current}\n\nInstruction: {instruction}\n\nOutput only the updated content."
#     )
#     result = file_manager("write", file_name, _strip_fences(updated) + "\n")
#     return f"Updated '{file_name}'.\n{result}"

# async def _file_analyze_csv(file_name: str, question: str) -> str:
#     """Read a CSV and answer a question about it using LLM reasoning."""
#     content = file_manager("read", file_name)
#     if content.startswith("Error"):
#         return content
#     answer = await _llm(
#         "You are a data analyst. Answer the question about the CSV data accurately. "
#         "Be concise and specific.",
#         f"CSV data from {file_name}:\n{content}\n\nQuestion: {question}\n\nAnswer:"
#     )
#     return f"From {file_name}:\n{answer}"

# async def _file_create_csv_from_llm(file_name: str, description: str, num_rows: int = 5) -> str:
#     """Generate CSV data via LLM and save it."""
#     raw = await _llm(
#         "You generate CSV data. Output ONLY the raw CSV including a header row. No markdown, no explanation.",
#         f"Generate a CSV file named {file_name} with {num_rows} rows of data.\n"
#         f"Description: {description}\nOutput ONLY the raw CSV text."
#     )
#     csv_text = _strip_fences(raw)
#     result = file_manager("write", file_name, csv_text + "\n")
#     return f"Created '{file_name}'.\n{result}"


# # ═════════════════════════════════════════════════════════════════════════
# # CUSTOM FILE AGENT — no tool calls for reading/analyzing, pure Python
# # ═════════════════════════════════════════════════════════════════════════

# class FileAgent(AssistantAgent):
#     """
#     FileAgent handles all file operations in pure Python.
#     Reading files and analyzing CSV data never goes through tool calls,
#     preventing Groq's malformed tool-call syntax errors.
#     Writing operations that need LLM (create_txt, update_txt, create_csv)
#     are also handled internally.
#     """

#     def __init__(self):
#         super().__init__(
#             name="FileAgent",
#             model_client=model_client,
#             tools=[],
#             system_message=(
#                 "You are FileAgent. The file operation result is shown above. "
#                 "Present it clearly to the user and end with TERMINATE."
#             ),
#         )

#     async def on_messages_stream(
#         self,
#         messages: Sequence[BaseChatMessage],
#         cancellation_token,
#     ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:

#         user_question = ""
#         for msg in messages:
#             if getattr(msg, "source", "") == "user":
#                 user_question = msg.content
#                 break
#         if not user_question:
#             user_question = messages[-1].content if messages else ""

#         result = await self._handle(user_question)
#         reply = f"{result}\n\nTERMINATE"
#         yield Response(chat_message=TextMessage(content=reply, source=self.name))

#     async def _handle(self, q: str) -> str:
#         ql = q.lower()

#         # List files
#         if any(kw in ql for kw in ["list files", "show files", "what files", "available files"]):
#             return _file_list()

#         # Read a specific file
#         file_match = re.search(r'([\w\-\.]+\.(?:csv|txt))', q)
#         file_name  = file_match.group(1) if file_match else None

#         # Analyze CSV (filter, total, cheapest, etc.)
#         analyze_kws = ["analyze", "analyse", "give me", "find", "list the", "show the",
#                        "total", "cheapest", "expensive", "count", "emp_id", "employees",
#                        "filter", "where", "greater than", "less than", "more than"]
#         if file_name and file_name.endswith(".csv") and any(kw in ql for kw in analyze_kws):
#             question = q
#             return await _file_analyze_csv(file_name, question)

#         # Read file contents
#         if file_name and any(kw in ql for kw in ["read", "show", "display", "open", "contents", "content of"]):
#             return _file_read(file_name)

#         # Create CSV with data
#         if any(kw in ql for kw in ["create", "make", "generate"]) and file_name and file_name.endswith(".csv"):
#             # Extract row count
#             row_match = re.search(r'(\d+)\s+rows?', ql)
#             num_rows  = int(row_match.group(1)) if row_match else 5
#             return await _file_create_csv_from_llm(file_name, q, num_rows)

#         # Create TXT file
#         if any(kw in ql for kw in ["create", "make", "write"]) and file_name and file_name.endswith(".txt"):
#             row_match = re.search(r'(\d+)\s+(?:rows?|lines?)', ql)
#             num_lines = int(row_match.group(1)) if row_match else 10
#             return await _file_create_txt(file_name, q, num_lines)

#         # Update/edit TXT file
#         if any(kw in ql for kw in ["update", "edit", "change", "modify"]) and file_name:
#             return await _file_update_txt(file_name, q)

#         # Fallback: if a file is mentioned, read it
#         if file_name:
#             return _file_read(file_name)

#         # No file mentioned
#         return _file_list()


# # ═════════════════════════════════════════════════════════════════════════
# # CODE TOOLS
# # ═════════════════════════════════════════════════════════════════════════

# async def tool_generate_code(description: str) -> str:
#     """
#     Generate and display Python code. Does NOT save to a file.
#     Arg: description — what the code should do e.g. 'fibonacci series'
#     """
#     code = await _llm(
#         "Expert Python programmer. Output ONLY raw Python code, no markdown.",
#         f"Write complete well-commented Python code for: {description}\n"
#         "Include main() and if __name__ == '__main__': block. Output ONLY raw Python code."
#     )
#     return _strip_fences(code)


# async def tool_save_code(spec: str) -> str:
#     """
#     Generate Python code and save it to a file.
#     Format: "filename | description of what the code should do"
#     Example: "fibonacci.txt | fibonacci series generator"
#     Example: "calc.py | basic calculator with add subtract multiply divide"
#     """
#     parts = [p.strip() for p in spec.split("|", 1)]
#     file_name   = parts[0]
#     description = parts[1] if len(parts) > 1 else file_name
#     code = await _llm(
#         "Expert Python programmer. Output ONLY raw Python code, no markdown.",
#         f"Write complete well-commented Python code for: {description}\n"
#         "Include main() and if __name__ == '__main__': block. Output ONLY raw Python code."
#     )
#     code = _strip_fences(code)
#     result = file_manager("write", file_name, code + "\n")
#     return f"Code saved.\n{result}\n\nPreview:\n{code[:300]}"


# async def tool_run_python(code: str) -> str:
#     """
#     Execute Python code and return stdout.
#     Only stdlib: csv, json, math, statistics, collections, io, datetime.
#     No os/subprocess/sys/shutil.
#     Arg: code — complete Python source code.
#     """
#     return local_python_executor(code)


# # ═════════════════════════════════════════════════════════════════════════
# # AGENTS
# # ═════════════════════════════════════════════════════════════════════════

# def build_agents():

#     file_agent = FileAgent()   # Custom agent — no tool calls, pure Python file engine

#     code_agent = AssistantAgent(
#         name="CodeAgent",
#         model_client=model_client,
#         tools=[tool_generate_code, tool_save_code, tool_run_python],
#         system_message="""You are CodeAgent. You generate and run Python code.

# Tools:
#   tool_generate_code(description) — generate and show code (not saved to file)
#   tool_save_code(spec)            — generate and save: "filename | description"
#   tool_run_python(code)           — execute Python code

# Use tool_generate_code to display code.
# Use tool_save_code to save code to a file.

# Always end with: TERMINATE""",
#     )

#     db_agent = DBAgent()   # Custom agent — no tools, pure Python DB engine

#     summariser = AssistantAgent(
#         name="Summariser",
#         model_client=model_client,
#         tools=[],
#         system_message="""You are Summariser. After a specialist finishes, write a clear 2-4 sentence summary of the result.
# Do not call any tools. Always end with: TERMINATE""",
#     )

#     return file_agent, code_agent, db_agent, summariser


# # ═════════════════════════════════════════════════════════════════════════
# # MAIN
# # ═════════════════════════════════════════════════════════════════════════

# async def main():
#     print("\n" + "═" * 62)
#     print("  Day 3 — AutoGen Multi-Agent Orchestrator")
#     print("  Agents : FileAgent | CodeAgent | DBAgent | Summariser")
#     print("  Routing: deterministic Python (no LLM selector)")
#     print("  DB     : pure Python engine (no tool calls for DB)")
#     print("  Logs   : log_day3.json")
#     print()
#     print("  Examples:")
#     print("    • Create clothes.csv with 5 rows of product data")
#     print("    • From clothes.csv total price of shoes and socks")
#     print("    • Generate code for fibonacci series")
#     print("    • Generate code for calculator and save it in cal.txt")
#     print("    • How many rows in data_import table")
#     print("    • Show first 3 rows of name_table")
#     print("    • From the database extract all the data")
#     print("    • List the cheapest product in clothes table")
#     print()
#     print("  Type 'exit' to quit.")
#     print("═" * 62 + "\n")

#     file_agent, code_agent, db_agent, summariser = build_agents()
#     termination = TextMentionTermination("TERMINATE")
#     selector    = make_selector()

#     team = SelectorGroupChat(
#         participants=[file_agent, code_agent, db_agent, summariser],
#         model_client=model_client,
#         termination_condition=termination,
#         max_turns=20,
#         selector_func=selector,
#     )

#     while True:
#         try:
#             user_input = input("You: ").strip()
#         except (EOFError, KeyboardInterrupt):
#             print("\nGoodbye!")
#             break

#         if not user_input:
#             continue
#         if user_input.lower() in {"exit", "quit", "q"}:
#             print("Goodbye!")
#             break

#         print()
#         execution_steps = []
#         try:
#             async for msg in team.run_stream(task=user_input):
#                 if hasattr(msg, "source") and hasattr(msg, "content"):
#                     source  = msg.source
#                     content = msg.content
#                     if isinstance(content, str) and content.strip():
#                         print(f"---------- {source} ----------")
#                         print(content)
#                         execution_steps.append({"agent": source, "result": content})
#         except Exception as e:
#             err = str(e)
#             if "429" in err or "rate_limit_exceeded" in err:
#                 m = re.search(r"Please try again in ([\dm\s\.]+)", err)
#                 wait = m.group(1).strip() if m else "a few minutes"
#                 print(f"\n[Rate Limit] Daily token quota reached. Wait {wait}.\n")
#             else:
#                 print(f"\n[Error] {e}\n")

#         save_log(user_input, execution_steps)
#         await team.reset()
#         print()

#     await model_client.close()


# if __name__ == "__main__":
#     asyncio.run(main())

"""
main.py — Day 3 Orchestrator (AutoGen, fully dynamic)
Model backend: .env via config.py (Groq or Ollama)

Solution to Groq tool-call syntax bug:
  DBAgent has NO tools. All DB work is done in pure Python inside
  a custom on_messages_stream override — the LLM never generates
  a tool call for DB operations, eliminating all syntax errors.

Install: pip install -U "autogen-agentchat" "autogen-ext[openai]" python-dotenv
Run:     python main.py
"""

import asyncio
import csv
import io
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from typing import AsyncGenerator, Sequence

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import (
    BaseAgentEvent, BaseChatMessage, TextMessage, AgentEvent
)
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination

from src.utils.config import client as model_client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from src.tools.code_executor import local_python_executor
from src.tools.db_agent       import query_database, get_schema, clean_sql, DB_AGENT_SYSTEM_PROMPT
from src.tools.file_agent     import file_manager


# ── Paths & helpers ───────────────────────────────────────────────────────

def _data_dir():
    return os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data"
    )

def _db_path():
    return os.path.join(_data_dir(), "business.db")

def _strip_fences(text):
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    return re.sub(r"\n?```$", "", text.strip()).strip()

async def _llm(system: str, user: str, retries: int = 2) -> str:
    """Single-turn LLM call with automatic retry on rate limit (429)."""
    import asyncio
    from autogen_core.models import SystemMessage, UserMessage
    for attempt in range(retries + 1):
        try:
            r = await model_client.create(messages=[
                SystemMessage(content=system, source="system"),
                UserMessage(content=user, source="user"),
            ])
            return r.content
        except Exception as e:
            err = str(e)
            if ("429" in err or "rate_limit_exceeded" in err) and attempt < retries:
                # Parse wait time from error message, default to 65 seconds
                m = re.search(r"try again in ([\d\.]+)s", err)
                wait = float(m.group(1)) + 2 if m else 65
                print(f"[Rate Limit] Waiting {wait:.0f}s before retry ({attempt+1}/{retries})...")
                await asyncio.sleep(wait)
            else:
                raise


# ── Logger ────────────────────────────────────────────────────────────────

LOG_FILE = "log_day3.json"

def save_log(user_query: str, execution_steps: list) -> None:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_query": user_query,
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


# ── Pure-Python Router ────────────────────────────────────────────────────

_DB_KEYWORDS = [
    "database", "data_import", "sql", "sqlite", "_table",
    "from the database", "from database", "extract all", "load into", "load csv",
    "rows in", "how many rows", "rows of", "count rows",
    "list tables", "show tables", "check the db",
    "first 3 rows", "first three rows", "first 5 rows", "first five rows",
    "all rows", "all data from",
    "from clothes table", "from data_import", "from name_table",
    "from laptops", "from the clothes", "from the data",
    "clothes table", "data_import table", "name_table",
]

_CODE_KEYWORDS = [
    "generate code", "generate a code", "write code", "write a code",
    "python code for", "create a program", "write a program",
    "save it in", "save the code", "store the code",
    "generate a python", "write python",
]

def _classify(text: str) -> str:
    t = text.lower()
    # Static keyword match
    if any(kw in t for kw in _DB_KEYWORDS):
        return "db"
    # Dynamic pattern: "in X table" / "from X table" / "of X table"
    # catches any table name even if not in the static keyword list
    if re.search(r"(?:in|from|of|into)\s+(?:the\s+)?(\w+)\s+table", t):
        return "db"
    # "X table show/list/find/count/rows" pattern
    if re.search(r"(\w+)\s+table", t) and any(
        kw in t for kw in ["show", "list", "find", "count", "rows", "cheapest",
                            "expensive", "total", "first", "all", "extract"]):
        return "db"
    if any(kw in t for kw in _CODE_KEYWORDS):
        return "code"
    return "file"

def make_selector():
    def selector_func(messages: Sequence[BaseAgentEvent | BaseChatMessage]) -> str | None:
        if len(messages) == 1:
            return {"db": "DBAgent", "code": "CodeAgent", "file": "FileAgent"}[
                _classify(messages[0].content)]

        last_source  = getattr(messages[-1], "source", "")
        last_content = getattr(messages[-1], "content", "") or ""
        if not isinstance(last_content, str):
            last_content = ""

        if "TERMINATE" in last_content and last_source in ("FileAgent", "CodeAgent", "DBAgent"):
            return "Summariser"
        if last_source == "Summariser":
            return None
        if last_source in ("FileAgent", "CodeAgent", "DBAgent"):
            return last_source

        return {"db": "DBAgent", "code": "CodeAgent", "file": "FileAgent"}[
            _classify(messages[0].content if messages else "")]

    return selector_func


# ═════════════════════════════════════════════════════════════════════════
# DB ENGINE — pure Python, no tool calls, no LLM-generated syntax
# ═════════════════════════════════════════════════════════════════════════

async def _db_get_schema_text() -> str:
    """Read live schema from SQLite and return as text."""
    db = _db_path()
    if not os.path.exists(db):
        return "No database found."
    try:
        lines = []
        with sqlite3.connect(db) as conn:
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
        if not tables:
            return "Database exists but has no tables yet."
        with sqlite3.connect(db) as conn:
            for t in tables:
                count = conn.execute(f'SELECT COUNT(*) FROM "{t}";').fetchone()[0]
                cur   = conn.execute(f'SELECT * FROM "{t}" LIMIT 3;')
                cols  = [d[0] for d in cur.description] if cur.description else []
                rows  = cur.fetchall()
                lines.append(f"\nTable: {t}  ({count} rows)")
                lines.append(f"  Columns: {', '.join(cols)}")
                if rows:
                    lines.append("  Sample rows:")
                    for row in rows:
                        lines.append("    " + " | ".join(str(v) for v in row))
        return "\n".join(lines)
    except Exception as e:
        return f"DB read error: {e}"


async def _db_answer(user_question: str) -> str:
    """
    Answer any DB question in pure Python:
    1. Read live schema
    2. Generate SQL via LLM (internal call, never a tool call)
    3. Execute SQL
    4. Return formatted result
    """
    schema_text = await _db_get_schema_text()

    if "No database" in schema_text or "no tables" in schema_text:
        return schema_text

    # Generate SQL
    sql_raw = await _llm(
        DB_AGENT_SYSTEM_PROMPT,
        f"Database schema:\n{schema_text}\n\nUser question: {user_question}\n\n"
        "Write ONE valid SQLite SELECT statement. Output ONLY the raw SQL."
    )
    sql = clean_sql(sql_raw)
    result = query_database(sql)

    # Auto-retry with LIKE fallback
    if "No rows matched" in result and "WHERE" in sql.upper():
        sql_raw = await _llm(
            DB_AGENT_SYSTEM_PROMPT,
            f"Database schema:\n{schema_text}\n\nUser question: {user_question}\n\n"
            "Previous query returned no rows. Rewrite using LIKE '%value%' COLLATE NOCASE. "
            "Output ONLY the raw SQL."
        )
        sql = clean_sql(sql_raw)
        result = query_database(sql)

    return f"SQL: {sql}\n\nResults:\n{result}"


async def _db_load_csv(csv_file: str, table_name: str) -> str:
    """Load a CSV file into SQLite. Pure Python, no tool calls."""
    db       = _db_path()
    csv_path = os.path.join(_data_dir(), csv_file)
    if not os.path.exists(csv_path):
        return f"Error: '{csv_file}' not found in data/."
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader  = csv.reader(f)
            headers = next(reader)
            rows    = list(reader)
        os.makedirs(os.path.dirname(db), exist_ok=True)
        with sqlite3.connect(db) as conn:
            cols = ", ".join(f'"{h.strip()}" TEXT' for h in headers)
            conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
            conn.execute(f'CREATE TABLE "{table_name}" ({cols});')
            conn.executemany(
                f'INSERT INTO "{table_name}" VALUES ({",".join(["?"]*len(headers))});', rows)
            conn.commit()
        return (f"Loaded {len(rows)} rows into table '{table_name}' from '{csv_file}'.\n"
                f"Columns: {', '.join(headers)}")
    except Exception as e:
        return f"Error: {e}"


# ═════════════════════════════════════════════════════════════════════════
# CUSTOM DB AGENT — no tools, all logic in Python
# ═════════════════════════════════════════════════════════════════════════

async def _db_all_tables() -> str:
    """Query every table in the DB and return all results."""
    db = _db_path()
    if not os.path.exists(db):
        return "No database found."
    try:
        with sqlite3.connect(db) as conn:
            tables = [r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
        if not tables:
            return "Database has no tables yet."
        parts = []
        for t in tables:
            result = query_database(f'SELECT * FROM "{t}" LIMIT 50;')
            parts.append(f"=== Table: {t} ===\n{result}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"DB Error: {e}"


class DBAgent(AssistantAgent):
    """
    DBAgent handles all database operations entirely in Python.
    It has NO tools, so the LLM never generates a tool call.
    All SQL generation and execution happens in _db_answer().
    """

    def __init__(self):
        super().__init__(
            name="DBAgent",
            model_client=model_client,
            tools=[],
            system_message=(
                "You are DBAgent. You have already executed the database query "
                "and the result is shown in the conversation. "
                "Summarise the result clearly for the user and end with TERMINATE."
            ),
        )

    async def on_messages_stream(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token,
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        """Override: intercept, run DB logic in Python, yield result as text."""

        # Find the original user question from message history
        user_question = ""
        for msg in messages:
            if getattr(msg, "source", "") == "user":
                user_question = msg.content
                break
        if not user_question:
            user_question = messages[-1].content if messages else ""

        # Detect intent and run appropriate DB operation
        q = user_question.lower()

        # Only trigger CSV load when the message explicitly says
        # "load X.csv into table Y" or "import X.csv as Y"
        load_match = re.search(
            r'([\w\-]+\.csv)\s+(?:into|as|to)\s+(?:a\s+)?(?:the\s+)?(?:database|table|db|my\s+database|(?:table\s+)?)([\w]*)',
            q
        )
        if load_match and any(kw in q for kw in ["load", "import", "convert", "add", "insert", "move"]):
            csv_file   = load_match.group(1)
            table_name = load_match.group(2).strip() or csv_file.replace(".csv", "").replace("-", "_")
            result = await _db_load_csv(csv_file, table_name)
        elif any(kw in q for kw in ["list tables", "show tables", "what tables", "available tables"]):
            result = await _db_get_schema_text()
        elif any(kw in q for kw in ["all the data", "extract all", "all data"]) and "table" not in q:
            # "extract all data" with no specific table → query every table
            result = await _db_all_tables()
        else:
            result = await _db_answer(user_question)

        # Yield ONLY the Response — yielding TextMessage separately causes duplicate output
        reply = f"{result}\n\nTERMINATE"
        yield Response(
            chat_message=TextMessage(content=reply, source=self.name)
        )


# ═════════════════════════════════════════════════════════════════════════
# FILE ENGINE — pure Python helpers, used by FileAgent internally
# ═════════════════════════════════════════════════════════════════════════

def _file_list() -> str:
    data_dir = _data_dir()
    if not os.path.exists(data_dir):
        return "data/ directory does not exist yet."
    files = [f for f in os.listdir(data_dir) if f.endswith((".csv", ".txt"))]
    return ("Files in data/:\n" + "\n".join(f"  • {f}" for f in sorted(files))
            if files else "No files found in data/.")

def _file_read(file_name: str) -> str:
    return file_manager("read", file_name)

def _file_write_csv(file_name: str, headers: list, rows: list) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    return file_manager("write", file_name, buf.getvalue())

def _file_append_csv(file_name: str, rows: list) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return file_manager("append", file_name, buf.getvalue())

async def _file_create_txt(file_name: str, description: str, num_lines: int = 10) -> str:
    content = await _llm(
        "Generate plain text file content. Output ONLY the raw text lines, no markdown.",
        f"Generate exactly {num_lines} lines. Description: {description}\nOutput only the lines."
    )
    result = file_manager("write", file_name, _strip_fences(content) + "\n")
    return f"Created '{file_name}'.\n{result}"

async def _file_update_txt(file_name: str, instruction: str) -> str:
    current = file_manager("read", file_name)
    if current.startswith("Error"):
        return current
    updated = await _llm(
        "Edit file content as instructed. Output ONLY the complete updated content.",
        f"Current content:\n{current}\n\nInstruction: {instruction}\n\nOutput only the updated content."
    )
    result = file_manager("write", file_name, _strip_fences(updated) + "\n")
    return f"Updated '{file_name}'.\n{result}"

async def _file_analyze_csv(file_name: str, question: str) -> str:
    """Read a CSV and answer a question using only its actual data values."""
    raw = file_manager("read", file_name)
    if raw.startswith("Error"):
        return raw

    # Parse headers and a sample row dynamically so the prompt is data-driven
    lines = [l for l in raw.strip().split("\n") if l.strip()]
    headers = lines[0] if lines else ""
    sample  = lines[1] if len(lines) > 1 else ""

    system = (
        f"You are a data analyst working with a CSV file named '{file_name}'.\n"
        f"The columns are: {headers}\n"
        f"A sample row looks like: {sample}\n\n"
        "Rules:\n"
        "- Answer using ONLY the values present in the data. Never guess or infer.\n"
        "- Filter rows by the exact column values, not by assumptions about names.\n"
        "- If the question asks about a column that exists, use that column directly.\n"
        "- Show each matching result on its own line with the relevant column values.\n"
        "- If no rows match, say so clearly."
    )

    user = (
        f"Full CSV data:\n{raw}\n\n"
        f"Question: {question}\n\n"
        "Answer based only on the data above:"
    )

    answer = await _llm(system, user)
    return f"From {file_name}:\n{answer}"

async def _file_create_csv_from_llm(file_name: str, description: str, num_rows: int = 5) -> str:
    """Generate CSV data via LLM and save it."""
    raw = await _llm(
        "You generate CSV data. Output ONLY the raw CSV including a header row. No markdown, no explanation.",
        f"Generate a CSV file named {file_name} with {num_rows} rows of data.\n"
        f"Description: {description}\nOutput ONLY the raw CSV text."
    )
    csv_text = _strip_fences(raw)
    result = file_manager("write", file_name, csv_text + "\n")
    return f"Created '{file_name}'.\n{result}"


# ═════════════════════════════════════════════════════════════════════════
# CUSTOM FILE AGENT — no tool calls for reading/analyzing, pure Python
# ═════════════════════════════════════════════════════════════════════════

class FileAgent(AssistantAgent):
    """
    FileAgent handles all file operations in pure Python.
    Reading files and analyzing CSV data never goes through tool calls,
    preventing Groq's malformed tool-call syntax errors.
    Writing operations that need LLM (create_txt, update_txt, create_csv)
    are also handled internally.
    """

    def __init__(self):
        super().__init__(
            name="FileAgent",
            model_client=model_client,
            tools=[],
            system_message=(
                "You are FileAgent. The file operation result is shown above. "
                "Present it clearly to the user and end with TERMINATE."
            ),
        )

    async def on_messages_stream(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token,
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:

        user_question = ""
        for msg in messages:
            if getattr(msg, "source", "") == "user":
                user_question = msg.content
                break
        if not user_question:
            user_question = messages[-1].content if messages else ""

        result = await self._handle(user_question)
        reply = f"{result}\n\nTERMINATE"
        yield Response(chat_message=TextMessage(content=reply, source=self.name))

    async def _handle(self, q: str) -> str:
        ql = q.lower()

        # List files
        if any(kw in ql for kw in ["list files", "show files", "what files", "available files"]):
            return _file_list()

        # Read a specific file
        file_match = re.search(r'([\w\-\.]+\.(?:csv|txt))', q)
        file_name  = file_match.group(1) if file_match else None

        # Analyze CSV (filter, total, cheapest, etc.)
        analyze_kws = ["analyze", "analyse", "give me", "find", "list the", "show the",
                       "total", "cheapest", "expensive", "count", "emp_id", "employees",
                       "filter", "where", "greater than", "less than", "more than"]
        if file_name and file_name.endswith(".csv") and any(kw in ql for kw in analyze_kws):
            question = q
            return await _file_analyze_csv(file_name, question)

        # Read file contents
        if file_name and any(kw in ql for kw in ["read", "show", "display", "open", "contents", "content of"]):
            return _file_read(file_name)

        # Create CSV with data
        if any(kw in ql for kw in ["create", "make", "generate"]) and file_name and file_name.endswith(".csv"):
            # Extract row count
            row_match = re.search(r'(\d+)\s+rows?', ql)
            num_rows  = int(row_match.group(1)) if row_match else 5
            return await _file_create_csv_from_llm(file_name, q, num_rows)

        # Create TXT file
        if any(kw in ql for kw in ["create", "make", "write"]) and file_name and file_name.endswith(".txt"):
            row_match = re.search(r'(\d+)\s+(?:rows?|lines?)', ql)
            num_lines = int(row_match.group(1)) if row_match else 10
            return await _file_create_txt(file_name, q, num_lines)

        # Update/edit TXT file
        if any(kw in ql for kw in ["update", "edit", "change", "modify"]) and file_name:
            return await _file_update_txt(file_name, q)

        # Fallback: if a file is mentioned, read it
        if file_name:
            return _file_read(file_name)

        # No file mentioned
        return _file_list()


# ═════════════════════════════════════════════════════════════════════════
# CODE TOOLS
# ═════════════════════════════════════════════════════════════════════════

# ═════════════════════════════════════════════════════════════════════════
# CODE ENGINE — pure Python, no tool calls
# ═════════════════════════════════════════════════════════════════════════

async def _generate_and_save_code(description: str, file_name: str) -> str:
    """Generate complete Python code, save full version to data/<file_name>."""
    system_prompt = (
        "You are an expert Python programmer. "
        "Output ONLY raw Python code — no markdown fences, no explanation."
    )
    user_prompt = (
        f"Write complete, correct, well-commented Python code for: {description}\n"
        "Requirements:\n"
        "1. Write a COMPLETE, PROPER program with all necessary logic and comments\n"
        "2. Use input() to get values from the user where appropriate\n"
        "3. Include a main() function\n"
        "4. End with: if __name__ == '__main__': main()\n"
        "5. Only stdlib: math, statistics, csv, json, collections, datetime, io\n"
        "6. No os, sys, subprocess, shutil imports\n"
        "7. Every print must have a descriptive label\n"
        "Output ONLY raw Python code."
    )

    code = _strip_fences(await _llm(system_prompt, user_prompt))

    # Save the FULL code including input() — this is what the user gets
    out_path = os.path.join(_data_dir(), file_name)
    os.makedirs(_data_dir(), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(code + "\n")

    # Verify syntax/logic by running a version with input() replaced
    # so execution does not block — only for error detection, not for saving
    import re as _re
    test_code = _re.sub(r'input\s*\([^)]*\)', '"5"', code)
    test_result = local_python_executor(test_code)

    # If error, regenerate and re-save
    if test_result.startswith("Python Error") or test_result.startswith("[SECURITY"):
        code = _strip_fences(await _llm(
            system_prompt,
            f"This code has an error:\n\n{code}\n\nError: {test_result}\n\n"
            "Rewrite it fixing the error. Output ONLY raw Python code."
        ))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        test_code = _re.sub(r'input\s*\([^)]*\)', '"5"', code)
        test_result = local_python_executor(test_code)

    return (
        f"Saved: {file_name} ({len(code)} bytes)\n\n"
        f"{code}\n\n"
        f"--- Verified output (with example inputs) ---\n{test_result}"
    )


# ═════════════════════════════════════════════════════════════════════════
# CUSTOM CODE AGENT — no tool calls, all logic in Python
# ═════════════════════════════════════════════════════════════════════════

class CodeAgent(AssistantAgent):
    """
    CodeAgent generates and saves Python code entirely in Python.
    No tool calls = no Groq syntax errors.
    """

    def __init__(self):
        super().__init__(
            name="CodeAgent",
            model_client=model_client,
            tools=[],
            system_message=(
                "You are CodeAgent. The code has been generated, verified, and saved. "
                "Briefly confirm what was done and end with TERMINATE."
            ),
        )

    async def on_messages_stream(
        self,
        messages: Sequence[BaseChatMessage],
        cancellation_token,
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:

        user_question = ""
        for msg in messages:
            if getattr(msg, "source", "") == "user":
                user_question = msg.content
                break
        if not user_question:
            user_question = messages[-1].content if messages else ""

        result = await self._handle(user_question)
        reply = f"{result}\n\nTERMINATE"
        yield Response(chat_message=TextMessage(content=reply, source=self.name))

    async def _handle(self, user_question: str) -> str:
        q = user_question.lower()

        # Extract explicit filename if given: "save to X.py", "store in X.txt", "in X.py"
        file_match = re.search(
            r'(?:save(?:\s+it)?\s+(?:to|in|as)|store(?:\s+it)?\s+in|in)\s+([\w\-\.]+\.(?:py|txt))',
            q
        )
        explicit_file = file_match.group(1) if file_match else None

        # Extract description — strip file-related instructions
        description = re.sub(
            r'(?:write|generate|create|make)\s+(?:a\s+)?(?:python\s+)?code\s+(?:for|to)\s*',
            "", q, flags=re.I
        ).strip()
        description = re.sub(
            r'(?:and\s+)?(?:save|store)(?:\s+it)?\s+(?:to|in|as)?\s*[\w\-\.]*\.(?:py|txt)\s*',
            "", description, flags=re.I
        ).strip() or user_question

        # Derive filename
        if explicit_file:
            file_name = explicit_file
            # Force .py extension
            if not file_name.endswith(".py"):
                file_name = os.path.splitext(file_name)[0] + ".py"
        else:
            slug = re.sub(r"[^a-z0-9]+", "_", description).strip("_")[:35]
            file_name = f"{slug}.py"

        return await _generate_and_save_code(description, file_name)


# ═════════════════════════════════════════════════════════════════════════
# AGENTS
# ═════════════════════════════════════════════════════════════════════════

def build_agents():

    file_agent = FileAgent()   # Custom agent — no tool calls, pure Python file engine

    code_agent = CodeAgent()   # Custom agent — no tool calls, pure Python code engine

    db_agent = DBAgent()   # Custom agent — no tools, pure Python DB engine

    summariser = AssistantAgent(
        name="Summariser",
        model_client=model_client,
        tools=[],
        system_message="""You are Summariser. After a specialist finishes, write a clear 2-4 sentence summary of the result.
Do not call any tools. Always end with: TERMINATE""",
    )

    return file_agent, code_agent, db_agent, summariser


# ═════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════

async def main():
    print("\n" + "═" * 62)
    print("  Day 3 — AutoGen Multi-Agent Orchestrator")
    print("  Agents : FileAgent | CodeAgent | DBAgent | Summariser")
    print("  Routing: deterministic Python (no LLM selector)")
    print("  DB     : pure Python engine (no tool calls for DB)")
    print("  Logs   : log_day3.json")
    print()
    print("  Examples:")
    print("    • Create clothes.csv with 5 rows of product data")
    print("    • From clothes.csv total price of shoes and socks")
    print("    • Generate code for fibonacci series")
    print("    • Generate code for calculator and save it in cal.txt")
    print("    • How many rows in data_import table")
    print("    • Show first 3 rows of name_table")
    print("    • From the database extract all the data")
    print("    • List the cheapest product in clothes table")
    print()
    print("  Type 'exit' to quit.")
    print("═" * 62 + "\n")

    file_agent, code_agent, db_agent, summariser = build_agents()
    termination = TextMentionTermination("TERMINATE")
    selector    = make_selector()

    team = SelectorGroupChat(
        participants=[file_agent, code_agent, db_agent, summariser],
        model_client=model_client,
        termination_condition=termination,
        max_turns=20,
        selector_func=selector,
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
            err = str(e)
            if "429" in err or "rate_limit_exceeded" in err:
                m = re.search(r"Please try again in ([\dm\s\.]+)", err)
                wait = m.group(1).strip() if m else "a few minutes"
                print(f"\n[Rate Limit] Daily token quota reached. Wait {wait}.\n")
            else:
                print(f"\n[Error] {e}\n")

        save_log(user_input, execution_steps)
        await team.reset()
        print()

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())