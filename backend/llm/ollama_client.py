import ollama

def ask_llm(prompt, json_mode=True):
    options = {
        "num_ctx": 8192,
        "temperature": 0.2
    }
    
    kwargs = {
        "model": "qwen2.5-coder:3b",
        "keep_alive": "1h",
        "options": options,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    if json_mode:
        kwargs["format"] = "json"
        
    response = ollama.chat(**kwargs)

    return response["message"]["content"]
