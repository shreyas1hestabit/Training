# # # import asyncio
# # # import csv as csv_module
# # # import io
# # # import os
# # # import json
# # # import re
# # # from collections import Counter
# # # from datetime import datetime

# # # from autogen_core.models import UserMessage

# # # from src.utils.config import client
# # # from src.tools.code_executor import python_tool
# # # from src.tools.db_agent import db_tool
# # # from src.tools.file_agent import file_manager


# # # # ---------------------------------------------------------------------------
# # # # SECURITY GUARDS
# # # # ---------------------------------------------------------------------------

# # # def is_safe_sql(query: str) -> bool:
# # #     forbidden = ["drop", "delete", "truncate", "update", "alter"]
# # #     return not any(word in query.lower() for word in forbidden)


# # # def is_safe_python(code: str) -> bool:
# # #     forbidden = ["os.remove", "os.rmdir", "shutil", "subprocess", "sys.exit"]
# # #     return not any(word in code.lower() for word in forbidden)


# # # # ---------------------------------------------------------------------------
# # # # HELPERS
# # # # ---------------------------------------------------------------------------

# # # def extract_code(raw: str) -> str:
# # #     """
# # #     Strips ALL markdown code fences from LLM output.
# # #     Handles ```python, ```py, ``` and any other variant.
# # #     """
# # #     # Remove opening fence (``` optionally followed by a language tag)
# # #     cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
# # #     # Remove closing fence
# # #     cleaned = re.sub(r"\n?```$", "", cleaned.strip())
# # #     return cleaned.strip()


# # # async def call_llm(prompt: str) -> str:
# # #     """Calls the AutoGen LLM client and returns the text response."""
# # #     response = await client.create(messages=[UserMessage(content=prompt, source="user")])
# # #     # autogen_core returns a CreateResult; .content is the string text
# # #     return str(response.content).strip()


# # # async def save_log(query: str, steps: list):
# # #     log_file = "logs_day3.json"
# # #     log_entry = {
# # #         "timestamp": datetime.now().isoformat(),
# # #         "user_query": query,
# # #         "execution_steps": steps,
# # #     }
# # #     logs = []
# # #     if os.path.exists(log_file):
# # #         try:
# # #             with open(log_file, "r") as f:
# # #                 logs = json.load(f)
# # #         except Exception:
# # #             logs = []
# # #     logs.append(log_entry)
# # #     with open(log_file, "w") as f:
# # #         json.dump(logs, f, indent=4)


# # # # ---------------------------------------------------------------------------
# # # # CSV ANALYSIS ENGINE  (pure Python — no LLM-generated code)
# # # # ---------------------------------------------------------------------------

# # # def analyze_csv(rows: list, columns: list, operation: dict) -> str:
# # #     """
# # #     Executes a structured CSV operation entirely in Python.
# # #     `operation` is a dict with keys:
# # #         type   : "unique" | "filter" | "count" | "list" | "top_n"
# # #         column : column name to operate on (stripped, matched case-insensitively)
# # #         filter_column : (for filter) column to filter by
# # #         filter_value  : (for filter) value to match (case-insensitive)
# # #         n      : (for top_n) number of results
# # #     """
# # #     op_type = operation.get("type", "list")

# # #     # Case-insensitive column lookup
# # #     col_map = {c.strip().lower(): c.strip() for c in columns}

# # #     def resolve(col_hint: str):
# # #         """Return the real column name from a hint, or None."""
# # #         if not col_hint:
# # #             return None
# # #         hint = col_hint.strip().lower()
# # #         if hint in col_map:
# # #             return col_map[hint]
# # #         # partial match
# # #         for k, v in col_map.items():
# # #             if hint in k or k in hint:
# # #                 return v
# # #         return None

# # #     target_col = resolve(operation.get("column", ""))
# # #     filter_col = resolve(operation.get("filter_column", ""))
# # #     filter_val = (operation.get("filter_value") or "").strip().lower()

# # #     if op_type == "unique":
# # #         if not target_col:
# # #             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
# # #         seen = set()
# # #         results = []
# # #         for row in rows:
# # #             val = row.get(target_col, "").strip()
# # #             if val and val not in seen:
# # #                 seen.add(val)
# # #                 results.append(val)
# # #         return "\n".join(sorted(results)) if results else "No values found."

# # #     elif op_type == "filter":
# # #         if not target_col or not filter_col:
# # #             return f"Need both a display column and a filter column. Available: {columns}"
# # #         results = []
# # #         for row in rows:
# # #             if row.get(filter_col, "").strip().lower() == filter_val:
# # #                 results.append(row.get(target_col, "").strip())
# # #         return "\n".join(results) if results else f"No rows where {filter_col}={filter_val}."

# # #     elif op_type == "count":
# # #         if filter_col and filter_val:
# # #             count = sum(
# # #                 1 for row in rows
# # #                 if row.get(filter_col, "").strip().lower() == filter_val
# # #             )
# # #             return f"Count of rows where {filter_col}={filter_val}: {count}"
# # #         return f"Total rows: {len(rows)}"

# # #     elif op_type == "top_n":
# # #         n = int(operation.get("n", 5))
# # #         if not target_col:
# # #             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
# # #         counts = Counter(row.get(target_col, "").strip() for row in rows)
# # #         top = counts.most_common(n)
# # #         return "\n".join(f"{v}: {c}" for v, c in top)

# # #     else:  # "list" — just dump the column
# # #         if not target_col:
# # #             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
# # #         results = [row.get(target_col, "").strip() for row in rows if row.get(target_col)]
# # #         return "\n".join(results) if results else "No values found."


# # # # ---------------------------------------------------------------------------
# # # # FILE + CODE AGENT PIPELINE
# # # # ---------------------------------------------------------------------------

# # # async def run_file_code_pipeline(user_query: str, target_file: str) -> list:
# # #     """
# # #     Step 1 — File Agent  : Read + parse the CSV into rows.
# # #     Step 2 — Plan Agent  : LLM returns a JSON operation descriptor (what to do).
# # #     Step 3 — Code Agent  : Python executes the operation deterministically.
# # #     Step 4 — Report Agent: LLM summarises the results in plain English.
# # #     """
# # #     steps = []

# # #     # ------------------------------------------------------------------
# # #     # Step 1 — Read and parse CSV
# # #     # ------------------------------------------------------------------
# # #     raw_content = file_manager(action="read", file_name=target_file)
# # #     if raw_content.startswith("Error"):
# # #         print(f"[File Agent] {raw_content}")
# # #         return steps

# # #     reader = csv_module.DictReader(io.StringIO(raw_content))
# # #     rows = list(reader)
# # #     columns = list(rows[0].keys()) if rows else []

# # #     steps.append({"agent": "File Agent", "file": target_file, "status": "Read Success"})
# # #     print(f"[File Agent] Read '{target_file}' — {len(rows)} rows, columns: {columns}")

# # #     # ------------------------------------------------------------------
# # #     # Step 2 — Plan: ask LLM what operation to perform (JSON only)
# # #     # ------------------------------------------------------------------
# # #     plan_prompt = f"""You are a data analysis planner. Given a user query and CSV columns, 
# # # return a JSON object describing the operation to perform.

# # # CSV columns: {columns}
# # # User query: {user_query}

# # # Return ONLY a valid JSON object with these fields:
# # # {{
# # #   "type": "unique" | "filter" | "count" | "list" | "top_n",
# # #   "column": "<column name to display or analyse>",
# # #   "filter_column": "<column to filter by, or empty string>",
# # #   "filter_value": "<value to filter for, or empty string>",
# # #   "n": <number for top_n, or 5>
# # # }}

