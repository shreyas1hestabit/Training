import asyncio
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Import only the agents
from src.agents.research_agent import research_agent
from src.agents.summarizer_agent import summarizer_agent
from src.agents.answer_agent import answer_agent

load_dotenv()

async def save_to_log(user_query, research, summary, final_answer,timings):
    """Saves the structured pipeline results to JSON."""
    log_file = "conversation_logs_hardcode_updated_again.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": user_query,
        "timings":timings,
        "steps": [
            {"agent": "Researcher", "output": research},
            {"agent": "Summarizer", "output": summary},
            {"agent": "Answer_Agent", "output": final_answer}
        ]
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

# async def run_pipeline():
#     print("\n--- ⚡ FAST PIPELINE ONLINE (v0.7.5) ---")
    
#     while True:
#         user_query = input("\nUser Request (or 'exit'): ").strip()
#         if user_query.lower() in ["exit", "quit"]: break
#         if not user_query: continue

#         await research_agent.reset()
#         await summarizer_agent.reset()
#         await answer_agent.reset()

        
#         print(f" Starting Pipeline...")

#         # STEP 1: Research (User -> Researcher)
#         print("Step 1: Researching...")
#         res_result = await research_agent.run(task=user_query)
#         raw_research = res_result.messages[-1].content
#         if len(raw_research) < 20 or "html" in raw_research.lower():
#             print(" Error: Researcher returned rubbish. Retrying...")
#             # Add a retry or just skip to next input
#             continue
#         print(f" Research Complete.")

#         # STEP 2: Summarize (Researcher -> Summarizer)
#         print("Step 2: Summarizing...")
#         sum_result = await summarizer_agent.run(task=f"Summarize this data: {raw_research}")
#         summary_text = sum_result.messages[-1].content
#         print(f" Summary Complete.")

#         # STEP 3: Final Answer (Summarizer -> Answer Agent)
#         print("Step 3: Formatting...")
#         ans_result = await answer_agent.run(task=f"Format this for the user: {summary_text}")
#         final_output = ans_result.messages[-1].content

#         # OUTPUT TO USER
#         print("\n" + "="*40)
#         print(final_output)
#         print("="*40)

#         # LOGGING
#         await save_to_log(user_query, raw_research, summary_text, final_output)

async def run_pipeline():
    print("\n--- ⚡ FAST PIPELINE ONLINE (v0.7.5) ---")
    
    # while True:
    #     user_query = input("\nUser Request (or 'exit'): ").strip()
    #     if user_query.lower() in ["exit", "quit"]: break
    #     if not user_query: continue

    #     # 1. MANUALLY CLEAR CONTEXT (To stop the "French Canadian" gibberish)
    #     # We access the _model_context we defined in the agent files
    #     try:
    #         await research_agent._model_context.clear()
    #         await summarizer_agent._model_context.clear()
    #         await answer_agent._model_context.clear()
    #     except AttributeError:
    #         # Fallback if context isn't initialized yet
    #         pass
    while True:
        user_query = input("\nUser Request (or 'exit'/'clear'): ").strip()
        
        if user_query.lower() in ["exit", "quit"]: break
        
        # Manually clear only when the user wants a fresh start
        if user_query.lower() == "clear":
            for agent in [research_agent, summarizer_agent, answer_agent]:
                if hasattr(agent, "_model_context") and agent._model_context:
                    await agent._model_context.clear()
            print(" Memory cleared!")
            continue

        print(f" Starting Pipeline...")
        start_time = time.time()
        
        # STEP 1: Research
        s1 = time.time()
        print(" Step 1: Researching...")
        res_result = await research_agent.run(task=user_query)
        raw_research = res_result.messages[-1].content
        r_time = round(time.time() - s1, 2)

        # STEP 2: Summarize
        s2 = time.time()
        print(f" Step 2: Summarizing ({r_time}s)...")
        sum_result = await summarizer_agent.run(task=f"Data: {raw_research}")
        summary_text = sum_result.messages[-1].content
        s_time = round(time.time() - s2, 2)

        # STEP 3: Final Answer
        s3 = time.time()
        print(f" Step 3: Formatting ({s_time}s)...")
        # ans_result = await answer_agent.run(task=f"Summary: {summary_text}")
        ans_result = await answer_agent.run(task=f"Original Request: {user_query}. Summary to format: {summary_text}")
        final_output = ans_result.messages[-1].content
        f_time = round(time.time() - s3, 2)

        print(f"\n Pipeline Complete in {round(time.time() - start_time, 2)}s")
        print("="*40 + "\n" + final_output + "\n" + "="*40)

        # LOGGING
        await save_to_log(user_query, raw_research, summary_text, final_output, {"res": r_time, "sum": s_time, "ans": f_time})

if __name__ == "__main__":
    asyncio.run(run_pipeline())