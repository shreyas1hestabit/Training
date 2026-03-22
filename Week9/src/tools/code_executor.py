# import sys
# import io

# def local_python_executor(code: str) -> str:
#     """Executes python code locally and returns the standard output."""
#     old_stdout = sys.stdout
#     redirected_output = io.StringIO()
#     sys.stdout = redirected_output
#     try:
#         exec(code)
#         return redirected_output.getvalue()
#     except Exception as e:
#         return f"Python Error: {str(e)}"
#     finally:
#         sys.stdout = old_stdout

# python_tool = {
#     "name": "python_executor",
#     "description": "Execute python code for math or data analysis.",
#     "func": local_python_executor
# }

import sys
import io


def local_python_executor(code: str) -> str:
    """Executes python code locally and returns the standard output."""
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    try:
        exec(code, {})
        output = redirected_output.getvalue()
        return output if output.strip() else "Success: Code ran but produced no output."
    except Exception as e:
        return f"Python Error: {str(e)}"
    finally:
        sys.stdout = old_stdout


python_tool = {
    "name": "python_executor",
    "description": "Execute python code for math or data analysis.",
    "func": local_python_executor,
}