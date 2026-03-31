# """
# src/tools/code_executor.py — Python Code Execution Tool
# ---------------------------------------------------------
# Improvements over original:
#   • Pre-imports common stdlib into the execution namespace
#     (math, statistics, csv, json, collections, datetime)
#   • Strips input() calls so generated code never blocks waiting for user input
#   • Stronger code generation prompt that forbids input() and enforces
#     hardcoded example values
#   • Isolated execution namespace with safe builtins only
#   • Captures both stdout AND return value of last expression
#   • Saves every execution result to logs/code_output.txt
#   • Detects and blocks dangerous calls (os.remove, subprocess, etc.)
#   • Returns structured dict so orchestrator can log cleanly
# """

# import sys
# import io
# import os
# import re
# import math
# import statistics
# import csv
# import json
# import collections
# import datetime
# from datetime import datetime as _datetime_cls

# # ── Paths ────────────────────────────────────────────────────────────────
# _ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# _LOG_DIR  = os.path.join(_ROOT, "logs")
# _OUT_FILE = os.path.join(_LOG_DIR, "code_output.txt")
# os.makedirs(_LOG_DIR, exist_ok=True)

# # ── System prompt ─────────────────────────────────────────────────────────
# CODE_AGENT_SYSTEM_PROMPT = """
# You are the Code Execution Agent — an expert Python programmer.

# YOUR JOB:
# 1. Receive a task that requires Python computation or data analysis.
# 2. Write clean, complete, runnable Python code that solves the task.
# 3. The code will be executed directly — output ONLY the Python code.

# STRICT RULES:
# - Output ONLY raw Python code. No markdown fences, no explanations.
# - Every result must be printed with print() using a clear label.
# - Use only the standard library: math, statistics, csv, json, collections, datetime, io.
# - Do NOT import os, subprocess, sys, shutil, or any file-system-altering module.
# - Do NOT use input() or any interactive prompts — use hardcoded example values instead.
# - Do NOT use open() to write files — the executor handles output persistence.
# - If the task involves data passed as a string, read it with io.StringIO.
# - Always handle exceptions inside the code with try/except and print errors.
# - Always include a main() function with hardcoded example values.
# - Always end with: if __name__ == '__main__': main()
# - Produce concise, labelled output (e.g. "Average revenue: 42300.00").
# """

# # ── Blocked patterns (security guard) ────────────────────────────────────
# _BLOCKED = [
#     r"\bos\.remove\b",
#     r"\bos\.rmdir\b",
#     r"\bos\.unlink\b",
#     r"\bshutil\b",
#     r"\bsubprocess\b",
#     r"\bsys\.exit\b",
# ]


# def _is_safe(code: str) -> tuple[bool, str]:
#     for pattern in _BLOCKED:
#         if re.search(pattern, code):
#             return False, f"Blocked pattern detected: `{pattern}`"
#     return True, ""


# def _save_output(code: str, output: str) -> None:
#     """Append execution record to logs/code_output.txt."""
#     with open(_OUT_FILE, "a", encoding="utf-8") as f:
#         f.write(f"\n{'='*60}\n")
#         f.write(f"Timestamp : {_datetime_cls.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
#         f.write(f"{'─'*60}\n")
#         f.write("CODE:\n")
#         f.write(code.strip() + "\n")
#         f.write(f"{'─'*60}\n")
#         f.write("OUTPUT:\n")
#         f.write(output.strip() + "\n")


# def _strip_input_calls(code: str) -> str:
#     """
#     Replace input(...) calls with a hardcoded default value ("0") so
#     generated code never blocks waiting for user input in the executor.
#     """
#     return re.sub(r'input\s*\([^)]*\)', '"0"', code)


# def local_python_executor(code: str) -> str:
#     """
#     Execute Python code in an isolated namespace.
#     Returns stdout as a string.
#     Also saves output to logs/code_output.txt.
#     """
#     # Strip accidental markdown fences
#     code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
#     code = re.sub(r"\n?```$",          "", code.strip()).strip()

#     # Strip input() calls so execution never blocks
#     code = _strip_input_calls(code)

#     # Security check
#     safe, reason = _is_safe(code)
#     if not safe:
#         result = f"[SECURITY BLOCKED] {reason}"
#         _save_output(code, result)
#         return result

#     # Isolated execution
#     old_stdout = sys.stdout
#     sys.stdout  = buf = io.StringIO()

#     # Safe builtins — remove nested code execution only
#     import builtins as _builtins_mod
#     safe_builtins = vars(_builtins_mod).copy()
#     for _bad in ("exec", "eval", "compile"):
#         safe_builtins.pop(_bad, None)

#     # Pre-import common stdlib so generated code can use them directly
#     # without needing import statements (which may fail in isolated namespace)
#     safe_globals = {
#         "__builtins__": safe_builtins,
#         "io":          io,
#         "math":        math,
#         "statistics":  statistics,
#         "csv":         csv,
#         "json":        json,
#         "collections": collections,
#         "datetime":    datetime,
#     }

