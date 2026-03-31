# import asyncio
# import os
# from autogen_agentchat.agents import AssistantAgent
# from autogen_agentchat.ui import Console
# from src.utils.config import client
# import src.day3.tools.file_agent as file_tool
# import src.day3.tools.db_agent as db_tool
# import src.day3.tools.code_executor as code_tool

# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(CURRENT_DIR, "data")
# os.makedirs(DATA_DIR, exist_ok=True)

# file_tool.DATA_DIR = DATA_DIR
# db_tool.DATA_DIR = DATA_DIR
# code_tool.DATA_DIR = DATA_DIR

# async def main():
#     agent = AssistantAgent(
#         name="Data_Engineer",
#         model_client=client,
#         tools=[
#             file_tool.read_file, 
#             file_tool.write_to_file, 
#             db_tool.query_database, 
#             code_tool.execute_python_code
#         ],
#         system_message=f"""You are a Precise Data Engineer. Storage: {DATA_DIR}
        
#         CRITICAL MULTI-STEP PROTOCOL:
#         1. COMPLETION: If a user asks for an update (e.g., 'Update price'), you must:
#            - First: Find the row/table.
#            - Second: Execute the UPDATE or write the new file immediately.
#            - Third: Show the final result to confirm.
#         2. DO NOT STOP: If a prompt has two parts (e.g., 'What tables? Then show data'), you must call BOTH tools in sequence. Do not wait for a second user prompt.
#         3. OUTPUT: Always print the results to the console using tool outputs or 'print()' in Python.
#         4. PATHS: You are already inside the data directory. Use direct filenames like 'laptop.db'."""
#     )

#     print(f"--- System Rebooted: Multi-Step Logic Fixed ---")
#     while True:
#         query = input("\nQuery: ")
#         if query.lower() in ["exit", "quit"]: break
#         await Console(agent.run_stream(task=query))

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
# Ensure we are pointing to the correct data directory
DATA_DIR = os.path.join(CURRENT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# --- Inject Data Directory into Tools ---
file_tool.DATA_DIR = DATA_DIR
db_tool.DATA_DIR = DATA_DIR
code_tool.DATA_DIR = DATA_DIR

async def main():
    # 1. Define Termination: The team stops as soon as "TERMINATE" is detected in a message.
    termination = TextMentionTermination("TERMINATE")

    # 2. Define Specialist Agents with "Silent Success" instructions
    # This prevents the "Acknowledged" loop by forcing them to end the turn immediately.
    
    file_agent = AssistantAgent(
        name="File_Manager",
        model_client=client,
        tools=[file_tool.read_file, file_tool.write_to_file],
        system_message=f"""You handle File I/O in {DATA_DIR}. 
        - When you complete a task (like creating or reading a file), summarize the result in one sentence and say 'TERMINATE'.
        - DO NOT suggest next steps or ask the user for more instructions.
        - If another agent has already provided a summary, just say 'TERMINATE'."""
    )

    db_agent = AssistantAgent(
        name="DB_Admin",
        model_client=client,
        tools=[db_tool.query_database],
        system_message="""You are a SQL expert managing .db files. 
        - After running a query, provide the result and say 'TERMINATE'.
        - Do not engage in conversation or repeat information already provided by others."""
    )

    code_agent = AssistantAgent(
        name="Code_Analyst",
        model_client=client,
        tools=[code_tool.execute_python_code],
        system_message="""You solve data problems using Python. 
        - Use code to generate data, clean duplicates, or perform math.
        - After the code executes, show the result and say 'TERMINATE'.
        - Use specific brands/names if provided by the user; otherwise, be consistent with existing data."""
    )

    # 3. Create the Team with Turn Control
    team = SelectorGroupChat(
        participants=[file_agent, db_agent, code_agent],
        model_client=client,
        termination_condition=termination,
        max_turns=5  # Strictly limit turns to prevent multi-agent chatter
    )

    print(f"--- Day 3 Team: Operational (Role Isolation Active) ---")
    
    while True:
        query = input("\nQuery (or 'exit'): ")
        if query.lower() in ["exit", "quit"]: break
        if not query.strip(): continue
        
        try:
            # We use team.run_stream to allow the selector to coordinate between agents
            await Console(team.run_stream(task=query))
        except Exception as e:
            # Catching the API connection errors specifically
            if "name resolution" in str(e).lower() or "connection" in str(e).lower():
                print("\n[Network Error] API Connection lost. Please check your internet and try again.")
            else:
                print(f"\n[System Error] {e}")

if __name__ == "__main__":
    asyncio.run(main())