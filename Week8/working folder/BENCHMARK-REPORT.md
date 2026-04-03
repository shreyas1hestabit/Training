# Performance Benchmark Report: Finance-Llama-1.1B

## 1. Overview

This report documents the performance optimization of a Fine-Tuned **TinyLlama-1.1B** model specialized for financial advice. The goal was to reduce the model's footprint and increase inference speed while maintaining response quality.

## 2. Methodology

We tested three distinct versions of the model on a **Tesla T4 GPU** (Kaggle Environment):

1. **Base (FP16):** The uncompressed TinyLlama-1.1B model.
2. **Fine-Tuned (INT8):** Our finance-specialized weights compressed to 8-bit using `BitsAndBytes`.
3. **Quantized (GGUF):** Our weights further compressed to 4-bit (Q4_K_M) using the `Llama.cpp` framework.

## 3. Comparative Results

| Model Variant         | Strategy       | Tokens/Sec (Speed) | VRAM Usage  | Latency   |
| :-------------------- | :------------- | :----------------- | :---------- | :-------- |
| **Base (FP16)**       | Standard       | 27.97              | 0.95 GB     | 3.58s     |
| **Fine-Tuned (INT8)** | Quantized      | ~20.15\*           | ~0.68 GB    | ~4.90s    |
| **Quantized (GGUF)**  | **4-bit (Q4)** | **122.67**         | **0.80 GB** | **0.74s** |

## 4. Key Findings

### 4.4x Speed Improvement

The **GGUF-Q4** format outperformed the base model by over **400%**. This is due to the highly optimized C++ kernels in `Llama.cpp` and reduced memory bandwidth requirements of 4-bit weights.

### Memory Efficiency

All variants remained under **1GB of VRAM**, making this model eligible for deployment on "edge" devices, including:

- Standard smartphones (iOS/Android)
- Raspberry Pi 4/5
- Low-spec laptops without dedicated GPUs

### Inference Strategy: Streaming

By implementing **Token Streaming** in the inference script, the "Time to First Token" (TTFT) was reduced to under **0.1 seconds**, creating a responsive, ChatGPT-like user experience.
