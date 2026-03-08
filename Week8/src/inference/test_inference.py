import sys
from llama_cpp import Llama

# 1. Initialize the model
# We use n_gpu_layers=-1 to ensure the entire model runs on the Kaggle T4 GPU
print(" Loading Finance-AI (Optimized GGUF)...")
llm = Llama(
    model_path="quantized/model.gguf", 
    n_gpu_layers=-1, 
    n_ctx=1024,      # Context window
    verbose=False    # Keeps the output clean
)

def ask_finance_bot(question):
    # Defining a clear prompt format helps the model stay in 'expert' mode
    prompt = f"Instruction: You are a professional financial advisor. Answer the following question accurately.\n\nQuestion: {question}\n\nResponse:"
    
    print(f"\nPrompt: {question}")
    print(" Response: ", end="")
    
    # 2. Start streaming the response
    # stream=True makes the tokens appear as they are generated
    stream = llm(
        prompt,
        max_tokens=256,
        stop=["Question:", "Instruction:"], # Prevents the model from rambling
        stream=True
    )

    for output in stream:
        token = output["choices"][0]["text"]
        sys.stdout.write(token)
        sys.stdout.flush()
    print("\n" + "-"*50)

# --- EXECUTION ---
if __name__ == "__main__":
    # Test cases to verify the fine-tuning knowledge
    test_questions = [
        "What is the difference between a Bull and a Bear market?",
        "How does high inflation affect my savings?"
    ]
    
    for q in test_questions:
        ask_finance_bot(q)
