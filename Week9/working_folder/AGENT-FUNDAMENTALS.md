## Project Overview

This project demonstrates a **Multi-Agent Orchestration System** built with **AutoGen (v0.7.5)** and a local **Phi-3** model via **Ollama**. The system is designed as a three-tier pipeline to research, summarize, and format data based on user queries.

---

## System Architecture

The system uses a **Sequential Pipeline** to optimize performance on local hardware (CPU). This avoids the overhead of a standard Group Chat.

| Agent            | Role                     | Responsibility                                               |
| :--------------- | :----------------------- | :----------------------------------------------------------- |
| **Researcher**   | Data Fact Extraction     | Scans internal model weights for raw facts and lists them.   |
| **Summarizer**   | Information Distillation | Filters raw research into exactly 3-5 concise bullet points. |
| **Answer_Agent** | PR & Formatting          | Wraps the summary in a professional, polite response.        |

---

## Technical Specifications

### 1. Model Configuration

- **Model:** Phi-3 Mini (3.8B Parameters)
- **Provider:** Ollama (Local)
- **Temperature:** 0 (Strictly Factual/Deterministic)
- **Context Management:** `BufferedChatCompletionContext` (Size: 10)
- **Stabilization:** `repeat_penalty: 1.2` and `top_p: 0.1` to prevent gibberish.

### 2. Selective Memory Management

The system maintains a "sliding window" of the last 10 messages. This allows for **Entity Resolution** (e.g., asking about "Steve Jobs" and then asking "What is **his** nationality?").

- **Manual Reset:** A `clear` command was implemented to manually wipe context if the model hits a token limit.

---

## Challenges & Solutions

### 1. The "Gibberish" Hallucination

**Challenge:** Small local models can leak training data (HTML/Random tokens) when confused.
**Solution:** Hardcoded `temperature: 0` and implemented a manual `_model_context.clear()` function to ensure a clean slate when needed.

### 2. Latency Issues

**Challenge:** Standard AutoGen teams took 5+ minutes per query on a CPU.
**Solution:** Switched to a **Fast Pipeline**. By manually orchestrating the agent hand-offs in `main.py`, we reduced the total execution time to **100-140 seconds**.

### 3. Subject Persistence

**Challenge:** Agents losing track of the subject across multiple turns.
**Solution:** Removed automatic resets at the start of loops, relying on the `BufferedChatCompletionContext` to handle the history correctly.

---

## Performance Metrics (Local CPU)

- **Avg. Research Time:** ~20s
- **Avg. Summary Time:** ~25s
- **Avg. Formatting Time:** ~45s
- **Total Pipeline Latency:** ~100s - 130s

---

## Logging & Traceability

All interactions are stored in `conversation_logs_hardcode_updated.json`, capturing:

- **Timestamps** & **User Queries**.
- **Individual Agent Timings** for performance benchmarking.
- **Full Trace** of internal data exchange for debugging.

---
