# FINAL REPORT — WEEK 9: AGENTIC AI & MULTI-AGENT SYSTEM DESIGN

**Author:** Shreyas Singhal  
**Bootcamp:** AI Systems Engineering — Week 9  
**Framework:** AutoGen (AgentChat stable API — `autogen_agentchat`, `autogen_ext`, `autogen_core`)  
**Models:** `llama3.2` via Ollama (Days 1–4) · `llama-3.3-70b-versatile` / `llama-3.1-8b-instant` via Groq (Days 2–5)  
**Date:** March 2026

---

## Table of Contents

1. [Week Overview](#1-week-overview)
2. [Tech Stack](#2-tech-stack)
3. [Day 1 — Agent Foundations & Message-Based Communication](#3-day-1--agent-foundations--message-based-communication)
4. [Day 2 — Multi-Agent Orchestration](#4-day-2--multi-agent-orchestration)
5. [Day 3 — Tool-Calling Agents](#5-day-3--tool-calling-agents)
6. [Day 4 — Memory Systems](#6-day-4--memory-systems)
7. [Day 5 — Capstone: NEXUS AI](#7-day-5--capstone-nexus-ai)
8. [Full Project Structure](#8-full-project-structure)
9. [Week Completion Criteria](#9-week-completion-criteria)

---

## 1. Week Overview

Week 9 covered the design and implementation of autonomous multi-agent AI systems from first principles. Starting with a single pipeline of three sequential agents and building up to a fully autonomous nine-agent system with memory, planning, tool use, self-reflection, and failure recovery, the week produced five progressively complex deliverables — each day building directly on the work of the previous one.

The core philosophy throughout was strict **role isolation**: every agent has a single responsibility, a unique system prompt, and is forbidden from performing the work of any other agent. This ensures predictable, debuggable behaviour across multi-agent pipelines.

---

## 2. Tech Stack

| Component             | Technology                                                               |
| --------------------- | ------------------------------------------------------------------------ |
| Agent framework       | `autogen_agentchat` (stable), `autogen_ext`, `autogen_core`              |
| LLM inference (local) | Ollama — `llama3.2`                                                      |
| LLM inference (cloud) | Groq API — `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`             |
| Vector memory         | FAISS (`faiss-cpu`) + `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| Long-term memory      | SQLite3 (built-in Python)                                                |
| Session memory        | Custom Python dataclass (`SessionMemory`)                                |
| Database tool         | SQLite3 with read-only security guard                                    |
| Code execution        | Isolated `exec()` namespace with blocked-pattern security                |
| File tool             | `.csv` / `.txt` read/write restricted to `data/` directory               |
| Logging               | Per-day JSON log files + structured per-agent trace                      |
| Config                | `python-dotenv`, auto-selects Groq or Ollama from environment            |

---

## 3. Day 1 — Agent Foundations & Message-Based Communication

### Objective

Understand the Perception → Reasoning → Action loop by building three single-purpose agents that pass messages in a strict linear chain.

### What Was Built

#### `src/agents/research_agent.py`

A fact-reporting agent built on `AssistantAgent` with a `BufferedChatCompletionContext(buffer_size=10)` memory window — meeting the spec's "memory window = 10" requirement exactly.

Key design decisions:

- Uses conversation history to resolve pronouns ("he", "it") so follow-up questions work naturally
- Returns `DATA NOT FOUND: Subject unknown` rather than hallucinating when the subject is ambiguous
- Output-only bullet points; ends with `TERMINATE` to signal pipeline completion
- `extra_kwargs` (`temperature=0`, `top_p=0.1`, `repeat_penalty=1.2`, `seed=42`) force deterministic, non-hallucinating output from the local Ollama model

```python
research_agent = AssistantAgent(
    name="Researcher",
    model_client=client,
    system_message="""Task: Fact Reporter.
    1. Use previous conversation history to identify subjects.
    2. If subject is unclear, say 'DATA NOT FOUND: Subject unknown'.
    3. DO NOT invent fake biographies.
    4. Provide ONLY bullet points. End with TERMINATE.""",
    model_context=BufferedChatCompletionContext(buffer_size=10),
)
```

#### `src/agents/summarizer_agent.py`

Accepts raw research output and condenses it to **exactly 3 bullet points** — no more, no less. Passes the `DATA NOT FOUND` error signal through unchanged, preserving the error contract across the pipeline.

#### `src/agents/answer_agent.py`

A PR Interface agent that wraps the summary in a professional greeting and closing. Enforces a hard pass-through rule: if input contains `MISSION DISPOSIBLE` or `NO DATA FOUND`, it replies with only that phrase and nothing else — no greetings, no apologies.

#### `main.py` — The Three-Agent Pipeline

Sequential orchestrator that runs all three agents, times each step, and logs every run:

```
User Query
    ↓ (ResearcherAgent)  raw bullet facts     → r_time
    ↓ (SummarizerAgent)  3-bullet condensed   → s_time
    ↓ (AnswerAgent)      polished response    → f_time
    ↓
conversation_logs.json  (timestamp, query, per-step output, timings)
```

A `clear` command wipes all three agents' model contexts simultaneously.

### Deliverables

```
src/agents/research_agent.py
src/agents/summarizer_agent.py
src/agents/answer_agent.py
main.py
conversation_logs.json
```

---

## 4. Day 2 — Multi-Agent Orchestration

### Objective

Design an agent hierarchy with dynamic task decomposition, parallel workers, and quality validation — implementing the Planner → Executor → Validator pattern.

### What Was Built

#### `src/utils/config.py` — Shared Model Client

Central configuration module that auto-selects between Groq and Ollama based on whether `GROQ_API_KEY` is present in the environment. All Day 2–5 agents import this single `client` object, eliminating duplication and allowing backend switching without code changes.

```python
if _groq_api_key:
    client = OpenAIChatCompletionClient(model=_groq_model,
                                        base_url="https://api.groq.com/openai/v1", ...)
else:
    client = OpenAIChatCompletionClient(model=_ollama_model,
                                        base_url=_ollama_base_url, ...)
```

#### `src/orchestrator/planner.py` — PlannerAgent

Decomposes any user request into a numbered task list (`TASK 1: ...`, `TASK 2: ...`). Self-instructs to use 1 task for simple requests and enforces a maximum of 5 tasks. The exact `TASK N:` format allows reliable regex extraction in the orchestrator without an additional parsing LLM call.

#### `src/agents/worker_agent.py` — WorkerAgent

A focused task executor with an explicit instruction to operate only on its assigned task — forbidden from importing context from previous conversations or unrelated topics. This isolation is what allows the same worker agent instance to be reused across all tasks in a run without context pollution.

#### `src/agents/validator.py` — ValidatorAgent

A quality-control agent that compares aggregated worker output against the original user request. Checks for: hallucinations (fake citations/DOIs), logic errors, and completeness. Issues `VALIDATED` or `REJECTED` with specific reasons.

#### `main_v2.py` — Dynamic DAG Orchestrator

Three-phase pipeline with detailed execution logging:

```
Phase 1: PlannerAgent         → extract TASK N: lines via regex → cap at 3 for hardware safety
Phase 2: WorkerAgent × N      → sequential execution, timing per worker
Phase 3: ValidatorAgent       → check all combined output against original query
         ↓
logs_day2.json  (worker_id, assigned_task, output, duration per worker)
```

The hardware safety cap (`tasks = tasks[:3]`) was a deliberate engineering decision to protect the local machine from spawning excessive parallel LLM calls.

### Deliverables

```
src/utils/config.py
src/orchestrator/planner.py
src/agents/worker_agent.py
src/agents/validator.py
main_v2.py
logs_day2.json
```

---

## 5. Day 3 — Tool-Calling Agents

### Objective

Build agents that use real tools — Python execution, SQLite querying, and file I/O — and orchestrate them with deterministic routing.

### What Was Built

#### `src/tools/code_executor.py` — Python Code Execution Tool

Executes Python in a sandboxed, isolated `exec()` namespace with multiple layers of protection:

- **Security guard:** regex blocklist rejects `os.remove`, `shutil`, `subprocess`, `sys.exit`
- **`input()` stripping:** replaces `input(...)` calls with `"0"` so generated code never blocks execution
- **Pre-imported stdlib:** `math`, `statistics`, `csv`, `json`, `collections`, `datetime` available without import statements
- **Markdown fence stripping:** cleans LLM output before execution
- **Output logging:** every execution appended to `logs/code_output.txt` with timestamp, code, and output
- **Error recovery:** syntax/runtime errors returned as strings, never raised to the caller

The system prompt instructs the LLM to always use a `main()` function with hardcoded example values and forbids `input()` in generated code — ensuring generated code always runs without interaction.

#### `src/tools/db_agent.py` — SQLite Database Tool

A read-only SQLite interface providing three key functions:

- `query_database(sql)` — executes SQL with a destructive-keyword guard, returns formatted rows with column headers
- `get_schema(table)` — returns column names and up to 5 sample values per column; used to build schema-aware SQL prompts
- `clean_sql(raw)` — strips markdown fences and non-SQL lines from LLM output

The system prompt instructs the LLM to always use `CAST(REPLACE(...))` for currency columns to avoid lexicographic sort errors, and to use `LIKE '%value%' COLLATE NOCASE` for text matching. The orchestrator implements an **auto-retry with LIKE fallback**: if a query returns no rows, it regenerates the SQL with fuzzy matching enabled.

#### `src/tools/file_agent.py` — File Manager Tool

Handles `.csv` and `.txt` files (only) in the `data/` directory. Supports `read`, `write`, and `append`. Validates extension before acting. A `save_analysis_report()` helper appends timestamped analysis reports to a named file — called by the orchestrator at the end of every file/code pipeline run.

#### `main_v3.py` — Tool-Calling Orchestrator with SelectorGroupChat

Four agents orchestrated via `SelectorGroupChat` with a **pure Python deterministic selector** — no LLM call for routing:

| Agent        | Routed when query matches                                 |
| ------------ | --------------------------------------------------------- |
| `DBAgent`    | `database`, `sql`, table keywords, `"in X table"` pattern |
| `CodeAgent`  | `generate code`, `write python`, `save it in *.py`        |
| `FileAgent`  | All other queries (CSV creation, read/write)              |
| `Summariser` | Always called after the specialist agent finishes         |

`CodeAgent` and `DBAgent` are custom `AssistantAgent` subclasses that override `on_messages_stream()` to perform their entire pipeline in Python (LLM call → execute → return result), bypassing AutoGen's tool-call mechanism. This was a deliberate workaround for Groq's strict tool-call JSON format requirements and rate limits.

The code generation pipeline adds **automatic syntax verification and error correction**: if the generated code fails a test run, it is regenerated with the error message appended to the prompt. The final saved file always contains `input()` calls for user interactivity; only the test run uses the `input()` → `"0"` substitution.

### Deliverables

```
src/tools/code_executor.py
src/tools/db_agent.py
src/tools/file_agent.py
main_v3.py
logs/code_output.txt
logs/db_output.txt
logs/file_output.txt
log_day3.json
```

---

## 6. Day 4 — Memory Systems

### Objective

Build a persistent three-tier memory system that stores conversation history, extracts facts, summarises episodes, and recalls relevant context via semantic search.

### What Was Built

#### `src/memory/session_memory.py` — Tier 1: Session Memory

A sliding-window in-session memory using Python `@dataclass`. Stores `Message(role, content, timestamp)` objects. The window is configurable (`max_turns=10` default = 20 messages). Provides three access patterns:

- `get_context()` — dict list for direct LLM API injection
- `get_history_text()` — plain-text transcript for summarisation
- `last_n_text(n)` — quick recent-context injection

#### `src/memory/long_term_memory.py` — Tier 2: Long-Term Memory (SQLite)

Full SQLite persistence with three tables:

```sql
facts      — key/value store (upsert, full-text search, per-key delete)
episodes   — LLM-generated conversation summaries with timestamps
recall_log — audit trail of every memory retrieval (query, type, memory_id)
```

The `facts` table uses upsert semantics: the same key is updated rather than duplicated, keeping facts current. `search_facts(keyword)` provides `LIKE`-based full-text search across both key and value columns.

#### `src/memory/vector_store.py` — Tier 3: Vector Memory (FAISS)

A FAISS `IndexFlatL2` store backed by `sentence-transformers/all-MiniLM-L6-v2`. Key design points:

- `add()` / `add_batch()` — single or bulk embed-and-store
- `search(query, top_k, score_threshold)` — L2 distance semantic search; `score_threshold=2.0` filters loosely-related results
- `delete_by_source(source)` — rebuilds the index from filtered metadata (FAISS flat index has no in-place deletion)
- `format_context(results)` — formats as `[Memory N | source: X] text` blocks for LLM prompt injection
- Index + metadata persisted to `faiss.index` + `vector_metadata.json` after every write

#### `src/memory/memory_agent.py` — MemoryAgent: Three-Tier Orchestrator

The `MemoryAgent` class wires all three tiers into a single `chat()` method:

```
Turn N:
  1. Add user message to session (Tier 1)
  2. Vector search top-k=3 (Tier 3)
  3. Inject all SQLite facts if ≤10; keyword search otherwise (Tier 2)
  4. Build enriched prompt: system + memory context + session history
  5. Direct client.create() call (avoids AssistantAgent history bleed)
  6. Store response in session
  7. Isolated fact-extraction LLM call (temperature=0) → SQLite + vector
  Every 6 turns:
  8. Summarise session → SQLite episode + vector store
```

Facts injection strategy: facts are prepended to the **user turn** (not the system message) as a grounding block — the model follows user-turn context more reliably than system instructions alone.

**Session bootstrapping** on startup loads all persisted facts and recent episodes into the vector store, deduplicating against existing entries. Memory is immediately available in a fresh session.

#### `main_v4.py` — Memory CLI

Interactive session with named commands:

| Command       | Effect                                                    |
| ------------- | --------------------------------------------------------- |
| `/memory`     | Print session, vector, SQLite counts and total turn count |
| `/facts`      | List all stored facts from SQLite                         |
| `/episodes`   | List 5 most recent episode summaries                      |
| `/clear`      | Clear session history (long-term memory intact)           |
| `/wipe-facts` | Delete all facts from SQLite and vector store             |

Every turn — including commands — is logged to `logs_day4.json` with the full memory snapshot and a list of recalled memories for that turn.

### Deliverables

```
src/memory/session_memory.py
src/memory/long_term_memory.py   (+  long_term.db created at runtime)
src/memory/vector_store.py       (+  faiss.index, vector_metadata.json)
src/memory/memory_agent.py
main_v4.py
logs_day4.json
```

---

## 7. Day 5 — Capstone: NEXUS AI

### Objective

Integrate all prior work — agents, orchestration, tools, memory — into a fully autonomous, self-improving system that can solve any open-ended task.

### Agent Roster

| Agent        | Role                                           | Model tier |
| ------------ | ---------------------------------------------- | ---------- |
| Orchestrator | Task decomposition, final synthesis            | Primary    |
| Planner      | Numbered step plan, max 5 steps                | Primary    |
| Researcher   | Factual background, domain knowledge           | Primary    |
| Coder        | Fenced working code + usage example            | Primary    |
| Analyst      | Key findings, risks, recommendations (bullets) | Primary    |
| Critic       | Score 1–10 + PASS / NEEDS_WORK verdict         | Fast       |
| Optimizer    | Rewrites output to fix critique issues         | Primary    |
| Validator    | VALID / INVALID against original task          | Fast       |
| Reporter     | Compiles all outputs into structured markdown  | Primary    |

All agents use `autogen_agentchat.agents.AssistantAgent`. A **fresh instance is created per call** to prevent conversation history from bleeding across unrelated tasks.

### Pipeline Modes

Tasks are auto-classified as FAST or FULL by keyword matching:

```
FAST  (simple queries):
  Researcher [opt: Coder] → Reporter → Validator

FULL  (RAG / architecture / startup / strategy):
  Planner → Step Agents (Researcher / Coder / Analyst, keyword-routed)
           → Reporter → Validator → Reflector
```

Every agent output passes through a **Critic → Optimizer loop** (max 2 retries, pass threshold ≥ 7/10) before moving to the next stage.

### Three-Tier Memory (extended from Day 4)

| Tier            | Class                                          | Persistence         |
| --------------- | ---------------------------------------------- | ------------------- |
| Session history | `SessionHistory`, 6-turn window                | Current process     |
| Vector store    | `NexusVectorStore`, FAISS + `all-MiniLM-L6-v2` | `nexus_faiss.index` |
| Facts store     | `NexusFacts`, LLM-extracted JSON               | `nexus_facts.json`  |

`ConversationMemory.build_context()` assembles all three tiers and injects the result into every task prompt before execution begins.

### Tools (extended from Day 3)

| Tool                       | Function                                          |
| -------------------------- | ------------------------------------------------- |
| `run_python`               | Isolated Python execution (blocked-pattern guard) |
| `read_file` / `write_file` | UTF-8 file I/O                                    |
| `analyze_csv`              | Column types, row count, 5-row preview            |
| `web_search_stub`          | Placeholder (replace with Tavily/SerpAPI)         |
| `generate_diagram`         | Mermaid code block via LLM                        |

CSV files are auto-detected in plan step text via regex and analysed before the relevant agent runs.

### Structured Output Per Task

```
logs/task_01_design_a_rag_pipeline_20260330_082203/
├── report.md         ← full markdown report with metadata header
└── code/
    ├── snippet_01.py
    └── snippet_02.py
```

Code blocks are extracted from the final report first. If the Reporter agent strips fenced blocks, the system falls back to raw coder outputs captured in `orchestrator.last_code_outputs` before the reporter runs.

### Logging and Tracing

`NexusLogger` writes structured JSON events to `nexus_trace_two.json`. Every agent start/end, critic review, optimizer run, tool call, validation result, and self-reflection is recorded with timestamp, agent name, task reference, and relevant data payload.

### CLI

```bash
# Interactive session (default)
python -m nexus_ai_two.main_v5

# Single task
python -m nexus_ai_two.main_v5 --task "Design a RAG pipeline for 50k documents"
python -m nexus_ai_two.main_v5 --task "Plan a startup in AI for healthcare"
```

Interactive commands: `memory`, `history`, `clear`, `reset`, `exit`.

### Example Results

| Task                                             | Mode | Duration | Outcome            |
| ------------------------------------------------ | ---- | -------- | ------------------ |
| Design a RAG pipeline for 50k documents          | FULL | ~28s     | VALID, 8/10 critic |
| Plan a startup in AI for healthcare              | FULL | ~30s     | VALID, 8/10 critic |
| Generate backend architecture for a scalable app | FULL | ~35s     | VALID, 8/10 critic |
| Analyze CSV and create business strategy         | FULL | ~40s     | VALID, 8/10 critic |

### Deliverables

```
nexus_ai_two/main_v5.py
nexus_ai_two/config.py
nexus_ai_two/agents.py
nexus_ai_two/orchestrator.py
nexus_ai_two/memory.py
nexus_ai_two/conversation_memory.py
nexus_ai_two/logger.py
nexus_ai_two/tools.py
nexus_ai_two/logs/
```

---

## 8. Full Project Structure

```
Week9/
├── main.py                         ← Day 1: three-agent pipeline
├── main_v2.py                      ← Day 2: DAG orchestrator
├── main_v3.py                      ← Day 3: tool-calling agents
├── main_v4.py                      ← Day 4: memory-enabled agent
│
├── src/
│   ├── utils/
│   │   └── config.py               ← shared model client (Groq / Ollama)
│   │
│   ├── agents/
│   │   ├── research_agent.py       ← Day 1
│   │   ├── summarizer_agent.py     ← Day 1
│   │   ├── answer_agent.py         ← Day 1
│   │   ├── worker_agent.py         ← Day 2
│   │   └── validator.py            ← Day 2
│   │
│   ├── orchestrator/
│   │   └── planner.py              ← Day 2
│   │
│   ├── tools/
│   │   ├── code_executor.py        ← Day 3
│   │   ├── db_agent.py             ← Day 3
│   │   └── file_agent.py           ← Day 3
│   │
│   └── memory/
│       ├── session_memory.py       ← Day 4
│       ├── long_term_memory.py     ← Day 4
│       ├── vector_store.py         ← Day 4
│       └── memory_agent.py         ← Day 4
│
├── nexus_ai_two/                   ← Day 5: NEXUS AI capstone
│   ├── main_v5.py
│   ├── config.py
│   ├── agents.py
│   ├── orchestrator.py
│   ├── memory.py
│   ├── conversation_memory.py
│   ├── logger.py
│   ├── tools.py
│   └── logs/
│       ├── nexus_trace_two.json
│       ├── nexus_memory.json
│       ├── nexus_faiss.index
│       ├── nexus_facts.json
│       └── task_NN_<slug>_<timestamp>/
│           ├── report.md
│           └── code/
│
├── data/
│   ├── business.db                 ← SQLite database (Day 3)
│   └── *.csv / *.py / *.txt        ← files generated by Day 3 agents
│
└── logs/
    ├── conversation_logs.json      ← Day 1
    ├── logs_day2.json              ← Day 2
    ├── log_day3.json               ← Day 3
    ├── logs_day4.json              ← Day 4
    ├── code_output.txt             ← Day 3
    ├── db_output.txt               ← Day 3
    └── file_output.txt             ← Day 3
```

---

## 9. Week Completion Criteria

| Capability                       | Status | Day / File                                             |
| -------------------------------- | ------ | ------------------------------------------------------ |
| Multi-agent orchestration        | DONE   | All days                                               |
| Orchestrator + Planner           | DONE   | Day 2: `planner.py` · Day 5: `orchestrator.py`         |
| Tool calling: Python execution   | DONE   | Day 3: `code_executor.py`                              |
| Tool calling: Database (SQLite)  | DONE   | Day 3: `db_agent.py`                                   |
| Tool calling: File I/O           | DONE   | Day 3: `file_agent.py`                                 |
| Short-term (session) memory      | DONE   | Day 4: `session_memory.py`                             |
| Long-term memory (SQLite)        | DONE   | Day 4: `long_term_memory.py`                           |
| Vector memory (FAISS)            | DONE   | Day 4: `vector_store.py`                               |
| Self-reflection                  | DONE   | Day 5: `orchestrator._reflect()`                       |
| Self-improvement (Critic loop)   | DONE   | Day 5: `_critique_and_optimize()`                      |
| Multi-step planning              | DONE   | Day 2 + Day 5: `PlannerAgent`                          |
| Role switching / routing         | DONE   | Day 3: `_classify()` · Day 5: `route_step()`           |
| Logs + Tracing (JSON)            | DONE   | All days: per-day JSON logs + `NexusLogger`            |
| Failure recovery                 | DONE   | Day 5: `run_with_recovery()`                           |
| Memory window = 10               | DONE   | Day 1: `BufferedChatCompletionContext(buffer_size=10)` |
| No paid API (fully local option) | DONE   | Ollama fallback in `config.py`                         |
| Per-task output folders          | DONE   | Day 5: `logs/task_NN_<slug>_<timestamp>/`              |