# # # Examples:
# # # - "unique first names"      → {{"type":"unique","column":"First Name","filter_column":"","filter_value":"","n":5}}
# # # - "all males"               → {{"type":"filter","column":"First Name","filter_column":"Sex","filter_value":"Male","n":5}}
# # # - "how many females"        → {{"type":"count","column":"","filter_column":"Sex","filter_value":"Female","n":5}}
# # # - "top 5 job titles"        → {{"type":"top_n","column":"Job Title","filter_column":"","filter_value":"","n":5}}

# # # Return ONLY the JSON. No explanation. No markdown.
# # # """
# # #     raw_plan = await call_llm(plan_prompt)
# # #     # Strip any accidental fences
# # #     clean_plan = extract_code(raw_plan).strip().strip("```json").strip("```").strip()

# # #     try:
# # #         operation = json.loads(clean_plan)
# # #     except json.JSONDecodeError:
# # #         # Fallback: try to extract JSON with regex
# # #         m = re.search(r'\{.*\}', clean_plan, re.DOTALL)
# # #         try:
# # #             operation = json.loads(m.group()) if m else {}
# # #         except Exception:
# # #             operation = {}

# # #     if not operation:
# # #         operation = {"type": "list", "column": columns[0] if columns else "", "filter_column": "", "filter_value": "", "n": 5}

# # #     print(f"[Plan Agent] Operation: {operation}")
# # #     steps.append({"agent": "Plan Agent", "operation": operation})

# # #     # ------------------------------------------------------------------
# # #     # Step 3 — Execute with pure Python (zero LLM-generated code)
# # #     # ------------------------------------------------------------------
# # #     execution_output = analyze_csv(rows, columns, operation)
# # #     print(f"[Code Agent] Output:\n{execution_output}")
# # #     steps.append({"agent": "Code Agent", "result": execution_output})

# # #     # ------------------------------------------------------------------
# # #     # Step 4 — Report
# # #     # ------------------------------------------------------------------
# # #     report_prompt = f"""A user asked: "{user_query}"

# # # The data analysis produced this output:
# # # {execution_output}

# # # Answer the user's question in plain English using ONLY the output above.
# # # Do NOT write any code. Do NOT suggest any code. Just answer clearly in 2-5 sentences.
# # # """
# # #     report = await call_llm(report_prompt)
# # #     print(f"\n[Report]\n{report}\n")
# # #     steps.append({"agent": "Report Agent", "result": report})

# # #     return steps



# # # # ---------------------------------------------------------------------------
# # # # DATABASE AGENT PIPELINE
# # # # ---------------------------------------------------------------------------

# # # async def run_db_pipeline(user_query: str) -> list:
# # #     """Converts natural language to SQL, runs it, returns results."""
# # #     steps = []

# # #     sql_prompt = f"""Convert the following request to a valid SQLite SQL query.
# # # Output ONLY the raw SQL — no markdown, no explanation.

# # # Request: {user_query}
# # # """
# # #     raw_sql = await call_llm(sql_prompt)
# # #     sql_query = extract_code(raw_sql)  # strips fences if LLM added them

# # #     if not is_safe_sql(sql_query):
# # #         print("[Security] Destructive SQL detected (DROP/DELETE/TRUNCATE/UPDATE/ALTER). Blocked.")
# # #         steps.append({"agent": "DB Agent", "result": "BLOCKED by security guard"})
# # #         return steps

# # #     print(f"[DB Agent] Running SQL: {sql_query}")
# # #     db_results = db_tool["func"](sql_query)
# # #     print(f"[DB Agent] Result:\n{db_results}")
# # #     steps.append({"agent": "DB Agent", "query": sql_query, "result": db_results})

# # #     return steps


# # # # ---------------------------------------------------------------------------
# # # # MAIN ORCHESTRATOR
# # # # ---------------------------------------------------------------------------

# # # async def dynamic_tool_orchestrator():
# # #     print("\n=== DAY 3: SECURE DYNAMIC ORCHESTRATOR ONLINE ===")
# # #     print("Commands: ask about a .csv/.txt file, ask a database/sql question, or type 'exit'\n")

# # #     while True:
# # #         user_query = input("Enter Request (or 'exit'): ").strip()
# # #         if user_query.lower() == "exit":
# # #             break
# # #         if not user_query:
# # #             continue

# # #         steps_taken = []

# # #         # Route: file query
# # #         file_match = re.search(r"[\w\.\-]+\.(csv|txt)", user_query, re.IGNORECASE)
# # #         if file_match:
# # #             target_file = file_match.group(0)
# # #             steps_taken = await run_file_code_pipeline(user_query, target_file)

# # #         # Route: database query
# # #         elif "database" in user_query.lower() or "sql" in user_query.lower():
# # #             steps_taken = await run_db_pipeline(user_query)

# # #         else:
# # #             # Fallback: plain LLM answer
# # #             answer = await call_llm(user_query)
# # #             print(f"\n[LLM] {answer}\n")
# # #             steps_taken.append({"agent": "LLM", "result": answer})

# # #         await save_log(user_query, steps_taken)


# # # if __name__ == "__main__":
# # #     asyncio.run(dynamic_tool_orchestrator())


# # import asyncio
# # import csv as csv_module
# # import io
# # import os
# # import json
# # import re
# # from collections import Counter
# # from datetime import datetime

# # from autogen_core.models import UserMessage

# # from src.utils.config import client
# # from src.tools.code_executor import python_tool
# # from src.tools.db_agent import db_tool
# # from src.tools.file_agent import file_manager


# # # ---------------------------------------------------------------------------
# # # SECURITY GUARDS
# # # ---------------------------------------------------------------------------

# # def is_safe_sql(query: str) -> bool:
# #     forbidden = ["drop", "delete", "truncate", "update", "alter"]
# #     return not any(word in query.lower() for word in forbidden)


# # def is_safe_python(code: str) -> bool:
# #     forbidden = ["os.remove", "os.rmdir", "shutil", "subprocess", "sys.exit"]
# #     return not any(word in code.lower() for word in forbidden)


# # # ---------------------------------------------------------------------------
# # # HELPERS
# # # ---------------------------------------------------------------------------

# # def extract_code(raw: str) -> str:
# #     """
# #     Strips ALL markdown code fences from LLM output.
# #     Handles ```python, ```py, ``` and any other variant.
# #     """
# #     # Remove opening fence (``` optionally followed by a language tag)
# #     cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
# #     # Remove closing fence
# #     cleaned = re.sub(r"\n?```$", "", cleaned.strip())
# #     return cleaned.strip()


# # async def call_llm(prompt: str) -> str:
# #     """Calls the AutoGen LLM client and returns the text response."""
# #     response = await client.create(messages=[UserMessage(content=prompt, source="user")])
# #     # autogen_core returns a CreateResult; .content is the string text
# #     return str(response.content).strip()


# # async def save_log(query: str, steps: list):
# #     log_file = "logs_day3.json"
# #     log_entry = {
# #         "timestamp": datetime.now().isoformat(),
# #         "user_query": query,
# #         "execution_steps": steps,
# #     }
# #     logs = []
# #     if os.path.exists(log_file):
# #         try:
# #             with open(log_file, "r") as f:
# #                 logs = json.load(f)
# #         except Exception:
# #             logs = []
# #     logs.append(log_entry)
# #     with open(log_file, "w") as f:
# #         json.dump(logs, f, indent=4)


# # # ---------------------------------------------------------------------------
# # # CSV ANALYSIS ENGINE  (pure Python — no LLM-generated code)
# # # ---------------------------------------------------------------------------

