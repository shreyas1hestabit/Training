import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

load_dotenv()

# Common Client Setup
client = OpenAIChatCompletionClient(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": "unknown",
        
    },
    # CRITICAL: This stops the "rubbish" output
    extra_kwargs={
        "temperature": 0,    # Forces deterministic, factual output
        "top_p": 0.1,        # Limits the vocabulary to the most likely words
        "max_tokens": 800,    # Prevents the model from rambling forever
        "repeat_penalty": 1.2, # Prevents the model from looping on the same words
        "seed": 42             # Ensures consistent results
    }
)

# Requirement: Memory Window = 10
memory_window = BufferedChatCompletionContext(buffer_size=10)

research_agent = AssistantAgent(
    name="Researcher",
    model_client=client,
    # system_message="""Task: Fact Reporter. 
    # 1. Use previous conversation history to identify subjects (like 'he' or 'it').
    # 2. If the subject is still unclear, say 'DATA NOT FOUND: Subject unknown'.
    # 3. DO NOT invent fake biographies. 
    # 4. Provide ONLY bullet points. End with TERMINATE.""",
    system_message="""Task: Fact Reporter. 
    1. Provide factual data regarding the user's topic.
    2. If the exact specific value isn't found, provide the closest scientific approximation.
    3. Provide ONLY bullet points. End with TERMINATE.""",
    model_context=memory_window,
)