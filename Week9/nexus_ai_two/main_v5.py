# """
# nexus_ai_two/main.py
# ---------------------
# NEXUS AI — Groq Edition Entry Point

# Run:
#     python -m nexus_ai_two.main                     # interactive
#     python -m nexus_ai_two.main --demo              # all 4 demo tasks
#     python -m nexus_ai_two.main --task "your task"  # single task
# """

# import asyncio
# import argparse
# import sys
# from pathlib import Path

# sys.path.insert(0, str(Path(__file__).parent.parent))

# from nexus_ai_two.orchestrator import NexusOrchestrator
# from nexus_ai_two.config import LOGS_DIR


# DEMO_TASKS = [
#     "Plan a startup in AI for healthcare — include business model, MVP, target market, tech stack, and go-to-market strategy.",
#     "Generate backend architecture for a scalable web application — include database design, API structure, caching, auth, and deployment.",
#     "Analyze this CSV file (sales_data.csv) and create a comprehensive business strategy based on the findings.",
#     "Design a RAG pipeline for 50,000 documents — include chunking strategy, embedding model, vector store, retrieval logic, and LLM integration.",
# ]


# def print_banner():
#     print("""
# ╔══════════════════════════════════════════════════════════════╗
# ║        NEXUS AI — Autonomous Multi-Agent System              ║
# ║        Powered by Groq · llama-3.1-8b-instant               ║
# ║        Multi-agent · Memory · Tools · Self-reflection        ║
# ╚══════════════════════════════════════════════════════════════╝
# """)


# def save_report(task: str, report: str, index: int = 0) -> Path:
#     safe = "".join(c if c.isalnum() else "_" for c in task[:40]).strip("_")
#     path = LOGS_DIR / f"report_{index:02d}_{safe}.md"
#     path.write_text(f"# NEXUS AI Report\n\n**Task:** {task}\n\n---\n\n{report}", encoding="utf-8")
#     print(f"\n[NEXUS] Report saved → {path}")
#     return path


# async def run_single(task: str, index: int = 0):
#     nexus  = NexusOrchestrator()
#     report = await nexus.run_with_recovery(task)
#     print("\n" + "="*60)
#     print("FINAL REPORT")
#     print("="*60)
#     print(report)
#     save_report(task, report, index)
#     return report


# async def run_demo():
#     print_banner()
#     nexus = NexusOrchestrator()
#     for i, task in enumerate(DEMO_TASKS, 1):
#         print(f"\n{'─'*60}\nDEMO TASK {i}/{len(DEMO_TASKS)}\n{'─'*60}")
#         report = await nexus.run_with_recovery(task)
#         save_report(task, report, i)
#     stats = nexus.memory.stats()
#     print(f"\n[NEXUS] Done. {stats['tasks']} tasks, {stats['reflections']} reflections stored.")


# async def run_interactive():
#     print_banner()
#     print("Type your task and press Enter. Commands: 'memory' | 'exit'\n")
#     nexus = NexusOrchestrator()
#     count = 0
#     while True:
#         try:
#             task = input("NEXUS> ").strip()
#         except (EOFError, KeyboardInterrupt):
#             print("\n[NEXUS] Goodbye.")
#             break
#         if not task:
#             continue
#         if task.lower() == "exit":
#             print("[NEXUS] Goodbye.")
#             break
#         if task.lower() == "memory":
#             s = nexus.memory.stats()
#             print(f"\n  Tasks: {s['tasks']} | Facts: {s['facts']} | Reflections: {s['reflections']}")
#             for t in nexus.memory.get_recent_tasks(3):
#                 print(f"  [{t['timestamp'][:10]}] {t['task'][:60]}")
#             print()
#             continue
#         count += 1
#         report = await nexus.run_with_recovery(task)
#         save_report(task, report, count)


# def main():
#     parser = argparse.ArgumentParser(description="NEXUS AI — Groq Edition")
#     parser.add_argument("--demo", action="store_true", help="Run all 4 demo tasks")
#     parser.add_argument("--task", type=str,            help="Run a single task")
#     args = parser.parse_args()

#     if args.demo:
#         asyncio.run(run_demo())
#     elif args.task:
#         print_banner()
#         asyncio.run(run_single(args.task, index=1))
#     else:
#         asyncio.run(run_interactive())


