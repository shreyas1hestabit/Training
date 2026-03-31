# import asyncio
# import os
# from autogen_agentchat.agents import AssistantAgent
# from autogen_agentchat.ui import Console
# from autogen_agentchat.teams import SelectorGroupChat
# from autogen_agentchat.conditions import TextMentionTermination
# from src.utils.config import client

# import src.day3.tools.file_agent as file_tool
# import src.day3.tools.db_agent as db_tool
# import src.day3.tools.code_executor as code_tool

# # --- Setup Paths ---
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# # Ensure we are pointing to the correct data directory
# DATA_DIR = os.path.join(CURRENT_DIR, "data")
# os.makedirs(DATA_DIR, exist_ok=True)

# # --- Inject Data Directory into Tools ---
# file_tool.DATA_DIR = DATA_DIR
# db_tool.DATA_DIR = DATA_DIR
# code_tool.DATA_DIR = DATA_DIR

# async def main():
#     # 1. Define Termination: The team stops as soon as "TERMINATE" is detected in a message.
#     termination = TextMentionTermination("TERMINATE")

#     # 2. Define Specialist Agents with "Silent Success" instructions
#     # This prevents the "Acknowledged" loop by forcing them to end the turn immediately.
    
#     file_agent = AssistantAgent(
#         name="File_Manager",
#         model_client=client,
#         tools=[file_tool.read_file, file_tool.write_to_file],
#         system_message=f"""You handle File I/O in {DATA_DIR}. 
#         - When you complete a task (like creating or reading a file), summarize the result in one sentence and say 'TERMINATE'.
#         - DO NOT suggest next steps or ask the user for more instructions.
#         - If another agent has already provided a summary, just say 'TERMINATE'."""
#     )

#     db_agent = AssistantAgent(
#         name="DB_Admin",
#         model_client=client,
#         tools=[db_tool.query_database],
#         system_message="""You are a SQL expert managing .db files.
        
#         CRITICAL OPERATIONAL RULE:
#         1. ATOMIC QUERIES: SQLite only allows ONE statement per tool call. 
#         2. MULTI-STEP TASKS: If you need to 'Create a table' and 'Insert data':
#            - First: Call 'query_database' with the CREATE TABLE statement.
#            - Second: Wait for the success message.
#            - Third: Call 'query_database' again with the INSERT INTO statement.
#         3. NO SEMICOLONS: Never combine multiple commands (e.g., CREATE...; INSERT...) in a single call.
#         4. TERMINATION: Once the final change is confirmed, say 'Database Updated. TERMINATE'."""
#     )

#     code_agent = AssistantAgent(
#         name="Code_Analyst",
#         model_client=client,
#         tools=[code_tool.execute_python_code],
#         system_message="""You solve data problems using Python. 
#         - Use code to generate data, clean duplicates, or perform math.
#         - After the code executes, show the result and say 'TERMINATE'.
#         - Use specific brands/names if provided by the user; otherwise, be consistent with existing data."""
#     )

#     # 3. Create the Team with Turn Control
#     team = SelectorGroupChat(
#         participants=[file_agent, db_agent, code_agent],
#         model_client=client,
#         termination_condition=termination,
#         max_turns=5  # Strictly limit turns to prevent multi-agent chatter
#     )

#     print(f"--- Day 3 Team: Operational (Role Isolation Active) ---")
    
#     while True:
#         query = input("\nQuery (or 'exit'): ")
#         if query.lower() in ["exit", "quit"]: break
#         if not query.strip(): continue
        
#         try:
#             # We use team.run_stream to allow the selector to coordinate between agents
#             await Console(team.run_stream(task=query))
#         except Exception as e:
#             # Catching the API connection errors specifically
#             if "name resolution" in str(e).lower() or "connection" in str(e).lower():
#                 print("\n[Network Error] API Connection lost. Please check your internet and try again.")
#             else:
#                 print(f"\n[System Error] {e}")

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
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

# --- Inject Data Directory into Tools ---
file_tool.DATA_DIR = DATA_DIR
db_tool.DATA_DIR = DATA_DIR
code_tool.DATA_DIR = DATA_DIR

async def main():
    termination = TextMentionTermination("TERMINATE")

    file_agent = AssistantAgent(
        name="File_Manager",
        model_client=client,
        tools=[file_tool.read_file, file_tool.write_to_file],
        system_message=f"""You handle File I/O in {DATA_DIR}. 
        - If a user wants to create a table as a file (e.g., 'bottle.db'), confirm if they mean a SQL Database or a CSV file.
        - After a tool call, say 'Task Complete. TERMINATE'."""
    )

    db_agent = AssistantAgent(
        name="DB_Admin",
        model_client=client,
        tools=[db_tool.query_database],
        system_message="""You are a SQL expert. 
        - ATOMICITY: SQLite only allows ONE statement per tool call. 
        - BULK DATA: If you need to insert more than 5 rows, DELEGATE the task to the Code_Analyst. Do not call 'query_database' in a loop.
        - After a call, say 'Database Action Finished. TERMINATE'."""
    )

    code_agent = AssistantAgent(
        name="Code_Analyst",
        model_client=client,
        tools=[code_tool.execute_python_code],
        system_message=f"""You solve complex data tasks using Python.
        - PHYSICAL STORAGE: Always connect to actual .db files in {DATA_DIR}. 
        - CRITICAL: NEVER use ':memory:' for sqlite3 connections. Your work must persist.
        - After code execution, summarize the output and say 'Analysis Finished. TERMINATE'."""
    )

    team = SelectorGroupChat(
        participants=[file_agent, db_agent, code_agent],
        model_client=client,
        termination_condition=termination,
        max_turns=8 # Increased slightly to allow for hand-offs
    )

    print(f"--- Day 3 Team: Operational (Bulk-Handling & Persistence Fixed) ---")
    
    while True:
        query = input("\nQuery (or 'exit'): ")
        if query.lower() in ["exit", "quit"]: break
        if not query.strip(): continue
        
        try:
            # await Console(team.run_stream(task=query))
            # earlier when ran this query output became messy because it was showing all the intermediate results
            result = await team.run(task=query)
            # Only print the very last message from the team
            print(f"\nFinal Result: {result.messages[-1].content}")
        except Exception as e:
            print(f"\n[System Error] {e}")

if __name__ == "__main__":
    asyncio.run(main())