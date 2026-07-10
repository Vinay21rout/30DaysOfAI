from typing import Any
from pydantic import BaseModel


class MCPResponse(BaseModel):
    success: bool
    tool: str
    message: str
    data: Any = None