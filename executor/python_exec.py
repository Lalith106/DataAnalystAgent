import pandas as pd
import numpy as np
from data.dataset_store import get_df

import re

def clean_code(code: str):
    # Remove markdown blocks
    code = re.sub(r"```python", "", code)
    code = re.sub(r"```", "", code)

    return code.strip()

def execute_python(code: str) -> str:
    # Get the dataset from the store
    df = get_df()
    
    # Create a local namespace for code execution
    local_namespace = {'pd': pd, 'np': np, 'df': df}
    code = clean_code(code)
    print("------------------code to execute------------------")
    print(code)
    print("---------------------------------------------")
    
    try:
        # Execute the code in the local namespace
        exec(code, {}, local_namespace)
        
        # Capture the result if it's stored in a variable named 'result'
        result = local_namespace.get('result', 'Code executed successfully. No result variable found.')
        return str(result)
    except Exception as e:
        return f"Error executing code: {str(e)}"