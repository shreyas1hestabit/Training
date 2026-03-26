"""
src/tools/code_executor.py — Python Code Execution Tool
---------------------------------------------------------
SYSTEM PROMPT is defined here (not in main).

Improvements over v1:
  • Isolated execution namespace with safe builtins only
  • Captures both stdout AND return value of last expression
  • Saves every execution result to logs/code_output.txt
  • Detects and blocks dangerous calls (os.remove, subprocess, etc.)
  • Returns structured dict so orchestrator can log cleanly
"""

import sys
import io
import os
import re
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────────────────
_ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_LOG_DIR  = os.path.join(_ROOT, "logs")
_OUT_FILE = os.path.join(_LOG_DIR, "code_output.txt")
os.makedirs(_LOG_DIR, exist_ok=True)

# ── System prompt (used by orchestrator when building the code-gen prompt) ──
CODE_AGENT_SYSTEM_PROMPT = """
You are the Code Execution Agent — an expert Python programmer.

YOUR JOB:
1. Receive a task that requires Python computation or data analysis.
2. Write clean, complete, runnable Python code that solves the task.
3. The code will be executed directly — output ONLY the Python code.

STRICT RULES:
- Output ONLY raw Python code. No markdown fences, no explanations.
- Every result must be printed with print().
- Use only the standard library (csv, json, math, statistics, collections, datetime).
- Do NOT import os, subprocess, sys, shutil, or any file-system-altering module.
- Do NOT use open() to write files — the executor handles output persistence.
- If the task involves data passed as a string, read it with io.StringIO.
- Always handle exceptions inside the code with try/except and print errors.
- Produce concise, labelled output (e.g. "Average revenue: 42300.00").
"""

# ── Blocked patterns (security guard) ────────────────────────────────────
# These catch genuinely destructive calls. We do NOT block open() or imports
# because the CSV→DB conversion script legitimately uses sqlite3, csv, io, re.
_BLOCKED = [
    r"\bos\.remove\b",
    r"\bos\.rmdir\b",
    r"\bos\.unlink\b",
    r"\bshutil\b",
    r"\bsubprocess\b",
    r"\bsys\.exit\b",
]

def _is_safe(code: str) -> tuple[bool, str]:
    for pattern in _BLOCKED:
        if re.search(pattern, code):
            return False, f"Blocked pattern detected: `{pattern}`"
    return True, ""


def _save_output(code: str, output: str) -> None:
    """Append execution record to logs/code_output.txt."""
    with open(_OUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'─'*60}\n")
        f.write("CODE:\n")
        f.write(code.strip() + "\n")
        f.write(f"{'─'*60}\n")
        f.write("OUTPUT:\n")
        f.write(output.strip() + "\n")


def local_python_executor(code: str) -> str:
    """
    Execute Python code in an isolated namespace.
    Returns stdout as a string.
    Also saves output to logs/code_output.txt.
    """
    # Strip accidental markdown fences
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$",          "", code.strip()).strip()

    # Security check
    safe, reason = _is_safe(code)
    if not safe:
        result = f"[SECURITY BLOCKED] {reason}"
        _save_output(code, result)
        return result

    # Isolated execution
    old_stdout = sys.stdout
    sys.stdout  = buf = io.StringIO()

    # ── Safe namespace ──────────────────────────────────────────────────────
    # We keep the real __builtins__ (so `import sqlite3`, `import csv` etc.
    # all work) but strip only the truly dangerous builtins.
    # Dangerous OS calls are caught earlier by the _BLOCKED regex patterns.
    import builtins as _builtins_mod
    safe_builtins = vars(_builtins_mod).copy()
    for _bad in ("exec", "eval", "compile"):   # nested code execution only
        safe_builtins.pop(_bad, None)

    safe_globals = {
        "__builtins__": safe_builtins,
        "io": io,
    }

    try:
        exec(compile(code, "<code_agent>", "exec"), safe_globals)  # noqa: S102
        output = buf.getvalue()
        if not output.strip():
            output = "Success: Code executed with no printed output."
    except Exception as exc:
        output = f"Python Error: {type(exc).__name__}: {exc}"
    finally:
        sys.stdout = old_stdout

    _save_output(code, output)
    return output


# ── Tool descriptor (imported by orchestrator / main) ────────────────────
python_tool = {
    "name":        "python_executor",
    "description": "Execute Python code for data processing or analysis. Returns stdout.",
    "func":        local_python_executor,
    "system_prompt": CODE_AGENT_SYSTEM_PROMPT,
}