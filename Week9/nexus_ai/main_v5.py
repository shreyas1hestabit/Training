"""
nexus_ai/main.py
----------------
NEXUS AI — Entry Point

Run:
    python -m nexus_ai.main                    # interactive mode
    python -m nexus_ai.main --demo             # run all 4 example tasks
    python -m nexus_ai.main --task "your task" # run a single task

Logs written to: nexus_ai/logs/
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path so nexus_ai package resolves correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from nexus_ai.orchestrator import NexusOrchestrator
from nexus_ai.config import LOGS_DIR


# ---------------------------------------------------------------------------
# Demo tasks (the 4 required examples from the spec)
# ---------------------------------------------------------------------------

DEMO_TASKS = [
    "Plan a startup in AI for healthcare — include business model, MVP, target market, tech stack, and go-to-market strategy.",
    "Generate backend architecture for a scalable web application — include database design, API structure, caching, auth, and deployment strategy.",
    "Analyze this CSV file (sales_data.csv) and create a comprehensive business strategy based on the findings.",
    "Design a RAG (Retrieval-Augmented Generation) pipeline for 50,000 documents — include chunking strategy, embedding model, vector store, retrieval logic, and LLM integration.",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           NEXUS AI — Autonomous Multi-Agent System           ║
║         Multi-agent · Memory · Tools · Self-reflection       ║
╚══════════════════════════════════════════════════════════════╝
""")


def save_report(task: str, report: str, index: int = 0):
    """Save a task report to the logs directory."""
    safe_name = "".join(c if c.isalnum() else "_" for c in task[:40]).strip("_")
    filename  = LOGS_DIR / f"report_{index:02d}_{safe_name}.md"
    filename.write_text(f"# NEXUS AI Report\n\n**Task:** {task}\n\n---\n\n{report}", encoding="utf-8")
    print(f"\n[NEXUS] Report saved → {filename}")
    return filename


# ---------------------------------------------------------------------------
# Run modes
# ---------------------------------------------------------------------------

async def run_single_task(task: str, index: int = 0):
    """Run one task through NEXUS AI and save the report."""
    nexus = NexusOrchestrator()
    report = await nexus.run_with_recovery(task)

    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(report)

    save_report(task, report, index)
    return report


async def run_demo():
    """Run all 4 demo tasks sequentially."""
    print_banner()
    print(f"Running {len(DEMO_TASKS)} demo tasks...\n")

    nexus = NexusOrchestrator()

    for i, task in enumerate(DEMO_TASKS, 1):
        print(f"\n{'─'*60}")
        print(f"DEMO TASK {i}/{len(DEMO_TASKS)}")
        print(f"{'─'*60}")

        report = await nexus.run_with_recovery(task)
        save_report(task, report, i)

        print(f"\n[Task {i} complete]\n")

    stats = nexus.memory.stats()
    print(f"\n[NEXUS] All demo tasks complete.")
    print(f"[NEXUS] Memory: {stats['tasks']} tasks, {stats['reflections']} reflections stored.")


async def run_interactive():
    """Interactive REPL for NEXUS AI."""
    print_banner()
    print("Type your task and press Enter. Type 'exit' to quit.")
    print("Commands: 'memory' — show memory stats | 'exit' — quit\n")

    nexus = NexusOrchestrator()
    task_count = 0

    while True:
        try:
            task = input("NEXUS> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[NEXUS] Shutting down.")
            break

        if not task:
            continue

        if task.lower() == "exit":
            print("[NEXUS] Goodbye.")
            break

        if task.lower() == "memory":
            stats = nexus.memory.stats()
            print(f"\n  Tasks completed : {stats['tasks']}")
            print(f"  Facts stored    : {stats['facts']}")
            print(f"  Reflections     : {stats['reflections']}")
            recent = nexus.memory.get_recent_tasks(3)
            if recent:
                print("  Recent tasks:")
                for t in recent:
                    print(f"    [{t['timestamp'][:10]}] {t['task'][:60]}")
            print()
            continue

        task_count += 1
        report = await nexus.run_with_recovery(task)
        save_report(task, report, task_count)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="NEXUS AI — Autonomous Multi-Agent System")
    parser.add_argument("--demo",  action="store_true", help="Run all 4 demo tasks")
    parser.add_argument("--task",  type=str,            help="Run a single task")
    args = parser.parse_args()

    if args.demo:
        asyncio.run(run_demo())
    elif args.task:
        print_banner()
        asyncio.run(run_single_task(args.task, index=1))
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()