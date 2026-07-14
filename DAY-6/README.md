# Day 6: Restructured Discord MCP Server

This folder contains a modularized and enhanced version of the Discord Model Context Protocol (MCP) server, designed to send messages, rich embeds, and files to a Discord channel via webhooks.

## Architecture & Directory Structure

We split the codebase into clean modules for scalability and easy maintenance:

```
DAY-6/
├── .env                       # Local environment variables (ignored by Git)
├── .env.example               # Template environment variables
├── discord_server.py          # Server entry point (loads env, starts FastMCP stdio server)
├── requirements.txt           # Package dependencies
├── test_discord_tools.py      # Automated console test suite for verifying tools
├── tools/
│   ├── __init__.py            # Python package init
│   └── discord_tools.py       # Discord tool definitions (send_message, send_embed_message, send_file)
└── utils/
    ├── __init__.py            # Python package init
    └── mcp.py                 # FastMCP server configuration
```

---

## Discord Tools Provided

### 1. `send_message`
- **Description**: Sends a basic plain text message to your Discord channel.
- **Parameters**: 
  - `msg` (string): The text contents to send.

### 2. `send_embed_message`
- **Description**: Sends a structured, rich embed message.
- **Parameters**: 
  - `title` (string): Header title of the embed card.
  - `description` (string): Main description/body text.
  - `color_hex` (string, optional): Border hex color (e.g. `'FF5733'`, default is green `'00FF00'`).
  - `username` (string, optional): Override the webhook sender's display name.
  - `avatar_url` (string, optional): Override the webhook sender's profile picture URL.

### 3. `send_file`
- **Description**: Uploads and posts a local file to the Discord channel.
- **Parameters**: 
  - `file_path` (string): Path to the file to upload.
  - `content` (string, optional): Accompanying text message to display above the file.
  - `username` (string, optional): Override the webhook sender's display name.

---

## Setup & Running

### 1. Installation
Install the package dependencies inside your virtual environment:
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in this folder and configure your Discord Webhook URL:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_id/your_webhook_token
```

### 3. Start the MCP Server
To run the server locally on `stdio` transport:
```bash
python discord_server.py
```
Or for local development and testing, run using the FastMCP developer console:
```bash
fastmcp dev discord_server.py
```

### 4. Running Verification Tests
To test all three tools against your configured Discord webhook:
```bash
python test_discord_tools.py
```
