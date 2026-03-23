# MEMORY-SYSTEM.md — Day 4: Memory Systems

## The Three Memory Tiers

### Tier 1 — Session Memory (`session_memory.py`)

**Type:** Short-term / Episodic
**Storage:** Python list in RAM
**Lifetime:** Current process only — lost on exit or `/clear`

Holds the rolling conversation as `Message` objects (role, content, timestamp).
A configurable window (`max_turns=10`) keeps only the most recent 20 messages,
dropping older ones automatically.

---

### Tier 2 — Long-Term Memory (`long_term_memory.py`)

**Type:** Semantic facts + Episodic summaries
**Storage:** SQLite (`memory/long_term.db`)
**Lifetime:** Persistent across all sessions

Three tables:

| Table        | Contents                                                   |
| ------------ | ---------------------------------------------------------- |
| `facts`      | Key/value pairs extracted from user messages               |
| `episodes`   | LLM-generated 2-sentence summaries of past conversations   |
| `recall_log` | Audit trail — every memory retrieval logged with timestamp |

```python
ltm = LongTermMemory()

# Facts
ltm.save_fact("user_name", "User name is Shreya", source="user")
ltm.get_fact("user_name")           # "User name is Shreya"
ltm.get_all_facts()                 # {"user_name": "User name is Shreya", ...}
ltm.search_facts("Shreya")          # keyword search across keys and values
ltm.delete_fact("user_name")

# Episodes
ltm.save_episode("Shreya introduced herself as a software engineer trainee at HestaBit.")
ltm.get_recent_episodes(n=5)        # last 5 episode summaries

# Stats
ltm.stats()  #  {"facts": 7, "episodes": 1, "recall_log": 64}
```

**SQLite schema:**

```sql
CREATE TABLE facts (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    key     TEXT NOT NULL,           -- slugified fact key
    value   TEXT NOT NULL,           -- full fact string (third person)
    source  TEXT,                    -- "user" | "conversation"
    created TEXT NOT NULL,
    updated TEXT NOT NULL
);

CREATE TABLE episodes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT NOT NULL,           -- 2-sentence LLM summary
    raw     TEXT,                    -- full transcript
    created TEXT NOT NULL
);

CREATE TABLE recall_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    query       TEXT NOT NULL,
    memory_type TEXT NOT NULL,       -- "vector" | "fact" | "episode"
    memory_id   INTEGER,
    recalled_at TEXT NOT NULL
);
```

---

### Tier 3 — Vector Memory (`vector_store.py`)

**Type:** Semantic / Similarity-based recall
**Storage:** FAISS flat L2 index (`memory/faiss.index`) + JSON metadata
**Lifetime:** Persistent — saved to disk after every write
**Embedding model:** `all-MiniLM-L6-v2` (384 dimensions, ~22 MB, downloads once)

Finds semantically related memories even when keywords don't match. Searching
`"what do you know about my job?"` can retrieve `"User is a software engineer trainee"`
without the word "job" appearing in the stored fact.

```python
store = VectorStore()

# Store
store.add("User name is Shreya", source="fact")
store.add_batch(["fact one", "fact two"], source="batch")

# Search
results = store.search("what is the user's name?", top_k=3)
for r in results:
    print(r["score"], r["text"])
# 0.31  User name is Shreya

# Format for prompt injection
ctx = store.format_context(results)
# "[Memory 1 | source: fact] User name is Shreya\n..."

store.count()                        # number of stored entries
store.delete_by_source("episode")    # remove all episode entries
store.reset()                        # wipe everything
```

**L2 distance guide:**

| Score   | Meaning                                      |
| ------- | -------------------------------------------- |
| < 0.5   | Highly relevant                              |
| 0.5–1.2 | Related                                      |
| 1.2–2.0 | Loosely related (still retrieved by default) |
| > 2.0   | Filtered out                                 |

---

## Full Per-Turn Pipeline

```
User message
      │

┌---------------------┐
│  Session Memory     │  Add user message to rolling window
└---------------------┘
           │

┌---------------------┐
│  _retrieve_context  │  1. FAISS semantic search (top-K similar facts/episodes)
│                     │  2. If ≤10 facts in SQLite → inject ALL facts
│                     │     If >10 facts → keyword search on relevant words
└---------------------┘
           │

┌---------------------┐
│  _build_messages    │  System: behaviour rules + known facts
│                     │  User:   [Context block with facts] + conversation history
└---------------------┘
           │

┌---------------------┐
│  LLM (temp=0.1)     │  Generate grounded response
└---------------------┘
           │

┌---------------------┐
│  Session Memory     │  Add assistant response to rolling window
└---------------------┘
           │

┌---------------------┐
│  _extract_facts     │  Isolated LLM call (temp=0, no history passed)
│  (temp=0)           │  Returns JSON array of third-person facts
│                     │  ->saved to SQLite + FAISS
└---------------------┘
           │
            (every 6 turns)
┌---------------------┐
│  _summarise_and_    │  LLM generates 2-sentence episode summary
│  _store             │  -> saved to SQLite episodes + FAISS
└---------------------┘
```

