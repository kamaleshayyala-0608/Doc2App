import json
from llm.ollama_client import ask_llm
from llm.prompts import FILE_GENERATION_PROMPT
import re

def generate_file(file_path, architecture, generated_files, requirements=None):
    generated_context = "\n".join(generated_files.keys())
    
    req_context = f"\nRequirements:\n{requirements}\n" if requirements else ""
    
    prompt = f"""
    {FILE_GENERATION_PROMPT}
    {req_context}
    Architecture:
    {architecture}

    Previously generated files:
    {generated_context}

    Generate ONLY:
    {file_path}
    """
    
    # We want raw code, unless it is a JSON file, which we want as JSON
    is_json = file_path.endswith(".json")
    response = ask_llm(prompt, json_mode=is_json)
    
    if is_json:
        from utils.json_parser import extract_json
        data = extract_json(response)
        if data is not None:
            return json.dumps(data, indent=2)
        try:
            data = json.loads(response)
            return json.dumps(data, indent=2)
        except Exception:
            pass
            
    # Try to extract and concatenate all code blocks
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", response, re.DOTALL)
    if blocks:
        return "\n\n".join(b.strip() for b in blocks).strip()
        
    # Fallback to stripping fences manually if extraction failed
    response = re.sub(r"```[a-zA-Z]*\n", "", response)
    response = re.sub(r"```", "", response).strip()
    
    return response
