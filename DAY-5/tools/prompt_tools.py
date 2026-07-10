from utils.mcp import mcp
from groq import Groq

from utils.config import GROQ_API_KEY
from utils.config import DEFAULT_MODEL

client = Groq(api_key=GROQ_API_KEY)


@mcp.tool()
def improve_prompt(prompt: str):
    """
    Improve an AI prompt.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Improve prompts for LLMs."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content