# # def analyze_csv(rows: list, columns: list, operation: dict) -> str:
# #     """
# #     Executes a structured CSV operation entirely in Python.
# #     `operation` is a dict with keys:
# #         type   : "unique" | "filter" | "count" | "list" | "top_n"
# #         column : column name to operate on (stripped, matched case-insensitively)
# #         filter_column : (for filter) column to filter by
# #         filter_value  : (for filter) value to match (case-insensitive)
# #         n      : (for top_n) number of results
# #     """
# #     op_type = operation.get("type", "list")

# #     # Case-insensitive column lookup
# #     col_map = {c.strip().lower(): c.strip() for c in columns}

# #     def resolve(col_hint: str):
# #         """Return the real column name from a hint, or None."""
# #         if not col_hint:
# #             return None
# #         hint = col_hint.strip().lower()
# #         if hint in col_map:
# #             return col_map[hint]
# #         # partial match
# #         for k, v in col_map.items():
# #             if hint in k or k in hint:
# #                 return v
# #         return None

# #     target_col = resolve(operation.get("column", ""))
# #     filter_col = resolve(operation.get("filter_column", ""))
# #     filter_val = (operation.get("filter_value") or "").strip().lower()

# #     if op_type == "unique":
# #         if not target_col:
# #             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
# #         seen = set()
# #         results = []
# #         for row in rows:
# #             val = row.get(target_col, "").strip()
# #             if val and val not in seen:
# #                 seen.add(val)
# #                 results.append(val)
# #         return "\n".join(sorted(results)) if results else "No values found."

# #     elif op_type == "filter":
# #         if not target_col or not filter_col:
# #             return f"Need both a display column and a filter column. Available: {columns}"
# #         results = []
# #         for row in rows:
# #             cell = row.get(filter_col, "").strip().lower()
# #             # Try exact match first, then partial match
# #             if cell == filter_val or filter_val in cell or cell in filter_val:
# #                 results.append(row.get(target_col, "").strip())
# #         return "\n".join(results) if results else f"No rows found where '{filter_col}' matches '{filter_val}'."

# #     elif op_type == "count":
# #         if filter_col and filter_val:
# #             count = sum(
# #                 1 for row in rows
# #                 if row.get(filter_col, "").strip().lower() == filter_val
# #             )
# #             return f"Count of rows where {filter_col}={filter_val}: {count}"
# #         return f"Total rows: {len(rows)}"

# #     elif op_type == "top_n":
# #         n = int(operation.get("n", 5))
# #         if not target_col:
# #             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
# #         counts = Counter(row.get(target_col, "").strip() for row in rows)
# #         top = counts.most_common(n)
# #         return "\n".join(f"{v}: {c}" for v, c in top)

# #     else:  # "list" — just dump the column
# #         if not target_col:
# #             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
# #         results = [row.get(target_col, "").strip() for row in rows if row.get(target_col)]
# #         return "\n".join(results) if results else "No values found."


# # # ---------------------------------------------------------------------------
# # # FILE + CODE AGENT PIPELINE
# # # ---------------------------------------------------------------------------

# # async def run_file_code_pipeline(user_query: str, target_file: str) -> list:
# #     """
# #     Step 1 — File Agent   : Read + parse the CSV into rows.
# #     Step 1b— Normalise    : Rewrite vague query into explicit column references.
# #     Step 2 — Plan Agent   : LLM returns a JSON operation descriptor.
# #     Step 3 — Code Agent   : Python executes the operation deterministically.
# #     Step 4 — Report Agent : LLM summarises the results in plain English.
# #     """
# #     steps = []

# #     # ------------------------------------------------------------------
# #     # Step 1 — Read and parse CSV
# #     # ------------------------------------------------------------------
# #     raw_content = file_manager(action="read", file_name=target_file)
# #     if raw_content.startswith("Error"):
# #         print(f"[File Agent] {raw_content}")
# #         return steps

# #     reader = csv_module.DictReader(io.StringIO(raw_content))
# #     rows = list(reader)
# #     columns = list(rows[0].keys()) if rows else []

# #     # Build a value sample: for each column, show up to 5 distinct values
# #     # so the LLM can resolve implicit references like "homeopath" → Job Title
# #     value_samples = {}
# #     for col in columns:
# #         seen = []
# #         for row in rows:
# #             v = row.get(col, "").strip()
# #             if v and v not in seen:
# #                 seen.append(v)
# #             if len(seen) == 5:
# #                 break
# #         value_samples[col] = seen

# #     steps.append({"agent": "File Agent", "file": target_file, "status": "Read Success"})
# #     print(f"[File Agent] Read '{target_file}' — {len(rows)} rows, columns: {columns}")

# #     # ------------------------------------------------------------------
# #     # Step 1b — Normalise: translate vague query to explicit column terms
# #     # ------------------------------------------------------------------
# #     normalise_prompt = f"""You are a query translator for CSV analysis.

# # The CSV has these columns and sample values:
# # {json.dumps(value_samples, indent=2)}

# # Original user query: "{user_query}"

# # Rewrite the query so it explicitly names the CSV column and the exact value to filter/display.
# # If the query mentions a job title like "homeopath" or "lawyer", map it to the "Job Title" column.
# # If it mentions a gender like "male" or "female", map it to the "Sex" column.
# # Keep it short — one sentence. Do NOT explain. Just output the rewritten query.

# # Examples:
# # "give me names of all homeopath"   → "give me First Name where Job Title is Homeopath"
# # "all females"                       → "give me First Name where Sex is Female"
# # "unique job titles"                 → "give me unique values of Job Title"
# # "first name of all the lawyers"     → "give me First Name where Job Title is Lawyer"
# # """
# #     normalised_query = await call_llm(normalise_prompt)
# #     normalised_query = normalised_query.strip().strip('"')
# #     print(f"[Normalise] '{user_query}' → '{normalised_query}'")

# #     # ------------------------------------------------------------------
# #     # Step 2 — Plan: ask LLM what operation to perform (JSON only)
# #     # ------------------------------------------------------------------
# #     plan_prompt = f"""You are a data analysis planner. Given a user query and CSV columns,
# # return a JSON object describing the operation to perform.

# # CSV columns: {columns}
# # User query: {normalised_query}

# # Return ONLY a valid JSON object with EXACTLY these 5 fields — no extra fields:
# # {{
# #   "type": "unique" | "filter" | "count" | "list" | "top_n",
# #   "column": "<column name from the CSV to display in results>",
# #   "filter_column": "<column name from the CSV to filter BY — use exact column name>",
# #   "filter_value": "<the value to match in filter_column>",
# #   "n": 5
# # }}

# # RULES:
# # - "column"        = what to SHOW in output (e.g. "First Name")
# # - "filter_column" = the column to filter ON (e.g. "Job Title", "Sex")
# # - "filter_value"  = the exact value to match (e.g. "Homeopath", "Male")
# # - NEVER add extra keys. ALL filter info goes ONLY into filter_column and filter_value.

# # Examples:
# # Query: "give me First Name where Job Title is Homeopath"
# # → {{"type":"filter","column":"First Name","filter_column":"Job Title","filter_value":"Homeopath","n":5}}

# # Query: "give me unique values of First Name"
# # → {{"type":"unique","column":"First Name","filter_column":"","filter_value":"","n":5}}

# # Query: "give me First Name where Sex is Male"
# # → {{"type":"filter","column":"First Name","filter_column":"Sex","filter_value":"Male","n":5}}

# # Query: "how many females"
# # → {{"type":"count","column":"","filter_column":"Sex","filter_value":"Female","n":5}}

