## 1. Executive Summary

This project involved fine-tuning a **TinyLlama-1.1B** model on financial datasets, quantizing it for edge-device compatibility, and deploying it as a high-performance local API.

---

## 2. The Journey: Step-by-Step

### Phase 1: Fine-Tuning (Days 1-2)

- **Dataset:** Generated synthetic dataset.
- **Technique:** Employed **LoRA (Low-Rank Adaptation)** to train the model on specialized financial terminology while keeping the base weights frozen.
- **Goal:** Improve the model's ability to explain complex financial concepts like "liquidity," "dividends," and "market volatility."

### Phase 2: Quantization (Day 3)

- **Problem:** The original FP16 model was too large (~2.2GB) and slow for standard CPUs.
- **Solution:** Converted the model to **GGUF (4-bit Q4_K_M)** format.
- **Result:** Reduced model size to **~700MB** and improved inference speed by **400%**.

### Phase 3: Benchmarking (Day 4)

- **Hardware:** Tested on Tesla T4 (Kaggle) and local Intel/AMD CPU.
- **Metrics:** \* **FP16:** 27 tokens/sec | 2.2GB RAM
  - **GGUF (4-bit):** 120+ tokens/sec | 0.8GB RAM
- **Conclusion:** GGUF is the superior format for local deployment and low-resource environments.

### Phase 4: Production Deployment (Day 5)

- **Infrastructure:** Built a **FastAPI** microservice.
- **Architecture:** Implemented a **Singleton Model Loader** to ensure the model stays in memory, reducing request latency.
- **API Endpoints:** Created `/generate` for raw completion and `/chat` for structured interaction.

---

## 3. Technical Challenges & Solutions

- **Environment Conflicts:** Solved local installation "hanging" by utilizing pre-compiled CPU-specific wheels for `llama-cpp-python`.
- **Path Management:** Used `os.path.abspath` logic in `config.py` to ensure the API works on both Kaggle and local VS Code without manual path edits.

---
