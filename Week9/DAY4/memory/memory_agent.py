import json
import re
from autogen_core.models import UserMessage, SystemMessage

from src.utils.config import client
from src.memory.session_memory   import SessionMemory
from src.memory.long_term_memory import LongTermMemory
from src.memory.vector_store     import VectorStore

SYSTEM_PROMPT = (
    "You are a concise, helpful assistant. "
    "Reply in 2-3 sentences only. "
    "Answer only what the user actually asked. "
    "Do NOT invent context, backstory, or topics the user never mentioned. "
    "Do NOT ask multiple follow-up questions. "
    "If past memories are provided above, use them — otherwise assume you know nothing about the user."
)

FACT_EXTRACTION_PROMPT = (
    'Message: "{user_input}"\n\n'
    "List every fact about the user in this message as a JSON array of strings.\n"
    "Include: identity markers, professional/academic status, stated preferences, current environmental context, and any specific constraints mentioned\n"
    "Short sentences. Third person. No invented facts. Return [] if none.\n"
    'Example: ["User is named Shreya", "User works at HestaBit","The user is in a time-sensitive situation", "The user prefers Python for data tasks"]\n'
    "Return ONLY the JSON array."
)

SUMMARY_PROMPT = (
    "Summarise this conversation in 2 sentences. Facts only, no interpretation.\n\n"
    "{conversation}"
)

