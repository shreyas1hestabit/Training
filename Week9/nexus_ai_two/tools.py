"""
nexus_ai_two/tools.py
----------------------
Real tools for NEXUS AI — Groq edition.
Identical to nexus_ai/tools.py except imports from nexus_ai_two.config.
"""

import sys
import io
import csv as csv_module
import json
from pathlib import Path
from autogen_core.models import UserMessage, SystemMessage
from nexus_ai_two.config import FAST_MODEL


def run_python(code: str) -> str:
    """Execute Python in an isolated namespace. Returns stdout or error."""
    forbidden = ["os.remove", "os.rmdir", "shutil.rmtree", "subprocess", "sys.exit"]
    if any(f in code for f in forbidden):
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


def read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: File not found — {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def write_file(path: str, content: str) -> str:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written: {path} ({len(content)} chars)"
    except Exception as e:
        return f"Error writing file: {e}"


def analyze_csv(path: str, max_rows: int = 5) -> str:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv_module.DictReader(f)
            rows   = list(reader)
        if not rows:
            return "CSV is empty."
        columns = list(rows[0].keys())
        n_rows  = len(rows)
        type_map = {}
        for col in columns:
            values  = [r[col] for r in rows if r[col].strip()]
            numeric = sum(1 for v in values if v.replace(".", "").replace("-", "").isdigit())
            type_map[col] = "numeric" if numeric > len(values) * 0.8 else "text"
        summary = {
            "file":    path,
            "rows":    n_rows,
            "columns": columns,
            "types":   type_map,
            "preview": [dict(r) for r in rows[:max_rows]],
        }
        return json.dumps(summary, indent=2)
    except FileNotFoundError:
        return f"Error: CSV not found — {path}"
    except Exception as e:
        return f"CSV Error: {e}"


def web_search_stub(query: str) -> str:
    """Stub — replace with Tavily or SerpAPI in production."""
    return (
        f"[Web search stub] Query: '{query}'\n"
        f"Install tavily-python and set TAVILY_API_KEY to enable real search.\n"
        f"Mock result: relevant topics for '{query}': best practices, frameworks, recent trends."
    )


async def generate_diagram(description: str) -> str:
    try:
        result = await FAST_MODEL.create(
            messages=[
                SystemMessage(content=(
                    "Generate a Mermaid diagram. "
                    "Return ONLY a valid ```mermaid ... ``` code block."
                )),
                UserMessage(content=f"Diagram for: {description}", source="user"),
            ],
        )
        return str(result.content).strip()
    except Exception as e:
        return f"[Diagram Error] {e}"


TOOL_REGISTRY = {
    "run_python":       {"func": run_python,       "description": "Execute Python code"},
    "read_file":        {"func": read_file,         "description": "Read a file"},
    "write_file":       {"func": write_file,        "description": "Write a file"},
    "analyze_csv":      {"func": analyze_csv,       "description": "Parse CSV and return stats"},
    "web_search":       {"func": web_search_stub,   "description": "Search the web"},
    "generate_diagram": {"func": generate_diagram,  "description": "Generate a Mermaid diagram"},
}