# # Query: "top 5 job titles"
# # → {{"type":"top_n","column":"Job Title","filter_column":"","filter_value":"","n":5}}

# # Return ONLY the JSON object. No explanation. No markdown. No extra keys.
# # """
# #     raw_plan = await call_llm(plan_prompt)

# #     # Strip markdown fences
# #     clean_plan = re.sub(r"^```[a-zA-Z]*\n?", "", raw_plan.strip())
# #     clean_plan = re.sub(r"\n?```$", "", clean_plan.strip()).strip()

# #     # Parse JSON
# #     operation = {}
# #     try:
# #         operation = json.loads(clean_plan)
# #     except json.JSONDecodeError:
# #         m = re.search(r'\{.*?\}', clean_plan, re.DOTALL)
# #         try:
# #             operation = json.loads(m.group()) if m else {}
# #         except Exception:
# #             operation = {}

# #     # Repair malformed JSON: LLM sometimes adds {"Job Title":"Lawyer"} as a loose key
# #     known_keys = {"type", "column", "filter_column", "filter_value", "n"}
# #     extra_keys = {k: v for k, v in operation.items() if k not in known_keys}
# #     if extra_keys and (not operation.get("filter_column") or not operation.get("filter_value")):
# #         repair_col, repair_val = next(iter(extra_keys.items()))
# #         if repair_col in columns:
# #             operation["filter_column"] = repair_col
# #             operation["filter_value"] = str(repair_val)
# #             print(f"[Plan Agent] Repaired JSON: filter_column={repair_col}, filter_value={repair_val}")
# #         for k in extra_keys:
# #             operation.pop(k, None)

# #     if not operation.get("type"):
# #         operation = {"type": "list", "column": columns[0] if columns else "",
# #                      "filter_column": "", "filter_value": "", "n": 5}

# #     print(f"[Plan Agent] Operation: {operation}")
# #     steps.append({"agent": "Plan Agent", "operation": operation})

# #     # ------------------------------------------------------------------
# #     # Step 3 — Execute with pure Python (zero LLM-generated code)
# #     # ------------------------------------------------------------------
# #     execution_output = analyze_csv(rows, columns, operation)
# #     print(f"[Code Agent] Output:\n{execution_output}")
# #     steps.append({"agent": "Code Agent", "result": execution_output})

# #     # ------------------------------------------------------------------
# #     # Step 4 — Report
# #     # ------------------------------------------------------------------
# #     report_prompt = f"""A user asked: "{user_query}"

# # A data analysis on the CSV file produced this exact output:
# # {execution_output}

# # Write a clear 1-3 sentence answer to the user's question based STRICTLY on the output above.
# # - Do NOT hallucinate or add any information not present in the output.
# # - Do NOT mention file names, ages, or anything not in the output.
# # - Do NOT write any code or suggest any code.
# # - If the output is a list of names, just say how many there are and list them (or a sample if very long).
# # """
# #     report = await call_llm(report_prompt)
# #     print(f"\n[Report]\n{report}\n")
# #     steps.append({"agent": "Report Agent", "result": report})

# #     return steps



# # # ---------------------------------------------------------------------------
# # # DATABASE AGENT PIPELINE
# # # ---------------------------------------------------------------------------

# # async def run_db_pipeline(user_query: str) -> list:
# #     """Converts natural language to SQL, runs it, returns results."""
# #     steps = []

# #     sql_prompt = f"""Convert the following request to a valid SQLite SQL query.
# # Output ONLY the raw SQL — no markdown, no explanation.

# # Request: {user_query}
# # """
# #     raw_sql = await call_llm(sql_prompt)
# #     sql_query = extract_code(raw_sql)  # strips fences if LLM added them

# #     if not is_safe_sql(sql_query):
# #         print("[Security] Destructive SQL detected (DROP/DELETE/TRUNCATE/UPDATE/ALTER). Blocked.")
# #         steps.append({"agent": "DB Agent", "result": "BLOCKED by security guard"})
# #         return steps

# #     print(f"[DB Agent] Running SQL: {sql_query}")
# #     db_results = db_tool["func"](sql_query)
# #     print(f"[DB Agent] Result:\n{db_results}")
# #     steps.append({"agent": "DB Agent", "query": sql_query, "result": db_results})

# #     return steps


# # # ---------------------------------------------------------------------------
# # # MAIN ORCHESTRATOR
# # # ---------------------------------------------------------------------------

# # async def dynamic_tool_orchestrator():
# #     print("\n=== DAY 3: SECURE DYNAMIC ORCHESTRATOR ONLINE ===")
# #     print("Commands: ask about a .csv/.txt file, ask a database/sql question, or type 'exit'\n")

# #     while True:
# #         user_query = input("Enter Request (or 'exit'): ").strip()
# #         if user_query.lower() == "exit":
# #             break
# #         if not user_query:
# #             continue

# #         steps_taken = []

# #         # Route: file query
# #         file_match = re.search(r"[\w\.\-]+\.(csv|txt)", user_query, re.IGNORECASE)
# #         if file_match:
# #             target_file = file_match.group(0)
# #             steps_taken = await run_file_code_pipeline(user_query, target_file)

# #         # Route: database query
# #         elif "database" in user_query.lower() or "sql" in user_query.lower():
# #             steps_taken = await run_db_pipeline(user_query)

# #         else:
# #             # Fallback: plain LLM answer
# #             answer = await call_llm(user_query)
# #             print(f"\n[LLM] {answer}\n")
# #             steps_taken.append({"agent": "LLM", "result": answer})

# #         await save_log(user_query, steps_taken)


# # if __name__ == "__main__":
# #     asyncio.run(dynamic_tool_orchestrator())


# import asyncio
# import csv as csv_module
# import io
# import os
# import json
# import re
# from collections import Counter
# from datetime import datetime

# from autogen_core.models import UserMessage

# from src.utils.config import client
# from src.tools.code_executor import python_tool
# from src.tools.db_agent import db_tool
# from src.tools.file_agent import file_manager


# # ---------------------------------------------------------------------------
# # SECURITY GUARDS
# # ---------------------------------------------------------------------------

# def is_safe_sql(query: str) -> bool:
#     forbidden = ["drop", "delete", "truncate", "update", "alter"]
#     return not any(word in query.lower() for word in forbidden)


# def is_safe_python(code: str) -> bool:
#     forbidden = ["os.remove", "os.rmdir", "shutil", "subprocess", "sys.exit"]
#     return not any(word in code.lower() for word in forbidden)


# # ---------------------------------------------------------------------------
# # HELPERS
# # ---------------------------------------------------------------------------

# def extract_code(raw: str) -> str:
#     """
#     Strips ALL markdown code fences from LLM output.
#     Handles ```python, ```py, ``` and any other variant.
#     """
#     # Remove opening fence (``` optionally followed by a language tag)
#     cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
#     # Remove closing fence
#     cleaned = re.sub(r"\n?```$", "", cleaned.strip())
#     return cleaned.strip()


# async def call_llm(prompt: str) -> str:
#     """Calls the AutoGen LLM client and returns the text response."""
#     response = await client.create(messages=[UserMessage(content=prompt, source="user")])
#     # autogen_core returns a CreateResult; .content is the string text
#     return str(response.content).strip()


# async def save_log(query: str, steps: list):
#     log_file = "logs_day3.json"
#     log_entry = {
#         "timestamp": datetime.now().isoformat(),
#         "user_query": query,
#         "execution_steps": steps,
#     }
#     logs = []
#     if os.path.exists(log_file):
#         try:
#             with open(log_file, "r") as f:
#                 logs = json.load(f)
#         except Exception:
#             logs = []
#     logs.append(log_entry)
#     with open(log_file, "w") as f:
#         json.dump(logs, f, indent=4)


