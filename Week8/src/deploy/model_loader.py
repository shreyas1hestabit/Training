import os
from llama_cpp import Llama
from src.deploy.config import Config

class ModelLoader:
    _instance = None

    @classmethod
    def get_model(cls):
        if cls._instance is None:
            if not os.path.exists(Config.MODEL_PATH):
                raise FileNotFoundError(f" Model not found! Ensure your .gguf file is in: {Config.MODEL_PATH}")
            
            print(f" Loading Finance-LLM into RAM...")
            cls._instance = Llama(
                model_path=Config.MODEL_PATH,
                n_gpu_layers=0,  # Forced to 0 for your CPU
                n_threads=Config.THREADS,
                n_ctx=Config.CONTEXT_SIZE,
                verbose=False
            )
        return cls._instance