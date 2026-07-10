# 🚀 Day 05 — AICore MCP: Suite of AI Engineering MCP Tools

A powerful Model Context Protocol (MCP) server built with **FastMCP** that provides LLMs (in Claude Desktop, Cursor, or other MCP-compatible clients) with a comprehensive suite of utilities for **AI Engineering, Token Estimation, RAG preprocessing, JSON manipulation, and Dataset analysis**.

---

## 📌 Features & Tools

The server organizes its utilities into modules under `tools/`:

### 1. 🪙 Token Tools (`tools/token_tools.py`)
- **`estimate_tokens`**: Computes the exact number of tokens in a string using `tiktoken` (`cl100k_base` encoding).
- **`text_statistics`**: Provides basic statistics (character count, word count, line count, paragraphs, estimated reading and speaking time).

### 2. 📄 Markdown Tools (`tools/markdown_tools.py`)
- **`markdown_to_html`**: Converts raw markdown into HTML markup.
- **`extract_headers`**: Extracts all headers (`#` to `######`) from a document.
- **`count_markdown_elements`**: Counts headers, code blocks, lists, links, and images.

### 3. 📦 JSON Tools (`tools/json_tools.py`)
- **`validate_json`**: Verifies if a JSON string is syntactically valid and returns parsing errors if not.
- **`pretty_json`**: Auto-indents and formats a JSON string.
- **`minify_json`**: Removes whitespace and minifies JSON strings.

### 4. 📊 Dataset Tools (`tools/dataset_tools.py`)
- **`dataset_summary`**: Performs automatic exploratory analysis on a CSV file (row/column counts, column names, missing value counts, and duplicates).
- **`detect_target_column`**: Automatically inspects the dataset to guess the label/target column (defaults to the last column).

### 5. ✂️ RAG Tools (`tools/rag_tools.py`)
- **`clean_text`**: Normalizes and cleans whitespace in raw text before processing.
- **`chunk_text`**: Chunks a document into overlapping segments of customizable size and overlap for vector ingestion.

### 6. 🔗 Embedding & Similarity Tools (`tools/embedding_tools.py`)
- **`text_similarity`**: Computes the cosine similarity score between two texts using TF-IDF feature extraction.

### 7. 💡 Prompt Engineering Tools (`tools/prompt_tools.py`)
- **`improve_prompt`**: Optimizes and improves user-written prompts for LLMs using **Groq**'s `llama-3.3-70b-versatile` model.

---

## 🛠 Tech Stack
- **FastMCP (Model Context Protocol)**
- **Groq API**
- **Tiktoken**
- **Pandas**
- **Scikit-Learn**
- **Markdown**

---

## 🚀 Running the Server

### Prerequisite: Environment Setup
1. Create your `.env` file inside `DAY-5/`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### Option 1: Running in Dev Mode (Inspector UI)
From the `DAY-5` directory, run:
```bash
mcp dev server.py
```
This boots the server and opens the interactive MCP Inspector UI in your browser for live testing.

### Option 2: Registering in Cursor or Claude Desktop
Add the following configuration block:

#### **Claude Desktop Config (`%APPDATA%\Claude\claude_desktop_config.json`)**:
```json
{
  "mcpServers": {
    "aicore-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "mcp",
        "run",
        "c:/Users/ACER/OneDrive/Desktop/30DaysOfAI-CHALLENGE-IN-PUBLIC/DAY-5/server.py"
      ],
      "env": {
        "GROQ_API_KEY": "your_groq_api_key_here"
      }
    }
  }
}
```
