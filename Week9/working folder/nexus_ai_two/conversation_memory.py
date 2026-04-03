import json
import re
from pathlib import Path
from datetime import datetime
from autogen_core.models import UserMessage, SystemMessage

from nexus_ai_two.config import LOGS_DIR, PRIMARY_MODEL

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False

EMBED_MODEL  = "all-MiniLM-L6-v2"
EMBED_DIM    = 384
INDEX_PATH   = LOGS_DIR / "nexus_faiss.index"
META_PATH    = LOGS_DIR / "nexus_vector_meta.json"
FACTS_PATH   = LOGS_DIR / "nexus_facts.json"

class SessionHistory:
    """
    Stores the current multi-turn conversation as a list of
    {"role": "user"|"assistant", "content": "..."} dicts.
    Max window = last 6 exchanges (12 messages).
    """

    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self._turns: list[dict] = []

    def add(self, role: str, content: str):
        self._turns.append({"role": role, "content": content, "ts": datetime.now().isoformat()})
        # Trim to window
        limit = self.max_turns * 2
        if len(self._turns) > limit:
            self._turns = self._turns[-limit:]

    def get_recent_text(self, n: int = 4) -> str:
        """Return last n messages as a plain-text block."""
        recent = self._turns[-n:]
        lines  = []
        for m in recent:
            prefix = "User" if m["role"] == "user" else "NEXUS"
            lines.append(f"[{prefix}]: {m['content'][:400]}")
        return "\n".join(lines)

    def get_all(self) -> list[dict]:
        return list(self._turns)

    def clear(self):
        self._turns.clear()

    def __len__(self):
        return len(self._turns)

