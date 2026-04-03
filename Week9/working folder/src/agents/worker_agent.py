from autogen_agentchat.agents import AssistantAgent
from src.utils.config import client

worker_agent = AssistantAgent(
    name="Worker",
    model_client=client,
    system_message="""ROLE: Technical Analyst.
    1. PROHIBITION: Never invent specific statistics, percentages, or citations. 
    2. DATA STYLE: Use qualitative descriptions (e.g., 'significant decrease', 'majority of carriers') unless you are quoting a well-known, foundational fact.
    3. NO QUESTIONS: Do not ask the user for more info. If details are missing, describe the general industry standard.
    4. ACCURACY: If you do not have a search tool, provide a high-level conceptual analysis. 
    5. TERMINATE."""
)