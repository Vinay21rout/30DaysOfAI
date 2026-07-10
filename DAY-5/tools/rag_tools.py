from utils.mcp import mcp


@mcp.tool()
def clean_text(text: str):
    """
    Clean text before chunking.
    """

    return " ".join(text.split())


@mcp.tool()
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
):
    """
    Split text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks