import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

# Shared client configuration for all agents
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
    extra_kwargs={
        "temperature": 0,
        "top_p": 0.1,
        "max_tokens": 800
    }
)