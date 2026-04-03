# ARCHITECTURE.md — NEXUS AI

## System Overview

```
|-----------------------------------------------------------------|
|                        USER INPUT                               |
|-----------------------------------------------------------------|
                          │

-------------------------------------------------------------------
│                  CONVERSATION MEMORY                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Session      │  │ FAISS Vector     │  │ Facts Store      │  │
│  │ History      │  │ Store            │  │ (JSON)           │  │
│  │ (RAM)        │  │ (faiss.index)    │  │ (nexus_facts)    │  │
│  │ last 6 turns │  │ semantic search  │  │ extracted facts  │  │
│  └──────────────┘  └──────────────────┘  └──────────────────┘  │
│           │                  │                    │            │
│           -----------------------------------------            │
│                              │ build_context()                 │
------------------------------------------------------------------
                               │ memory context injected into task

-------------------------------------------------------------------
│                      TASK CLASSIFIER                            │
│            classify_task() -> "fast" or "full"                  │
-------------------------------------------------------------------
                   │                      │
          "fast"   │                      │  "full"

    ------------------------  ---------------------------------
    │   FAST PIPELINE      │  │      FULL PIPELINE            │
    │                      │  │                               │
    │  Researcher          │  │  Planner (max 5 steps)        │
    │      |               │  │      |                        │
    │  Coder (if needed)   │  │  [Role Router]                │
    │      |               │  │      |                        │
    │  Reporter            │  │  Researcher / Coder /         │
    │      |               │  │  Analyst (per step)           │
    │  Validator           │  │      |                        │
    ------------------------  │  Critic -> Optimizer loop      │
                               │      |                        │
                               │  Reporter                     │
                               │      |                        │
                               │  Validator                    │
                               │      |                        │
                               │  Self-reflection              │
                               ---------------------------------
                                          │

                               ------------------------
                               │  store_task()        │
                               │  -> FAISS + Facts     │
                               │  -> memory_two.json   │
                               │  -> report_*.md       │
                               ------------------------
```

---

## The 9 Agents

### Agent Interaction Flow

```
User task
    │

[ORCHESTRATOR] ─── classify_task() ---> Fast / Full
    │
    ├── Fast path:  Researcher ---> Coder ---> Reporter ---> Validator
    │
    └── Full path:
            │

        [PLANNER] -> numbered steps (max 5)
            │
            └── For each step:
                    │

                [ROLE ROUTER] -> Researcher | Coder | Analyst
                    │

                Agent runs step
                    │

                [CRITIC] scores 1-10
                    │
                    ├── score >= 7 -> PASS -> next step
                    │
                    └── score < 7 -> NEEDS_WORK
                                        │

                                    [OPTIMIZER] rewrites
                                        │

                                    [CRITIC] re-scores
                                    (max 2 retries)
            │

        [REPORTER] compiles all step outputs -> markdown report
            │

        [VALIDATOR] checks completeness -> VALID / INVALID
            │
            ├── VALID -> done
            │
            └── INVALID -> [OPTIMIZER] final pass
                              │

        [SELF-REFLECTION] 1-sentence improvement note -> stored in memory
```

---

## Memory Architecture

### Three-Tier Design

```
---------------------------------------------------------------
│                   CONVERSATION MEMORY                       │
│                  (conversation_memory.py)                   │
│                                                             │
│  -------------------------------------------------------   │
│  │  TIER 1 — SESSION HISTORY (SessionHistory class)    │   │
│  │                                                     │   │
│  │  Storage : Python list (RAM only)                   │   │
│  │  Window  : Last 6 turns (12 messages)               │   │
│  │  Purpose : Immediate follow-up questions            │   │
│  │  Example : "add a re-ranking layer to that design"  │   │
│  -------------------------------------------------------   │
│                                                            │
│  -------------------------------------------------------   │
│  │  TIER 2 — FAISS VECTOR STORE (NexusVectorStore)     │   │
│  │                                                     │   │
│  │  Storage : nexus_faiss.index + nexus_vector_meta    │   │
│  │  Model   : all-MiniLM-L6-v2 (384 dimensions)        │   │
│  │  Metric  : L2 distance (threshold 1.8)              │   │
│  │  Purpose : Semantic recall of past work             │   │
│  │  Example : "what did we design for 50k documents?"  │   │
│  -------------------------------------------------------   │
│                                                            │
│  -------------------------------------------------------   │
│  │  TIER 3 — FACTS STORE (NexusFacts class)            │   │
│  │                                                     │   │
│  │  Storage : nexus_facts.json                         │   │
│  │  Source  : LLM-extracted from task reports          │   │
│  │  Purpose : Specific technical decisions             │   │
│  │  Example : "FAISS with cosine similarity selected"  │   │
│  -------------------------------------------------------   │
--------------------------------------------------------------
```

### Memory Lifecycle Per Task

```
New user task
      │

build_context(task)
  ├── session.get_recent_text(4)    -> "## Recent conversation"
  ├── vector.search(task, top_k=2) -> "## Relevant past work"
  └── facts.get_recent(5)          -> "## Known facts"
      │

context injected into task_with_context
      │

[Pipeline runs with enriched task]
      │

store_task(task, report)
  ├── session.add("user", task)
  ├── session.add("assistant", report[:600])
  ├── vector.add(task + report summary)
  └── _extract_facts() -> async LLM -> facts.add("key decision")
```

