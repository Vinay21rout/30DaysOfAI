import streamlit as st
import os
import sys
import importlib.util
import io
import contextlib
import re

# Set page configuration with premium dark theme aesthetics
st.set_page_config(
    page_title="Skills-Powered Agentic Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for vibrant, premium UI
st.markdown("""
    <style>
    /* Dark Gradient background and global overrides */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #161b22 100%);
        color: #c9d1d9;
    }
    
    /* Header Gradient styling */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #58a6ff 0%, #bc8cff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* Custom cards for skills listing */
    .skill-card {
        background-color: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(88, 166, 255, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .skill-title {
        color: #58a6ff;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .skill-desc {
        font-size: 0.9rem;
        color: #8b949e;
        margin-top: 4px;
    }
    
    /* Logs Panel styling */
    .log-box {
        font-family: 'Courier New', monospace;
        background-color: #0b0d11;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 10px;
        color: #39ff14; /* Neon green logs */
        max-height: 250px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Dynamic import to handle the hyphenated script filename
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "agent_system", 
    os.path.join(os.path.dirname(__file__), "skills-powered-agentic-system.py")
)
agent_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_system)

SkillRegistry = agent_system.SkillRegistry
ToolExecutor = agent_system.ToolExecutor
SkillLoader = agent_system.SkillLoader
Agent = agent_system.Agent
SKILLS_BASE_DIR = agent_system.SKILLS_BASE_DIR

# Initialize Session State
if "registry" not in st.session_state:
    st.session_state.registry = SkillRegistry()
    st.session_state.executor = ToolExecutor()
    st.session_state.loader = SkillLoader(st.session_state.registry)
    
    # Auto-load existing skills on startup
    if os.path.exists(SKILLS_BASE_DIR):
        for item in os.listdir(SKILLS_BASE_DIR):
            item_path = os.path.join(SKILLS_BASE_DIR, item)
            if os.path.isdir(item_path):
                if not item.startswith(".") and item != "__pycache__":
                    try:
                        st.session_state.loader.register_skill(item)
                    except Exception as e:
                        pass
                        
    st.session_state.agent = Agent(
        st.session_state.registry,
        st.session_state.executor,
        st.session_state.loader
    )
    st.session_state.chat_history = []

# Sidebar Controls
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #bc8cff;'>🚀 Skill Manager</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # List Installed Skills
    st.markdown("### 📂 Installed Skills")
    skills = st.session_state.registry.list_skills()
    if skills:
        for skill_name in skills:
            skill = st.session_state.registry.get_skill(skill_name)
            tool_names = [t.get("name") if isinstance(t, dict) else t for t in skill.tools]
            
            st.markdown(f"""
                <div class='skill-card'>
                    <div class='skill-title'>⚙️ {skill.name}</div>
                    <div class='skill-desc'>{skill.description}</div>
                    <div style='font-size: 0.8rem; margin-top: 5px; color: #58a6ff;'>
                        <b>Tools:</b> {", ".join(tool_names) if tool_names else 'None (Prompt-Only)'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No skills registered yet. Try installing one below or drop a skill directory!")

    st.markdown("---")
    
    # Install Skill section
    st.markdown("### 📥 Install New Skill")
    install_tab_github, install_tab_npm = st.tabs(["GitHub", "NPM"])
    
    with install_tab_github:
        repo_url = st.text_input("GitHub Repo URL", placeholder="https://github.com/user/repo.git")
        subdir = st.text_input("Subfolder (optional)", placeholder="e.g. data-analysis")
        skill_name_git = st.text_input("Target Skill Name", placeholder="e.g. data-analysis")
        
        if st.button("Install from GitHub", use_container_width=True):
            if repo_url and skill_name_git:
                with st.spinner("Cloning and registering skill..."):
                    # Capture stdout to show install logs
                    f = io.StringIO()
                    with contextlib.redirect_stdout(f):
                        st.session_state.loader.install_from_github(
                            repo_url.strip(), 
                            skill_name_git.strip(), 
                            subdir.strip() if subdir else None
                        )
                    log_output = f.getvalue()
                    st.text_area("Installation Logs", value=log_output, height=120)
                    st.rerun()
            else:
                st.error("Please fill in Repo URL and Target Skill Name.")
                
    with install_tab_npm:
        package_name = st.text_input("npm Package Name", placeholder="e.g. markdown-parser")
        skill_name_npm = st.text_input("Target Skill Name (NPM)", placeholder="e.g. parser")
        
        if st.button("Install from npm", use_container_width=True):
            if package_name and skill_name_npm:
                with st.spinner("Installing npm package..."):
                    f = io.StringIO()
                    with contextlib.redirect_stdout(f):
                        st.session_state.loader.install_from_npm(package_name.strip(), skill_name_npm.strip())
                    log_output = f.getvalue()
                    st.text_area("Installation Logs", value=log_output, height=120)
                    st.rerun()
            else:
                st.error("Please fill in Package Name and Target Skill Name.")

# Main Interface
st.markdown("<div class='main-header'>🧠 Skills-Powered Agentic Engine</div>", unsafe_allow_html=True)
st.write("Ask the agent questions. It will dynamically route queries, execute local skill tools, and summarize results.")
st.markdown("---")

# Render Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "logs" in message and message["logs"]:
            with st.expander("⚙️ Execution Trace / ReAct Logs"):
                st.code(message["logs"], language="text")

# Chat Input
if prompt := st.chat_input("Enter your query (e.g. add 15 and 35 using calculator)"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.chat_history.append({"role": "user", "content": prompt, "logs": None})
    
    # Process Query and Capture execution trace
    with st.chat_message("assistant"):
        f = io.StringIO()
        with st.spinner("Routing query and executing skills..."):
            with contextlib.redirect_stdout(f):
                try:
                    st.session_state.agent.handle_query(prompt)
                except Exception as e:
                    print(f"❌ Execution crashed: {e}")
        
        raw_output = f.getvalue()
        
        # Parse the final chatbot output from stdout
        # stdout format has helper lines and ends with 🤖 response
        lines = raw_output.split("\n")
        assistant_resp = ""
        logs_list = []
        
        for line in lines:
            if line.startswith("🤖 "):
                assistant_resp = line.replace("🤖 ", "", 1).strip()
            elif line.strip():
                logs_list.append(line.strip())
                
        if not assistant_resp:
            # Fallback if no 🤖 prefix is found
            assistant_resp = "I have processed your request, but could not formulate a conversational answer."
            
        logs_str = "\n".join(logs_list)
        
        st.markdown(assistant_resp)
        if logs_str:
            with st.expander("⚙️ Execution Trace / ReAct Logs", expanded=True):
                st.code(logs_str, language="text")
                
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": assistant_resp, 
        "logs": logs_str
    })
