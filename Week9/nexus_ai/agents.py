"""
nexus_ai/agents.py
------------------
All 9 NEXUS AI specialist agents.
Each agent wraps a single LLM call with its persona and exposes
an async `run(task, context="")` method.
"""

import re
from autogen_core.models import UserMessage, SystemMessage
from nexus_ai.config import PRIMARY_MODEL, FAST_MODEL, AGENT_PERSONAS


# ---------------------------------------------------------------------------
# Base Agent
# ---------------------------------------------------------------------------

class BaseAgent:
    """
    Thin wrapper around a single LLM call.
    Every specialist agent inherits this and sets self.role.
    """

    def __init__(self, role: str, model=None, temperature: float = 0.3):
        self.role        = role
        self.model       = model or PRIMARY_MODEL
        self.temperature = temperature
        self.persona     = AGENT_PERSONAS[role]

    async def run(self, task: str, context: str = "") -> str:
        user_content = task
        if context:
            user_content = f"Context from prior steps:\n{context}\n\nYour task:\n{task}"

        try:
            result = await self.model.create(
                messages=[
                    SystemMessage(content=self.persona),
                    UserMessage(content=user_content, source="user"),
                ],
            )
            return str(result.content).strip()
        except Exception as e:
            return f"[{self.role.upper()} ERROR] {e}"

    def __repr__(self):
        return f"{self.__class__.__name__}(role={self.role})"


# ---------------------------------------------------------------------------
# Specialist Agents
# ---------------------------------------------------------------------------

class PlannerAgent(BaseAgent):
    """
    Decomposes a task into a numbered execution plan.
    Returns structured plan text and a parsed list of steps.
    """
    def __init__(self):
        super().__init__("planner", temperature=0.2)

    async def plan(self, task: str, context: str = "") -> tuple[str, list[str]]:
        """Returns (raw_plan_text, list_of_step_strings)."""
        raw = await self.run(task, context)
        # Parse numbered steps: "1. ...", "2. ..." etc.
        steps = re.findall(r'^\d+\.\s+(.+)$', raw, re.MULTILINE)
        return raw, steps


class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("researcher", temperature=0.4)


class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__("coder", temperature=0.2)


class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyst", temperature=0.2)


class CriticAgent(BaseAgent):
    """
    Reviews another agent's output.
    Returns (raw_review, score: int, verdict: str).
    """
    def __init__(self):
        super().__init__("critic", model=FAST_MODEL, temperature=0.1)

    async def review(self, output: str, original_task: str) -> tuple[str, int, str]:
        """Returns (review_text, score 1-10, 'PASS' | 'NEEDS_WORK')."""
        task = (
            f"Original task given to the agent:\n{original_task}\n\n"
            f"Agent output to review:\n{output}"
        )
        raw = await self.run(task)

        # Extract score
        score_match = re.search(r'\b([1-9]|10)\s*/\s*10\b', raw)
        score = int(score_match.group(1)) if score_match else 5

        verdict = "PASS" if "PASS" in raw.upper() else "NEEDS_WORK"
        return raw, score, verdict


class OptimizerAgent(BaseAgent):
    """Rewrites an output based on Critic's review."""
    def __init__(self):
        super().__init__("optimizer", temperature=0.3)

    async def optimize(self, original: str, critique: str, task: str) -> str:
        context = (
            f"Original task:\n{task}\n\n"
            f"Original output:\n{original}\n\n"
            f"Critic's review:\n{critique}"
        )
        return await self.run("Improve the original output based on the critique above.", context)


class ValidatorAgent(BaseAgent):
    """Final quality gate — returns VALID or INVALID with reasons."""
    def __init__(self):
        super().__init__("validator", model=FAST_MODEL, temperature=0.1)

    async def validate(self, final_output: str, original_task: str) -> tuple[str, bool]:
        """Returns (validation_report, is_valid: bool)."""
        task = (
            f"Original user task:\n{original_task}\n\n"
            f"Final system output to validate:\n{final_output}"
        )
        raw = await self.run(task)
        is_valid = "INVALID" not in raw.upper() or "VALID" in raw.upper().split("INVALID")[0]
        return raw, is_valid


class ReporterAgent(BaseAgent):
    """Compiles all agent outputs into a final polished report."""
    def __init__(self):
        super().__init__("reporter", temperature=0.4)

    async def compile(self, all_outputs: dict, original_task: str) -> str:
        context_parts = [f"### {agent_name}\n{output}"
                         for agent_name, output in all_outputs.items()]
        context = "\n\n---\n\n".join(context_parts)
        task = f"Original user task: {original_task}\n\nCompile all agent outputs into a final report."
        return await self.run(task, context)


class OrchestratorAgent(BaseAgent):
    """
    Master coordinator — not called directly for subtasks,
    but used for meta-decisions like routing and synthesis.
    """
    def __init__(self):
        super().__init__("orchestrator", temperature=0.2)

    async def synthesise(self, outputs: dict, task: str) -> str:
        """Produce a brief synthesis / executive decision from all outputs."""
        parts = [f"{k}: {v[:300]}..." for k, v in outputs.items()]
        context = "\n\n".join(parts)
        return await self.run(f"Synthesise all outputs for task: {task}", context)