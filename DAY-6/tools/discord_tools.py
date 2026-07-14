import os
import json
import requests
from utils.mcp import mcp

DEFAULT_WEBHOOK = "https://discord.com/api/webhooks/1526457798685364294/QyHKg9NwbU7SyZCQ1EnSfidYRW_fgV1ruwb7J31D1DkxqTeNmgpHSI1tltPu1fwjSf3M"

def get_webhook_url() -> str:
    """Helper function to retrieve the configured Discord webhook URL."""
    return os.getenv("DISCORD_WEBHOOK_URL", DEFAULT_WEBHOOK)

@mcp.tool()
def send_message(msg: str) -> str:
    """
    Send a plain text message to the Discord server via webhook.

    :param msg: The message content to send.
    """
    webhook = get_webhook_url()
    payload = {
        "content": msg
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)
        if response.status_code in [200, 204]:
            return "Message sent successfully."
        else:
            return f"Failed to send message. Status: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"An error occurred while sending message: {str(e)}"

@mcp.tool()
def send_embed_message(
    title: str,
    description: str,
    color_hex: str = "00FF00",
    username: str = None,
    avatar_url: str = None
) -> str:
    """
    Send a rich embed message to the Discord server via webhook.

    :param title: The title of the embed.
    :param description: The description/body of the embed.
    :param color_hex: Optional hex color code for the embed border (e.g. 'FF0000', '3498DB'). Defaults to '00FF00'.
    :param username: Optional username override for the webhook sender.
    :param avatar_url: Optional avatar image URL override for the webhook sender.
    """
    webhook = get_webhook_url()
    
    # Parse hex color
    try:
        color = int(color_hex.lstrip('#'), 16)
    except ValueError:
        color = 0x00FF00  # Default to green if invalid

    embed = {
        "title": title,
        "description": description,
        "color": color
    }
    
    payload = {
        "embeds": [embed]
    }
    
    if username:
        payload["username"] = username
    if avatar_url:
        payload["avatar_url"] = avatar_url

    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)
        if response.status_code in [200, 204]:
            return "Embed message sent successfully."
        else:
            return f"Failed to send embed. Status: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"An error occurred while sending embed: {str(e)}"

@mcp.tool()
def send_file(
    file_path: str,
    content: str = "",
    username: str = None
) -> str:
    """
    Upload and send a file to the Discord server via webhook.

    :param file_path: The absolute or relative path to the file to upload.
    :param content: Optional text content to send along with the file.
    :param username: Optional username override for the webhook sender.
    """
    webhook = get_webhook_url()
    
    if not os.path.exists(file_path):
        return f"Error: File not found at path: {file_path}"
        
    payload = {}
    if content:
        payload["content"] = content
    if username:
        payload["username"] = username

    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f)
            }
            if payload:
                # Discord allows custom parameters via payload_json in multipart requests
                files["payload_json"] = (None, json.dumps(payload), "application/json")
                
            response = requests.post(webhook, files=files)
            if response.status_code in [200, 204]:
                return f"File '{os.path.basename(file_path)}' sent successfully."
            else:
                return f"Failed to send file. Status: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"An error occurred while sending file: {str(e)}"
