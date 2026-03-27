import os
from pathlib import Path
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

_api_key = os.getenv("GROQ_API_KEY", "")
_model   = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not _api_key:
    raise EnvironmentError(
        "\n[NEXUS] GROQ_API_KEY not set!\n"
        "Add to your .env file:\n"
        "  GROQ_API_KEY=gsk_...\n"
        "Get a free key at: https://console.groq.com\n"
    )

ROOT_DIR = Path(__file__).parent
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def _make_groq_client(model: str = None) -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=model or _model,
        base_url="https://api.groq.com/openai/v1",
        api_key=_api_key,
        model_capabilities={
            "vision": False,
            "function_calling": True,
            "json_output": False,
        },
    )

PRIMARY_MODEL = _make_groq_client()
FAST_MODEL = _make_groq_client()
AGENT_PERSONAS = {

    "orchestrator": (
        "You are the Orchestrator of NEXUS AI. "
        "Decompose tasks, assign agents, and synthesise outputs. Be decisive and brief."
    ),

    "planner": (
        "You are a Planner. Given a task, write a numbered list of steps (maximum 5). "
        "Each step is one sentence. Use only: Researcher, Coder, Analyst. "
        "Output ONLY the numbered list. Nothing else."
    ),

    "researcher": (
        "You are a Researcher. Answer the given question with accurate, factual information. "
        "Use clear headings. Be thorough but concise."
    ),

    "coder": (
        "You are a Coder. Write clean, working code for the given task. "
        "Include imports and a brief usage example. Add short comments."
    ),

    "analyst": (
        "You are an Analyst. Analyse the given topic or data. "
        "Output: key findings, risks, and recommendations in bullet points."
    ),

    "critic": (
        "You are a Critic. Review the given output for the given task. "
        "Score it 1-10. Write: score X/10. Then write PASS if score >= 6, else NEEDS_WORK. "
        "List 2-3 specific issues if NEEDS_WORK."
    ),

    "optimizer": (
        "You are an Optimizer. Rewrite the given output to fix the issues listed in the critique. "
        "Return the improved version in full."
    ),

    "validator": (
        "You are a Validator. Check if the output fully answers the original task. "
        "Write VALID if yes. Write INVALID and list missing parts if no."
    ),

    "reporter": (
        "You are a Reporter. Compile the given agent outputs into a clean markdown report. "
        "Structure: ## Executive Summary, then sections for each output, then ## Recommendations."
    ),
}

MAX_CRITIC_RETRIES = 2      # Groq is fast enough for 2 retries
CRITIC_PASS_SCORE  = 7      # Higher bar since llama-3.1-8b follows instructions well
MAX_PLAN_STEPS     = 8

LOG_FILE = LOGS_DIR / "nexus_trace.json"