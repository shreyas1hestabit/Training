import asyncio
import argparse
import re
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from nexus_ai_two.orchestrator import NexusOrchestrator
from nexus_ai_two.config import LOGS_DIR

LANG_EXT: dict[str, str] = {
    "python":     ".py",
    "py":         ".py",
    "javascript": ".js",
    "js":         ".js",
    "typescript": ".ts",
    "ts":         ".ts",
    "bash":       ".sh",
    "sh":         ".sh",
    "sql":        ".sql",
    "yaml":       ".yaml",
    "yml":        ".yaml",
    "json":       ".json",
    "html":       ".html",
    "css":        ".css",
    "dockerfile": ".dockerfile",
    "mermaid":    ".mmd",
    "text":       ".txt",
    "":           ".txt",
}


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        NEXUS AI — Autonomous Multi-Agent System              ║
║        Powered by Groq · llama-3.1-8b-instant                ║
║        Multi-agent · Memory · Tools · Self-reflection        ║
╚══════════════════════════════════════════════════════════════╝
""")


def _safe_name(text: str, max_len: int = 40) -> str:
    return "".join(c if c.isalnum() else "_" for c in text[:max_len]).strip("_")


def _extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """Return (language, code) pairs for every fenced block with content > 10 chars."""
    pattern = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    return [
        (m.group(1).lower().strip(), m.group(2).strip())
        for m in pattern.finditer(text)
        if len(m.group(2).strip()) > 10
    ]


def save_report(
    task: str,
    report: str,
    index: int = 0,
    raw_code_outputs: list[str] | None = None,
) -> Path:
    """
    Creates  logs/task_NN_<slug>_<timestamp>/
      ├── report.md
      └── code/
          ├── snippet_01.py
          └── snippet_02.py   (etc.)

    Code blocks are taken from the final report first.
    If the reporter stripped them, falls back to raw coder agent outputs.
    """
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"task_{index:02d}_{_safe_name(task)}_{timestamp}"
    task_dir    = LOGS_DIR / folder_name
    task_dir.mkdir(parents=True, exist_ok=True)

    # 1 ── report.md ─────────────────────────────────────────────────────────
    report_path = task_dir / "report.md"
    report_path.write_text(
        f"# NEXUS AI Report\n\n"
        f"**Task:** {task}\n\n"
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"---\n\n"
        f"{report}",
        encoding="utf-8",
    )
    print(f"\n[NEXUS] report.md → {report_path}")

    # 2 ── collect code blocks ───────────────────────────────────────────────
    blocks = _extract_code_blocks(report)

    if not blocks and raw_code_outputs:
        print("[NEXUS] No code blocks in report — scanning raw coder outputs...")
        for raw in raw_code_outputs:
            blocks.extend(_extract_code_blocks(raw))

    # 3 ── save code files ───────────────────────────────────────────────────
    if blocks:
        code_dir = task_dir / "code"
        code_dir.mkdir(exist_ok=True)
        ext_counter: dict[str, int] = {}
        saved: list[Path] = []
        for lang, code in blocks:
            ext = LANG_EXT.get(lang, ".txt")
            ext_counter[ext] = ext_counter.get(ext, 0) + 1
            fp = code_dir / f"snippet_{ext_counter[ext]:02d}{ext}"
            fp.write_text(code, encoding="utf-8")
            saved.append(fp)
        print(f"[NEXUS] {len(saved)} code file(s) → {code_dir}")
        for f in saved:
            print(f"        {f.name}")
    else:
        print("[NEXUS] No code blocks found — only report.md saved.")

    print(f"[NEXUS] Folder → {task_dir}\n")
    return task_dir

async def run_single(task: str, index: int = 1):
    nexus  = NexusOrchestrator()
    report = await nexus.run_with_recovery(task)
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(report)
    save_report(task, report, index, raw_code_outputs=nexus.last_code_outputs)
    return report


async def run_interactive():
    print_banner()
    print("Type your task and press Enter. NEXUS will plan, research, code, and report.")
    print("Follow-up questions are supported — NEXUS remembers the whole session.")
    print()
    print("Commands:")
    print("  memory   — show memory statistics")
    print("  history  — show session conversation history")
    print("  clear    — clear session history (keeps vector store & facts)")
    print("  reset    — wipe ALL memory")
    print("  exit     — quit")
    print()

    nexus = NexusOrchestrator()
    count = 0

    while True:
        try:
            task = input("NEXUS> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[NEXUS] Goodbye.")
            break

        if not task:
            continue

        # ── built-in commands ──────────────────────────────────────────────
        if task.lower() == "exit":
            print("[NEXUS] Goodbye.")
            break

        if task.lower() == "memory":
            s = nexus.memory.stats()
            c = nexus.conv.status()
            print("\n  === Memory Status ===")
            print(f"  Session turns   : {c['session_turns']}")
            print(f"  Vector entries  : {c['vector_entries']}")
            print(f"  Facts stored    : {c['facts_stored']}")
            print(f"  Tasks completed : {s['tasks']}")
            print(f"  Reflections     : {s['reflections']}")
            print()
            continue

        if task.lower() == "history":
            turns = nexus.conv.session.get_all()
            if not turns:
                print("  (no conversation history yet)\n")
            else:
                print("\n  === Session History ===")
                for t in turns:
                    prefix = "You  " if t["role"] == "user" else "NEXUS"
                    print(f"  [{prefix}] {t['content'][:120]}...")
                print()
            continue

        if task.lower() == "clear":
            nexus.conv.clear_session()
            print("[Session history cleared. Vector store and facts intact.]\n")
            continue

        if task.lower() == "reset":
            nexus.conv.reset_all()
            print("[All memory wiped — vector store, facts, and session.]\n")
            continue

        # ── run task ───────────────────────────────────────────────────────
        count += 1
        report = await nexus.run_with_recovery(task)
        save_report(task, report, count, raw_code_outputs=nexus.last_code_outputs)


def main():
    parser = argparse.ArgumentParser(
        description="NEXUS AI — Autonomous Multi-Agent System (Groq Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive session (default)
  python -m nexus_ai_two.main_v5

  # Run a single task directly
  python -m nexus_ai_two.main_v5 --task "Design a RAG pipeline for 50k documents"
  python -m nexus_ai_two.main_v5 --task "Plan a startup in AI for healthcare"
  python -m nexus_ai_two.main_v5 --task "Generate backend architecture for a scalable web app"
        """,
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Run a single task and exit (use quotes for multi-word tasks)",
    )
    args = parser.parse_args()

    print_banner()

    if args.task:
        asyncio.run(run_single(args.task.strip(), index=1))
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()