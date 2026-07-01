from .llm import ask_llm
from .prompts import GENERATOR_PROMPT


def generate_code(user_prompt: str):

    answer = ask_llm(
        GENERATOR_PROMPT,
        user_prompt
    )

    return {
        "response": answer
    }