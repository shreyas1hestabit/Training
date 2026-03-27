import time
import re
from autogen_core.models import UserMessage, SystemMessage

from nexus_ai_two.agents import (
    PlannerAgent, ResearcherAgent, CoderAgent, AnalystAgent,
    CriticAgent, OptimizerAgent, ValidatorAgent, ReporterAgent,
    OrchestratorAgent,
)
from nexus_ai_two.tools   import analyze_csv, web_search_stub
from nexus_ai_two.memory  import NexusMemory
from nexus_ai_two.conversation_memory import ConversationMemory
from nexus_ai_two.logger  import NexusLogger
from nexus_ai_two.config  import PRIMARY_MODEL, MAX_CRITIC_RETRIES, CRITIC_PASS_SCORE

ROLE_KEYWORDS = {
    "researcher": ["research", "gather", "find", "explain", "what is", "describe",
                   "how does", "background", "investigate", "overview"],
    "coder":      ["code", "implement", "write", "build", "develop", "program",
                   "script", "function", "example", "flask", "api", "class"],
    "analyst":    ["analyze", "analyse", "evaluate", "assess", "csv", "metrics",
                   "insights", "compare", "benchmark", "measure"],
    "reporter":   ["report", "compile", "summarise", "summarize", "document"],
}

def route_step(step: str) -> str:
    step_lower = step.lower()
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in step_lower for kw in keywords):
            return role
    return "researcher"


def classify_task(task: str) -> str:
    """Returns 'fast' for simple tasks, 'full' for complex multi-domain tasks."""
    complex_signals = [
        "startup", "architecture", "pipeline", "strategy", "business plan",
        "design system", "scalable", "production", "end-to-end",
        "comprehensive", "complete system", "plan and implement",
        "rag", "microservices", "infrastructure",
    ]
    return "full" if any(s in task.lower() for s in complex_signals) else "fast"

