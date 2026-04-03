import json
import os
import numpy as np
from datetime import datetime
from typing import List, Dict

CHAT_LOG_FILE = "src/logs/CHAT-LOGS.json"
MAX_MEMORY = 5

class NpEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,np.integer):
            return int(obj)
        if isinstance(obj,np.floating):
            return float(obj)
        if isinstance(obj,np.ndarray):
            return obj.tolist()
        return super(NpEncoder,self).default(obj) 
class MemoryStore:
    def __init__(self):
        if not os.path.exists(CHAT_LOG_FILE):
            with open(CHAT_LOG_FILE, "w") as f:
                json.dump([], f)

    def _load_logs(self) -> List[Dict]:
        with open(CHAT_LOG_FILE, "r") as f:
            return json.load(f)

    def _save_logs(self, logs: List[Dict]):
        with open(CHAT_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4, cls=NpEncoder)

    def add_interaction(self, interaction: Dict):
        logs = self._load_logs()
        logs.append(interaction)
        self._save_logs(logs)

    def get_last_messages(self, n: int = MAX_MEMORY) -> List[Dict]:
        logs = self._load_logs()
        return logs[-n:]

    def format_memory_for_prompt(self) -> str:
        messages = self.get_last_messages()
        formatted = ""
        for m in messages:
            formatted += f"User: {m['question']}\nAssistant: {m['answer']}\n\n"
        return formatted