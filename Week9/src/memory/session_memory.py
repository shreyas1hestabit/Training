"""
memory/session_memory.py
------------------------
SHORT-TERM MEMORY — lives only for the current Python process session.

Stores the rolling conversation history (user + assistant turns) and
exposes helpers to build a trimmed context window for the LLM prompt.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ---------------------------------------------------------------------------
# Session Memory
# ---------------------------------------------------------------------------

class SessionMemory:
    """
    Holds the current conversation as a list of Message objects.

    Parameters
    ----------
    max_turns : int
        Maximum number of TURNS (one user + one assistant = 1 turn) to keep
        in the window. Older turns are dropped when the limit is exceeded.
        Default: 10 turns (20 messages).
    system_prompt : str | None
        Optional system prompt injected at position 0 of every context build.
    """

    def __init__(self, max_turns: int = 10, system_prompt: str | None = None):
        self.max_turns = max_turns
        self.system_prompt = system_prompt
        self._messages: list[Message] = []

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add(self, role: Literal["user", "assistant"], content: str) -> None:
        """Append a message and trim to window size."""
        self._messages.append(Message(role=role, content=content))
        self._trim()

    def _trim(self) -> None:
        """Keep only the most recent max_turns * 2 messages."""
        limit = self.max_turns * 2
        if len(self._messages) > limit:
            self._messages = self._messages[-limit:]

    def clear(self) -> None:
        """Wipe the session (e.g. when user types 'new chat')."""
        self._messages.clear()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_context(self) -> list[dict]:
        """
        Return messages as a list of dicts ready for the LLM API.
        Injects the system prompt at position 0 if one was set.

        Returns
        -------
        list[dict]  e.g. [{"role": "user", "content": "..."}, ...]
        """
        ctx = []
        if self.system_prompt:
            ctx.append({"role": "system", "content": self.system_prompt})
        for m in self._messages:
            ctx.append({"role": m.role, "content": m.content})
        return ctx

    def get_history_text(self) -> str:
        """
        Return a plain-text transcript of the conversation.
        Useful for summarisation and long-term memory extraction.
        """
        lines = []
        for m in self._messages:
            prefix = "User" if m.role == "user" else "Assistant"
            lines.append(f"[{prefix}] {m.content}")
        return "\n".join(lines)

    def last_n_text(self, n: int = 4) -> str:
        """Return the last n messages as plain text (for quick context injection)."""
        recent = self._messages[-n:]
        lines = []
        for m in recent:
            prefix = "User" if m.role == "user" else "Assistant"
            lines.append(f"[{prefix}] {m.content}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return f"SessionMemory(messages={len(self._messages)}, max_turns={self.max_turns})"