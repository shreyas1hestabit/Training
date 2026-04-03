# AI Agents Learning Project
### Days 1–4: From Single Agents to Memory-Enabled Multi-Agent Systems

A hands-on project building progressively advanced AI agent systems using **AutoGen**, **Ollama** (local LLM), **SQLite**, and **FAISS** — entirely offline, no external API required.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Day 1 — Agent Foundations](#day-1--agent-foundations--message-based-communication)
- [Day 2 — Multi-Agent Orchestration](#day-2--multi-agent-orchestration)
- [Day 3 — Tool-Calling Agents](#day-3--tool-calling-agents)
- [Day 4 — Memory Systems](#day-4--memory-systems)
- [Concept Coverage](#concept-coverage)
- [Key Design Patterns](#key-design-patterns)
- [Configuration Reference](#configuration-reference)

---

## Project Overview

This project is a structured 4-day learning curriculum for building AI agent systems from first principles. Each day introduces a new layer of capability:

| Day | Topic | What's Built |
|-----|-------|--------------|
| 1 | Agent Foundations | 3 specialized agents in a sequential pipeline |
| 2 | Multi-Agent Orchestration | Planner → parallel Workers → Validator DAG |
| 3 | Tool-Calling Agents | File, database, and code-execution agents |
| 4 | Memory Systems | 3-tier persistent memory (session + SQLite + FAISS) |

Every component runs **fully locally** using Ollama — no OpenAI API key, no cloud calls, no data leaves your machine.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent framework | `autogen-agentchat` | Agent creation, tool calling, group chat |
| LLM runtime | Ollama | Local model inference |
| LLM client | `autogen-ext[openai]` | OpenAI-compatible client pointed at Ollama |
| Vector search | `faiss-cpu` | Semantic similarity search |
| Embeddings | `sentence-transformers` | Text → 384-dim vectors |
| Persistent memory | SQLite (`sqlite3`) | Facts, episodes, recall audit log |
| Data manipulation | `pandas`, `numpy` | CSV/DataFrame operations in tools |
| Config | `python-dotenv` | Environment variable management |

---

## Project Structure

```
project/
├── .env                          # LLM config (model name, Ollama URL, key)
│
├── src/
│   ├── utils/
│   │   └── config.py             # Shared OpenAIChatCompletionClient
│   │
│   ├── day1/
│   │   └── agents/
│   │       ├── research_agent.py
│   │       ├── summarizer_agent.py
│   │       └── answer_agent.py
│   │
│   ├── day2/
│   │   ├── orchestrator/
│   │   │   └── planner.py
│   │   ├── agents/
│   │   │   ├── worker_agent.py
│   │   │   ├── reflection_agent.py
│   │   │   └── validator.py
│   │   └── main.py
│   │
│   ├── day3/
│   │   ├── tools/
│   │   │   ├── file_agent.py     # read_file, write_to_file
│   │   │   ├── db_agent.py       # query_database
│   │   │   └── code_executor.py  # execute_python_code
│   │   ├── data/                 # DATA_DIR — all tool I/O isolated here
│   │   └── main.py
│   │
│   └── day4/
│       ├── memory/
│       │   ├── session_memory.py
│       │   ├── long_term_memory.py
│       │   ├── vector_store.py
│       │   └── memory_agent.py
│       ├── long_term.db          # SQLite database (auto-created)
│       ├── faiss.index           # FAISS binary index (auto-created)
│       ├── vector_metadata.json  # FAISS text labels (auto-created)
│       └── main_v4.py
│
└── logs/
    ├── logs_day2.json
    └── logs_day4.json
```

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed and running
- A pulled model (e.g. `ollama pull llama3.2`)

### Install dependencies

```bash
pip install autogen-agentchat autogen-ext[openai] python-dotenv
pip install pandas numpy faiss-cpu sentence-transformers
```

### Configure `.env`

```env
MODEL_NAME=llama3.2
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama
```

### Verify Ollama is running

```bash
ollama list          # confirm your model is available
ollama serve         # start the server if not already running
```

---

## Day 1 — Agent Foundations + Message-Based Communication

### What it does

Three specialized agents in a fixed sequential pipeline. Each agent has a unique role, unique system prompt, and a 10-message memory window.

```
User → Research Agent → raw bullet facts
     → Summarizer Agent → exactly 3 bullets
     → Answer Agent → polished response
```

### Key concepts introduced

- **Agentic loop** — perception → reasoning → action
- **Role-based intelligence modelling** — system prompt defines agent identity and behavior
- **Message protocol** — `{"role": ..., "content": ...}` structure
- **Memory window** — `BufferedChatCompletionContext(buffer_size=10)` simulates short-term memory
- **Role isolation** — each agent is forbidden from doing another agent's job
- **Chain-of-thought isolation** — separate `model_context` per agent

### Files

| File | Agent Name | Role |
|------|-----------|------|
| `research_agent.py` | Researcher | Finds facts, outputs bullet points, guards against hallucination |
| `summarizer_agent.py` | Summarizer | Compresses to exactly 3 bullets, passes through error signals |
| `answer_agent.py` | AnswerBot | PR interface — wraps bullets in professional greeting and closing |

### LLM parameters (all agents)

```python
extra_kwargs={
    "temperature": 0,       # deterministic output
    "top_p": 0.1,           # conservative token sampling
    "max_tokens": 800,      # prevents runaway responses
    "repeat_penalty": 1.2,  # stops looping behavior in local models
    "seed": 42              # reproducible results
}
```

### Run

```python
# No dedicated main.py for Day 1 — agents are imported and chained manually
from src.day1.agents.research_agent import research_agent
from src.day1.agents.summarizer_agent import summarizer_agent
from src.day1.agents.answer_agent import answer_agent

res1 = await research_agent.run(task="Who is Nikola Tesla?")
res2 = await summarizer_agent.run(task=str(res1.messages[-1].content))
res3 = await answer_agent.run(task=str(res2.messages[-1].content))
print(res3.messages[-1].content)
```

---

## Day 2 — Multi-Agent Orchestration

### What it does

A 4-agent DAG (Directed Acyclic Graph) architecture. A Planner breaks the user query into independent subtasks, Workers execute them in parallel, a Reflection agent synthesizes the results, and a Validator checks quality.

```
User Query
    ↓
Planner  (creates TASK: lines)
    ↓
re.findall() extracts tasks
    ↓
asyncio.gather() → [Worker 1 | Worker 2 | Worker 3]  ← parallel
    ↓
detailed_audit[ ]  (blackboard — all outputs collected here)
    ↓
Reflection Agent  (merges, cleans, synthesizes)
    ↓
Validator Agent  (VALIDATED or REJECTED + reasons)
    ↓
Final answer + saved to logs_day2.json
```

### Key concepts introduced

- **DAG execution** — tasks at the same level run in parallel, no circular dependencies
- **Planner–Executor–Validator pattern** — strict separation of planning, doing, and checking
- **Parallel execution** — `asyncio.gather()` runs all workers simultaneously
- **Blackboard memory** — `detailed_audit` list is the shared space workers write to
- **Hierarchical orchestration** — fixed chain of command: Planner → Workers → Reflection → Validator
- **Regex extraction** — `re.findall(r"TASK:\s*(.*)", plan_text)` bridges LLM text to structured data
- **Task delegation** — Planner delegates to Workers via extracted task strings

### Files

| File | Agent | Role |
|------|-------|------|
| `orchestrator/planner.py` | Planner | Breaks query into 1-3 independent TASK: lines |
| `agents/worker_agent.py` | Worker | Executes one assigned task, no invented statistics |
| `agents/reflection_agent.py` | Reflector | Merges worker outputs into one coherent response |
| `agents/validator.py` | Validator | Checks final answer against original query |
| `main.py` | Orchestrator | Runs all 4 phases, logs to JSON |

### Planner output format (strict)

```
TASK: [Specific Instruction]
TASK: [Specific Instruction]
TASK: [Specific Instruction]
```

If the Planner deviates from this format, `re.findall()` returns an empty list and the fallback fires:
```python
if not tasks:
    tasks = [f"Directly address: {user_query}"]
```

### Parallel worker execution

```python
async def run_single_worker(i, task_desc):
    res = await worker_agent.run(task=contextual_prompt)
    return {
        "worker_id": i + 1,
        "assigned_task": task_desc,
        "output": str(res.messages[-1].content),
        "duration": round(time.time() - start_time, 2)
    }

detailed_audit = await asyncio.gather(
    *[run_single_worker(i, t) for i, t in enumerate(tasks)]
)
```

### Run

```bash
cd src/day2
python main.py
```

---

## Day 3 — Tool-Calling Agents

### What it does

Three agents that can act on the real world — reading and writing files, querying and modifying SQLite databases, and executing arbitrary Python code. A `SelectorGroupChat` dynamically routes each turn to the right agent based on a decision table.

```
User Query
    ↓
SelectorGroupChat (selector_prompt decision table)
    ↓ (picks agent dynamically each turn)
┌─────────────┐  ┌─────────────┐  ┌─────────────────┐
│ File_Manager│  │  DB_Admin   │  │  Code_Analyst   │
│ read_file   │  │ query_db    │  │ execute_python  │
│ write_file  │  │             │  │                 │
└──────┬──────┘  └──────┬──────┘  └────────┬────────┘
       └─────────────────┴──────────────────┘
                         ↓
                    DATA_DIR boundary
                 /src/day3/data/ only
                         ↓
              TextMentionTermination("TERMINATE")
                         ↓
               result.messages[-1].content
```

### Key concepts introduced

- **Tool calling** — LLM generates JSON tool call requests, AutoGen runs the Python function, result injected back
- **SelectorGroupChat** — dynamic routing via LLM decision table, not fixed pipeline
- **`description=` parameter** — metadata the selector reads to decide which agent fits
- **`selector_prompt`** — hard routing rules replacing LLM guesswork
- **DATA_DIR isolation** — filesystem boundary (separate from Python import system)
- **`exec()` sandbox** — `exec_globals` whitelist controls what LLM-generated code can access
- **Swarm orchestration** — agents are peers, lateral delegation via system prompts
- **Path traversal prevention** — `os.path.basename()` strips directory components from user-supplied paths

### Files

| File | Tools Exposed | Restriction |
|------|--------------|-------------|
| `tools/file_agent.py` | `read_file`, `write_to_file` | Reads any file, writes <10 rows manually |
| `tools/db_agent.py` | `query_database` | SQLite only, one statement per call |
| `tools/code_executor.py` | `execute_python_code` | `exec()` with `pd`, `np`, `sqlite3`, `os` whitelisted |
| `main.py` | — | Sets DATA_DIR on all modules, builds agents and team |

### DATA_DIR injection (late binding pattern)

```python
# Tool files declare empty DATA_DIR at module level:
DATA_DIR = ""   # in file_agent.py, db_agent.py, code_executor.py

# main.py sets the real path at runtime:
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")

file_tool.DATA_DIR = DATA_DIR   # sets module attribute directly
db_tool.DATA_DIR   = DATA_DIR
code_tool.DATA_DIR = DATA_DIR
```

> **Note:** `DATA_DIR` is a filesystem restriction only. It does not affect Python imports. `src/utils/config.py` is accessible via normal Python imports regardless of DATA_DIR.

### Selector routing rules

```
Write/run code, scripts, programs    → Code_Analyst
Calculate, compute (factorial, etc.) → Code_Analyst
Generate data, bulk insert (>5 rows) → Code_Analyst
CSV modify/append/update/add columns → Code_Analyst
Convert CSV ↔ DB                     → Code_Analyst
SQL query, schema check, single-row  → DB_Admin
Simple file read, small manual write → File_Manager
Unsure                               → Code_Analyst  (safe default)
```

### Run

```bash
cd src/day3
python main.py
# Query (or 'exit'): Analyze sales.csv and generate top 5 insights
```

---

## Day 4 — Memory Systems

### What it does

A single `MemoryAgent` with three-tier persistent memory. The agent remembers facts, conversation episodes, and semantically similar context across sessions — even after restarting the program.

```
User message
    ↓
Step 1  session.add(user_input)              [Tier 1 — RAM]
Step 2  _retrieve_context()
            ├── FAISS semantic search         [Tier 3 — read]
            └── SQLite facts (all or keyword) [Tier 2 — read]
Step 3  _build_messages()
            system rules + memory_context + session history
Step 4  _call_llm() → response
Step 5  session.add(response)                [Tier 1 — RAM]
Step 6  _extract_and_store_facts()
            isolated LLM call (temp=0)
            ├── SQLite save_fact()            [Tier 2 — write]
            └── FAISS add()                  [Tier 3 — write]
Step 7  every 6 turns: _summarise_and_store()
            isolated LLM call
            ├── SQLite save_episode()         [Tier 2 — write]
            └── FAISS add(summary)           [Tier 3 — write]
    ↓
Response returned to user
```

### The Three Memory Tiers

| Tier | Technology | Scope | Persists? | Search type |
|------|-----------|-------|-----------|-------------|
| Session | `SessionMemory` (`_messages` list) | Current conversation only | No — lost on exit | None (rolling window) |
| Long-term | SQLite `long_term.db` | All sessions | Yes | Keyword / full scan |
| Vector | FAISS `faiss.index` | All sessions | Yes | Semantic similarity (L2 distance) |

### SQLite Schema (`long_term.db`)

```sql
-- Semantic memory: one canonical fact per key (upsert pattern)
CREATE TABLE facts (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    key     TEXT NOT NULL,      -- normalized lookup key
    value   TEXT NOT NULL,      -- human-readable sentence injected into prompts
    source  TEXT,               -- "user" or "episode"
    created TEXT NOT NULL,
    updated TEXT NOT NULL
);

-- Episodic memory: 2-sentence summaries generated every 6 turns
CREATE TABLE episodes (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT NOT NULL,      -- LLM-generated summary
    raw     TEXT,               -- full transcript (optional)
    created TEXT NOT NULL
);

-- Audit trail: every FAISS retrieval event logged here
CREATE TABLE recall_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    query       TEXT NOT NULL,
    memory_type TEXT NOT NULL,  -- "vector" | "fact" | "episode"
    memory_id   INTEGER,        -- cross-reference to vector_metadata.json index
    recalled_at TEXT NOT NULL
);
```

### FAISS Storage (`faiss.index` + `vector_metadata.json`)

Two files must always stay in sync — position N in `faiss.index` always corresponds to `_metadata[N]`:

```
faiss.index (binary — unreadable as text):
  position 0: [0.023, -0.142, 0.089, ...]   ← 384 float32 numbers
  position 1: [0.187,  0.091, -0.044, ...]
  position 2: [-0.04,  0.231,  0.156, ...]
  ...

vector_metadata.json (readable JSON):
  [
    {"id": 0, "text": "User name is Shreya",         "source": "fact",    "meta": {}},
    {"id": 1, "text": "User works at HestaBit",      "source": "fact",    "meta": {}},
    {"id": 2, "text": "User is a software engineer", "source": "fact",    "meta": {}},
    {"id": 3, "text": "Episode 1 summary...",        "source": "episode", "meta": {"episode_id": 1}}
  ]
```

Embedding model: `all-MiniLM-L6-v2` (22MB, 384 dimensions, runs locally)

### How semantic search works

```
Query: "What do you know about my job?"
  ↓
model.encode() → [0.14, -0.09, 0.31, ...]  (384 numbers)
  ↓
FAISS computes L2 distance to every stored vector:
  "User works at HestaBit"              → distance 0.43  ← close (job-related)
  "User is a software engineer trainee" → distance 0.61  ← close
  "User loves painting"                 → distance 1.95  ← distant
  "User name is Shreya"                 → distance 1.82  ← distant
  ↓
Returns top_k=3 results below score_threshold=2.0
```

Distance 0 = identical. Distance ~2.0 = loosely related. Above 2.0 = filtered out.

### Bootstrap on startup

Every time `MemoryAgent()` is created, `_bootstrap_facts()` runs:

```python
def _bootstrap_facts(self) -> None:
    facts = self.long_term.get_all_facts()          # read from SQLite
    existing_texts = {e["text"] for e in self.vector.get_all()}  # read from FAISS
    new_facts = [v for v in facts.values() if v not in existing_texts]
    if new_facts:
        self.vector.add_batch(new_facts, source="fact_bootstrap")
```

This syncs SQLite → FAISS on startup. If `faiss.index` is deleted or corrupted, all facts are re-embedded from SQLite automatically.

### Files

| File | Responsibility |
|------|---------------|
| `memory/session_memory.py` | Rolling message window, `Message` dataclass, `get_context()`, `get_history_text()` |
| `memory/long_term_memory.py` | SQLite CRUD for facts, episodes, recall_log. Upsert pattern for facts. |
| `memory/vector_store.py` | FAISS index management. `add()`, `search()`, `add_batch()`, `delete_by_source()` |
| `memory/memory_agent.py` | Orchestrates all 3 tiers. 7-step `chat()` pipeline. Fact extraction. Summarization. |
| `main_v4.py` | REPL loop, `/commands`, turn logging to JSON |

### Available commands

```
/memory      — show counts: session messages, vector entries, SQLite facts/episodes
/facts       — print all stored facts
/episodes    — print 5 most recent episode summaries
/clear       — wipe session memory (long-term intact)
/wipe-facts  — delete all facts from SQLite AND FAISS (both must be cleared together)
exit         — quit
```

### Run

```bash
cd src/day4
python main_v4.py
```

---

## Concept Coverage

| Concept | Day 1 | Day 2 | Day 3 | Day 4 |
|---------|-------|-------|-------|-------|
| Agentic system architecture | full | full | full | full |
| Single → multi-agent | single | multi | multi (swarm) | single+ |
| Role-based intelligence | full | full | full | full |
| Planner–Executor–Validator | partial | **full** | partial | partial |
| Tool-using agents | none | none | **full** | none |
| Multi-agent communication | basic (linear) | full (broadcast) | full (routed) | basic (internal) |
| Memory — short term | window | none | window | **all 3 tiers** |
| Memory — long term | none | none | none | **full** |
| Swarm orchestration | none | none | **full** | none |
| Hierarchical orchestration | none | **full** | none | none |
| Local AI automation | full | full | full | full |
| Message passing | linear | broadcast | routed | pipeline |
| State machine | implicit | phase-based | selector | turn-based |
| Blackboard memory | none | **full** | shared ctx | 3-tier |
| Chain-of-thought isolation | full | full | full | full |
| Role control | basic | full | **3-layer** | full |
| Task delegation | none | top-down | lateral | none |

---

## Key Design Patterns

### 1. Late binding for module-level config
Tool modules declare `DATA_DIR = ""`. `main.py` sets the real value after import.
Allows tools to be used independently without knowing the project's directory structure at module load time.

### 2. Upsert for facts
`save_fact()` does SELECT first, then UPDATE or INSERT based on result.
Ensures one canonical value per key — facts update rather than duplicate across sessions.

### 3. Error passthrough signals
`DATA NOT FOUND` passes from Research → Summarizer → Answer without modification.
`MISSION DISPOSIBLE` triggers a special response in Answer agent.
Clean failure propagation — downstream agents know not to process a bad upstream result.

### 4. Isolated LLM calls for extraction
Fact extraction and summarization use completely separate LLM calls with no conversation history.
Prevents the extractor from being influenced by conversation context and inventing facts.

### 5. FAISS + metadata parallel files
FAISS stores binary vectors. A parallel JSON file stores text labels.
Position N in `faiss.index` always equals index N in `vector_metadata.json`. This invariant must never break — FAISS deletion requires full index rebuild to preserve it.

### 6. Graceful degradation
Vector store is optional. If `faiss-cpu` or `sentence-transformers` is not installed, `MemoryAgent` disables vector search and falls back to SQLite keyword search only.

```python
try:
    self.vector = VectorStore()
except ImportError as e:
    print(f"[Memory] Vector store disabled: {e}")
    self.use_vector = False
    self.vector = None
```

### 7. `asyncio.sleep(1)` before each team run
Prevents rate limiting on cloud LLMs. Uses `await asyncio.sleep` (not `time.sleep`) to yield control to the event loop rather than blocking the entire process.

---

## Configuration Reference

### `.env` variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `MODEL_NAME` | `llama3.2` | Model pulled in Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Redirects OpenAI client to local Ollama |
| `OLLAMA_API_KEY` | `ollama` | Required by client protocol even though Ollama ignores it |

### LLM parameters

| Parameter | Value | Effect |
|-----------|-------|--------|
| `temperature` | `0` | Fully deterministic output |
| `top_p` | `0.1` | Limits token pool to top 10% probability mass |
| `max_tokens` | `800` | Hard cap on response length |
| `repeat_penalty` | `1.2` | Prevents looping behavior in local models |
| `seed` | `42` | Reproducible results across runs |

### Memory parameters (Day 4)

| Parameter | Default | Effect |
|-----------|---------|--------|
| `max_turns` | `10` | Session memory window (10 turns = 20 messages) |
| `summarise_every` | `6` | Turns between automatic episode summarization |
| `vector_top_k` | `3` | Number of FAISS results to retrieve per query |
| `score_threshold` | `2.0` | L2 distance cutoff — results above this are filtered out |
| `use_vector` | `True` | Enable/disable FAISS semantic search |

---

## Notes

- All LLM calls go to `localhost` via Ollama. No data leaves the machine.
- `long_term.db`, `faiss.index`, and `vector_metadata.json` are created automatically on first run of Day 4.
- The `data/` directory in Day 3 is created automatically by `os.makedirs(DATA_DIR, exist_ok=True)`.
- Logs are append-only JSON files. Each run adds to the existing file rather than overwriting.
- The `recall_log` table in SQLite records every FAISS retrieval event. It is an audit trail for debugging — it does not affect agent behavior.
