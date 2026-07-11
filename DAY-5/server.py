from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel,Field

from tools import token_tools
from tools import prompt_tools
from tools import json_tools
from tools import dataset_tools
from tools import rag_tools
from tools import embedding_tools
from tools import markdown_tools

from resources import resource

from utils.mcp import mcp


@mcp.tool()
def ping():
    """ 
   Health check.
    """
    return {
        "status": "running",
        "server": "AICore MCP"
    }

   


if __name__ == "__main__":
    mcp.run()

