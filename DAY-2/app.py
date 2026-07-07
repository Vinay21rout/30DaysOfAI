import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from DocuMind import stream_pipeline, classifier_node

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="DocuMind AI — Live Doc Intelligence", page_icon="🧠", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp { background: #0f1117; }

/* Header */
.hero { text-align: center; padding: 2rem 0 1rem; }
.hero h1 { font-size: 3rem; font-weight: 600; background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
.hero p { color: #6b7280; font-size: 1rem; margin-top: 0.4rem; }

/* Chat bubbles */
.msg-user { display: flex; justify-content: flex-end; margin: 0.8rem 0; }
.msg-user .bubble { background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white; padding: 0.8rem 1.2rem; border-radius: 18px 18px 4px 18px;
    max-width: 70%; font-size: 0.95rem; line-height: 1.5; }

.msg-ai { display: flex; justify-content: flex-start; margin: 0.8rem 0; gap: 0.6rem; }
.ai-avatar { width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #06b6d4, #6366f1);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0; }
.msg-ai .bubble { background: #1e2130; color: #e2e8f0;
    padding: 0.8rem 1.2rem; border-radius: 18px 18px 18px 4px;
    max-width: 75%; font-size: 0.95rem; line-height: 1.6;
    border: 1px solid #2d3148; }

/* Mode badge */
.badge-chat { display: inline-block; background: #064e3b; color: #34d399;
    padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-bottom: 6px; }
.badge-docs { display: inline-block; background: #1e3a5f; color: #60a5fa;
    padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; margin-bottom: 6px; }

/* Pipeline steps */
.pipeline-box { background: #1e2130; border: 1px solid #2d3148;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0; }
.step { display: flex; align-items: center; gap: 0.6rem;
    padding: 0.4rem 0; color: #9ca3af; font-size: 0.85rem; }
.step.active { color: #f59e0b; }
.step.done { color: #34d399; }
.step-icon { font-size: 1rem; width: 20px; text-align: center; }

/* Source cards */
.source-card { background: #1e2130; border: 1px solid #2d3148; border-radius: 10px;
    padding: 0.6rem 1rem; margin: 0.3rem 0; font-size: 0.82rem; color: #60a5fa;
    word-break: break-all; }
.source-card:hover { border-color: #6366f1; }

/* Input area */
.stChatInput > div { background: #1e2130 !important; border: 1px solid #2d3148 !important;
    border-radius: 12px !important; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0d0f1a !important; border-right: 1px solid #1e2130; }
.sidebar-stat { background: #1e2130; border-radius: 10px; padding: 0.8rem 1rem;
    margin: 0.4rem 0; text-align: center; }
.sidebar-stat .val { font-size: 1.6rem; font-weight: 600; color: #8b5cf6; }
.sidebar-stat .lbl { font-size: 0.75rem; color: #6b7280; }

/* Scrollable chat */
.chat-container { max-height: 62vh; overflow-y: auto; padding-right: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []   # list of {role, content, category, urls}
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "chat_count" not in st.session_state:
    st.session_state.chat_count = 0
if "docs_count" not in st.session_state:
    st.session_state.docs_count = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 DocuMind AI")
    st.markdown("<p style='color:#6b7280;font-size:0.85rem'>Live Doc Intelligence · LangGraph · RAG · Groq · Chroma</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("### ⚡ Superpowers")
    st.markdown("""
    <div style='font-size:0.82rem;line-height:2.2;color:#9ca3af'>
    🌐 &nbsp;Searches the <b style='color:#e2e8f0'>live web</b> in real time<br>
    📄 &nbsp;Scrapes <b style='color:#e2e8f0'>full HTML pages</b>, not snippets<br>
    ✂️ &nbsp;<b style='color:#e2e8f0'>Chunks + embeds</b> every page locally<br>
    🔍 &nbsp;<b style='color:#e2e8f0'>Semantic retrieval</b> — top 8 chunks<br>
    🤖 &nbsp;Groq LLM answers <b style='color:#e2e8f0'>only from context</b><br>
    💾 &nbsp;Chroma DB <b style='color:#e2e8f0'>persisted to disk</b><br>
    ⚡ &nbsp;Token-by-token <b style='color:#e2e8f0'>streaming</b> output
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("### 📊 Session Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='sidebar-stat'><div class='val'>{st.session_state.total_queries}</div><div class='lbl'>Total</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='sidebar-stat'><div class='val'>{st.session_state.chat_count}</div><div class='lbl'>Chat</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='sidebar-stat'><div class='val'>{st.session_state.docs_count}</div><div class='lbl'>Docs</div></div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔄 Pipeline Flow")
    st.markdown("""
    <div style='color:#6b7280;font-size:0.82rem;line-height:2'>
    🟣 <b style='color:#a78bfa'>START</b><br>
    &nbsp;&nbsp;&nbsp;↓<br>
    🔵 <b style='color:#60a5fa'>Classifier</b><br>
    &nbsp;&nbsp;&nbsp;↓&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
    💬 <b style='color:#34d399'>Chat</b>&nbsp;&nbsp;&nbsp;&nbsp;📄 <b style='color:#f59e0b'>Docs</b><br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🔍 <b style='color:#f59e0b'>RAG</b><br>
    &nbsp;&nbsp;&nbsp;↓&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓<br>
    🏁 <b style='color:#a78bfa'>END</b>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.total_queries = 0
        st.session_state.chat_count = 0
        st.session_state.docs_count = 0
        st.rerun()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <h1>🧠 DocuMind AI</h1>
    <p style='font-size:1.05rem;color:#a78bfa;font-weight:500'>Live Documentation Intelligence Engine</p>
    <p style='margin-top:0.3rem'>Ask any technical question &mdash; I scrape the web, read full pages, embed them, retrieve the best context and stream a precise answer &mdash; all in real time</p>
</div>
""", unsafe_allow_html=True)

# ── Chat History ──────────────────────────────────────────────────────────────
chat_area = st.container()
with chat_area:
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class='msg-user'>
                <div class='bubble'>👤 {msg['content']}</div>
            </div>""", unsafe_allow_html=True)
        else:
            badge = f"<span class='badge-{'docs' if msg['category'] == 'docs' else 'chat'}'>{'📄 DOCS MODE' if msg['category'] == 'docs' else '💬 CHAT MODE'}</span>"
            st.markdown(f"""
            <div class='msg-ai'>
                <div class='ai-avatar'>🧠</div>
                <div>
                    {badge}
                    <div class='bubble'>{msg['content']}</div>
                </div>
            </div>""", unsafe_allow_html=True)

            if msg.get("urls"):
                with st.expander(f"🔗 {len(msg['urls'])} Sources Used", expanded=False):
                    for url in msg["urls"]:
                        st.markdown(f"<div class='source-card'>🌐 <a href='{url}' target='_blank' style='color:#60a5fa;text-decoration:none'>{url}</a></div>", unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about any library, framework, API, error, concept — I'll find the real answer from live docs...")

if user_input:
    # append user message
    st.session_state.history.append({"role": "user", "content": user_input, "category": "", "urls": []})
    st.session_state.total_queries += 1

    # show user bubble immediately
    st.markdown(f"""
    <div class='msg-user'>
        <div class='bubble'>👤 {user_input}</div>
    </div>""", unsafe_allow_html=True)

    # ── Pipeline Status Panel ─────────────────────────────────────────────────
    status_box = st.empty()

    def render_steps(steps):
        html = "<div class='pipeline-box'>"
        for icon, label, state in steps:
            cls = "done" if state == "done" else ("active" if state == "active" else "step")
            prefix = "✅" if state == "done" else ("⏳" if state == "active" else "⬜")
            html += f"<div class='step {cls}'><span class='step-icon'>{prefix}</span>{icon} {label}</div>"
        html += "</div>"
        status_box.markdown(html, unsafe_allow_html=True)

    # Step 1: Classifying
    render_steps([
        ("🔵", "Classifying query...", "active"),
        ("📄", "Fetching documents", ""),
        ("✂️", "Chunking & embedding", ""),
        ("🔍", "Retrieving context", ""),
        ("💡", "Generating answer", ""),
    ])

    # peek at category without consuming the generator
    safe_input = user_input[:500].replace("\n", " ").replace("\r", " ")
    state_peek = {"user_input": safe_input, "category": "", "urls": [], "raw_html": [], "chunks": [], "response": ""}
    state_peek = classifier_node(state_peek)
    category = state_peek["category"]

    if category == "docs":
        render_steps([
            ("🔵", "Classifying query", "done"),
            ("📄", "Fetching documents...", "active"),
            ("✂️", "Chunking & embedding", ""),
            ("🔍", "Retrieving context", ""),
            ("💡", "Generating answer", ""),
        ])
    else:
        render_steps([
            ("🔵", "Classifying query", "done"),
            ("💬", "Chat mode — generating answer...", "active"),
        ])

    # ── Stream Response ───────────────────────────────────────────────────────
    badge = f"<span class='badge-{'docs' if category == 'docs' else 'chat'}'>{'📄 DOCS MODE' if category == 'docs' else '💬 CHAT MODE'}</span>"
    response_box = st.empty()
    full_reply = ""
    final_state = None
    fetched = False

    for token, result in stream_pipeline(user_input):
        if token is not None:
            full_reply += token
            # update streaming bubble
            response_box.markdown(f"""
            <div class='msg-ai'>
                <div class='ai-avatar'>🧠</div>
                <div>
                    {badge}
                    <div class='bubble'>{full_reply}▌</div>
                </div>
            </div>""", unsafe_allow_html=True)

            # update pipeline steps mid-stream
            if category == "docs" and not fetched:
                fetched = True
                render_steps([
                    ("🔵", "Classifying query", "done"),
                    ("📄", "Fetching documents", "done"),
                    ("✂️", "Chunking & embedding", "done"),
                    ("🔍", "Retrieving context", "done"),
                    ("💡", "Generating answer...", "active"),
                ])
        else:
            final_state = result

    # final bubble without cursor
    response_box.markdown(f"""
    <div class='msg-ai'>
        <div class='ai-avatar'>🧠</div>
        <div>
            {badge}
            <div class='bubble'>{full_reply}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # all steps done
    if category == "docs":
        render_steps([
            ("🔵", "Classifying query", "done"),
            ("📄", "Fetching documents", "done"),
            ("✂️", "Chunking & embedding", "done"),
            ("🔍", "Retrieving context", "done"),
            ("💡", "Generating answer", "done"),
        ])
    else:
        render_steps([
            ("🔵", "Classifying query", "done"),
            ("💬", "Chat mode — answer generated", "done"),
        ])

    urls = final_state["urls"] if final_state else []

    # source cards
    if urls:
        with st.expander(f"🔗 {len(urls)} Sources Used", expanded=True):
            for url in urls:
                st.markdown(f"<div class='source-card'>🌐 <a href='{url}' target='_blank' style='color:#60a5fa;text-decoration:none'>{url}</a></div>", unsafe_allow_html=True)

    # persist to history
    st.session_state.history.append({"role": "ai", "content": full_reply, "category": category, "urls": urls})
    if category == "chat":
        st.session_state.chat_count += 1
    else:
        st.session_state.docs_count += 1
