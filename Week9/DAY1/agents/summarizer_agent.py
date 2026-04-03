import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

load_dotenv()

client = OpenAIChatCompletionClient(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": "unknown",
        "structured_output": False
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

memory_window = BufferedChatCompletionContext(buffer_size=10)

summarizer_agent = AssistantAgent(
    name="Summarizer",
    model_client=client,
    system_message="Task: Summarizer. Provide EXACTLY 3 bullet points. No more, no less. If input is 'DATA NOT FOUND', output 'DATA NOT FOUND'. End with TERMINATE.",
    model_context=memory_window,
)