class NexusOrchestrator:

    def __init__(self):
        self.planner    = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.coder      = CoderAgent()
        self.analyst    = AnalystAgent()
        self.critic     = CriticAgent()
        self.optimizer  = OptimizerAgent()
        self.validator  = ValidatorAgent()
        self.reporter   = ReporterAgent()
        self.master     = OrchestratorAgent()
        self.memory     = NexusMemory()
        self.conv       = ConversationMemory()   # ← conversational memory
        self.log        = NexusLogger()

        self._agents = {
            "researcher": self.researcher,
            "coder":      self.coder,
            "analyst":    self.analyst,
            "reporter":   self.reporter,
        }
        print(f"[NEXUS Memory] Session: {self.conv.status()}")

    async def run(self, task: str) -> str:
        start = time.time()
        self.log.start_task(task)

        mode = classify_task(task)
        print(f"\n  [NEXUS] Mode: {mode.upper()} | Model: llama-3.1-8b-instant (Groq)\n")

        # Inject conversation memory context
        conv_context = self.conv.build_context(task)
        if conv_context:
            print(f"  [NEXUS Memory] Injecting context ({self.conv.status()})")
            task_with_context = f"{task}\n\n{conv_context}"
        else:
            task_with_context = task

        report = await self._fast_pipeline(task_with_context) if mode == "fast" else await self._full_pipeline(task_with_context)

        # Store completed task in conversation memory
        self.conv.store_task(task, report)

        self.memory.save_task(task, report, {}, round(time.time() - start, 2))
        self.log.end_task(success=True, final_output=report)
        return report

    async def _fast_pipeline(self, task: str) -> str:
        print("  [NEXUS] Fast path: Researcher → Coder → Reporter\n")
        agent_outputs = {}
        task_lower    = task.lower()

        needs_research = any(w in task_lower for w in
                             ["explain", "what is", "describe", "how does", "why", "overview"])
        needs_code     = any(w in task_lower for w in
                             ["example", "code", "implement", "write", "flask", "script", "function"])

        if needs_research:
            self.log.agent_start("researcher", task)
            t0       = time.time()
            research = await self.researcher.run(task)
            self.log.agent_end("researcher", research, time.time() - t0)
            research = await self._critique_and_optimize(research, task, "researcher")
            agent_outputs["Research"] = research

        if needs_code:
            context   = agent_outputs.get("Research", "")
            code_task = f"Write a working code example for: {task}"
            self.log.agent_start("coder", code_task)
            t0   = time.time()
            code = await self.coder.run(code_task, context=context)
            self.log.agent_end("coder", code, time.time() - t0)
            code = await self._critique_and_optimize(code, code_task, "coder")
            agent_outputs["Code"] = code

        if not agent_outputs:
            self.log.agent_start("researcher", task)
            t0     = time.time()
            result = await self.researcher.run(task)
            self.log.agent_end("researcher", result, time.time() - t0)
            agent_outputs["Result"] = result

        # Final report + validation
        self.log.agent_start("reporter", "compile")
        t0     = time.time()
        report = await self.reporter.compile(agent_outputs, task)
        self.log.agent_end("reporter", report, time.time() - t0)

        val_report, is_valid = await self.validator.validate(report, task)
        self.log.validation_result(is_valid, val_report)
        if not is_valid:
            report = await self.optimizer.optimize(report, val_report, task)

        reflection = await self._reflect(task, report)
        self.log.reflection(reflection)
        self.memory.add_reflection(reflection, task)

        return report

    async def _full_pipeline(self, task: str) -> str:
        memory_ctx    = self.memory.build_context(task)
        enriched_task = f"{task}\n\n[Memory:]\n{memory_ctx}" if memory_ctx else task

        agent_outputs = {}

        # Plan
        constrained = (
            f"{enriched_task}\n\n"
            f"IMPORTANT: Maximum 5 steps. Each step one sentence. "
            f"Use only: Researcher, Coder, Analyst."
        )
        self.log.agent_start("planner", task)
        t0 = time.time()
        plan_text, steps = await self.planner.plan(constrained)
        self.log.agent_end("planner", plan_text, time.time() - t0)
        steps = steps[:5] or [task]
        self.log.plan(steps)
        agent_outputs["Plan"] = plan_text

        # Execute each step
        accumulated = ""
        for i, step in enumerate(steps, 1):
            role  = route_step(step)
            agent = self._agents.get(role, self.researcher)

            # Tool: CSV detection
            csv_match = re.search(r'[\w\.\-]+\.csv', step, re.IGNORECASE)
            if csv_match:
                csv_result = analyze_csv(csv_match.group(0))
                self.log.tool_call("analyze_csv", {"path": csv_match.group(0)}, csv_result[:100])
                accumulated += f"\nCSV Analysis:\n{csv_result[:400]}"

            self.log.agent_start(role, step)
            t0     = time.time()
            output = await agent.run(step, context=accumulated[:1000])
            self.log.agent_end(role, output, time.time() - t0)
            output = await self._critique_and_optimize(output, step, role)

            accumulated                       += f"\nStep {i}: {output[:500]}"
            agent_outputs[f"Step{i}_{role.title()}"] = output

        # Report
        self.log.agent_start("reporter", "compile")
        t0     = time.time()
        report = await self.reporter.compile(agent_outputs, task)
        self.log.agent_end("reporter", report, time.time() - t0)

        # Validation
        self.log.agent_start("validator", "validate")
        t0         = time.time()
        val_report, is_valid = await self.validator.validate(report, task)
        self.log.agent_end("validator", val_report, time.time() - t0)
        self.log.validation_result(is_valid, val_report)
        if not is_valid:
            self.log.optimizer_run(99)
            report = await self.optimizer.optimize(report, val_report, task)

        # Reflect
        reflection = await self._reflect(task, report)
        self.log.reflection(reflection)
        self.memory.add_reflection(reflection, task)

        return report

    async def _critique_and_optimize(self, output: str, task: str, role: str) -> str:
        review, score, verdict = await self.critic.review(output, task)
        self.log.critic_review(role, score, verdict, review)
        if verdict == "PASS" or score >= CRITIC_PASS_SCORE:
            return output
        for attempt in range(MAX_CRITIC_RETRIES):
            self.log.optimizer_run(attempt + 1)
            output = await self.optimizer.optimize(output, review, task)
            review, score, verdict = await self.critic.review(output, task)
            self.log.critic_review(role, score, verdict, review)
            if verdict == "PASS" or score >= CRITIC_PASS_SCORE:
                break
        return output

    async def _reflect(self, task: str, report: str) -> str:
        prompt = (
            f"Task: {task}\nReport preview: {report[:300]}\n\n"
            "In one sentence, what should be improved next time?"
        )
        try:
            result = await PRIMARY_MODEL.create(
                messages=[
                    SystemMessage(content="Give brief self-improvement notes."),
                    UserMessage(content=prompt, source="user"),
                ],
            )
            return str(result.content).strip()
        except Exception as e:
            return f"Reflection failed: {e}"

    async def run_with_recovery(self, task: str) -> str:
        try:
            return await self.run(task)
        except Exception as e:
            self.log.agent_error("orchestrator", str(e))
            print(f"\n[NEXUS] Error: {e}\n[NEXUS] Running recovery...")
            try:
                result = await self.researcher.run(task)
                return f"[Recovery mode]\n\n{result}"
            except Exception as e2:
                return f"[NEXUS ERROR] {e}\nRecovery also failed: {e2}"