---

## Fact Extraction Design

After each user message, a **fully isolated** LLM call extracts facts:

- Only the raw user message is passed — no conversation history, no context
- `temperature=0` for deterministic, non-creative output
- Facts stored in **third person** to avoid pronoun confusion when recalled
- Apostrophes avoided in fact text to prevent JSON parse errors

```
User says: "I am a software engineer trainee at HestaBit"

Fact extractor receives ONLY: "I am a software engineer trainee at HestaBit"

Returns: [
  "User is a software engineer trainee",
  "User works at HestaBit"
]
```

Facts skipped when:

- Message is a question (ends with `?`)
- Message is fewer than 3 words

---

## Memory Retrieval Strategy

The retrieval uses a dual approach to ensure nothing is missed:

**For small fact stores (≤10 facts):** All facts are always injected into the prompt.
This guarantees the agent never misses a relevant fact due to poor similarity scores,
which is especially important early in a session when the vector index has few entries.

**For large fact stores (>10 facts):** Multi-keyword search over SQLite combined with
FAISS semantic search. Keywords shorter than 4 characters are ignored to reduce noise.

Facts are injected as a `[Context]` block inside the **user turn** (not just the system
message) — models follow user-turn grounding more reliably than system instructions,
which reduces hallucination of unknown company names and proper nouns.

---

## Chat Loop Commands

| Command       | Action                                                                                |
| ------------- | ------------------------------------------------------------------------------------- |
| `/memory`     | Show live memory status — session messages, vector entries, SQLite counts, turn count |
| `/facts`      | List all facts stored in SQLite                                                       |
| `/episodes`   | List 5 most recent episode summaries                                                  |
| `/clear`      | Wipe session memory — long-term and vector store intact                               |
| `/reset`      | Wipe session + vector store — SQLite intact                                           |
| `/wipe-facts` | Delete all facts from SQLite and vector store                                         |
| `exit`        | Quit                                                                                  |

---

## Logging (`logs_day4.json`)

Every turn and every command is appended to `logs_day4.json`:

**Chat turn entry:**

```json
{
  "timestamp": "2026-03-23T12:48:01.336095",
  "user_input": "I work at HestaBit.",
  "agent_response": "Hello Shreya! How can I help with your work at HestaBit?",
  "memory_snapshot": {
    "session_messages": 4,
    "vector_entries": 2,
    "sqlite_facts": 2,
    "sqlite_episodes": 0,
    "turn_count": 2
  },
  "recalled_memories": [
    {
      "text": "User name is Shreya",
      "source": "fact",
      "score": 1.58
    }
  ]
}
```

**Command entry:**

```json
{
  "timestamp": "2026-03-23T12:57:36.398286",
  "command": "/facts",
  "result": {
    "facts": {
      "user_name_is_shreya": "User name is Shreya",
      "user_works_at_hestabit": "User works at HestaBit"
    }
  }
}
```

The `recalled_memories` field shows exactly which FAISS entries were retrieved
for each query, including their similarity scores — useful for debugging retrieval quality.

---

## Episodic vs Semantic Memory

| Type                 | What it stores                 | Module                                               | Example                                                               |
| -------------------- | ------------------------------ | ---------------------------------------------------- | --------------------------------------------------------------------- |
| Short-term           | Active conversation turns      | `session_memory.py`                                  | Last 10 turns                                                         |
| Semantic (facts)     | Explicit user statements       | `long_term_memory.py` (facts) + `vector_store.py`    | "User works at HestaBit"                                              |
| Episodic (summaries) | What happened in past sessions | `long_term_memory.py` (episodes) + `vector_store.py` | "Shreya introduced herself and shared her work on MERN stack and AI." |

---

## Lessons Learned During Development

### Fact extraction must be isolated

Passing conversation history to the fact extractor caused the model to confabulate
facts from the assistant's responses (hallucinated companies, invented hobbies).
The fix: pass only the raw user message with no surrounding context.

### `temperature=0` prevents hallucination in structured tasks

For JSON extraction tasks, temperature 0 produces the most literal output.
For chat responses, temperature 0.1 prevents the model from over-confidently
substituting unknown company names with known ones from training data.

### Facts must be stored in third person

Storing `"I work at HestaBit"` and injecting it back into the prompt confuses the
model — "I" now refers to the assistant. Third-person storage (`"User works at HestaBit"`)
eliminates this ambiguity completely.

### Facts injected in user turn > system message

Models follow user-turn context more literally than system instructions.
Injecting the `[Context]` block in the user message dramatically reduced
hallucinated substitutions for unknown proper nouns.

### Small store = inject everything

FAISS similarity search can miss relevant facts when the index is small and scores
are similar. For stores with 10 or fewer facts, all facts are always injected —
no retrieval logic needed, no misses possible.
