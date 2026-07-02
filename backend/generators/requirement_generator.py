from llm.ollama_client import ask_llm
from llm.prompts import REQUIREMENT_PROMPT


def generate_requirements(context):

    prompt = f"""
    {REQUIREMENT_PROMPT}

    Documentation:
    {context}
    """

    response = ask_llm(prompt)

    return response
