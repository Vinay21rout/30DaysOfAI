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
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "think of you as prompt engineer so simply takes the prompt and improve it as per the llm to provide quality output"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content