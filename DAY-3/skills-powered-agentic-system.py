# skills_powered_agentic_system.py

import os
import sys
import io
import re
import json
import shutil

# Force UTF-8 for standard output/error to prevent UnicodeEncodeErrors on Windows
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import html
import subprocess
import urllib.parse
from typing import Dict, List, Any
from pathlib import Path
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Security Helpers
# -----------------------------
SKILLS_BASE_DIR = os.path.realpath("./skills")
ALLOWED_EXECUTABLES = {"python", "python3", "node", "npm", "git", "bash", "sh"}

def sanitize_skill_name(name: str) -> str:
    """Allow only alphanumeric, dash, underscore. Prevents path traversal."""
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", name):
        raise ValueError(f"Invalid skill name: '{name}'. Only letters, numbers, - and _ allowed.")
    return name

def safe_skill_path(skill_name: str) -> str:
    """Resolve skill directory and assert it stays within SKILLS_BASE_DIR."""
    base = Path(SKILLS_BASE_DIR).resolve()
    target = base.joinpath(skill_name).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(f"Path traversal detected for skill: '{skill_name}'")
    return str(target)

def validate_command(command: List[str]) -> List[str]:
    """Ensure the executable is in the allowlist."""
    if not command:
        raise ValueError("Empty command.")
    # Dynamically resolve python/python3 to the current safe sys.executable
    if command[0].lower() in ("python", "python3"):
        command[0] = sys.executable
        return command
    # Block path separators to prevent executing local binaries masquerading as allowed names
    if "/" in command[0] or "\\" in command[0] or os.path.dirname(command[0]) != "":
        raise ValueError(f"Executable path must not contain directories: '{command[0]}'")
    exe = os.path.basename(command[0]).lower()
    # Strip .exe suffix on Windows
    exe = exe.replace(".exe", "")
    if exe not in ALLOWED_EXECUTABLES:
        raise ValueError(f"Executable '{command[0]}' is not allowed. Allowed: {ALLOWED_EXECUTABLES}")
    return command

