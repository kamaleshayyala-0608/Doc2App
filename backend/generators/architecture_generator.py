from llm.ollama_client import ask_llm
from llm.prompts import ARCHITECTURE_PROMPT


def generate_architecture(requirements):

    prompt = f"""
    {ARCHITECTURE_PROMPT}

    Requirements:
    {requirements}
    """

    response = ask_llm(prompt)

    return response