# # ---------------------------------------------------------------------------
# # CSV ANALYSIS ENGINE  (pure Python — no LLM-generated code)
# # ---------------------------------------------------------------------------

# def analyze_csv(rows: list, columns: list, operation: dict) -> str:
#     """
#     Executes a structured CSV operation entirely in Python.
#     `operation` is a dict with keys:
#         type          : "unique" | "filter" | "count" | "list" | "top_n"
#         column        : one column name OR comma-separated list of column names to display
#         filter_column : column to filter by
#         filter_value  : value to match (exact, case-insensitive)
#         n             : (for top_n) number of results
#     """
#     op_type = operation.get("type", "list")

#     # Case-insensitive column lookup map
#     col_map = {c.strip().lower(): c.strip() for c in columns}

#     def resolve_one(col_hint: str):
#         """Return the real column name for a single hint, or None."""
#         if not col_hint:
#             return None
#         hint = col_hint.strip().lower()
#         # Exact match first
#         if hint in col_map:
#             return col_map[hint]
#         # Partial match — hint is contained in a column name
#         for k, v in col_map.items():
#             if hint in k:
#                 return v
#         return None

#     def resolve_columns(col_str: str) -> list:
#         """
#         Handle 'First Name' OR 'First Name,Last Name' — returns a list of
#         resolved real column names, deduped and in order.
#         """
#         parts = [p.strip() for p in col_str.split(",") if p.strip()]
#         resolved = []
#         seen = set()
#         for part in parts:
#             r = resolve_one(part)
#             if r and r not in seen:
#                 resolved.append(r)
#                 seen.add(r)
#         return resolved

#     def row_matches_filter(row: dict) -> bool:
#         """Exact case-insensitive match only — avoids 'male' matching 'female'."""
#         if not filter_col or not filter_val:
#             return True
#         return row.get(filter_col, "").strip().lower() == filter_val

#     def format_row(row: dict, target_cols: list) -> str:
#         """Return one or more column values for a row, space-separated."""
#         return " ".join(row.get(c, "").strip() for c in target_cols)

#     # Resolve display columns (may be multiple)
#     target_cols = resolve_columns(operation.get("column", ""))
#     # Resolve filter column (always single)
#     filter_col = resolve_one(operation.get("filter_column", ""))
#     filter_val = (operation.get("filter_value") or "").strip().lower()

#     if op_type == "unique":
#         if not target_cols:
#             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
#         col = target_cols[0]  # unique operates on one column
#         seen = set()
#         results = []
#         for row in rows:
#             if not row_matches_filter(row):
#                 continue
#             val = row.get(col, "").strip()
#             if val and val not in seen:
#                 seen.add(val)
#                 results.append(val)
#         return "\n".join(sorted(results)) if results else "No values found."

#     elif op_type == "filter":
#         if not target_cols:
#             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
#         if not filter_col:
#             return f"No filter column found. Available: {columns}"
#         results = [format_row(row, target_cols) for row in rows if row_matches_filter(row)]
#         return "\n".join(results) if results else f"No rows found where '{filter_col}' = '{filter_val}'."

#     elif op_type == "count":
#         count = sum(1 for row in rows if row_matches_filter(row))
#         label = f"where {filter_col} = {filter_val}" if filter_col and filter_val else "(total)"
#         return f"Count {label}: {count}"

#     elif op_type == "top_n":
#         n = int(operation.get("n") or 5)
#         if not target_cols:
#             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
#         col = target_cols[0]
#         counts = Counter(
#             row.get(col, "").strip()
#             for row in rows
#             if row_matches_filter(row) and row.get(col, "").strip()
#         )
#         top = counts.most_common(n)
#         return "\n".join(f"{v}: {c}" for v, c in top)

#     else:  # "list"
#         if not target_cols:
#             return f"Could not find column '{operation.get('column')}'. Available: {columns}"
#         results = [
#             format_row(row, target_cols)
#             for row in rows
#             if row_matches_filter(row) and any(row.get(c, "").strip() for c in target_cols)
#         ]
#         return "\n".join(results) if results else "No values found."


# # ---------------------------------------------------------------------------
# # FILE + CODE AGENT PIPELINE
# # ---------------------------------------------------------------------------

# async def run_file_code_pipeline(user_query: str, target_file: str) -> list:
#     """
#     Step 1 — File Agent   : Read + parse the CSV into rows.
#     Step 1b— Normalise    : Rewrite vague query into explicit column references.
#     Step 2 — Plan Agent   : LLM returns a JSON operation descriptor.
#     Step 3 — Code Agent   : Python executes the operation deterministically.
#     Step 4 — Report Agent : LLM summarises the results in plain English.
#     """
#     steps = []

#     # ------------------------------------------------------------------
#     # Step 1 — Read and parse CSV
#     # ------------------------------------------------------------------
#     raw_content = file_manager(action="read", file_name=target_file)
#     if raw_content.startswith("Error"):
#         print(f"[File Agent] {raw_content}")
#         return steps

#     reader = csv_module.DictReader(io.StringIO(raw_content))
#     rows = list(reader)
#     columns = list(rows[0].keys()) if rows else []

#     # Build a value sample: for each column, show up to 5 distinct values
#     # so the LLM can resolve implicit references like "homeopath" → Job Title
#     value_samples = {}
#     for col in columns:
#         seen = []
#         for row in rows:
#             v = row.get(col, "").strip()
#             if v and v not in seen:
#                 seen.append(v)
#             if len(seen) == 5:
#                 break
#         value_samples[col] = seen

#     steps.append({"agent": "File Agent", "file": target_file, "status": "Read Success"})
#     print(f"[File Agent] Read '{target_file}' — {len(rows)} rows, columns: {columns}")

#     # ------------------------------------------------------------------
#     # Step 1b — Normalise: translate vague query to explicit column terms
#     # ------------------------------------------------------------------
#     normalise_prompt = f"""You are a query translator for CSV analysis.

# The CSV has these columns and sample values:
# {json.dumps(value_samples, indent=2)}

# Original user query: "{user_query}"

# Rewrite the query so it explicitly names the CSV column and the exact value to filter/display.
# If the query mentions a job title like "homeopath" or "lawyer", map it to the "Job Title" column.
# If it mentions a gender like "male" or "female", map it to the "Sex" column.
# Keep it short — one sentence. Do NOT explain. Just output the rewritten query.

# Examples:
# "give me names of all homeopath"   → "give me First Name where Job Title is Homeopath"
# "all females"                       → "give me First Name where Sex is Female"
# "unique job titles"                 → "give me unique values of Job Title"
# "first name of all the lawyers"     → "give me First Name where Job Title is Lawyer"
# """
#     normalised_query = await call_llm(normalise_prompt)
#     normalised_query = normalised_query.strip().strip('"')
#     print(f"[Normalise] '{user_query}' → '{normalised_query}'")

#     # ------------------------------------------------------------------
#     # Step 2 — Plan: ask LLM what operation to perform (JSON only)
#     # ------------------------------------------------------------------
#     plan_prompt = f"""You are a data analysis planner. Given a user query and CSV columns,
# return a JSON object describing the operation to perform.

# CSV columns: {columns}
# User query: {normalised_query}

# Return ONLY a valid JSON object with EXACTLY these 5 fields — no extra fields:
# {{
#   "type": "unique" | "filter" | "count" | "list" | "top_n",
#   "column": "<column name from the CSV to display in results>",
#   "filter_column": "<column name from the CSV to filter BY — use exact column name>",
#   "filter_value": "<the value to match in filter_column>",
#   "n": 5
# }}