def validate_url(url: str) -> str:
    """Only allow http/https URLs."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme '{parsed.scheme}'. Only http/https allowed.")
    return url

def parse_llm_json(content: str) -> dict:
    """Parse JSON from LLM response, stripping markdown fences if present."""
    content = content.strip()
    # Strip ```json ... ``` or ``` ... ``` wrappers
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    return json.loads(content.strip())

def safe_print(label: str, value: str):
    """Print the value directly to the console."""
    print(f"{label}{value}")

def force_rmtree(path: str):
    """Delete a directory path on Windows, clearing read-only permissions if needed."""
    import stat
    def onerror(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)

# -----------------------------
# Skill Class
# -----------------------------
class Skill:
    def __init__(self, name: str, description: str, prompt: str, tools: List[Dict]):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.tools = tools  # list of tool dicts from skill.json

    def get_tool(self, tool_name: str) -> Dict:
        for t in self.tools:
            if t.get("name") == tool_name:
                return t
        return None

    def __repr__(self):
        return f"<Skill: {self.name}>"

# -----------------------------
# Skill Registry
# -----------------------------
class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}

    def add_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def get_skill(self, name: str) -> Skill:
        return self.skills.get(name)

    def list_skills(self):
        return list(self.skills.keys())

# -----------------------------
# Skill Loader
# -----------------------------
class SkillLoader:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def install_from_github(self, repo_url: str, skill_name: str, subdir: str = None):
        try:
            skill_name = sanitize_skill_name(skill_name)
            repo_url = validate_url(repo_url)
            skill_dir = safe_skill_path(skill_name)
            if subdir:
                # Sanitize subdir path: allow alphanumeric, slash, dash, underscore
                if not re.fullmatch(r"[a-zA-Z0-9_\-\/]+", subdir):
                    raise ValueError(f"Invalid subdirectory path: '{subdir}'")
        except ValueError as e:
            print(f"❌ Validation error: {e}")
            return

        if subdir:
            temp_dir = os.path.realpath(os.path.join(SKILLS_BASE_DIR, f".temp_clone_{skill_name}"))
            safe_print("📥 Cloning repo to temporary location: ", temp_dir)
            result = subprocess.run(
                ["git", "clone", repo_url, temp_dir],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                print(f"❌ Clone failed: {result.stderr.strip()}")
                force_rmtree(temp_dir)
                return
            
            target_subdir_path = os.path.join(temp_dir, subdir)
            if not os.path.exists(target_subdir_path):
                print(f"❌ Subdirectory '{subdir}' not found in the cloned repository.")
                force_rmtree(temp_dir)
                return
            
            # Create final skill directory and move files from subdir
            os.makedirs(skill_dir, exist_ok=True)
            for item in os.listdir(target_subdir_path):
                s = os.path.join(target_subdir_path, item)
                d = os.path.join(skill_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)
            
            # Clean up temp clone
            force_rmtree(temp_dir)
        else:
            safe_print("📥 Cloning into ", skill_dir)
            result = subprocess.run(
                ["git", "clone", repo_url, skill_dir],
                capture_output=True, text=True, timeout=120
            )
            if result.stdout:
                print(result.stdout.strip())
            if result.returncode != 0:
                print(f"❌ Clone failed: {result.stderr.strip()}")
                return

        self.register_skill(skill_name)

    def install_from_npm(self, package_name: str, skill_name: str):
        try:
            skill_name = sanitize_skill_name(skill_name)
            # Validate package name: npm names are lowercase alphanumeric + @ / - _
            if not re.fullmatch(r"[@a-zA-Z0-9_\-/\.]+", package_name):
                raise ValueError(f"Invalid npm package name: '{package_name}'")
            skill_dir = safe_skill_path(skill_name)
        except ValueError as e:
            print(f"❌ Validation error: {e}")
            return

        os.makedirs(skill_dir, exist_ok=True)
        safe_print("📦 Installing npm package: ", package_name)
        result = subprocess.run(
            ["npm", "install", package_name, "--prefix", skill_dir],
            capture_output=True, text=True, timeout=120
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0:
            print(f"❌ npm install failed: {result.stderr.strip()}")
            return
        self.register_skill(skill_name)

    def register_skill(self, skill_name: str):
        try:
            skill_name = sanitize_skill_name(skill_name)
            skill_dir = safe_skill_path(skill_name)
        except ValueError as e:
            print(f"❌ Validation error: {e}")
            return

        skill_path = os.path.join(skill_dir, "skill.json")

        # Auto-generate skill.json if missing
        if not os.path.exists(skill_path):
            print(f"⚠️  No skill.json found for '{skill_name}', generating default...")
            default_data = {
                "name": skill_name,
                "description": f"Auto-generated skill for {skill_name}",
                "prompt": f"Provide useful responses related to {skill_name}.",
                "tools": [
                    {
                        "name": "run_main",
                        "command": ["python", os.path.join(skill_dir, "main.py")],
                        "args_as": "env"
                    }
                ]
            }
            os.makedirs(skill_dir, exist_ok=True)
            with open(skill_path, "w") as f:
                json.dump(default_data, f, indent=2)

        with open(skill_path) as f:
            data = json.load(f)

        # Normalize tools: support both List[str] and List[dict] formats
        raw_tools = data.get("tools", [])
        tools = [
            t if isinstance(t, dict) else {
                "name": t,
                "command": ["python", os.path.join(skill_dir, f"{t}.py")],
                "args_as": "env"
            }
            for t in raw_tools
        ]

        skill = Skill(
            name=data["name"],
            description=data["description"],
            prompt=data["prompt"],
            tools=tools
        )
        self.registry.add_skill(skill)
        safe_print("✅ Registered skill: ", skill.name)

# -----------------------------
# Tool Executor
# -----------------------------
class ToolExecutor:
    def execute_from_skill(self, skill: Skill, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute a tool defined inside a skill's skill.json."""
        tool_def = skill.get_tool(tool_name)
        if not tool_def:
            return f"❌ Tool '{html.escape(tool_name)}' not defined in skill '{html.escape(skill.name)}'."

        command = list(tool_def.get("command", []))
        args_as = tool_def.get("args_as", "env")

        if not command:
            return f"❌ No command defined for tool '{html.escape(tool_name)}'."

        try:
            command = validate_command(command)
        except ValueError as e:
            return f"❌ {html.escape(str(e))}"

        try:
            skill_dir = safe_skill_path(skill.name)
            if args_as == "args":
                # Sanitize each arg value before appending as CLI args (allowing backslashes for Windows paths)
                safe_args = [re.sub(r"[^\w\s\-.,:/\\]", "", str(v)) for v in args.values()]
                full_cmd = command + safe_args
                result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=60, cwd=skill_dir)
            else:
                # Pass args as env vars — safest method, no shell injection possible
                env = {
                    **os.environ,
                    **{re.sub(r"\W", "_", k.upper()): str(v) for k, v in args.items()}
                }
                result = subprocess.run(command, capture_output=True, text=True, timeout=60, env=env, cwd=skill_dir)

            output = result.stdout.strip() or result.stderr.strip()
            return output if output else "✅ Tool executed (no output)."
        except FileNotFoundError:
            return f"❌ Command not found: {html.escape(command[0])}"
        except subprocess.TimeoutExpired:
            return f"⏱️ Tool '{html.escape(tool_name)}' timed out."
        except Exception as e:
            return f"❌ Error running tool '{html.escape(tool_name)}': {html.escape(str(e))}"

