import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import the FastMCP server instance
from utils.mcp import mcp

# Import the tools to register them
from tools import discord_tools

if __name__ == "__main__":
    # Start the server using stdio transport
    mcp.run(transport="stdio")