import asyncio, os, json, time, re
from datetime import datetime
from src.utils.config import client
from src.orchestrator.planner import planner_agent
from src.agents.worker_agent import worker_agent
from src.agents.validator import validator_agent

async def save_day2_log(query, plan, detailed_audit, validation):
    """Saves the DAG execution details to logs_day2.json"""
    log_file = "logs_day2_again.json"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_query": query,
        "worker_count": len(detailed_audit),
        "planner_strategy": plan,
        "worker_audit_trail": detailed_audit,
        "validator_verdict": validation
    }

    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                logs = json.load(f)
        except:
            logs = []
            
    logs.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)
    print(f"\nLogged Dynamic Audit Trail ({len(detailed_audit)} workers) to {log_file}")

async def run_dag_orchestration():
    print("\n--- DAY 2: DYNAMIC DAG ORCHESTRATOR ONLINE ---")
    
    while True:
        user_query = input("\nEnter Request (or 'exit'): ").strip()
        if user_query.lower() == 'exit':
            break
        if not user_query:
            continue

        # Phase 1: Planning
        print("\nPhase 1: Planning Task Tree...")
        plan_res = await planner_agent.run(task=user_query)
        plan = str(plan_res.messages[-1].content)
        
        # Extract tasks using Regex
        tasks = re.findall(r"TASK \d+:.*", plan, re.IGNORECASE)
        
        # Hardware Safety Cap
        if len(tasks) > 3:
            print(f"Planner requested {len(tasks)} tasks. Capping to 3 for hardware stability.")
            tasks = tasks[:3]
                
        if not tasks:
            print("Planner failed to create tasks. Defaulting to single task.")
            tasks = [f"TASK 1: {user_query}"]

        # Phase 2: Execution
        num_workers = len(tasks)
        print(f"Phase 2: Launching {num_workers} Workers...")
        start_time = time.time()
        
        detailed_audit = []
        for i, t in enumerate(tasks):
            print(f"  > Processing Worker {i+1}/{num_workers}...")
            w_start = time.time()
            
            # Agents in v0.7.x are stateless by default per .run() call
            res = await worker_agent.run(task=t)
            w_end = round(time.time() - w_start, 2)
            
            detailed_audit.append({
                "worker_id": i + 1,
                "assigned_task": t,
                "output": str(res.messages[-1].content),
                "duration": w_end
            })
            print(f"  Worker {i+1} finished in {w_end}s")
        
        combined_data = "\n\n".join([item["output"] for item in detailed_audit])
        print(f"All {num_workers} Workers finished in {round(time.time() - start_time, 2)}s")

        # Phase 3: Validation
        print("Phase 3: Validating Multi-Agent Output...")
        val_res = await validator_agent.run(
            task=f"User Query: {user_query}\n\nAggregated Data:\n{combined_data}"
        )
        validation_status = str(val_res.messages[-1].content)

        print("\n" + "="*50)
        print(f"FINAL VALIDATION STATUS:\n{validation_status}")
        print("="*50)

        # Log results
        await save_day2_log(user_query, plan, detailed_audit, validation_status)

if __name__ == "__main__":
    asyncio.run(run_dag_orchestration())