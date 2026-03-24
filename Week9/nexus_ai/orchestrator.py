"""
nexus_ai/orchestrator.py
-------------------------
NEXUS AI Master Orchestrator.

Implements the full pipeline:
    1. Plan          — Planner decomposes task into steps
    2. Execute       — Each step routed to the right agent
    3. Critique      — Critic reviews key outputs
    4. Optimize      — Optimizer rewrites if score < threshold
    5. Validate      — Validator does final quality check
    6. Report        — Reporter compiles final deliverable
    7. Reflect       — Self-reflection stored in memory
    8. Log           — Full trace written to logs/

Supports role switching: the Orchestrator dynamically assigns agents
based on keywords in each plan step.
"""

import time
import re
from autogen_core.models import UserMessage, SystemMessage

from nexus_ai.agents import (
    PlannerAgent, ResearcherAgent, CoderAgent, AnalystAgent,
    CriticAgent, OptimizerAgent, ValidatorAgent, ReporterAgent,
    OrchestratorAgent,
)
from nexus_ai.tools   import TOOL_REGISTRY, analyze_csv, web_search_stub
from nexus_ai.memory  import NexusMemory
from nexus_ai.logger  import NexusLogger
from nexus_ai.config  import PRIMARY_MODEL, MAX_CRITIC_RETRIES, CRITIC_PASS_SCORE


# ---------------------------------------------------------------------------
# Role Router — maps plan step keywords → agent
# ---------------------------------------------------------------------------

ROLE_KEYWORDS = {
    "researcher":  ["research", "gather", "find", "investigate", "look up", "background", "survey"],
    "coder":       ["code", "implement", "write", "build", "develop", "program", "script", "function"],
    "analyst":     ["analyze", "analyse", "evaluate", "assess", "review data", "csv", "metrics", "insights"],
    "planner":     ["plan", "roadmap", "timeline", "milestones", "breakdown", "strategy"],
    "reporter":    ["report", "compile", "summarise", "summarize", "present", "document"],
}

def route_step(step: str) -> str:
    """Return the best agent role for a given plan step description."""
    step_lower = step.lower()
    for role, keywords in ROLE_KEYWORDS.items():
        if any(kw in step_lower for kw in keywords):
            return role
    return "researcher"  # safe default


# ---------------------------------------------------------------------------
# NEXUS Orchestrator
# ---------------------------------------------------------------------------

