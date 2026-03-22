# import os

# def file_manager(action: str, file_name: str, content: str = "") -> str:
#     """Reads or writes local files. Actions: 'read' or 'write'."""
#     try:
#         if action == "read":
#             if not os.path.exists(file_name):
#                 return f"Error: {file_name} not found."
#             with open(file_name, "r") as f:
#                 return f.read()
#         elif action == "write":
#             with open(file_name, "w") as f:
#                 f.write(content)
#             return f"Success: File {file_name} saved."
#         return "Error: Use 'read' or 'write'."
#     except Exception as e:
#         return f"File Error: {str(e)}"

# file_tool = {
#     "name": "file_manager",
#     "description": "Read or write local files like .csv or .txt.",
#     "func": file_manager
# }

import os


def file_manager(action: str, file_name: str, content: str = "") -> str:
    """Reads or writes local files. Actions: 'read' or 'write'."""
    try:
        if action == "read":
            if not os.path.exists(file_name):
                return f"Error: {file_name} not found."
            with open(file_name, "r", encoding="utf-8") as f:
                return f.read()
        elif action == "write":
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Success: File {file_name} saved."
        return "Error: Use 'read' or 'write'."
    except Exception as e:
        return f"File Error: {str(e)}"


file_tool = {
    "name": "file_manager",
    "description": "Read or write local files like .csv or .txt.",
    "func": file_manager,
}