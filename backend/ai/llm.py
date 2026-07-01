import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_llm(system_prompt: str, user_prompt: str):

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        temperature=0.2,
        max_tokens=1200,
    )

    return response.choices[0].message.content