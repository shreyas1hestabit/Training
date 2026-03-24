"""
nexus_ai/tools.py
-----------------
Real tools available to NEXUS AI agents.

Tools:
    run_python(code)          — execute Python in a sandbox, capture stdout
    read_file(path)           — read any text file
    write_file(path, content) — write text to a file
    analyze_csv(path)         — parse a CSV and return summary stats + preview
    web_search_stub(query)    — placeholder (replace with real search API)
    generate_diagram(desc)    — returns a Mermaid diagram string from a description
"""

import sys
import io
import os
import csv as csv_module
import json
from pathlib import Path
from autogen_core.models import UserMessage, SystemMessage
from nexus_ai.config import FAST_MODEL


# ---------------------------------------------------------------------------
# Python Execution
# ---------------------------------------------------------------------------

def run_python(code: str) -> str:
    """Execute Python in an isolated namespace. Returns stdout or error."""
    _forbidden = ["os.remove", "os.rmdir", "shutil.rmtree", "subprocess", "sys.exit"]
    if any(f in code for f in _forbidden):
        return "[BLOCKED] Dangerous operation detected."

    old_stdout = sys.stdout
    sys.stdout = buf = io.StringIO()
    try:
        exec(code, {})
        output = buf.getvalue()
        return output.strip() if output.strip() else "Code ran successfully (no output)."
    except Exception as e:
        return f"Python Error: {e}"
    finally:
        sys.stdout = old_stdout


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def read_file(path: str) -> str:
    """Read a text file. Returns content or error string."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: File not found — {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file. Creates parent directories as needed."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written: {path} ({len(content)} chars)"
    except Exception as e:
        return f"Error writing file: {e}"


# ---------------------------------------------------------------------------
# CSV Analysis
# ---------------------------------------------------------------------------

def analyze_csv(path: str, max_rows: int = 5) -> str:
    """
    Parse a CSV file and return:
    - Column names
    - Row count
    - Per-column type inference (numeric / text)
    - Preview of first max_rows rows
    """
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv_module.DictReader(f)
            rows = list(reader)

        if not rows:
            return "CSV is empty."

        columns = list(rows[0].keys())
        n_rows  = len(rows)

        # Type inference
        type_map = {}
        for col in columns:
            values = [r[col] for r in rows if r[col].strip()]
            numeric = sum(1 for v in values if v.replace(".", "").replace("-", "").isdigit())
            type_map[col] = "numeric" if numeric > len(values) * 0.8 else "text"

        # Preview
        preview = []
        for row in rows[:max_rows]:
            preview.append({k: v for k, v in row.items()})

        summary = {
            "file":    path,
            "rows":    n_rows,
            "columns": columns,
            "types":   type_map,
            "preview": preview,
        }
        return json.dumps(summary, indent=2)

    except FileNotFoundError:
        return f"Error: CSV not found — {path}"
    except Exception as e:
        return f"CSV Error: {e}"


# ---------------------------------------------------------------------------
# Web Search (stub — replace with real API)
# ---------------------------------------------------------------------------

def web_search_stub(query: str) -> str:
    """
    Placeholder for web search. In production, replace with:
        - Tavily API  (pip install tavily-python)
        - SerpAPI
        - DuckDuckGo  (pip install duckduckgo-search)
    """
    return (
        f"[Web search stub] Query: '{query}'\n"
        f"To enable real search: install tavily-python and set TAVILY_API_KEY.\n"
        f"Returning mock result for demonstration purposes.\n"
        f"Relevant topics for '{query}': market overview, key players, recent trends, best practices."
    )


# ---------------------------------------------------------------------------
# Diagram Generator (Mermaid via LLM)
# ---------------------------------------------------------------------------

async def generate_diagram(description: str) -> str:
    """
    Ask the LLM to generate a Mermaid diagram from a plain-text description.
    Returns a ```mermaid ... ``` code block.
    """
    try:
        result = await FAST_MODEL.create(
            messages=[
                SystemMessage(content=(
                    "You generate Mermaid diagrams. "
                    "Return ONLY a valid Mermaid code block — no explanation. "
                    "Start with ```mermaid and end with ```."
                )),
                UserMessage(
                    content=f"Generate a Mermaid diagram for: {description}",
                    source="user"
                ),
            ],
            extra_create_args={"temperature": 0.1},
        )
        return str(result.content).strip()
    except Exception as e:
        return f"[Diagram Error] {e}"


# ---------------------------------------------------------------------------
# Tool Registry — used by agents to discover available tools
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "run_python":       {"func": run_python,       "description": "Execute Python code and capture output"},
    "read_file":        {"func": read_file,         "description": "Read a text or CSV file"},
    "write_file":       {"func": write_file,        "description": "Write text content to a file"},
    "analyze_csv":      {"func": analyze_csv,       "description": "Parse CSV and return stats + preview"},
    "web_search":       {"func": web_search_stub,   "description": "Search the web for information"},
    "generate_diagram": {"func": generate_diagram,  "description": "Generate a Mermaid architecture diagram"},
}