# RULES:
# - "column"        = what to SHOW in output (e.g. "First Name")
# - "filter_column" = the column to filter ON (e.g. "Job Title", "Sex")
# - "filter_value"  = the exact value to match (e.g. "Homeopath", "Male")
# - NEVER add extra keys. ALL filter info goes ONLY into filter_column and filter_value.

# Examples:
# Query: "give me First Name where Job Title is Homeopath"
# → {{"type":"filter","column":"First Name","filter_column":"Job Title","filter_value":"Homeopath","n":5}}

# Query: "give me unique values of First Name"
# → {{"type":"unique","column":"First Name","filter_column":"","filter_value":"","n":5}}

# Query: "give me First Name where Sex is Male"
# → {{"type":"filter","column":"First Name","filter_column":"Sex","filter_value":"Male","n":5}}

# Query: "how many females"
# → {{"type":"count","column":"","filter_column":"Sex","filter_value":"Female","n":5}}

# Query: "top 5 job titles"
# → {{"type":"top_n","column":"Job Title","filter_column":"","filter_value":"","n":5}}

# Return ONLY the JSON object. No explanation. No markdown. No extra keys.
# """
#     raw_plan = await call_llm(plan_prompt)

#     # Strip markdown fences
#     clean_plan = re.sub(r"^```[a-zA-Z]*\n?", "", raw_plan.strip())
#     clean_plan = re.sub(r"\n?```$", "", clean_plan.strip()).strip()

#     # Parse JSON
#     operation = {}
#     try:
#         operation = json.loads(clean_plan)
#     except json.JSONDecodeError:
#         m = re.search(r'\{.*?\}', clean_plan, re.DOTALL)
#         try:
#             operation = json.loads(m.group()) if m else {}
#         except Exception:
#             operation = {}

#     # Repair malformed JSON: LLM sometimes adds {"Job Title":"Lawyer"} as a loose key
#     known_keys = {"type", "column", "filter_column", "filter_value", "n"}
#     extra_keys = {k: v for k, v in operation.items() if k not in known_keys}
#     if extra_keys and (not operation.get("filter_column") or not operation.get("filter_value")):
#         repair_col, repair_val = next(iter(extra_keys.items()))
#         if repair_col in columns:
#             operation["filter_column"] = repair_col
#             operation["filter_value"] = str(repair_val)
#             print(f"[Plan Agent] Repaired JSON: filter_column={repair_col}, filter_value={repair_val}")
#         for k in extra_keys:
#             operation.pop(k, None)

#     if not operation.get("type"):
#         operation = {"type": "list", "column": columns[0] if columns else "",
#                      "filter_column": "", "filter_value": "", "n": 5}

#     print(f"[Plan Agent] Operation: {operation}")
#     steps.append({"agent": "Plan Agent", "operation": operation})

#     # ------------------------------------------------------------------
#     # Step 3 — Execute with pure Python (zero LLM-generated code)
#     # ------------------------------------------------------------------
#     execution_output = analyze_csv(rows, columns, operation)
#     print(f"[Code Agent] Output:\n{execution_output}")
#     steps.append({"agent": "Code Agent", "result": execution_output})

#     # ------------------------------------------------------------------
#     # Step 4 — Report
#     # ------------------------------------------------------------------
#     report_prompt = f"""A user asked: "{user_query}"

# A data analysis on the CSV file produced this exact output:
# {execution_output}

# Write a clear 1-3 sentence answer to the user's question based STRICTLY on the output above.
# - Do NOT hallucinate or add any information not present in the output.
# - Do NOT mention file names, ages, or anything not in the output.
# - Do NOT write any code or suggest any code.
# - If the output is a list of names, just say how many there are and list them (or a sample if very long).
# """
#     report = await call_llm(report_prompt)
#     print(f"\n[Report]\n{report}\n")
#     steps.append({"agent": "Report Agent", "result": report})

#     return steps



# # ---------------------------------------------------------------------------
# # DATABASE AGENT PIPELINE
# # ---------------------------------------------------------------------------

# async def run_db_pipeline(user_query: str) -> list:
#     """Converts natural language to SQL, runs it, returns results."""
#     steps = []

#     sql_prompt = f"""Convert the following request to a valid SQLite SQL query.
# Output ONLY the raw SQL — no markdown, no explanation.

# Request: {user_query}
# """
#     raw_sql = await call_llm(sql_prompt)
#     sql_query = extract_code(raw_sql)  # strips fences if LLM added them

#     if not is_safe_sql(sql_query):
#         print("[Security] Destructive SQL detected (DROP/DELETE/TRUNCATE/UPDATE/ALTER). Blocked.")
#         steps.append({"agent": "DB Agent", "result": "BLOCKED by security guard"})
#         return steps

#     print(f"[DB Agent] Running SQL: {sql_query}")
#     db_results = db_tool["func"](sql_query)
#     print(f"[DB Agent] Result:\n{db_results}")
#     steps.append({"agent": "DB Agent", "query": sql_query, "result": db_results})

#     return steps


# # ---------------------------------------------------------------------------
# # MAIN ORCHESTRATOR
# # ---------------------------------------------------------------------------

# async def dynamic_tool_orchestrator():
#     print("\n=== DAY 3: SECURE DYNAMIC ORCHESTRATOR ONLINE ===")
#     print("Commands: ask about a .csv/.txt file, ask a database/sql question, or type 'exit'\n")

#     while True:
#         user_query = input("Enter Request (or 'exit'): ").strip()
#         if user_query.lower() == "exit":
#             break
#         if not user_query:
#             continue

#         steps_taken = []

#         # Route: file query
#         file_match = re.search(r"[\w\.\-]+\.(csv|txt)", user_query, re.IGNORECASE)
#         if file_match:
#             target_file = file_match.group(0)
#             steps_taken = await run_file_code_pipeline(user_query, target_file)

#         # Route: database query
#         elif "database" in user_query.lower() or "sql" in user_query.lower():
#             steps_taken = await run_db_pipeline(user_query)

#         else:
#             # Fallback: plain LLM answer
#             answer = await call_llm(user_query)
#             print(f"\n[LLM] {answer}\n")
#             steps_taken.append({"agent": "LLM", "result": answer})

#         await save_log(user_query, steps_taken)


# if __name__ == "__main__":
#     asyncio.run(dynamic_tool_orchestrator())

import asyncio
import csv as csv_module
import io
import os
import json
import re
from collections import Counter
from datetime import datetime

from autogen_core.models import UserMessage

from src.utils.config import client
from src.tools.code_executor import python_tool
from src.tools.db_agent import db_tool
from src.tools.file_agent import file_manager


# ---------------------------------------------------------------------------
# SECURITY GUARDS
# ---------------------------------------------------------------------------

def is_safe_sql(query: str) -> bool:
    forbidden = ["drop", "delete", "truncate", "update", "alter"]
    return not any(word in query.lower() for word in forbidden)


def is_safe_python(code: str) -> bool:
    forbidden = ["os.remove", "os.rmdir", "shutil", "subprocess", "sys.exit"]
    return not any(word in code.lower() for word in forbidden)


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def extract_code(raw: str) -> str:
    """
    Strips ALL markdown code fences from LLM output.
    Handles ```python, ```py, ``` and any other variant.
    """
    # Remove opening fence (``` optionally followed by a language tag)
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
    # Remove closing fence
    cleaned = re.sub(r"\n?```$", "", cleaned.strip())
    return cleaned.strip()


