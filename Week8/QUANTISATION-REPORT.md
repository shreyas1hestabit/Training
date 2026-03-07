We have moved from the high-precision training format (FP16) to optimized 8-bit and 4-bit versions.

### Model Specifications

**_Base Model:_** TinyLlama-1.1B (Fine-tuned on Financial Data)

**_Quantization Methods:_** llama.cpp (GGUF) and BitsAndBytes (Safetensors)

**_Target Hardware:_** Consumer-grade CPUs and Mobile Devices (RAM < 2GB)

### final file structure and analysis

| Model Version   | File Format | Precision    | Storage Size | Status              |
| --------------- | ----------- | ------------ | ------------ | ------------------- |
| Reference Model | GGUF        | FP16         | 2.2 GB       | Master Copy         |
| Mid-Range       | Safetensors | INT-8        | 1.1 GB       | High Accuracy       |
| Compressed      | Safetensors | INT-4        | 770 MB       | Standard 4-bit      |
| Optimized Edge  | GGUF        | Q4_0 (4-bit) | 607.23 MB    | Best for Deployment |

### key technical insights

- **_The "GGUF Advantage":_** Our most optimized file is the 607.23 MB GGUF. Although it is also 4-bit (like the 770 MB Safetensors version), it is 21% smaller because the GGUF format eliminates the metadata overhead found in standard Python/Hugging Face folders.

- **_Memory Efficiency:_** By reducing the model to ~607 MB, it can now be loaded into a system with as little as 1.2 GB of total RAM, making it viable for edge computing.

- **_Information Density:_** Despite a 72.4% reduction in total size from the original 2.2 GB file, the model retains the specialized financial weights (for terms like "Liquidity" and "Market Cap") developed during the Day 2 training phase.
