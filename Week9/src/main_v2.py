import asyncio, os, json, time, re #re: Regular Expression module. Used to "scrape" specific tasks out of the Planner's conversational text. Its job is to look at the "messy" conversational text from the Planner and extract only the "clean" instructions for the Workers.
from datetime import datetime
from src.utils.config import client
from src.orchestrator.planner import planner_agent
from src.agents.worker_agent import worker_agent
from src.agents.reflection_agent import reflection_agent 
from src.agents.validator import validator_agent

async def save_day2_log(query, plan, detailed_audit, validation):
    log_file = "logs_day2_again_updated.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_query": query,
        "planner_strategy": plan,
        "worker_audit_trail": detailed_audit,
        "validator_verdict": validation
    }
    
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                logs = json.load(f)
        except: logs = []
    
    logs.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)

async def run_dag_orchestration():
    print("\n" + "═"*60)
    print("  DAY 2: DYNAMIC DAG ORCHESTRATOR (PLANNER -> WORKERS -> VALIDATOR)")
    print("═" * 60)
    
    while True:
        user_query = input("\nEnter Request (or 'exit'): ").strip()
        if user_query.lower() in ['exit', 'quit']: break
        if not user_query: continue
        
        # --- PHASE 1: PLANNING ---
        print("\n[Phase 1] Architecting Task Tree...")
        plan_res = await planner_agent.run(task=user_query)
        plan_text = str(plan_res.messages[-1].content)
        
        # Find all occurrences of "TASK: ..."
        tasks = re.findall(r"TASK:\s*(.*)", plan_text, re.IGNORECASE)
        if not tasks:
            tasks = [f"Directly address: {user_query}"]

        # --- PHASE 2: WORKERS (PARALLEL) ---
        print(f"[Phase 2] Launching {len(tasks)} Workers in Parallel...")
        
        async def run_single_worker(i, task_desc):
            start_time = time.time()
            contextual_prompt = (
                f"OVERALL GOAL: {user_query}\n"
                f"YOUR SPECIFIC TASK: {task_desc}\n"
                "INSTRUCTION: Execute and provide data. Do NOT ask for more info."
            )
            res = await worker_agent.run(task=contextual_prompt)
            return {
                "worker_id": i + 1,
                "assigned_task": task_desc,
                "output": str(res.messages[-1].content),
                "duration": round(time.time() - start_time, 2)
            }

        # Gather results concurrently
        detailed_audit = await asyncio.gather(*[run_single_worker(i, t) for i, t in enumerate(tasks)]) #it is our blackboard memory. each worker_agent writes it's output here
        for audit in detailed_audit:
            print(f"  ✓ Worker {audit['worker_id']} finished in {audit['duration']}s")

        # --- PHASE 3: REFLECTION ---
        print("[Phase 3] Synthesizing Results...")
        combined_raw = "\n\n".join([f"--- DATA FROM TASK {d['worker_id']} ---\n{d['output']}" for d in detailed_audit])
        reflection_task = f"USER REQUEST: {user_query}\n\nRAW WORKER DATA:\n{combined_raw}\n\nTASK: Create one polished final answer."
        
        reflect_res = await reflection_agent.run(task=reflection_task)
        final_polished_answer = str(reflect_res.messages[-1].content)

        # --- PHASE 4: VALIDATION ---
        print("[Phase 4] Quality Control Check...")
        val_res = await validator_agent.run(
            task=f"USER REQUEST: {user_query}\n\nFINAL ANSWER:\n{final_polished_answer}"
        )
        validation_status = str(val_res.messages[-1].content)

        # --- FINAL OUTPUT ---
        print("\n" + "═"*50)
        print(f"FINAL ANSWER:\n{final_polished_answer}")
        print("─"*50)
        print(f"VALIDATION VERDICT: {validation_status}")
        print("═"*50)

        await save_day2_log(user_query, plan_text, detailed_audit, validation_status)

if __name__ == "__main__":
    asyncio.run(run_dag_orchestration())