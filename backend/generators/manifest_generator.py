from llm.ollama_client import ask_llm
from llm.prompts import MANIFEST_PROMPT
from utils.json_parser import extract_json

def generate_manifest(architecture):
    prompt = f"""
    {MANIFEST_PROMPT}

    Architecture:

    {architecture}
    """
    
    # Manifest expects JSON
    response = ask_llm(prompt, json_mode=True)
    manifest = extract_json(response)
    
    if manifest is None:
        manifest = {"files": []}
        
    files = manifest.get("files", [])
    if not isinstance(files, list):
        files = []
        
    required = [
        "package.json",
        "README.md",
        "src/main.jsx",
        "src/App.jsx"
    ]
    
    for file in required:
        if file not in files:
            files.append(file)
            
    manifest["files"] = files
    return manifest