class NexusVectorStore:
    """
    Stores task reports and key outputs as embeddings.
    On every new task, searches for semantically similar past work
    and injects it as context.
    """

    def __init__(self):
        self._available = VECTOR_AVAILABLE
        if not self._available:
            print("[NEXUS Memory] FAISS not available — vector search disabled.")
            return

        self._model    = SentenceTransformer(EMBED_MODEL)
        self._metadata: list[dict] = []
        self._index    = None
        self._load()

    def _load(self):
        if INDEX_PATH.exists() and META_PATH.exists():
            self._index = faiss.read_index(str(INDEX_PATH))
            self._metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
        else:
            self._index    = faiss.IndexFlatL2(EMBED_DIM)
            self._metadata = []

    def _save(self):
        faiss.write_index(self._index, str(INDEX_PATH))
        META_PATH.write_text(json.dumps(self._metadata, indent=2), encoding="utf-8")

    def add(self, text: str, source: str = "task", meta: dict = None):
        if not self._available or not text.strip():
            return
        vec = self._model.encode([text], convert_to_numpy=True).astype("float32")
        self._index.add(vec)
        self._metadata.append({
            "id":     len(self._metadata),
            "text":   text[:800],
            "source": source,
            "meta":   meta or {},
            "ts":     datetime.now().isoformat(),
        })
        self._save()

    def search(self, query: str, top_k: int = 3, threshold: float = 1.8) -> list[dict]:
        if not self._available or self._index.ntotal == 0:
            return []
        k   = min(top_k, self._index.ntotal)
        vec = self._model.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = self._index.search(vec, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or dist > threshold:
                continue
            entry = self._metadata[idx].copy()
            entry["score"] = float(dist)
            results.append(entry)
        return results

    def count(self) -> int:
        return self._index.ntotal if self._available and self._index else 0

    def reset(self):
        if not self._available:
            return
        self._index    = faiss.IndexFlatL2(EMBED_DIM)
        self._metadata = []
        self._save()

class NexusFacts:
    """
    Lightweight JSON-backed facts store.
    Extracts and stores key facts from each task output.
    Example: "The RAG pipeline uses FAISS with 384-dim embeddings"
    """

    def __init__(self):
        self._facts: list[dict] = []
        self._load()

    def _load(self):
        if FACTS_PATH.exists():
            try:
                self._facts = json.loads(FACTS_PATH.read_text(encoding="utf-8"))
            except Exception:
                self._facts = []

    def _save(self):
        FACTS_PATH.write_text(json.dumps(self._facts, indent=2), encoding="utf-8")

    def add(self, fact: str, source_task: str = ""):
        self._facts.append({
            "fact":   fact,
            "source": source_task[:80],
            "ts":     datetime.now().isoformat(),
        })
        self._save()

    def get_all(self) -> list[str]:
        return [f["fact"] for f in self._facts]

    def get_recent(self, n: int = 5) -> list[str]:
        return [f["fact"] for f in self._facts[-n:]]

    def clear(self):
        self._facts = []
        self._save()

class ConversationMemory:
    """
    Three-tier conversational memory for NEXUS AI:

        Tier 1 — Session history : last N turns of the current conversation
        Tier 2 — Vector store    : FAISS semantic search over past task reports
        Tier 3 — Facts store     : key facts extracted from task outputs

    Usage:
        memory = ConversationMemory()

        # Before each task — get relevant context
        context = memory.build_context(user_task)

        # After each task — store the output
        memory.store_task(user_task, final_report)

        # Add a user/assistant turn to session history
        memory.session.add("user", user_task)
        memory.session.add("assistant", final_report)
    """

    def __init__(self):
        self.session = SessionHistory(max_turns=6)
        self.vector  = NexusVectorStore()
        self.facts   = NexusFacts()

    def build_context(self, current_task: str) -> str:
        """
        Returns a formatted context string combining:
          - Recent session turns (what we just discussed)
          - Semantically similar past task reports (FAISS)
          - Known facts from previous tasks
        """
        parts = []

        # Tier 1: Session history (most important for follow-ups)
        if len(self.session) > 0:
            recent = self.session.get_recent_text(n=4)
            parts.append(
                "## Recent conversation\n"
                "(Use this to understand follow-up questions)\n"
                + recent
            )

        # Tier 2: Semantically similar past work
        if self.vector.count() > 0:
            results = self.vector.search(current_task, top_k=2)
            if results:
                lines = [f"- {r['text'][:300]}" for r in results]
                parts.append(
                    "## Relevant past work\n"
                    "(From previous tasks — use as background if relevant)\n"
                    + "\n".join(lines)
                )

        # Tier 3: Known facts
        recent_facts = self.facts.get_recent(5)
        if recent_facts:
            parts.append(
                "## Known facts from this session\n"
                + "\n".join(f"- {f}" for f in recent_facts)
            )

        if not parts:
            return ""

        return (
            "=== NEXUS Memory Context ===\n"
            + "\n\n".join(parts)
            + "\n=== End of Memory Context ===\n"
        )

    def store_task(self, task: str, report: str):
        """
        After a task completes:
        1. Add task + report summary to session history
        2. Store report in FAISS vector store
        3. Extract and store key facts
        """
        self.session.add("user", task)
        self.session.add("assistant", report[:600])
        combined = f"Task: {task}\n\nReport summary: {report[:600]}"
        self.vector.add(combined, source="task_report", meta={"task": task[:80]})
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._extract_facts(task, report))
        except Exception:
            pass

    async def _extract_facts(self, task: str, report: str):
        """Extract key technical facts from the report and store them."""
        prompt = (
            f"Task: {task}\n\n"
            f"Report (first 600 chars): {report[:600]}\n\n"
            "List 2-3 key technical facts or decisions from this report as a JSON array.\n"
            "Example: [\"The RAG pipeline uses FAISS with cosine similarity\", \"Chunk size is 512 tokens\"]\n"
            "Return ONLY the JSON array."
        )
        try:
            result = await PRIMARY_MODEL.create(
                messages=[
                    SystemMessage(content="Extract key facts. Return only a JSON array of strings."),
                    UserMessage(content=prompt, source="user"),
                ],
            )
            text = str(result.content).strip()
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()
            m = re.search(r'\[.*\]', text, re.DOTALL)
            if m:
                facts = json.loads(m.group())
                for fact in facts:
                    if isinstance(fact, str) and fact.strip():
                        self.facts.add(fact.strip(), source_task=task[:60])
        except Exception:
            pass

    def clear_session(self):
        """Clear session history only — vector store and facts persist."""
        self.session.clear()

    def reset_all(self):
        """Wipe everything including vector store and facts."""
        self.session.clear()
        self.vector.reset()
        self.facts.clear()

    def status(self) -> dict:
        return {
            "session_turns":  len(self.session),
            "vector_entries": self.vector.count(),
            "facts_stored":   len(self.facts.get_all()),
        }