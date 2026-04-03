from autogen_agentchat.agents import AssistantAgent
from src.utils.config import client

reflection_agent = AssistantAgent(
    name="Reflector",
    model_client=client,
    system_message="""ROLE: Expert Content Synthesizer.
    1. Merge multiple worker outputs into one seamless, professional response.
    2. Remove any "Worker 1 said..." or "Here is the result..." meta-talk.
    3. Fix any conflicting information.
    4. Ensure the final result directly answers the user's original query.
    
    Reply with 'TERMINATE' once finished."""
)