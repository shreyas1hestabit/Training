"""
nexus_ai_two/agents.py
-----------------------
All 9 NEXUS AI specialist agents — Groq edition.
Identical to nexus_ai/agents.py except imports from nexus_ai_two.config.
"""

import re
from autogen_core.models import UserMessage, SystemMessage
from nexus_ai_two.config import PRIMARY_MODEL, FAST_MODEL, AGENT_PERSONAS


class BaseAgent:
    def __init__(self, role: str, model=None):
        self.role    = role
        self.model   = model or PRIMARY_MODEL
        self.persona = AGENT_PERSONAS[role]

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


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("planner")

    async def plan(self, task: str, context: str = "") -> tuple[str, list[str]]:
        raw   = await self.run(task, context)
        steps = re.findall(r'^\d+\.\s+(.+)$', raw, re.MULTILINE)
        return raw, steps


class ResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("researcher")


class CoderAgent(BaseAgent):
    def __init__(self):
        super().__init__("coder")


class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__("analyst")


class CriticAgent(BaseAgent):
    def __init__(self):
        super().__init__("critic", model=FAST_MODEL)

    async def review(self, output: str, original_task: str) -> tuple[str, int, str]:
        task = (
            f"Original task:\n{original_task}\n\n"
            f"Output to review:\n{output}"
        )
        raw = await self.run(task)
        score_match = re.search(r'\b([1-9]|10)\s*/\s*10\b', raw)
        score   = int(score_match.group(1)) if score_match else 5
        verdict = "PASS" if "PASS" in raw.upper() else "NEEDS_WORK"
        return raw, score, verdict


class OptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("optimizer")

    async def optimize(self, original: str, critique: str, task: str) -> str:
        context = (
            f"Original task:\n{task}\n\n"
            f"Original output:\n{original}\n\n"
            f"Critic review:\n{critique}"
        )
        return await self.run("Improve the original output based on the critique.", context)


class ValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("validator", model=FAST_MODEL)

    async def validate(self, final_output: str, original_task: str) -> tuple[str, bool]:
        task = (
            f"Original task:\n{original_task}\n\n"
            f"Output to validate:\n{final_output}"
        )
        raw      = await self.run(task)
        is_valid = "INVALID" not in raw.upper()
        return raw, is_valid


class ReporterAgent(BaseAgent):
    def __init__(self):
        super().__init__("reporter")

    async def compile(self, all_outputs: dict, original_task: str) -> str:
        context_parts = [f"### {name}\n{output}" for name, output in all_outputs.items()]
        context = "\n\n---\n\n".join(context_parts)
        task    = f"Original task: {original_task}\n\nCompile all outputs into a final report."
        return await self.run(task, context)


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("orchestrator")

    async def synthesise(self, outputs: dict, task: str) -> str:
        parts   = [f"{k}: {v[:300]}..." for k, v in outputs.items()]
        context = "\n\n".join(parts)
        return await self.run(f"Synthesise all outputs for: {task}", context)