#     try:
#         exec(compile(code, "<code_agent>", "exec"), safe_globals)  # noqa: S102
#         output = buf.getvalue()
#         if not output.strip():
#             output = "Success: Code executed with no printed output."
#     except Exception as exc:
#         output = f"Python Error: {type(exc).__name__}: {exc}"
#     finally:
#         sys.stdout = old_stdout

#     _save_output(code, output)
#     return output


# # ── Tool descriptor ───────────────────────────────────────────────────────
# python_tool = {
#     "name":          "python_executor",
#     "description":   "Execute Python code for data processing or analysis. Returns stdout.",
#     "func":          local_python_executor,
#     "system_prompt": CODE_AGENT_SYSTEM_PROMPT,
# }

"""
src/tools/code_executor.py
"""

import sys
import io
import os
import re
import csv as _csv
import random
import math
import datetime
import itertools

_ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def local_python_executor(code: str) -> str:
    """
    Execute a Python code string and return stdout.

    Args:
        code: Valid Python code. No markdown fences.

    Returns:
        stdout output, or an error message.
    """
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip()).strip()
    code = re.sub(r'input\s*\([^)]*\)', '"0"', code)

    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        exec(code, {"__builtins__": __builtins__})  # noqa: S102
        output = buf.getvalue()
        return output if output.strip() else "Code executed successfully (no output)."
    except Exception as exc:
        return f"Python Error: {type(exc).__name__}: {exc}"
    finally:
        sys.stdout = old_stdout


def save_python_file(file_name: str, code: str) -> str:
    """
    Save Python source code as a .py file in the data directory.

    Always call local_python_executor first to verify the code runs,
    then call this to persist it.

    Args:
        file_name: Target filename. .py extension added if omitted.
        code:      Complete Python source. No markdown fences.

    Returns:
        Absolute file path and size in bytes, or an error message.
    """
    code = re.sub(r"^```[a-zA-Z]*\n?", "", code.strip())
    code = re.sub(r"\n?```$", "", code.strip()).strip()

    if not file_name.endswith(".py"):
        file_name += ".py"

    path = os.path.join(DATA_DIR, file_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return f"Saved: {path} ({os.path.getsize(path)} bytes)"


def generate_and_write_csv(file_name: str, generator_code: str) -> str:
    """
    Execute generator_code to produce `headers` and `rows`, then write the CSV.

    generator_code is a Python script that must define:
      headers — a list of column name strings
      rows    — a list of lists, each inner list being one complete row

    The script runs with access to: random, math, datetime, itertools
    It must NOT call open() or write any files.

    Args:
        file_name:      Target CSV filename.
        generator_code: Python script defining `headers` and `rows`.
                        No markdown fences. No open() calls.

    Returns:
        File path, exact row count written, and byte size — or an error.
    """
    generator_code = re.sub(r"^```[a-zA-Z]*\n?", "", generator_code.strip())
    generator_code = re.sub(r"\n?```$", "", generator_code.strip()).strip()

    namespace = {
        "__builtins__": __builtins__,
        "random":       random,
        "math":         math,
        "datetime":     datetime,
        "itertools":    itertools,
    }

    try:
        exec(generator_code, namespace)  # noqa: S102
    except Exception as exc:
        return f"Generator Error: {type(exc).__name__}: {exc}"

    headers = namespace.get("headers")
    rows    = namespace.get("rows")

    if not headers:
        return "Error: generator_code must define a `headers` list."
    if rows is None:
        return "Error: generator_code must define a `rows` list."
    if len(rows) == 0:
        return "Error: `rows` is empty — check the loop in generator_code."

    if not file_name.endswith(".csv"):
        file_name += ".csv"

    path = os.path.join(DATA_DIR, file_name)
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = _csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return (
            f"Success: '{file_name}' written with {len(rows)} data rows "
            f"({os.path.getsize(path)} bytes) → {path}"
        )
    except Exception as exc:
        return f"CSV Write Error: {type(exc).__name__}: {exc}"


def read_and_analyze_csv(file_name: str, analysis_code: str) -> str:
    """
    Read a CSV file and run Python analysis code against its rows.

    Use this to query, filter, sort, or aggregate a CSV file directly
    without loading it into a database.

    `rows` is pre-loaded as a list of dicts (all values are strings).
    Cast numeric fields before comparing: int(r['col']), float(r['col'])
    Use print() to output all results.

    Args:
        file_name:     CSV filename in the data directory.
        analysis_code: Python snippet using `rows`. No markdown fences.

    Returns:
        stdout from the analysis, or an error message.
    """
    csv_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(csv_path):
        return f"Error: '{file_name}' not found in {DATA_DIR}."

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(_csv.DictReader(f))
    except Exception as exc:
        return f"CSV Read Error: {type(exc).__name__}: {exc}"

    analysis_code = re.sub(r"^```[a-zA-Z]*\n?", "", analysis_code.strip())
    analysis_code = re.sub(r"\n?```$", "", analysis_code.strip()).strip()

    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        exec(analysis_code, {"__builtins__": __builtins__, "rows": rows})  # noqa: S102
        output = buf.getvalue()
        return output if output.strip() else "Analysis complete — no output was printed."
    except Exception as exc:
        return f"Analysis Error: {type(exc).__name__}: {exc}"
    finally:
        sys.stdout = old_stdout