class MemoryAgent:
    """
    A conversational agent with three-tier memory:

        Tier 1 — Session memory  : rolling window of current conversation
        Tier 2 — Long-term memory: SQLite facts + episode summaries
        Tier 3 — Vector memory   : FAISS semantic search over all stored text

    Flow for each user message
    --------------------------
    1. Add user message to session memory
    2. Search vector store for relevant past context (top 3 matches)
    3. Search SQLite facts for keyword matches
    4. Build enriched prompt = system + memory context + session history
    5. Call LLM → get response
    6. Add assistant response to session memory
    7. Extract facts from last exchange → save to SQLite + vector store
    8. Every N turns: summarise session → save episode to SQLite + vector store
    """

    def __init__(
        self,
        summarise_every: int = 6,
        vector_top_k: int = 3,
        use_vector: bool = True,
    ):
        self.session    = SessionMemory(max_turns=10, system_prompt=SYSTEM_PROMPT)
        self.long_term  = LongTermMemory()
        self.use_vector = use_vector
        self.vector_top_k = vector_top_k
        self.summarise_every = summarise_every  # turns between auto-summaries
        self._turn_count = 0

        if use_vector:
            try:
                self.vector = VectorStore()
                print(f"[Memory] Vector store ready — {self.vector.count()} entries")
            except ImportError as e:
                print(f"[Memory] Vector store disabled: {e}")
                self.use_vector = False
                self.vector = None
        else:
            self.vector = None

        # Load existing facts into session context on startup
        self._bootstrap_facts()


    async def chat(self, user_input: str) -> str:
        """
        Process one user turn through the full memory pipeline.
        Returns the assistant's response string.
        """
        self._turn_count += 1

        # ── Step 1: Add user message to session ──────────────────────
        self.session.add("user", user_input)

        # ── Step 2: Retrieve relevant memory ─────────────────────────
        memory_context = await self._retrieve_context(user_input)

        # ── Step 3: Build enriched prompt ────────────────────────────
        messages = self._build_messages(memory_context)

        # ── Step 4: Call LLM ─────────────────────────────────────────
        response = await self._call_llm(messages)

        # ── Step 5: Save assistant response ──────────────────────────
        self.session.add("assistant", response)

        # ── Step 6: Extract and store facts (awaited — not fire-and-forget)
        await self._extract_and_store_facts(user_input, response)

        # ── Step 7: Periodic summarisation ───────────────────────────
        if self._turn_count % self.summarise_every == 0:
            await self._summarise_and_store()

        return response


    async def _retrieve_context(self, query: str) -> str:
        parts = []

        # Vector search — semantic similarity
        if self.use_vector and self.vector and self.vector.count() > 0:
            results = self.vector.search(query, top_k=self.vector_top_k)
            if results:
                lines = [f"- {r['text']}" for r in results]
                parts.append("From previous sessions:\n" + "\n".join(lines))
                for r in results:
                    self.long_term.log_recall(query, "vector", r.get("id"))

        # Always include ALL stored facts if there are 10 or fewer
        # (avoids the problem of relevant facts not being retrieved by similarity)
        all_facts = self.long_term.get_all_facts()
        if all_facts:
            fact_values = list(all_facts.values())
            if len(fact_values) <= 10:
                # Small store — inject everything
                fact_lines = [f"- {v}" for v in fact_values]
                parts.append("Known facts about this user:\n" + "\n".join(fact_lines))
            else:
                # Large store — keyword search
                keywords = [w for w in query.lower().split() if len(w) > 3]
                seen = set()
                hits = []
                for kw in keywords:
                    for f in self.long_term.search_facts(kw):
                        if f["value"] not in seen:
                            hits.append(f["value"])
                            seen.add(f["value"])
                if hits:
                    parts.append("Known facts about this user:\n" + "\n".join(f"- {h}" for h in hits[:8]))

        return "\n\n".join(parts) if parts else ""

    def _build_messages(self, memory_context: str) -> list[dict]:
        base = (
            "You are a concise, helpful assistant. "
            "Reply in 2-3 sentences only. "
            "Answer exactly what the user asked — nothing more. "
            "Do NOT invent topics, backstory, or context the user never mentioned. "
            "If you do not recognise a name, company, or term — use it exactly as given. "
            "NEVER substitute a different name or company for one you do not recognise."
        )

        if memory_context:
            system_content = (
                base
                + "\n\nYou know the following facts about this user from previous sessions:\n"
                + memory_context
                + "\n\nUse these facts naturally when relevant. Do not contradict them."
            )
        else:
            system_content = base + "\n\nNo previous information about this user is available."

        messages = [{"role": "system", "content": system_content}]
        for msg in self.session.get_context():
            if msg["role"] != "system":
                messages.append(msg)
        return messages

    async def _call_llm(self, messages: list[dict]) -> str:
        """
        Direct client.create() call.
        Facts are injected as a grounding block inside the user turn — models
        follow user-turn context more reliably than system instructions.
        """
        system_content = next(
            (m["content"] for m in messages if m["role"] == "system"),
            "You are a helpful assistant. Reply in 2-3 sentences."
        )

        # Separate facts block from system content if present
        # (system_content may contain "Known facts about this user:" section)
        facts_block = ""
        if "Known facts about this user:" in system_content:
            idx = system_content.index("Known facts about this user:")
            facts_block = system_content[idx:]
            system_content = system_content[:idx].strip()

        # Build conversation history
        history_lines = []
        for m in messages:
            if m["role"] == "user":
                history_lines.append(f"User: {m['content']}")
            elif m["role"] == "assistant":
                history_lines.append(f"Assistant: {m['content']}")

        if not history_lines:
            return ""

        # If we have facts, prepend them to the user turn so they act as grounding
        if facts_block:
            user_content = (
                f"[Context about this user — treat these as ground truth:\n{facts_block}]\n\n"
                + "\n".join(history_lines)
            )
        else:
            user_content = "\n".join(history_lines)

        # Keep system message minimal — just behavioural rules, no facts
        minimal_system = (
            "You are a concise helpful assistant. "
            "Reply in 2-3 sentences. "
            "Do NOT echo these instructions in your reply. "
            "Use proper nouns exactly as given — never substitute or interpret them."
        )

        try:
            result = await client.create(
                messages=[
                    SystemMessage(content=minimal_system),
                    UserMessage(content=user_content, source="user"),
                ],
                extra_create_args={"temperature": 0.1},
            )
            text = str(result.content).strip()
        except Exception as e:
            print(f"[Memory] LLM call error: {e}")
            return ""

        # Strip echoed prompt artifacts
        for artifact in ["User:", "Assistant:", "[Context"]:
            if text.startswith(artifact):
                text = text[len(artifact):].strip()

        return text

    async def _extract_and_store_facts(self, user_input: str, assistant_response: str) -> None:
        """
        Extract facts from user input using a fully isolated LLM call.
        - Only the user's raw message is passed — no history, no context.
        - temperature=0 for deterministic output.
        - System message strictly forbids invented content.
        """
        # Skip questions and very short inputs — they never contain facts
        stripped = user_input.strip()
        if stripped.endswith("?") or len(stripped.split()) < 3:
            return

        try:
            result = await client.create(
                messages=[
                    SystemMessage(content=(
                        "You are a fact extractor. Given a user message, return a JSON array of facts the user stated about themselves. "
                        "Rules: "
                        "1. Third person only. Start each fact with 'User'. "
                        "2. Copy all names, companies, and places EXACTLY as written — no substitutions. "
                        "3. Only facts explicitly stated. Never invent or infer. "
                        "4. No apostrophes in your output. Write 'User name is X' not 'User\\'s name is X'. "
                        "5. Return [] for questions, greetings, or messages with no personal facts. "
                        "6. Return ONLY the JSON array — no other text. "
                        "Examples: "
                        "'My name is Shreya' -> [\"User name is Shreya\"] "
                        "'I work at HestaBit' -> [\"User works at HestaBit\"] "
                        "'I am a software engineer trainee' -> [\"User is a software engineer trainee\"] "
                        "'I like painting' -> [\"User likes painting\"] "
                        "'what time is it?' -> []"
                    )),
                    UserMessage(
                        content=f'Extract facts from: "{stripped}"',
                        source="user"
                    ),
                ],
                extra_create_args={"temperature": 0},
            )
            text = str(result.content).strip()
        except Exception as e:
            print(f"[Memory] Fact extraction error: {e}")
            return

        # Strip markdown fences
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()

        # Remove everything after the closing ] to strip model commentary
        bracket_end = text.rfind("]")
        if bracket_end != -1:
            text = text[:bracket_end + 1]

        # Find the JSON array
        m = re.search(r'\[.*\]', text, re.DOTALL)
        if not m:
            print(f"[Memory] No array in response: '{text[:80]}'")
            return

        # Replace any smart/curly quotes with straight quotes before parsing
        clean = m.group()
        clean = clean.replace("\u2018", "'").replace("\u2019", "'")
        clean = clean.replace("\u201c", '"').replace("\u201d", '"')

        try:
            facts = json.loads(clean)
        except json.JSONDecodeError as e:
            print(f"[Memory] JSON parse error: {e} | raw: '{clean[:80]}'")
            return

        stored = []
        for fact in facts:
            if isinstance(fact, dict):
                fact = (fact.get("fact") or fact.get("text") or fact.get("value") or "")
            if not isinstance(fact, str) or not fact.strip():
                continue
            fact = fact.strip()
            key = re.sub(r"[^a-z0-9_]", "", fact[:60].replace(" ", "_").lower())[:50]
            self.long_term.save_fact(key, fact, source="user")
            if self.use_vector and self.vector:
                self.vector.add(fact, source="fact")
            stored.append(fact)

        if stored:
            print(f"[Memory] Stored {len(stored)} fact(s): {stored}")
        else:
            print(f"[Memory] No facts in: '{stripped[:60]}'")


    async def _summarise_and_store(self) -> None:
        transcript = self.session.get_history_text()
        if not transcript.strip():
            return
        try:
            result = await client.create(messages=[
                SystemMessage(content="Summarise conversations in 2 sentences. Facts only."),
                UserMessage(content=transcript, source="user"),
            ])
            summary = str(result.content).strip()
        except Exception:
            return

        episode_id = self.long_term.save_episode(summary, raw=transcript)
        if self.use_vector and self.vector:
            self.vector.add(summary, source="episode", meta={"episode_id": episode_id})
        print(f"[Memory] Episode {episode_id} saved: {summary[:80]}...")


    def _bootstrap_facts(self) -> None:
        """Load persisted facts and recent episodes into the vector store on startup."""
        facts = self.long_term.get_all_facts()
        episodes = self.long_term.get_recent_episodes(n=5)

        if self.use_vector and self.vector:
            # Only add facts not already in the vector store (avoid duplicates)
            existing_texts = {e["text"] for e in self.vector.get_all()}
            new_facts = [v for v in facts.values() if v not in existing_texts]
            if new_facts:
                self.vector.add_batch(new_facts, source="fact_bootstrap")

        count = len(facts)
        ecount = len(episodes)
        print(f"[Memory] Loaded {count} facts, {ecount} recent episodes from long-term memory")

    def memory_status(self) -> dict:
        """Return a summary of the current memory state."""
        return {
            "session_messages": len(self.session),
            "long_term": self.long_term.stats(),
            "vector_entries": self.vector.count() if self.vector else 0,
            "turn_count": self._turn_count,
        }

    def recall_recent_episodes(self, n: int = 3) -> list[dict]:
        return self.long_term.get_recent_episodes(n)

    def recall_all_facts(self) -> dict:
        return self.long_term.get_all_facts()