from autogen_agentchat.agents import AssistantAgent
from src.utils.config import client

worker_agent = AssistantAgent(
    name="Worker",
    model_client=client,
    system_message="""ROLE: Focused Task Executor.
    STRICT RULE: Focus ONLY on the assigned TASK. 
    Do NOT bring in information from previous conversations or unrelated topics (like marine life or enzymes).
    If the task is about a party, provide ONLY party-related details.
    TERMINATE."""
)