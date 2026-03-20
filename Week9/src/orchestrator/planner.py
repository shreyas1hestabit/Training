from autogen_agentchat.agents import AssistantAgent
from src.utils.config import client

planner_agent = AssistantAgent(
    name="Planner",
    model_client=client,
    system_message="""You are the Task Architect. 
    Analyze the user request and break it into a logical sequence of sub-tasks.
    - If the request is simple, use 1 task.
    - If the request is complex, use as many as needed (suggested max 4 for efficiency).
    
    Format your response EXACTLY like this:
    TASK 1: [Description]
    TASK 2: [Description]
    ... Break this into the minimum necessary number of sub-tasks (MAXIMUM 5). If you create more than 5s, the mission will fail.
    
    Only output the tasks. No preamble."""
)