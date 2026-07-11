from utils.mcp import mcp

SUPPORTED_MODELS = {
    "Groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it"
    ]
}

@mcp.resource("config://supported-models")
def supported_models():
    return SUPPORTED_MODELS