import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
 
load_dotenv()
 
# ── Read all keys from .env ────────────────────────────────────────────────
_groq_api_key  = os.getenv("GROQ_API_KEY", "").strip()
_groq_model    = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
 
_ollama_api_key = os.getenv("OLLAMA_API_KEY", "ollama").strip() or "ollama"
_ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1").strip()
_ollama_model   = os.getenv("MODEL_NAME", "llama3.2").strip()
 
# ── Auto-select: Groq if key is set, Ollama otherwise ─────────────────────
if _groq_api_key:
    client = OpenAIChatCompletionClient(
        model=_groq_model,
        base_url="https://api.groq.com/openai/v1",
        api_key=_groq_api_key,
        model_info={
            "vision":            False,
            "function_calling":  True,
            "json_output":       True,
            "family":            "unknown",
            "structured_output": False,
        },
        extra_kwargs={
            "temperature": 0,
            "max_tokens":  2048,
        },
    )
    print(f"[Config] Backend: Groq  | model: {_groq_model}")
 
else:
    client = OpenAIChatCompletionClient(
        model=_ollama_model,
        base_url=_ollama_base_url,
        api_key=_ollama_api_key,
        model_info={
            "vision":            False,
            "function_calling":  True,
            "json_output":       False,
            "family":            "unknown",
            "structured_output": False,
        },
        extra_kwargs={
            "temperature": 0,
            "top_p":       0.1,
            "max_tokens":  1200,
        },
    )
    print(f"[Config] Backend: Ollama | model: {_ollama_model}")