class NexusOrchestrator:
    """
    Master controller for NEXUS AI.
    Call: await nexus.run(task) to execute a full multi-agent pipeline.
    """

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
        self.log        = NexusLogger()

        self._agents = {
            "researcher": self.researcher,
            "coder":      self.coder,
            "analyst":    self.analyst,
            "planner":    self.planner,
            "reporter":   self.reporter,
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def run(self, task: str) -> str:
        """
        Execute a full NEXUS AI pipeline for the given task.
        Returns the final report as a markdown string.
        """
        start = time.time()
        self.log.start_task(task)

        # Inject memory context into task
        memory_ctx = self.memory.build_context(task)
        enriched_task = task
        if memory_ctx:
            enriched_task = f"{task}\n\n[Memory context:]\n{memory_ctx}"

        agent_outputs: dict[str, str] = {}

        # ── Step 1: Plan ────────────────────────────────────────────
        self.log.agent_start("planner", f"Plan: {task}")
        t0 = time.time()
        plan_text, steps = await self.planner.plan(enriched_task)
        self.log.agent_end("planner", plan_text, time.time() - t0)
        self.log.plan(steps)
        agent_outputs["Planner"] = plan_text

        if not steps:
            steps = [task]  # fallback: treat the whole task as one step

        # ── Step 2: Execute each step ───────────────────────────────
        step_outputs: list[str] = []
        accumulated_context = plan_text

        for i, step in enumerate(steps, 1):
            role = route_step(step)
            agent = self._agents.get(role, self.researcher)

            self.log.agent_start(role, step)
            t0 = time.time()

            # Check if step involves a CSV file
            csv_match = re.search(r'[\w\.\-]+\.csv', step, re.IGNORECASE)
            if csv_match:
                csv_result = analyze_csv(csv_match.group(0))
                self.log.tool_call("analyze_csv", {"path": csv_match.group(0)}, csv_result[:100])
                accumulated_context += f"\n\nCSV Analysis:\n{csv_result}"

            # Check if step involves research / web search
            if role == "researcher" and "search" in step.lower():
                search_result = web_search_stub(step)
                self.log.tool_call("web_search", {"query": step}, search_result[:100])
                accumulated_context += f"\n\nSearch result:\n{search_result}"

            output = await agent.run(step, context=accumulated_context)
            duration = time.time() - t0
            self.log.agent_end(role, output, duration)

            # ── Critic loop for key steps ───────────────────────────
            output = await self._critique_and_optimize(output, step, role)

            step_outputs.append(f"**Step {i} ({role.title()}):** {step}\n\n{output}")
            accumulated_context += f"\n\nStep {i} output:\n{output[:600]}"
            agent_outputs[f"Step{i}_{role.title()}"] = output

        # ── Step 3: Final report ────────────────────────────────────
        self.log.agent_start("reporter", "Compile final report")
        t0 = time.time()
        final_report = await self.reporter.compile(agent_outputs, task)
        self.log.agent_end("reporter", final_report, time.time() - t0)

        # ── Step 4: Validation ──────────────────────────────────────
        self.log.agent_start("validator", "Validate final output")
        t0 = time.time()
        validation_report, is_valid = await self.validator.validate(final_report, task)
        self.log.agent_end("validator", validation_report, time.time() - t0)
        self.log.validation_result(is_valid, validation_report)

        # If invalid, run one final optimization pass
        if not is_valid:
            self.log.optimizer_run(attempt=99)
            t0 = time.time()
            final_report = await self.optimizer.optimize(
                final_report, validation_report, task
            )
            self.log.agent_end("optimizer", final_report, time.time() - t0)

        # ── Step 5: Self-reflection ─────────────────────────────────
        reflection = await self._reflect(task, final_report, agent_outputs)
        self.log.reflection(reflection)
        self.memory.add_reflection(reflection, task)

        # ── Step 6: Save to memory ─────────────────────────────────
        duration = time.time() - start
        self.memory.save_task(task, final_report, agent_outputs, duration)

        self.log.end_task(success=True, final_output=final_report)
        return final_report

    # ------------------------------------------------------------------
    # Critic + Optimizer loop
    # ------------------------------------------------------------------

    async def _critique_and_optimize(self, output: str, task: str, role: str) -> str:
        """
        Run the Critic on an agent's output.
        If score < CRITIC_PASS_SCORE, run the Optimizer (up to MAX_CRITIC_RETRIES).
        Returns the final (possibly improved) output.
        """
        current = output

        for attempt in range(MAX_CRITIC_RETRIES):
            t0 = time.time()
            review, score, verdict = await self.critic.review(current, task)
            self.log.critic_review(role, score, verdict, review)

            if verdict == "PASS" or score >= CRITIC_PASS_SCORE:
                break

            self.log.optimizer_run(attempt + 1)
            t0 = time.time()
            current = await self.optimizer.optimize(current, review, task)
            self.log.agent_end("optimizer", current, time.time() - t0)

        return current

    # ------------------------------------------------------------------
    # Self-reflection
    # ------------------------------------------------------------------

    async def _reflect(self, task: str, report: str, outputs: dict) -> str:
        """
        Ask the master agent to reflect on the run:
        what went well, what could improve, what to remember.
        """
        context = (
            f"Task: {task}\n\n"
            f"Number of agents used: {len(outputs)}\n"
            f"Report preview: {report[:400]}"
        )
        prompt = (
            "Reflect on this multi-agent task execution. "
            "In 2-3 sentences, note: what worked well, one thing to improve next time, "
            "and one fact worth remembering for future tasks."
        )
        try:
            result = await PRIMARY_MODEL.create(
                messages=[
                    SystemMessage(content="You are a self-improving AI system. Be concise and specific."),
                    UserMessage(content=f"{context}\n\n{prompt}", source="user"),
                ],
                extra_create_args={"temperature": 0.3},
            )
            return str(result.content).strip()
        except Exception as e:
            return f"Reflection failed: {e}"

    # ------------------------------------------------------------------
    # Failure recovery
    # ------------------------------------------------------------------

    async def run_with_recovery(self, task: str) -> str:
        """
        Wraps run() with failure recovery.
        On error, retries once with a simplified version of the task.
        """
        try:
            return await self.run(task)
        except Exception as e:
            self.log.agent_error("orchestrator", str(e))
            print(f"\n[NEXUS] Primary run failed: {e}")
            print("[NEXUS] Attempting recovery with simplified execution...")

            try:
                # Fallback: single researcher + reporter pass
                research = await self.researcher.run(task)
                report   = await self.reporter.compile({"Research": research}, task)
                self.log.end_task(success=False, final_output=report)
                return f"[Recovery mode]\n\n{report}"
            except Exception as e2:
                return f"[NEXUS ERROR] Both primary and recovery execution failed.\nPrimary: {e}\nRecovery: {e2}"