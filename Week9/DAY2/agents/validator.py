from autogen_agentchat.agents import AssistantAgent
from src.utils.config import client

validator_agent = AssistantAgent(
    name="Validator",
    model_client=client,
    system_message="""ROLE: Quality Control Expert.
    Compare the Final Answer against the original User Request.
    
    REJECT if:
    1. The answer contains questions directed at the user.
    2. There are fake citations or obvious hallucinations.
    3. The answer is incomplete.
    
    If accurate, say 'VALIDATED'. 
    If inaccurate, say 'REJECTED' and list the reasons clearly."""
)