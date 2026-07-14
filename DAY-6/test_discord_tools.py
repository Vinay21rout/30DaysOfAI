import os
from dotenv import load_dotenv
from tools import discord_tools

def main():
    # Load environment variables
    load_dotenv()
    
    print("=== Testing Discord Webhook Tools ===")
    
    # 1. Test send_message
    print("\n1. Testing send_message...")
    msg_res = discord_tools.send_message("Hello from the restructured Discord MCP Server!")
    print(f"Result: {msg_res}")
    
    # 2. Test send_embed_message
    print("\n2. Testing send_embed_message...")
    embed_res = discord_tools.send_embed_message(
        title="Restructured MCP Server",
        description="This message was sent using the new `send_embed_message` tool!",
        color_hex="00FF00",  # Green
        username="Antigravity Test Bot"
    )
    print(f"Result: {embed_res}")
    
    # 3. Test send_file
    print("\n3. Testing send_file...")
    test_file = "test_upload.txt"
    with open(test_file, "w") as f:
        f.write("This is a temporary test file uploaded to Discord via MCP send_file tool.")
        
    try:
        file_res = discord_tools.send_file(
            file_path=test_file,
            content="Uploading a test file!",
            username="Antigravity File Uploader"
        )
        print(f"Result: {file_res}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    main()
