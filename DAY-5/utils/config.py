"""
Global configuration for AICore MCP
"""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

DEFAULT_MODEL = "llama-3.3-70b-versatile"

MAX_CHUNK_SIZE = 1000

DEFAULT_CHUNK_OVERLAP = 200