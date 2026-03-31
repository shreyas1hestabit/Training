import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext

load_dotenv()

client = OpenAIChatCompletionClient(
    model=os.getenv("MODEL_NAME"),
    base_url=os.getenv("OLLAMA_BASE_URL"),
    api_key=os.getenv("OLLAMA_API_KEY"),
    model_info={
        "vision": False, #Tells the agent not to try and "look" at images.
        "function_calling": True, #This tells AutoGen that this model is smart enough to use tools
        "json_output": False, #Disables the specific "JSON Mode." You are using raw text or structured output instead.
        "family": "unknown",
        "structured_output": False
    },
    # CRITICAL: This stops the "rubbish" output
    extra_kwargs={
        "temperature": 0,    # Forces deterministic, factual output
        "top_p": 0.1,        #top_p --> probability filter
        # Limits the vocabulary to the most likely words. Nucleus Sampling." It tells the model to only consider the top 10% of most probable words. It cuts out the "weird" or "random" words that cause hallucinations.
        "max_tokens": 800,    # Prevents the model from rambling forever
        "repeat_penalty": 1.2, # Prevents the model from looping on the same words
        "seed": 42             # Ensures consistent results
    }
)

memory_window = BufferedChatCompletionContext(buffer_size=10) #bufferedchatcompletioncontext follows FIFO logic.

answer_agent = AssistantAgent(
    name="AnswerBot",
    model_client=client,
    # system_message="""ROLE: PR Interface.
    # TASK: Format the provided summary into a polite response.
    # STRICT CONDITION: If the text contains 'MISSION DISPOSIBLE' or 'NO DATA FOUND', you must reply with ONLY that exact phrase and NOTHING else. 
    # No greetings, no sign-offs, and no apologies if that condition is met.
    # Otherwise, wrap the bullets in a professional greeting and closing.""",
    system_message="""ROLE: PR Interface.
    TASK: Format the summary into a polite response.
    CONDITION: Only use 'MISSION DISPOSIBLE' if the summary is completely empty or contains a total failure message. 
    Otherwise, synthesize a professional response from the available bullets.""",
    model_context=memory_window,
)