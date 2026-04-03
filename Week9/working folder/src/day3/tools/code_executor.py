import io
import contextlib
import os

DATA_DIR = ""

def execute_python_code(code: str) -> str:
    """Execute Python code inside the data directory."""
    output = io.StringIO()
    old_cwd = os.getcwd()
    try:
        os.chdir(DATA_DIR)
        # We provide 'DATA_DIR' inside the globals so the agent can use it
        exec_globals = {
            'pd': __import__('pandas'),
            'np': __import__('numpy'),
            'sqlite3': __import__('sqlite3'),
            'os': __import__('os'),
            'DATA_DIR': DATA_DIR  # Explicitly provide the path
        }
        with contextlib.redirect_stdout(output):
            exec(code, exec_globals)
        return output.getvalue() or "Code executed successfully (no stdout)."
    except Exception as e:
        return f"Python Error: {str(e)}"
    finally:
        os.chdir(old_cwd)