# if __name__ == "__main__":
#     main()

"""
nexus_ai_two/main.py
---------------------
NEXUS AI — Groq Edition Entry Point

Run:
    python -m nexus_ai_two.main                     # interactive
    python -m nexus_ai_two.main --demo              # all 4 demo tasks
    python -m nexus_ai_two.main --task "your task"  # single task
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nexus_ai_two.orchestrator import NexusOrchestrator
from nexus_ai_two.config import LOGS_DIR


DEMO_TASKS = [
    "Plan a startup in AI for healthcare — include business model, MVP, target market, tech stack, and go-to-market strategy.",
    "Generate backend architecture for a scalable web application — include database design, API structure, caching, auth, and deployment.",
    "Analyze this CSV file (sales_data.csv) and create a comprehensive business strategy based on the findings.",
    "Design a RAG pipeline for 50,000 documents — include chunking strategy, embedding model, vector store, retrieval logic, and LLM integration.",
]


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        NEXUS AI — Autonomous Multi-Agent System              ║
║        Powered by Groq · llama-3.1-8b-instant                ║
║        Multi-agent · Memory · Tools · Self-reflection        ║
╚══════════════════════════════════════════════════════════════╝
""")


def save_report(task: str, report: str, index: int = 0) -> Path:
    safe = "".join(c if c.isalnum() else "_" for c in task[:40]).strip("_")
    path = LOGS_DIR / f"report_{index:02d}_{safe}.md"
    path.write_text(f"# NEXUS AI Report\n\n**Task:** {task}\n\n---\n\n{report}", encoding="utf-8")
    print(f"\n[NEXUS] Report saved → {path}")
    return path


async def run_single(task: str, index: int = 0):
    nexus  = NexusOrchestrator()
    report = await nexus.run_with_recovery(task)
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(report)
    save_report(task, report, index)
    return report


async def run_demo():
    print_banner()
    nexus = NexusOrchestrator()
    for i, task in enumerate(DEMO_TASKS, 1):
        print(f"\n{'─'*60}\nDEMO TASK {i}/{len(DEMO_TASKS)}\n{'─'*60}")
        report = await nexus.run_with_recovery(task)
        save_report(task, report, i)
    stats = nexus.memory.stats()
    print(f"\n[NEXUS] Done. {stats['tasks']} tasks, {stats['reflections']} reflections stored.")


async def run_interactive():
    print_banner()
    print("Type your task. Follow-up questions are supported — NEXUS remembers context.")
    print("Commands: 'memory' | 'history' | 'clear' | 'reset' | 'exit'\n")

    # Single orchestrator instance — persists across all turns in this session
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

        if task.lower() == "exit":
            print("[NEXUS] Goodbye.")
            break

        elif task.lower() == "memory":
            s = nexus.memory.stats()
            c = nexus.conv.status()
            print(f"\n  === Memory Status ===")
            print(f"  Session turns   : {c['session_turns']}")
            print(f"  Vector entries  : {c['vector_entries']}")
            print(f"  Facts stored    : {c['facts_stored']}")
            print(f"  Tasks completed : {s['tasks']}")
            print(f"  Reflections     : {s['reflections']}")
            print()
            continue

        elif task.lower() == "history":
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

        elif task.lower() == "clear":
            nexus.conv.clear_session()
            print("[Session history cleared. Vector store and facts intact.]\n")
            continue

        elif task.lower() == "reset":
            nexus.conv.reset_all()
            print("[All memory wiped — vector store, facts, and session.]\n")
            continue

        count += 1
        report = await nexus.run_with_recovery(task)
        save_report(task, report, count)


def main():
    parser = argparse.ArgumentParser(description="NEXUS AI — Groq Edition")
    parser.add_argument("--demo", action="store_true", help="Run all 4 demo tasks")
    parser.add_argument("--task", type=str,            help="Run a single task")
    args = parser.parse_args()

    if args.demo:
        asyncio.run(run_demo())
    elif args.task:
        print_banner()
        asyncio.run(run_single(args.task, index=1))
    else:
        asyncio.run(run_interactive())


if __name__ == "__main__":
    main()