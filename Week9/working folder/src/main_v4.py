import asyncio, os, json
from datetime import datetime
from src.memory.memory_agent import MemoryAgent

LOG_FILE = "logs_day4_again_updated_two.json"
def load_logs() -> list:
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []
def save_log(entry: dict) -> None:
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
def log_turn(
    user_input: str,
    response: str,
    memory_status: dict,
    recalled_memories: list,
) -> None:
    """Append one complete conversation turn to logs_day4.json."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "agent_response": response,
        "memory_snapshot": {
            "session_messages": memory_status["session_messages"],
            "vector_entries":   memory_status["vector_entries"],
            "sqlite_facts":     memory_status["long_term"]["facts"],
            "sqlite_episodes":  memory_status["long_term"]["episodes"],
            "turn_count":       memory_status["turn_count"],
        },
        "recalled_memories": recalled_memories,
    }
    save_log(entry)
def log_command(command: str, result: dict) -> None:
    """Log a /command invocation and its output."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "command": command,
        "result": result,
    }
    save_log(entry)

async def main():
    print("\n=== DAY 4: MEMORY-ENABLED AGENT ===")
    print("Commands: /memory  /facts  /episodes  /clear  /reset  /wipe-facts  exit\n")

    agent = MemoryAgent(
        summarise_every=6,
        vector_top_k=3,
        use_vector=True,
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Bye!")
            break
        elif user_input.lower() == "/memory":
            status = agent.memory_status()
            print("\n--- Memory Status ---")
            print(f"  Session messages : {status['session_messages']}")
            print(f"  Vector entries   : {status['vector_entries']}")
            print(f"  SQLite facts     : {status['long_term']['facts']}")
            print(f"  SQLite episodes  : {status['long_term']['episodes']}")
            print(f"  Total turns      : {status['turn_count']}")
            print()
            log_command("/memory", status)
            continue
        elif user_input.lower() == "/facts":
            facts = agent.recall_all_facts()
            if facts:
                print("\n--- Stored Facts ---")
                for k, v in facts.items():
                    print(f"  {v}")
            else:
                print("  (no facts stored yet)")
            print()
            log_command("/facts", {"facts": facts})
            continue
        elif user_input.lower() == "/episodes":
            episodes = agent.recall_recent_episodes(n=5)
            if episodes:
                print("\n--- Recent Episodes ---")
                for ep in episodes:
                    print(f"  [{ep['created'][:19]}] {ep['summary']}")
            else:
                print("  (no episodes stored yet)")
            print()
            log_command("/episodes", {"episodes": episodes})
            continue
        elif user_input.lower() == "/clear":
            agent.session.clear()
            print("[Session memory cleared. Long-term memory intact.]\n")
            log_command("/clear", {"result": "session cleared"})
            continue
        elif user_input.lower() == "/wipe-facts":
            facts = agent.recall_all_facts()
            for key in list(facts.keys()):
                agent.long_term.delete_fact(key)
            if agent.vector:
                agent.vector.delete_by_source("fact")
                agent.vector.delete_by_source("fact_bootstrap")
            print(f"[Wiped {len(facts)} facts from SQLite and vector store.]\n")
            log_command("/wipe-facts", {"wiped_count": len(facts)})
            continue

        recalled = []
        if agent.use_vector and agent.vector and agent.vector.count() > 0:
            recalled = agent.vector.search(user_input, top_k=agent.vector_top_k)
            recalled = [{"text": r["text"], "source": r["source"], "score": r["score"]}
                        for r in recalled]

        response = await agent.chat(user_input)
        print(f"\nAgent: {response}\n")
        log_turn(
            user_input=user_input,
            response=response,
            memory_status=agent.memory_status(),
            recalled_memories=recalled,
        )
if __name__ == "__main__":
    asyncio.run(main())