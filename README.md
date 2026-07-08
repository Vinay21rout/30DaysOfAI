# 🚀 30 Days of AI & Automation Challenge

## 📌 Overview
This repository documents my **30‑day public challenge** of building and sharing AI applications, automation workflows, and experimental projects.  
The goal is not perfection, but **consistency, creativity, and growth** — building in public to boost my GitHub and showcase practical AI engineering skills.

---

## 📅 Challenge Rules
- Build **1 project per day** for 30 days.  
- If I miss a day, I’ll make up for it by shipping **2 projects in one day**.  
- Each project will have its own folder with code, documentation, and instructions.  
- Daily updates will also be shared on LinkedIn to show consistency and progress.  

---

## ✅ Consistency Tracker

| Day | Date | Project Title | Tech Used | Status |
|:---:|------|---------------|-----------|:------:|
| 01 | 06 Jul 2025 | [AI Lead Generation Automation](./DAY-1/README.md) | LangGraph · Apify · Groq · Streamlit | ✅ Done |
| 02 | 07 Jul 2025 | [DocuMind AI – Live Documentation Intelligence Engine](./DAY-2/README.md) | LangGraph · Groq · DuckDuckGo · BeautifulSoup · Chroma · HuggingFace · Streamlit | ✅ Done |
| 03 | 08 Jul 2026 | [Skills-Powered Agentic System](./DAY-3/README.md) | LangChain · Groq · Git · Streamlit | ✅ Done |
| 04 | -- | -- | -- | ⏳ Pending |
| 05 | -- | -- | -- | ⏳ Pending |
| 06 | -- | -- | -- | ⏳ Pending |
| 07 | -- | -- | -- | ⏳ Pending |
| 08 | -- | -- | -- | ⏳ Pending |
| 09 | -- | -- | -- | ⏳ Pending |
| 10 | -- | -- | -- | ⏳ Pending |
| 11 | -- | -- | -- | ⏳ Pending |
| 12 | -- | -- | -- | ⏳ Pending |
| 13 | -- | -- | -- | ⏳ Pending |
| 14 | -- | -- | -- | ⏳ Pending |
| 15 | -- | -- | -- | ⏳ Pending |
| 16 | -- | -- | -- | ⏳ Pending |
| 17 | -- | -- | -- | ⏳ Pending |
| 18 | -- | -- | -- | ⏳ Pending |
| 19 | -- | -- | -- | ⏳ Pending |
| 20 | -- | -- | -- | ⏳ Pending |
| 21 | -- | -- | -- | ⏳ Pending |
| 22 | -- | -- | -- | ⏳ Pending |
| 23 | -- | -- | -- | ⏳ Pending |
| 24 | -- | -- | -- | ⏳ Pending |
| 25 | -- | -- | -- | ⏳ Pending |
| 26 | -- | -- | -- | ⏳ Pending |
| 27 | -- | -- | -- | ⏳ Pending |
| 28 | -- | -- | -- | ⏳ Pending |
| 29 | -- | -- | -- | ⏳ Pending |
| 30 | -- | -- | -- | ⏳ Pending |

> ✅ Done &nbsp;·&nbsp; ⏳ Pending &nbsp;·&nbsp; 🔄 In Progress  

---

## 📌 Project Highlights

### Day 01 — AI Lead Generation Automation
A fully agentic LangGraph pipeline that scrapes real business listings from Google Maps via Apify, parses and filters leads, then auto-generates personalized cold emails using a single Groq LLM call with placeholder substitution — zero extra API calls per lead. Streamlit UI with live workflow tracker, leads table, email drafts, CSV export, and session history.

### Day 02 — DocuMind AI — Live Documentation Intelligence Engine
Not a chatbot. A **dual-mode agentic intelligence engine** built on LangGraph that autonomously decides whether a query needs live web knowledge or direct conversation. For technical queries it fires a full pipeline: searches DuckDuckGo, fetches **complete HTML pages** (not snippets), strips noise with BeautifulSoup, chunks with `RecursiveCharacterTextSplitter`, embeds locally with `all-MiniLM-L6-v2`, persists vectors in Chroma, retrieves top-8 semantically relevant chunks, and streams a **grounded, hallucination-resistant answer** via Groq — all in real time with a live pipeline status UI, token-by-token streaming, and source URL cards.

### Day 03 — Skills-Powered Agentic System
A modular, safe, and dynamic agentic framework that dynamically loads, installs, and executes tools ("skills") from local directories, GitHub repositories, or npm packages. Features a conversational ReAct reasoning loop that feeds tool outputs back into the LLM context for summarization or chaining, a zero-dependency frontmatter parser to support prompt-only skills (like `SKILL.md`), and comprehensive security/platform compatibility layers (CWD isolation, dynamic interpreter mapping, and Windows-safe folder deletion). Includes a Streamlit chat UI for live interaction, skill registry management, and installation tracking.

---

## 📂 Repository Structure:

30DaysOfAI/
│
├── DAY-1/
│   ├── ...
│   └── README.md
│
├── DAY-2/
│   ├── ...
│   └── README.md
│
...
└── README.md   # Overview + Tracker

---

## 💡 Why This Challenge?
Modern AI systems often face issues like **LLM hallucinations** and lack of transparency.  
By starting with **deterministic guardrails** and gradually moving into **Generative AI and Agentic systems**, this challenge demonstrates how to build **safe, scalable, and reliable AI applications**.

---

## 🛠 Skills Demonstrated
- Python & Automation  
- Generative AI & Agentic AI Engineering  
- Workflow Automation (n8n)  
- RAG Systems & Vector Databases  
- AI Guardrails & White‑Box Design  

---

## 🔗 Follow Along
- 📂 Repo: [GitHub – 30 Days of AI](https://github.com/Vinay21rout/30DaysOfAI)  
- 🔗 Daily updates on LinkedIn  

---

✨ Let’s make this **30‑day sprint** something crazy, consistent, and impactful!
