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
    """
    Create a Groq-backed OpenAIChatCompletionClient.
    model_capabilities is set explicitly because Groq models are not in
    AutoGen's built-in registry and would otherwise raise a UserWarning
    about the missing 'structured_output' field.
    """
    return OpenAIChatCompletionClient(
        model=model or _model,
        base_url="https://api.groq.com/openai/v1",
        api_key=_api_key,
        model_capabilities={
            "vision":            False,
            "function_calling":  True,
            "json_output":       False,
            "structured_output": False,   # suppresses AutoGen UserWarning
        },
    )


PRIMARY_MODEL = _make_groq_client()
FAST_MODEL    = _make_groq_client()

AGENT_PERSONAS: dict[str, str] = {

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
        "You are a Coder. Write clean, working code for the given task.\n"
        "STRICT RULES — you must follow all of these:\n"
        "1. Every piece of code MUST be inside a fenced block with the language tag.\n"
        "   Example:  ```python\nimport os\nprint('hello')\n```\n"
        "2. NEVER write code as plain prose or inline text. No exceptions.\n"
        "3. All imports go at the top of each code block.\n"
        "4. Include a short usage example in its own fenced block at the end.\n"
        "5. Add brief inline comments on key steps.\n"
        "If your response contains code, it MUST be inside a fenced block."
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
        "You are an Optimizer. Rewrite the given output to fix the issues in the critique.\n"
        "IMPORTANT: if the original contains fenced code blocks (```language ... ```), "
        "copy them into your improved version exactly — never convert code to prose.\n"
        "Return the full improved version."
    ),

    "validator": (
        "You are a Validator. Check if the output fully answers the original task. "
        "Write VALID if yes. Write INVALID and list missing parts if no."
    ),

    "reporter": (
        "You are a Reporter. Compile the given agent outputs into a clean markdown report.\n"
        "Structure: ## Executive Summary, one section per agent output, then ## Recommendations.\n"
        "CRITICAL RULES:\n"
        "1. Any fenced code block (```language ... ```) in an agent output MUST be copied verbatim "
        "   into a ## Code section of your report. Do not paraphrase or describe code.\n"
        "2. Never drop or rewrite fenced code blocks — they must appear in full.\n"
        "3. If multiple agents produced code, include all of their blocks."
    ),
}

MAX_CRITIC_RETRIES = 2
CRITIC_PASS_SCORE  = 7
MAX_PLAN_STEPS     = 8

LOG_FILE = LOGS_DIR / "nexus_trace.json"