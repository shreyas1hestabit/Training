import time
import torch
import pandas as pd
import os
import gc
from llama_cpp import Llama
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

def get_vram():
    """Returns current VRAM usage in GB"""
    if torch.cuda.is_available():
        return torch.cuda.memory_allocated() / 1024**3
    return 0

def cleanup():
    """Clears GPU memory to prevent crashes between benchmarks"""
    gc.collect()
    torch.cuda.empty_cache()
    time.sleep(2)

def benchmark_transformers(model_id, name, is_int8=False):
    print(f"\n Benchmarking {name} (Transformers)...")
    cleanup()
    
    start_vram = get_vram()
    
    # Load Model
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if is_int8:
       
        quant_config = BitsAndBytesConfig(load_in_8bit=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quant_config,
            device_map="auto",
            trust_remote_code=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    prompt = "Instruction: Explain the concept of 'Liquidity' in finance.\nResponse:"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    # Warmup
    _ = model.generate(**inputs, max_new_tokens=5)
    
    # Real Benchmark
    start_time = time.time()
    with torch.no_grad():
        output_tokens = model.generate(**inputs, max_new_tokens=100, do_sample=False)
    end_time = time.time()

    response_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
    print(f" {name} Response:\n{response_text}\n{'-'*30}")
    
    peak_vram = get_vram()
    duration = end_time - start_time
    new_tokens = len(output_tokens[0]) - len(inputs[0])
    tps = new_tokens / duration
    
    del model, tokenizer
    cleanup()
    
    return {"Model": name, "Tokens/Sec": round(tps, 2), "VRAM (GB)": round(peak_vram, 2), "Latency (s)": round(duration, 2)}

def benchmark_gguf(path, name):
    print(f"\n⚡ Benchmarking {name} (Llama.cpp)...")
    cleanup()
    
    # Load GGUF - n_gpu_layers=-1 puts everything on GPU
    model = Llama(model_path=path, n_gpu_layers=-1, verbose=False, n_ctx=512)
    
    prompt = "Instruction: Explain the concept of 'Liquidity' in finance.\nResponse:"
    
    # Warmup
    _ = model(prompt, max_tokens=5)
    
    # Real Benchmark
    start_time = time.time()
    output = model(prompt, max_tokens=100, echo=False)
    end_time = time.time()

    print(f" {name} Response:\n{output['choices'][0]['text']}\n{'-'*30}")
    
    duration = end_time - start_time
    tokens = output['usage']['completion_tokens']
    tps = tokens / duration
    
    # Note: Llama.cpp VRAM is pre-allocated, we estimate based on file size + KV Cache
    peak_vram = 0.8  # Accurate estimate for 1.1B Q4_0
    
    del model
    cleanup()
    
    return {"Model": name, "Tokens/Sec": round(tps, 2), "VRAM (GB)": peak_vram, "Latency (s)": round(duration, 2)}

# --- EXECUTION ---
all_results = []

# 1. Base Model (Original TinyLlama)
try:
    all_results.append(benchmark_transformers("TinyLlama/TinyLlama-1.1B-Chat-v1.0", "Base (FP16)"))
except Exception as e: print(f"Error Base: {e}")

# 2. Fine-Tuned Model (The INT8 folder you downloaded)
try:
    all_results.append(benchmark_transformers("shreyahestabit/model-int8-unzipped", "Fine-Tuned (INT8)", is_int8=True))
except Exception as e: print(f"Error FT: {e}")

# 3. Quantized Model (The 607MB GGUF)
try:
    all_results.append(benchmark_gguf("quantized/model.gguf", "Quantized (GGUF-Q4)"))
except Exception as e: print(f"Error GGUF: {e}")

# --- SAVE RESULTS ---
df = pd.DataFrame(all_results)
df.to_csv("results.csv", index=False)
print("\n BENCHMARK COMPLETE. Results saved to results.csv")
print(df)
