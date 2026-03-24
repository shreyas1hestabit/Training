"""
nexus_ai_two/memory.py
-----------------------
Persistent memory for NEXUS AI — Groq edition.
Identical to nexus_ai/memory.py except imports from nexus_ai_two.config.
"""

import json
from datetime import datetime
from pathlib import Path
from nexus_ai_two.config import LOGS_DIR


MEMORY_FILE = LOGS_DIR / "nexus_memory.json"


class NexusMemory:
    def __init__(self):
        self._data = {"task_history": [], "key_facts": [], "reflections": []}
        self._load()

    def _load(self):
        if MEMORY_FILE.exists():
            try:
                self._data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

    def _save(self):
        MEMORY_FILE.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def save_task(self, task: str, report: str, agent_outputs: dict, duration_s: float):
        self._data["task_history"].append({
            "timestamp":     datetime.now().isoformat(),
            "task":          task,
            "report":        report,
            "agent_outputs": {k: v[:500] for k, v in agent_outputs.items()},
            "duration_s":    round(duration_s, 2),
        })
        self._save()

    def get_recent_tasks(self, n: int = 3) -> list[dict]:
        return self._data["task_history"][-n:]

    def add_fact(self, fact: str, source_task: str = ""):
        self._data["key_facts"].append({
            "fact":      fact,
            "source":    source_task[:80],
            "timestamp": datetime.now().isoformat(),
        })
        self._save()

    def get_facts(self) -> list[str]:
        return [f["fact"] for f in self._data["key_facts"]]

    def add_reflection(self, reflection: str, task: str = ""):
        self._data["reflections"].append({
            "reflection": reflection,
            "task":       task[:80],
            "timestamp":  datetime.now().isoformat(),
        })
        self._save()

    def get_reflections(self, n: int = 3) -> list[str]:
        return [r["reflection"] for r in self._data["reflections"][-n:]]

    def build_context(self, current_task: str) -> str:
        parts = []
        recent = self.get_recent_tasks(3)
        if recent:
            lines = [f"- [{r['timestamp'][:10]}] {r['task'][:80]}" for r in recent]
            parts.append("Recent tasks:\n" + "\n".join(lines))
        facts = self.get_facts()
        if facts:
            parts.append("Known facts:\n" + "\n".join(f"- {f}" for f in facts[-5:]))
        reflections = self.get_reflections(2)
        if reflections:
            parts.append("Self-improvement notes:\n" + "\n".join(f"- {r}" for r in reflections))
        return "\n\n".join(parts) if parts else ""

    def stats(self) -> dict:
        return {
            "tasks":       len(self._data["task_history"]),
            "facts":       len(self._data["key_facts"]),
            "reflections": len(self._data["reflections"]),
        }