# -----------------------------
# Agent with Groq LLM
# -----------------------------
class Agent:
    def __init__(self, registry: SkillRegistry, executor: ToolExecutor, loader: SkillLoader):
        self.registry = registry
        self.executor = executor
        self.loader = loader
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            temperature=0.2
        )

    def handle_query(self, query: str):
        skills_info = []
        for s_name, s_obj in self.registry.skills.items():
            t_names = [t.get("name") if isinstance(t, dict) else t for t in s_obj.tools]
            skills_info.append(f"{s_name} (prompt: {s_obj.prompt}, tools: {t_names})")

        system_prompt = f"""
You are an advanced agentic router. For each user query, you can decide to use skills, install skills, or chat.
Available skills: {skills_info}

You respond in JSON format matching one of these schemas:
1. To use a tool from a skill:
   {{"action": "use_skill", "skill": "<skill_name>", "tool": "<tool_name>", "args": {{"<arg_key>": "<arg_val>"}}}}
2. To install a skill:
   {{"action": "install_github", "repo_url": "<url>", "skill": "<name>", "subdir": "<optional_subdirectory_path>"}}
   {{"action": "install_npm", "package": "<package>", "skill": "<name>"}}
3. To talk to the user or give the final answer:
   {{"action": "chat", "response": "<your conversational response>"}}

If you call a tool, the system will execute it and return the "Tool Result". You should then analyze the output and decide on the next action (either calling another tool/skill or providing the final conversational answer).
Note: For GitHub repositories containing multiple skills in subfolders, you MUST extract only the requested folder by specifying the "subdir" parameter (e.g. "subdir": "data-and-analytics").
Respond with raw JSON only.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        # Max 5 reasoning steps to support skill chaining and reasoning loops
        for step in range(5):
            response = self.llm.invoke(messages)
            try:
                decision = parse_llm_json(response.content)
            except Exception:
                decision = {"action": "chat", "response": response.content}

            action = decision.get("action", "chat")

            if action == "use_skill":
                skill_name = decision.get("skill", "")
                tool_name = decision.get("tool", "")
                skill = self.registry.get_skill(skill_name)
                
                if not skill:
                    err_msg = f"❌ Skill '{skill_name}' not found."
                    print(err_msg)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": err_msg})
                    continue
                
                # Support prompt-only skills
                if not skill.tools:
                    prompt_only_ctx = f"Skill '{skill.name}' is prompt-only (no executable tools). Instructions/Context to guide your answer: {skill.prompt}"
                    messages.append({"role": "assistant", "content": json.dumps(decision)})
                    messages.append({"role": "user", "content": prompt_only_ctx})
                    continue

                skill_tool_names = [t.get("name") if isinstance(t, dict) else t for t in skill.tools]
                if not tool_name or tool_name not in skill_tool_names:
                    tool_name = skill_tool_names[0] if skill_tool_names else None

                if not tool_name:
                    err_msg = f"❌ Skill '{skill.name}' has no tools defined."
                    print(err_msg)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": err_msg})
                    continue

                safe_print("🔍 Using skill: ", skill.name)
                args = decision.get("args", {})
                safe_print("⚙️  Running tool: ", tool_name)
                
                result = self.executor.execute_from_skill(skill, tool_name, args)
                print(f"🔧 Tool Result: {result}")
                
                # Feed tool result back into the agent context
                messages.append({"role": "assistant", "content": json.dumps(decision)})
                messages.append({"role": "user", "content": f"Tool '{tool_name}' Result: {result}"})

            elif action == "install_github":
                repo_url = str(decision.get("repo_url", ""))
                skill_name = str(decision.get("skill", ""))
                subdir = decision.get("subdir", None)
                if subdir:
                    subdir = str(subdir)
                self.loader.install_from_github(repo_url, skill_name, subdir)
                break

            elif action == "install_npm":
                package = str(decision.get("package", ""))
                skill_name = str(decision.get("skill", ""))
                self.loader.install_from_npm(package, skill_name)
                break

            elif action == "chat":
                safe_print("🤖 ", decision.get("response", ""))
                break
            else:
                print(f"⚠️  Unknown action: {action}")
                break

# -----------------------------
# Terminal Interface
# -----------------------------
class TerminalInterface:
    def __init__(self, agent: Agent):
        self.agent = agent

    def start(self):
        print("🚀 Skills-Powered Agentic System (Terminal Mode)")
        print("Commands: 'list skills' · 'exit'")
        while True:
            try:
                query = input("\n💬 Enter your query: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Exiting system.")
                break

            if not query:
                continue
            if query.lower() == "exit":
                print("👋 Exiting system.")
                break
            elif query.lower() in ["list skills", "show skills", "all skills"]:
                skills = self.agent.registry.list_skills()
                if skills:
                    print("📂 Installed Skills:")
                    for s in skills:
                        print(f"   - {html.escape(s)}")
                else:
                    print("📂 No skills installed yet.")
                continue

            self.agent.handle_query(query)

# -----------------------------
# Main Entry Point
# -----------------------------
if __name__ == "__main__":
    registry = SkillRegistry()
    executor = ToolExecutor()
    loader = SkillLoader(registry)

    # Auto-load existing skills from local directory on startup
    if os.path.exists(SKILLS_BASE_DIR):
        for item in os.listdir(SKILLS_BASE_DIR):
            item_path = os.path.join(SKILLS_BASE_DIR, item)
            if os.path.isdir(item_path):
                # Filter out hidden directories or temporary system folders
                if not item.startswith(".") and item != "__pycache__":
                    try:
                        loader.register_skill(item)
                    except Exception as e:
                        print(f"⚠️ Failed to auto-register skill '{item}': {e}")

    agent = Agent(registry, executor, loader)
    terminal = TerminalInterface(agent)
    terminal.start()
