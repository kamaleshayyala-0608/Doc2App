from llm.ollama_client import ask_llm
from llm.prompts import VALIDATION_PROMPT
import re

def validate_file(code):
    prompt = f"""
    {VALIDATION_PROMPT}
    
    Code to review:
    ```
    {code}
    ```
    """
    
    response = ask_llm(prompt, json_mode=False)
    
    # Try to extract and concatenate all code blocks first
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", response, re.DOTALL)
    if blocks:
        return "\n\n".join(b.strip() for b in blocks).strip()
        
    # Check for conversational prefixes; discard validation if found
    lower_res = response.lower().strip()
    conversational_prefixes = ["here is", "the code", "this is", "corrected code", "i have", "sure", "ok", "yes", "the provided"]
    for prefix in conversational_prefixes:
        if lower_res.startswith(prefix):
            print("Warning: Validation response seems conversational. Discarding validation.")
            return code
            
    # Fallback to stripping fences manually
    response = re.sub(r"```[a-zA-Z]*\n", "", response)
    response = re.sub(r"```", "", response).strip()
    
    return response
