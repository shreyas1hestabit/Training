# NEXUS AI — Autonomous Multi-Agent System

### Day 5 Capstone · AutoGen · Groq · llama-3.1-8b-instant

A fully autonomous multi-agent AI system that plans, executes, critiques, optimises, validates, and reports on complex tasks — with persistent conversational memory across sessions.

---

## Project Structure

```
Week9/
├── nexus_ai_two/
│   ├── main.py                  # Entry point
│   ├── config.py                # Groq client + agent personas + constants
│   ├── agents.py                # 9 specialist agent classes
│   ├── orchestrator.py          # Master pipeline engine
│   ├── tools.py                 # Python executor, file I/O, CSV analyser
│   ├── memory.py                # Persistent task memory (JSON)
│   ├── conversation_memory.py   # 3-tier conversational memory (session + FAISS + facts)
│   ├── logger.py                # Structured JSON trace logger
│   └── logs/
│       ├── nexus_trace_two.json      # Full event trace
│       ├── nexus_memory_two.json     # Persistent task memory
│       ├── nexus_faiss.index         # FAISS vector index (binary)
│       ├── nexus_vector_meta.json    # FAISS metadata
│       ├── nexus_facts.json          # Extracted technical facts
│       └── report_*.md               # Per-task final reports
└── src/
    └── utils/
        └── config.py            # Shared Ollama/Groq client (used by Days 3-5)
```

---

## Setup

```bash
# Install dependencies
pip install autogen-agentchat autogen-ext[openai] autogen-core
pip install faiss-cpu sentence-transformers   # for vector memory

# Add Groq API key to your .env file
echo "GROQ_API_KEY=gsk_..." >> .env
echo "GROQ_MODEL=llama-3.1-8b-instant" >> .env
```

---

## Running NEXUS AI

```bash
# Interactive mode (recommended)
python3 -m nexus_ai_two.main

# Run a single task
python3 -m nexus_ai_two.main --task "design a RAG pipeline for 50k documents"

# Run all 4 demo tasks
python3 -m nexus_ai_two.main --demo
```

---

## Interactive Commands

| Command   | Action                                                          |
| --------- | --------------------------------------------------------------- |
| `memory`  | Show memory status — session turns, vector entries, facts count |
| `history` | Print current session conversation history                      |
| `clear`   | Clear session history (vector store + facts persist)            |
| `reset`   | Wipe all memory — session, vector store, and facts              |
| `exit`    | Quit                                                            |

---

## The 9 Agents

| Agent            | Role                                         | Triggered by                  |
| ---------------- | -------------------------------------------- | ----------------------------- |
| **Orchestrator** | Decomposes tasks, routes steps, synthesises  | Every task                    |
| **Planner**      | Numbered 1–5 step execution plan             | Complex tasks (full pipeline) |
| **Researcher**   | Domain knowledge, best practices, concepts   | Research/explain steps        |
| **Coder**        | Production-quality code with examples        | Build/implement/write steps   |
| **Analyst**      | Data analysis, insights, risk assessment     | Analyse/CSV/metrics steps     |
| **Critic**       | Reviews output, scores 1–10, PASS/NEEDS_WORK | After every agent output      |
| **Optimizer**    | Rewrites output based on Critic feedback     | When score < 7                |
| **Validator**    | Final quality gate — VALID / INVALID         | After Reporter                |
| **Reporter**     | Compiles all outputs into a markdown report  | Final step always             |

---

## Memory System

NEXUS AI has **three-tier conversational memory** — you can ask follow-up questions and it remembers what was designed in previous tasks.

### Tier 1 — Session History

Rolling window of the last 6 conversation turns (in RAM).
Enables immediate follow-ups: `"now add a re-ranking layer to that design"`.

### Tier 2 — FAISS Vector Store

Semantic similarity search over all past task reports.
Stored in `logs/nexus_faiss.index` — persists across restarts.
When you ask a new task, NEXUS searches for similar past work and injects it as context.

### Tier 3 — Facts Store

Key technical facts extracted from each task (e.g. `"The RAG pipeline uses cosine similarity"`).
Stored in `logs/nexus_facts.json`.
Injects the 5 most recent facts into every new task prompt.

---

## Two Execution Modes

NEXUS automatically classifies every task and picks the right pipeline:

### Fast Mode (simple tasks)

Researcher -> (Coder) -> Reporter -> Validator  
Used for: explanations, single code examples, Q&A  
Time: ~30–60 seconds

### Full Mode (complex tasks)

Planner -> [Steps 1–5 with Critic loop] -> Reporter -> Validator -> Reflection  
Used for: startup planning, architecture design, pipeline design, business strategy  
Time: ~90–150 seconds

---

## Tools Available

| Tool               | Description                                           |
| ------------------ | ----------------------------------------------------- |
| `run_python`       | Execute Python in a safe sandbox, capture stdout      |
| `read_file`        | Read any text or CSV file                             |
| `write_file`       | Write content to a file                               |
| `analyze_csv`      | Parse CSV and return column types, row count, preview |
| `web_search`       | Web search stub (replace with Tavily/SerpAPI)         |
| `generate_diagram` | Generate a Mermaid architecture diagram via LLM       |

---

## Output Files

Every task produces three outputs:

```
nexus_ai_two/logs/
├── report_01_<task_name>.md     - Final polished markdown report
├── nexus_trace_two.json         - Full structured event log (all agents + timing)
└── nexus_memory_two.json        - Persistent task history + reflections
```

---

## Configuration (`config.py`)

| Setting              | Default                | Description                        |
| -------------------- | ---------------------- | ---------------------------------- |
| `GROQ_MODEL`         | `llama-3.1-8b-instant` | Change via `.env`                  |
| `MAX_CRITIC_RETRIES` | 2                      | Optimizer rewrites per output      |
| `CRITIC_PASS_SCORE`  | 7                      | Min score (1–10) to skip Optimizer |
| `MAX_PLAN_STEPS`     | 8                      | Max steps Planner can generate     |