async def call_llm(prompt: str) -> str:
    """Calls the AutoGen LLM client and returns the text response."""
    response = await client.create(messages=[UserMessage(content=prompt, source="user")])
    # autogen_core returns a CreateResult; .content is the string text
    return str(response.content).strip()


async def save_log(query: str, steps: list):
    log_file = "logs_day3.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_query": query,
        "execution_steps": steps,
    }
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)


# ---------------------------------------------------------------------------
# CSV ANALYSIS ENGINE  (pure Python — no LLM-generated code)
# ---------------------------------------------------------------------------

def _resolve_one(col_hint: str, col_map: dict) -> str | None:
    """Case-insensitive column lookup. Returns real column name or None."""
    if not col_hint:
        return None
    hint = col_hint.strip().lower()
    if hint in col_map:
        return col_map[hint]
    for k, v in col_map.items():
        if hint in k:
            return v
    return None


def _resolve_columns(col_str: str, col_map: dict) -> list:
    """Split comma-separated column hints and resolve each to a real column name."""
    parts = [p.strip() for p in col_str.split(",") if p.strip()]
    resolved, seen = [], set()
    for part in parts:
        r = _resolve_one(part, col_map)
        if r and r not in seen:
            resolved.append(r)
            seen.add(r)
    return resolved


def _row_passes(row: dict, filters: list) -> bool:
    """
    Evaluate ALL filters against a row (AND logic).
    Each filter is a dict with keys:
        column    : resolved column name
        op        : "eq" | "gt" | "lt" | "gte" | "lte" | "contains"
        value     : string value to compare against
    """
    for f in filters:
        col = f.get("column")
        op  = f.get("op", "eq")
        val = f.get("value", "").strip().lower()
        cell = row.get(col, "").strip().lower() if col else ""

        if op == "eq":
            if cell != val:
                return False
        elif op == "contains":
            if val not in cell:
                return False
        elif op in ("gt", "lt", "gte", "lte"):
            # Extract year prefix for date columns (YYYY-MM-DD → "YYYY")
            cell_num = cell[:4] if len(cell) >= 4 else cell
            try:
                c, v = float(cell_num), float(val)
            except ValueError:
                return False
            if op == "gt"  and not (c >  v): return False
            if op == "lt"  and not (c <  v): return False
            if op == "gte" and not (c >= v): return False
            if op == "lte" and not (c <= v): return False
    return True


def analyze_csv(rows: list, columns: list, operation: dict) -> str:
    """
    Executes a structured CSV operation entirely in Python.

    operation keys:
        type     : "unique" | "filter" | "count" | "list" | "top_n"
        column   : column(s) to display (comma-separated OK)
        filters  : list of filter dicts [{column, op, value}, ...]
                   OR legacy keys filter_column / filter_value (auto-converted)
        n        : top_n count (default 5)
    """
    op_type = operation.get("type", "list")
    col_map = {c.strip().lower(): c.strip() for c in columns}

    # ------------------------------------------------------------------
    # Build filters list — supports both new `filters` array and legacy
    # `filter_column` / `filter_value` single-filter keys
    # ------------------------------------------------------------------
    raw_filters = operation.get("filters") or []
    if not raw_filters:
        # Legacy single-filter fallback
        fc  = operation.get("filter_column", "")
        fv  = operation.get("filter_value", "")
        fop = operation.get("filter_op", "eq")
        if fc and fv:
            raw_filters = [{"column": fc, "op": fop, "value": fv}]

    # Resolve column names in each filter
    filters = []
    for f in raw_filters:
        resolved_col = _resolve_one(f.get("column", ""), col_map)
        if resolved_col:
            filters.append({
                "column": resolved_col,
                "op":     f.get("op", "eq"),
                "value":  str(f.get("value", "")),
            })

    target_cols = _resolve_columns(operation.get("column", ""), col_map)

    def fmt(row):
        return " ".join(row.get(c, "").strip() for c in target_cols)

    if op_type == "unique":
        if not target_cols:
            return f"Column '{operation.get('column')}' not found. Available: {columns}"
        col = target_cols[0]
        seen, results = set(), []
        for row in rows:
            if not _row_passes(row, filters):
                continue
            val = row.get(col, "").strip()
            if val and val not in seen:
                seen.add(val)
                results.append(val)
        return "\n".join(sorted(results)) if results else "No matching values found."

    elif op_type in ("filter", "list"):
        if not target_cols:
            return f"Column '{operation.get('column')}' not found. Available: {columns}"
        results = [fmt(row) for row in rows
                   if _row_passes(row, filters)
                   and any(row.get(c, "").strip() for c in target_cols)]
        if not results:
            filter_desc = " AND ".join(
                f"{f['column']} {f['op']} {f['value']}" for f in filters
            )
            return f"No rows found matching: {filter_desc or '(no filter)'}"
        return "\n".join(results)

    elif op_type == "count":
        count = sum(1 for row in rows if _row_passes(row, filters))
        filter_desc = " AND ".join(
            f"{f['column']} {f['op']} {f['value']}" for f in filters
        )
        return f"Count ({filter_desc or 'total'}): {count}"

    elif op_type == "top_n":
        n = int(operation.get("n") or 5)
        if not target_cols:
            return f"Column '{operation.get('column')}' not found. Available: {columns}"
        col = target_cols[0]
        counts = Counter(
            row.get(col, "").strip()
            for row in rows
            if _row_passes(row, filters) and row.get(col, "").strip()
        )
        top = counts.most_common(n)
        return "\n".join(f"{v}: {c}" for v, c in top) if top else "No data found."

    return "Unknown operation type."



# ---------------------------------------------------------------------------
# FILE + CODE AGENT PIPELINE
# ---------------------------------------------------------------------------

