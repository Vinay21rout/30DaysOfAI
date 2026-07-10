from models.response import MCPResponse


def success(tool, message, data=None):
    return MCPResponse(
        success=True,
        tool=tool,
        message=message,
        data=data
    )


def error(tool, message):
    return MCPResponse(
        success=False,
        tool=tool,
        message=message,
        data=None
    )