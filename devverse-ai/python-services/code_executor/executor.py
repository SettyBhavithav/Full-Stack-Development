import sys
import io
import traceback
from contextlib import redirect_stdout

def execute_python_code(code: str):
    """
    Executes a string of Python code and returns the printed output or error.
    Note: For a true production system, this should run in a sandboxed Docker container 
          or gVisor to prevent malicious code execution.
    """
    # Capture standard output
    f = io.StringIO()
    result_text = ""
    error_text = ""
    
    with redirect_stdout(f):
        try:
            # Execute the code in a confined dictionary scope
            exec_scope = {}
            exec(code, exec_scope)
            result_text = f.getvalue()
        except Exception as e:
            error_text = traceback.format_exc()
            
    if error_text:
        return {"status": "error", "output": error_text}
    
    return {"status": "success", "output": result_text}