async def run_file_code_pipeline(user_query: str, target_file: str) -> list:
    """
    Step 1 — File Agent   : Read + parse the CSV into rows.
    Step 1b— Normalise    : Rewrite vague query into explicit column references.
    Step 2 — Plan Agent   : LLM returns a JSON operation descriptor.
    Step 3 — Code Agent   : Python executes the operation deterministically.
    Step 4 — Report Agent : LLM summarises the results in plain English.
    """
    steps = []

    # ------------------------------------------------------------------
    # Step 1 — Read and parse CSV
    # ------------------------------------------------------------------
    raw_content = file_manager(action="read", file_name=target_file)
    if raw_content.startswith("Error"):
        print(f"[File Agent] {raw_content}")
        return steps

    reader = csv_module.DictReader(io.StringIO(raw_content))
    rows = list(reader)
    columns = list(rows[0].keys()) if rows else []

    # Build a value sample: for each column, show up to 5 distinct values
    # so the LLM can resolve implicit references like "homeopath" → Job Title
    value_samples = {}
    for col in columns:
        seen = []
        for row in rows:
            v = row.get(col, "").strip()
            if v and v not in seen:
                seen.append(v)
            if len(seen) == 5:
                break
        value_samples[col] = seen

    steps.append({"agent": "File Agent", "file": target_file, "status": "Read Success"})
    print(f"[File Agent] Read '{target_file}' — {len(rows)} rows, columns: {columns}")

    # ------------------------------------------------------------------
    # Step 1b — Normalise: translate vague query to explicit column terms
    # ------------------------------------------------------------------
    normalise_prompt = f"""You are a query translator for CSV data analysis.

The CSV has these columns and sample values:
{json.dumps(value_samples, indent=2)}

Original user query: "{user_query}"

Rewrite the query as a single explicit sentence using exact CSV column names.
Rules:
- Map job roles (e.g. "homeopath", "social worker") → Job Title column
- Map gender words (e.g. "males", "females") → Sex column
- Keep date conditions explicit (e.g. "born after 2000" → "Date of birth > 2000")
- If multiple conditions exist, include ALL of them with AND

Examples:
"names of all homeopath"                              → "First Name where Job Title = Homeopath"
"all males"                                           → "First Name where Sex = Male"
"social workers born after 2000"                      → "First Name, Last Name where Job Title = Social Worker AND Date of birth > 2000"
"female lawyers born before 1990"                     → "First Name where Sex = Female AND Job Title = Lawyer AND Date of birth < 1990"
"how many veterinary surgeons"                        → "count where Job Title = Veterinary surgeon"

Output ONLY the rewritten query. No explanation.
"""
    normalised_query = await call_llm(normalise_prompt)
    normalised_query = normalised_query.strip().strip('"')
    print(f"[Normalise] '{user_query}' → '{normalised_query}'")

    # ------------------------------------------------------------------
    # Step 2 — Plan: ask LLM to produce a structured operation JSON
    # ------------------------------------------------------------------
    plan_prompt = f"""You are a data analysis planner. Convert the user query into a JSON operation.

CSV columns: {columns}
User query: {normalised_query}

Return ONLY a valid JSON object with EXACTLY these fields:
{{
  "type": "filter" | "unique" | "count" | "list" | "top_n",
  "column": "<CSV column(s) to display, comma-separated if multiple>",
  "filters": [
    {{"column": "<exact CSV column name>", "op": "eq|gt|lt|gte|lte|contains", "value": "<value>"}},
    ...
  ],
  "n": 5
}}

Filter ops:
  "eq"       = exact match  (e.g. Sex = Male)
  "gt"       = greater than (e.g. year > 2000  → use first 4 chars of date)
  "lt"       = less than
  "gte"      = greater than or equal
  "lte"      = less than or equal
  "contains" = substring match

RULES:
- Put ALL conditions in the "filters" array — one object per condition
- For dates use the year only as value (e.g. "2000"), op "gt" means born AFTER that year
- Do NOT add any keys outside the schema above

Examples:
Query: "First Name where Sex = Male"
→ {{"type":"filter","column":"First Name","filters":[{{"column":"Sex","op":"eq","value":"Male"}}],"n":5}}

Query: "First Name, Last Name where Job Title = Social Worker AND Date of birth > 2000"
→ {{"type":"filter","column":"First Name,Last Name","filters":[{{"column":"Job Title","op":"eq","value":"Social Worker"}},{{"column":"Date of birth","op":"gt","value":"2000"}}],"n":5}}

Query: "First Name where Job Title = Homeopath"
→ {{"type":"filter","column":"First Name","filters":[{{"column":"Job Title","op":"eq","value":"Homeopath"}}],"n":5}}

Query: "count where Job Title = Lawyer"
→ {{"type":"count","column":"","filters":[{{"column":"Job Title","op":"eq","value":"Lawyer"}}],"n":5}}

Query: "unique values of Job Title"
→ {{"type":"unique","column":"Job Title","filters":[],"n":5}}

Return ONLY the JSON. No markdown. No explanation.
"""
    raw_plan = await call_llm(plan_prompt)

    # Strip markdown fences
    clean_plan = re.sub(r"^```[a-zA-Z]*\n?", "", raw_plan.strip())
    clean_plan = re.sub(r"\n?```$", "", clean_plan.strip()).strip()

    operation = {}
    try:
        operation = json.loads(clean_plan)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', clean_plan, re.DOTALL)
        try:
            operation = json.loads(m.group()) if m else {}
        except Exception:
            operation = {}

    # Ensure filters key always exists as a list
    if "filters" not in operation:
        operation["filters"] = []

    # Legacy repair: if old-style filter_column/filter_value keys present, migrate them
    if operation.get("filter_column") and operation.get("filter_value"):
        operation["filters"].insert(0, {
            "column": operation.pop("filter_column"),
            "op": "eq",
            "value": operation.pop("filter_value"),
        })

    if not operation.get("type"):
        operation = {"type": "list", "column": columns[0] if columns else "",
                     "filters": [], "n": 5}

    print(f"[Plan Agent] Operation: {operation}")
    steps.append({"agent": "Plan Agent", "operation": operation})

    # ------------------------------------------------------------------
    # Step 3 — Execute with pure Python (zero LLM-generated code)
    # ------------------------------------------------------------------
    execution_output = analyze_csv(rows, columns, operation)
    print(f"[Code Agent] Output:\n{execution_output}")
    steps.append({"agent": "Code Agent", "result": execution_output})

    # ------------------------------------------------------------------
    # Step 4 — Report
    # ------------------------------------------------------------------
    report_prompt = f"""A user asked: "{user_query}"

A data analysis on the CSV file produced this exact output:
{execution_output}

Write a clear 1-3 sentence answer to the user's question based STRICTLY on the output above.
- Do NOT hallucinate or add any information not present in the output.
- Do NOT mention file names, ages, or anything not in the output.
- Do NOT write any code or suggest any code.
- If the output is a list of names, just say how many there are and list them (or a sample if very long).
"""
    report = await call_llm(report_prompt)
    print(f"\n[Report]\n{report}\n")
    steps.append({"agent": "Report Agent", "result": report})

    return steps



# ---------------------------------------------------------------------------
# DATABASE AGENT PIPELINE
# ---------------------------------------------------------------------------

async def run_db_pipeline(user_query: str) -> list:
    """Converts natural language to SQL, runs it, returns results."""
    steps = []

    sql_prompt = f"""Convert the following request to a valid SQLite SQL query.
Output ONLY the raw SQL — no markdown, no explanation.

Request: {user_query}
"""
    raw_sql = await call_llm(sql_prompt)
    sql_query = extract_code(raw_sql)  # strips fences if LLM added them

    if not is_safe_sql(sql_query):
        print("[Security] Destructive SQL detected (DROP/DELETE/TRUNCATE/UPDATE/ALTER). Blocked.")
        steps.append({"agent": "DB Agent", "result": "BLOCKED by security guard"})
        return steps

    print(f"[DB Agent] Running SQL: {sql_query}")
    db_results = db_tool["func"](sql_query)
    print(f"[DB Agent] Result:\n{db_results}")
    steps.append({"agent": "DB Agent", "query": sql_query, "result": db_results})

    return steps


# ---------------------------------------------------------------------------
# MAIN ORCHESTRATOR
# ---------------------------------------------------------------------------

async def dynamic_tool_orchestrator():
    print("\n=== DAY 3: SECURE DYNAMIC ORCHESTRATOR ONLINE ===")
    print("Commands: ask about a .csv/.txt file, ask a database/sql question, or type 'exit'\n")

    while True:
        user_query = input("Enter Request (or 'exit'): ").strip()
        if user_query.lower() == "exit":
            break
        if not user_query:
            continue

        steps_taken = []

        # Route: file query
        file_match = re.search(r"[\w\.\-]+\.(csv|txt)", user_query, re.IGNORECASE)
        if file_match:
            target_file = file_match.group(0)
            steps_taken = await run_file_code_pipeline(user_query, target_file)

        # Route: database query
        elif "database" in user_query.lower() or "sql" in user_query.lower():
            steps_taken = await run_db_pipeline(user_query)

        else:
            # Fallback: plain LLM answer
            answer = await call_llm(user_query)
            print(f"\n[LLM] {answer}\n")
            steps_taken.append({"agent": "LLM", "result": answer})

        await save_log(user_query, steps_taken)


if __name__ == "__main__":
    asyncio.run(dynamic_tool_orchestrator())