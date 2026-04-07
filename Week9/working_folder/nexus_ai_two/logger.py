import json
import time
from datetime import datetime
from nexus_ai_two.config import LOGS_DIR

TRACE_FILE = LOGS_DIR / "nexus_trace_two.json"


class NexusLogger:
    def __init__(self):
        self._entries: list[dict] = []
        self._task_start: float   = 0.0
        self._current_task: str   = ""

    def start_task(self, task: str):
        self._task_start   = time.time()
        self._current_task = task
        self._entries      = []
        self._log("TASK_START", "orchestrator", {"task": task})
        print(f"\n{'='*60}")
        print(f"[NEXUS] Task: {task[:80]}")
        print(f"{'='*60}")

    def end_task(self, success: bool, final_output: str = ""):
        duration = round(time.time() - self._task_start, 2)
        self._log("TASK_END", "orchestrator", {
            "success":        success,
            "duration_s":     duration,
            "output_preview": final_output[:200],
        })
        self._flush()
        print(f"\n[NEXUS] Task {'completed' if success else 'failed'} in {duration}s")

    def agent_start(self, agent: str, task_desc: str):
        self._log("AGENT_START", agent, {"task": task_desc[:200]})
        print(f"\n  [{agent.upper()}] Starting...")

    def agent_end(self, agent: str, output: str, duration_s: float = 0):
        self._log("AGENT_END", agent, {
            "output_preview": output[:300],
            "duration_s":     round(duration_s, 2),
        })
        preview = output[:100].replace("\n", " ")
        print(f"  [{agent.upper()}] Done ({round(duration_s,1)}s) → {preview}...")

    def agent_error(self, agent: str, error: str):
        self._log("AGENT_ERROR", agent, {"error": error})
        print(f"  [{agent.upper()}] ERROR: {error}")

    def critic_review(self, agent_reviewed: str, score: int, verdict: str, review: str):
        self._log("CRITIC_REVIEW", "critic", {
            "reviewed": agent_reviewed,
            "score":    score,
            "verdict":  verdict,
            "review":   review[:300],
        })
        icon = "✓" if verdict == "PASS" else "✗"
        print(f"  [CRITIC] {icon} {agent_reviewed} — {score}/10 ({verdict})")

    def optimizer_run(self, attempt: int):
        self._log("OPTIMIZER_RUN", "optimizer", {"attempt": attempt})
        print(f"  [OPTIMIZER] Improvement attempt {attempt}...")

    def tool_call(self, tool: str, args: dict, result: str):
        self._log("TOOL_CALL", "tool", {
            "tool":   tool,
            "args":   {k: str(v)[:100] for k, v in args.items()},
            "result": result[:200],
        })
        print(f"  [TOOL] {tool} → {result[:60]}...")

    def validation_result(self, is_valid: bool, report: str):
        self._log("VALIDATION", "validator", {"is_valid": is_valid, "report": report[:300]})
        icon = "✓" if is_valid else "✗"
        print(f"  [VALIDATOR] {icon} {'VALID' if is_valid else 'INVALID'}")

    def reflection(self, text: str):
        self._log("REFLECTION", "orchestrator", {"reflection": text[:400]})
        print(f"  [REFLECTION] {text[:100]}...")

    def plan(self, steps: list[str]):
        self._log("PLAN", "planner", {"steps": steps})
        print(f"\n  [PLAN] {len(steps)} steps:")
        for i, s in enumerate(steps, 1):
            print(f"    {i}. {s[:80]}")

    def _log(self, event_type: str, agent: str, data: dict):
        self._entries.append({
            "timestamp": datetime.now().isoformat(),
            "event":     event_type,
            "agent":     agent,
            "task":      self._current_task[:80],
            "data":      data,
        })

    def _flush(self):
        existing = []
        if TRACE_FILE.exists():
            try:
                existing = json.loads(TRACE_FILE.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        existing.extend(self._entries)
        TRACE_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")