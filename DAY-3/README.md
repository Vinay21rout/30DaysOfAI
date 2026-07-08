# Day 3: Skills-Powered Agentic System

A safe, modular, and dynamic agentic routing system that uses LLMs (via Groq and Llama 3.1) to dynamically load, install, and execute modular tools ("skills") from local directories, GitHub repositories, or npm packages.

## 🚀 Key Features

* **Dynamic Skill Routing**: The agent uses an LLM to analyze your query and determine the appropriate action (routing to a specific tool within a skill, installing a new skill, or chatting).
* **Robust Tool Normalization**: Supports complex tool definitions or simple string-defined tools, which automatically default to running `python <skill_dir>/<tool_name>.py`.
* **Zero-Shell Execution & Sandbox Isolation**: Spawns tool executables directly without launching a command shell, preventing shell-injection vectors.
* **Command & Path Sanitization**: Blocks relative path execution exploits and restricts tools to a predefined allowlist of system executables (`python`, `python3`, `node`, `npm`, `git`, `bash`, `sh`).
* **Path Traversal Shield**: Verifies resolved skill directory paths using robust, case-insensitive containment assertions (via Python's `pathlib`).
* **Process CWD Isolation**: Automatically sets the subprocess working directory to the targeted skill folder, enabling proper local script imports and relative file loads within skills.

---

## 📂 Project Structure

```text
DAY-3/
├── skills/                     # Local registry of installed/created skills
│   └── calculator/             # Example skill directory
│       ├── skill.json          # Tool metadata & configs
│       ├── add.py              # Tool script (execution via env variables)
│       └── subtract.py         # Tool script (string-defined tool fallback)
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── skills-powered-agentic-system.py  # Main agent entry point
```

---

## 🛠️ Installation & Setup

1. Make sure you have activated your Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file in the `DAY-3` directory containing your Groq API key:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```

---

## ⚙️ How Skills Work

Skills are self-contained modules placed inside the `skills/` folder. Each skill has a `skill.json` configuration file.

### Example `skill.json` Configuration:
```json
{
  "name": "calculator",
  "description": "A skill to perform basic arithmetic operations like addition and subtraction.",
  "prompt": "Use this skill to add or subtract numbers.",
  "tools": [
    {
      "name": "add",
      "command": ["python", "add.py"],
      "args_as": "env"
    },
    "subtract"
  ]
}
```

* **Dict-defined Tools**: Specify a custom CLI command sequence (e.g. `["python", "add.py"]`) and argument delivery strategy (e.g. `"args_as": "env"` or `"args_as": "args"`).
* **String-defined Tools**: Provide a simple name (e.g. `"subtract"`). The system automatically resolves this to execute `python <skill_dir>/subtract.py` as an environment-isolated task.

---

## 🎮 Running the Agent

Start the terminal agent:
```bash
python skills-powered-agentic-system.py
```

### Examples of Prompt Commands:
* **Using a skill**: `add 5 and 10 using the calculator`
* **Installing a skill from GitHub**: `install github repository https://github.com/username/repo-name as my-skill`
* **Installing a skill from npm**: `install npm package some-package-name as my-skill`
* **General Conversation**: `explain the concept of agentic design patterns`
