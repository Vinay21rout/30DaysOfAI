from utils.mcp import mcp
import json


@mcp.tool()
def validate_json(json_text: str):
    """
    Validate JSON.
    """

    try:
        json.loads(json_text)

        return {
            "valid": True,
            "message": "Valid JSON"
        }

    except Exception as e:

        return {
            "valid": False,
            "error": str(e)
        }


@mcp.tool()
def pretty_json(json_text: str):
    """
    Format JSON.
    """

    data = json.loads(json_text)

    return json.dumps(data, indent=4)


@mcp.tool()
def minify_json(json_text: str):
    """
    Remove spaces from JSON.
    """

    data = json.loads(json_text)

    return json.dumps(data)