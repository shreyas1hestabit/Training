import asyncio, os, time, json #Essential for Agentic AI. Agents often wait for LLM responses; asyncio allows the program to "pause" and "resume" without freezing.
from datetime import datetime
from dotenv import load_dotenv
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

async def run_pipeline():
    print("\n--- ⚡ FAST PIPELINE ONLINE (v0.7.5) ---")
    while True: #Keeps the application alive so you can have a conversation rather than running the script once and it dying.
        user_query = input("\nUser Request (or 'exit'/'clear'): ").strip() #strip is for data sanitization. it removes whitespaces from the begining and end of string.
        
        if user_query.lower() in ["exit", "quit"]: break
        if user_query.lower() == "clear": #Episodic Memory. This line explicitly wipes the "10-message buffer" we set in the agents.
            for agent in [research_agent, summarizer_agent, answer_agent]: #You are looping through every specialized worker you created. You treat them as a group so you don't have to write the reset logic three times.
                if hasattr(agent, "_model_context") and agent._model_context: #(agent, "_model_context") ----> checks: "Does this agent actually have a memory object attached to it?"
                    # agent._model_context ----> Sometimes an agent can have a memory slot, but it’s currently set to None (empty/null). This happens if you initialized the agent without a model_context parameter.
                    #both are necessary for clear command to run.
                    # example--> at entry do you have wallet (hasattr(agent, "_model_context")) and do you have money in that wallet (agent._model_context).
                    await agent._model_context.clear()
            print(" Memory cleared!")
            continue

        print(f" Starting Pipeline...")
        start_time = time.time() #exact time the pipeline of three agents start
        s1 = time.time() #A temporary "lap timer" for the Research Agent.
        print(" Step 1: Researching...")
        res_result = await research_agent.run(task=user_query)
        raw_research = res_result.messages[-1].content #extracting only the final answer.
        r_time = round(time.time() - s1, 2)

        s2 = time.time()
        print(f" Step 2: Summarizing ({r_time}s)...")
        sum_result = await summarizer_agent.run(task=f"Data: {raw_research}")
        summary_text = sum_result.messages[-1].content
        s_time = round(time.time() - s2, 2)

        s3 = time.time()
        print(f" Step 3: Formatting ({s_time}s)...")
        ans_result = await answer_agent.run(task=f"Original Request: {user_query}. Summary to format: {summary_text}")
        final_output = ans_result.messages[-1].content
        f_time = round(time.time() - s3, 2)

        print(f"\n Pipeline Complete in {round(time.time() - start_time, 2)}s") #From the moment the user hit Enter to the final polite response, it took X seconds.
        print("="*40 + "\n" + final_output + "\n" + "="*40)

        await save_to_log(user_query, raw_research, summary_text, final_output, {"res": r_time, "sum": s_time, "ans": f_time})

if __name__ == "__main__":
    asyncio.run(run_pipeline())