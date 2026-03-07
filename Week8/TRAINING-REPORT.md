# Training Report: Finance-TinyLlama-1.1B

## 1. Model Configuration

- **Base Model:** TinyLlama/TinyLlama-1.1B-Chat-v1.0
- **Fine-Tuning Method:** QLoRA (4-bit Quantization)
- **Rank (r):** 16
- **Alpha:** 32
- **Target Modules:** q_proj, v_proj, k_proj, o_proj

## 2. Hyperparameters

- **Learning Rate:** 2e-4
- **Batch Size:** 4
- **Gradient Accumulation:** 4
- **Epochs:** 3
- **Optimizer:** Paged AdamW 32-bit

## 3. Results

- **Trainable Parameters:** ~1.1M (approx. 0.1% of total)
- **Training Duration:** 04:33
- **Final Loss:** 0.107

## 4. Hardware

- **GPU:** NVIDIA Tesla T4 (15GB VRAM)
- **Precision:** FP16 (BFloat16 disabled due to hardware constraints)
