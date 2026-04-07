import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from src.utils.config import client

import src.day3.tools.file_agent as file_tool
import src.day3.tools.db_agent as db_tool
import src.day3.tools.code_executor as code_tool

# --- Setup Paths ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

file_tool.DATA_DIR = DATA_DIR
db_tool.DATA_DIR = DATA_DIR
code_tool.DATA_DIR = DATA_DIR

async def main():
    termination = TextMentionTermination("TERMINATE")

    GLOBAL_CONSTRAINT = (
        "Be concise. Do not explain your reasoning. "
        "Use tools immediately. Max 1 sentence responses. "
        "Never ask for confirmation."
    )

    file_agent = AssistantAgent(
        name="File_Manager",
        model_client=client,
        tools=[file_tool.read_file, file_tool.write_to_file],
        description=(
            "Handles simple file reads and small file writes (<10 rows of manually specified data). "
            "Do NOT select for: data generation, bulk operations, CSV manipulation, "
            "format conversions, analysis, computation, or code writing."
        ),
        system_message=f"""You handle simple file I/O in {DATA_DIR}. {GLOBAL_CONSTRAINT}

YOU DO:
- Read any file (.txt, .csv, .json) to inspect or display contents.
- Write small files with <10 rows of manually provided data.

YOU NEVER DO:
- Answer code/programming questions. DELEGATE to Code_Analyst.
- Analyze or filter data. DELEGATE to Code_Analyst.
- Compute anything. DELEGATE to Code_Analyst.

YOU DELEGATE to Code_Analyst:
- Creating files with generated, sequential, or random data (any size).
- Any CSV modification: appending rows, updating values, adding columns.
- Any conversion between formats (CSV <-> DB).
- Any data analysis, filtering, or computation.
- Any bulk operation (>10 rows).

After your task, say 'Task Complete. TERMINATE'."""
    )

    db_agent = AssistantAgent(
        name="DB_Admin",
        model_client=client,
        tools=[db_tool.query_database],
        description=(
            "Handles SQL operations: schema checks, SELECT queries, single-row INSERT/UPDATE/DELETE, "
            "ALTER TABLE, CREATE TABLE. Do NOT select for: bulk inserts (>5 rows), "
            "data generation, CSV operations, format conversions, or code writing."
        ),
        system_message=f"""You are the SQL expert for SQLite databases in {DATA_DIR}. {GLOBAL_CONSTRAINT}

YOU DO:
- Schema inspection via sqlite_master.
- SELECT queries for reading, filtering, listing data.
- Single-row INSERT, UPDATE, DELETE with precise WHERE clauses.
- ALTER TABLE to add columns. CREATE TABLE for new schemas.
- One SQL statement per tool call. For multiple operations, make multiple sequential tool calls.

RULES:
- INSERT: never DROP or recreate tables. Append only.
- UPDATE: always use WHERE to target specific rows. Never update all rows blindly.
- For multi-part queries (e.g., "insert rows AND list items"), handle each part with separate tool calls in sequence.

YOU DELEGATE to Code_Analyst:
- Bulk inserts (>5 rows) or generated/sequential/random data.
- CSV <-> DB conversions.
- Any Python computation or code writing.

After your task, say 'Database Finished. TERMINATE'."""
    )

    code_agent = AssistantAgent(
        name="Code_Analyst",
        model_client=client,
        tools=[code_tool.execute_python_code],
        description=(
            "Handles ALL: bulk data generation (any size), CSV manipulation (append/update/add columns), "
            "format conversions (CSV<->DB), bulk DB inserts, data analysis, computation, "
            "and writing/executing any Python code. Select this agent for generated data, "
            "large operations, multi-step data tasks, and any code/script requests."
        ),
        system_message=f"""You are the Python engineer. Work directory: {DATA_DIR}. {GLOBAL_CONSTRAINT}

YOU HANDLE:
- Generating datasets of any size for CSV or SQLite DB files.
- All CSV manipulation: appending rows, updating specific values, adding columns.
- All format conversions: CSV to DB, DB to CSV.
- Bulk database inserts (>5 rows) using sqlite3 + executemany().
- Data analysis, filtering, aggregation.
- Writing and executing any Python program the user requests.
- NEVER describe code as text. ALWAYS use execute_python_code tool to run it. Even for simple calculations, execute the code

CRITICAL RULES:
1. PATHS: Always use absolute paths. DATA_DIR = '{DATA_DIR}'. Never use ':memory:' for SQLite.
2. CSV READ-MODIFY-WRITE: To append rows — read existing CSV with pandas, create new rows as DataFrame, concatenate, write back. To update values — read with pandas, modify with .loc or boolean indexing, write back. To add columns — read with pandas, add column, write back. NEVER overwrite or lose existing data.
3. DB APPEND: Use INSERT INTO with executemany(). Never DROP tables. Open DB with sqlite3.connect(absolute_path).
4. UNIQUENESS: Every generated row must have distinct values. Use incrementing IDs, varied realistic names, randomized prices/quantities. Verify no duplicates with existing data before writing.
5. PRINT RESULTS: If the task involves ANY calculation (factorial, sum, fibonacci, statistics, etc.), you MUST print() the computed result. Always print() key outputs so they appear in terminal.
6. PURE CODE TASKS: If asked to write a program (palindrome, sorting, etc.), write complete working code and execute it. If it computes something, print the output.
7. MULTI-PART TASKS: If the query has multiple parts (e.g., "insert 10 rows and list items with quantity > 50"), handle ALL parts in a single Python script.
8. CONVERSION: For CSV->DB: read CSV with pandas, create table, insert all rows. For DB->CSV: query all rows, write to CSV with pandas. Preserve all data.

After execution, say 'Analysis Finished. TERMINATE'."""
    )

    selector_prompt = """Select the next agent from {participants}.

{roles}

Conversation:
{history}

RULES (follow strictly):
- Write/run code, scripts, programs -> Code_Analyst
- Calculate, compute, factorial, sqrt, fibonacci -> Code_Analyst
- Generate data, bulk insert (>5 rows) -> Code_Analyst
- CSV modify/append/update/add columns/analyze -> Code_Analyst
- Convert CSV <-> DB -> Code_Analyst
- SQL query, schema check, single-row DB ops -> DB_Admin
- Simple file read, small manual write (<10 rows) -> File_Manager
- Unsure -> Code_Analyst

Output ONLY the agent name, nothing else."""

    team = SelectorGroupChat(
        participants=[file_agent, db_agent, code_agent],
        model_client=client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        max_turns=10
    )

    print(f"--- Day 3 Team: Operational (Token Optimized) ---")
    
    while True:
        query = input("\nQuery (or 'exit'): ")
        if query.lower() in ["exit", "quit"]: break
        if not query.strip(): continue
        
        try:
            await asyncio.sleep(1) 
            result = await team.run(task=query)
            print(f"\nFinal Result: {result.messages[-1].content}")
        except Exception as e:
            print(f"\n[System Error] {e}")

if __name__ == "__main__":
    asyncio.run(main())