---

## Task Classifier

```python
COMPLEX_SIGNALS = [
    "startup", "architecture", "pipeline", "strategy",
    "scalable", "production", "rag", "microservices",
    "infrastructure", "end-to-end", "comprehensive"
]
```

| Task contains      | Pipeline | Agents used | Avg time |
| ------------------ | -------- | ----------- | -------- |
| None of the above  | Fast     | 2-3 agents  | ~30-60s  |
| Any complex signal | Full     | 5-9 agents  | ~90-150s |

---

## Role Router

The orchestrator dynamically routes each plan step to the right agent:

```python
ROLE_KEYWORDS = {
    "researcher": ["research", "explain", "what is", "describe", "how does"],
    "coder":      ["code", "implement", "write", "build", "example", "flask"],
    "analyst":    ["analyze", "evaluate", "csv", "metrics", "compare"],
    "reporter":   ["report", "compile", "summarise", "document"],
}
```

If no keyword matches -> defaults to **Researcher**.

---

## Tool System

```
TOOL_REGISTRY
    ├── run_python(code)          -> exec() in isolated namespace, return stdout
    ├── read_file(path)           -> read UTF-8 text file
    ├── write_file(path, content) -> write to file, create dirs
    ├── analyze_csv(path)         -> columns, types, row count, preview
    ├── web_search(query)         -> stub (replace with Tavily/SerpAPI)
    └── generate_diagram(desc)    -> LLM generates Mermaid code block
```

CSV tool auto-triggers when any plan step contains a `.csv` filename.

---

## Critic + Optimizer Loop

```
Agent output
      │

Critic.review(output, task)
      │
      ├── score >= 7 -> PASS -> return output as-is
      │
      └── score < 7 -> NEEDS_WORK
              │

        Optimizer.optimize(output, critique, task)
              │

        Critic.review(improved_output, task)
              │
              ├── PASS -> return improved output
              │
              └── still NEEDS_WORK -> return best version after 2 retries
```

---

## Logging — Event Types

Every event is written to `logs/nexus_trace_two.json`:

| Event           | Meaning                                         |
| --------------- | ----------------------------------------------- |
| `TASK_START`    | New task begins                                 |
| `TASK_END`      | Task complete with duration and success flag    |
| `AGENT_START`   | Agent begins work                               |
| `AGENT_END`     | Agent finishes with output preview and duration |
| `AGENT_ERROR`   | Agent threw an exception                        |
| `CRITIC_REVIEW` | Critic score + verdict                          |
| `OPTIMIZER_RUN` | Optimizer rewrite attempt number                |
| `TOOL_CALL`     | Tool invoked with args and result preview       |
| `VALIDATION`    | Validator VALID/INVALID result                  |
| `REFLECTION`    | Post-task self-improvement note                 |
| `PLAN`          | Planner steps list                              |

---

## Failure Recovery

```
Primary pipeline fails
        │

log.agent_error("orchestrator", error)
        │

Fallback: Researcher.run(task)
        │
        ├── Success -> "[Recovery mode]\n\n{result}"
        │
        └── Also fails -> "[NEXUS ERROR] {e1}\nRecovery: {e2}"
```

---

## File Outputs Per Task

```
nexus_ai_two/logs/
├── report_01_<task>.md          <-- polished markdown report
├── nexus_trace_two.json         <-- append-only structured event log
├── nexus_memory_two.json        <-- task history + reflections
├── nexus_faiss.index            <-- FAISS binary index
├── nexus_vector_meta.json       <-- text + metadata for each FAISS entry
└── nexus_facts.json             <-- extracted technical facts
```

---

## Configuration Reference

| Parameter            | File                     | Default                | Effect                          |
| -------------------- | ------------------------ | ---------------------- | ------------------------------- |
| `GROQ_MODEL`         | `.env`                   | `llama-3.1-8b-instant` | LLM model for all agents        |
| `GROQ_API_KEY`       | `.env`                   | _(required)_           | Groq authentication             |
| `MAX_CRITIC_RETRIES` | `config.py`              | `2`                    | Max Optimizer rewrites per step |
| `CRITIC_PASS_SCORE`  | `config.py`              | `7`                    | Min score to skip Optimizer     |
| `MAX_PLAN_STEPS`     | `config.py`              | `8`                    | Hard cap on Planner output      |
| `max_turns`          | `conversation_memory.py` | `6`                    | Session history window          |
| `threshold`          | `conversation_memory.py` | `1.8`                  | FAISS L2 distance cutoff        |

---

## Comparison: Day 4 vs Day 5 Memory

| Feature                  | Day 4 (Memory Agent)          | Day 5 (NEXUS AI)            |
| ------------------------ | ----------------------------- | --------------------------- |
| Use case                 | Single-user chatbot           | Multi-agent task system     |
| Session memory           | Rolling 10-turn window        | Rolling 6-turn window       |
| Vector store             | FAISS over conversation facts | FAISS over task reports     |
| Persistent store         | SQLite (facts + episodes)     | JSON (nexus_facts + memory) |
| Fact extraction          | After every message           | After every completed task  |
| Memory injection         | System message                | Task prompt enrichment      |
| Follow-up support        | Per-message                   | Per-task                    |
| Persists across restarts | Yes                           | Yes                         |
