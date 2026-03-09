import os

class Config:
    # Finds the folder where 'deploy' is located
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Points to /quantized/model.gguf
    MODEL_PATH = os.path.join(BASE_DIR, "quantized", "model.gguf")
    
    # Optimization for your CPU
    THREADS = os.cpu_count() or 4
    CONTEXT_SIZE = 2048