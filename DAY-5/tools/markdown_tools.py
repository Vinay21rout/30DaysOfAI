from utils.mcp import mcp
import markdown
import re


@mcp.tool()
def markdown_to_html(markdown_text: str) -> str:
    """
    Convert Markdown text to HTML.
    """
    return markdown.markdown(markdown_text)


@mcp.tool()
def extract_headers(markdown_text: str):
    """
    Extract all headers (H1-H6) from Markdown text to help generate TOC or inspect structure.
    """
    headers = []
    for line in markdown_text.splitlines():
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            headers.append({
                "level": level,
                "text": text
            })
    return headers


@mcp.tool()
def count_markdown_elements(markdown_text: str):
    """
    Count various Markdown elements such as headers, code blocks, lists, links, and images.
    """
    headers = len(re.findall(r'^(#{1,6})\s+', markdown_text, re.MULTILINE))
    code_blocks = len(re.findall(r'^```', markdown_text, re.MULTILINE)) // 2
    links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_text))
    images = len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', markdown_text))
    unordered_lists = len(re.findall(r'^[\s]*[-\*\+]\s+', markdown_text, re.MULTILINE))
    ordered_lists = len(re.findall(r'^[\s]*\d+\.\s+', markdown_text, re.MULTILINE))

    return {
        "headers": headers,
        "code_blocks": code_blocks,
        "links": links - images, # subtract images as they also match link pattern
        "images": images,
        "unordered_list_items": unordered_lists,
        "ordered_list_items": ordered_lists
    }