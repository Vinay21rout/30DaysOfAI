from utils.mcp import mcp
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")


@mcp.tool()
def estimate_tokens(text: str):
    """
    Estimate the number of tokens in a text.
    """

    tokens = len(encoding.encode(text))

    return {
        "characters": len(text),
        "words": len(text.split()),
        "tokens": tokens,
    }


@mcp.tool()
def text_statistics(text: str):
    """
    Return basic text statistics.
    """

    words = text.split()

    return {
        "characters": len(text),
        "words": len(words),
        "lines": len(text.splitlines()),
        "paragraphs": len([p for p in text.split("\n\n") if p.strip()]),
        "reading_time_minutes": round(len(words) / 200, 2),
        "speaking_time_minutes": round(len(words) / 130, 2),
    }