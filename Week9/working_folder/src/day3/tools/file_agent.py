import os
import pandas as pd

# Global path set by main.py
DATA_DIR = ""

def read_file(filename: str) -> str:
    """Read a file from the data folder."""
    path = os.path.join(DATA_DIR, os.path.basename(filename))
    if not os.path.exists(path):
        return f"Error: {filename} not found."
    
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(path)
            return f"Columns: {list(df.columns)}\nPreview:\n{df.head(5).to_string()}"
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

def write_to_file(filename: str, content: str) -> str:
    """Write text to a file in the data folder."""
    path = os.path.join(DATA_DIR, os.path.basename(filename))
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Saved to {filename}"
    except Exception as e:
        return f"Error: {str(e)}"