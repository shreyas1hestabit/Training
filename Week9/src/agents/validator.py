from autogen_agentchat.agents import AssistantAgent
from src.utils.config import client

validator_agent = AssistantAgent(
    name="Validator",
    model_client=client,
    system_message="""You are a Quality Control Expert. 
    Compare the Worker's output to the original User Request.
    Check for: 
    1. Hallucinations (Fake citations/DOIs).
    2. Logic errors.
    3. Completeness.
    If accurate, say 'VALIDATED'. If not, say 'REJECTED' and list why."""
)