# 🧠 Day 02 – DocuMind AI · Web-Aware RAG Chat Assistant

## 📌 What It Does
A dual-mode AI assistant powered by a LangGraph pipeline that **automatically decides** whether to answer from its own knowledge (chat mode) or **search the web, scrape full HTML pages, chunk them, embed into Chroma, retrieve the most relevant context, and stream a grounded answer** — all in real time with a live pipeline status UI.

---

## 🔁 Workflow

```
User Input (natural language query)
        ↓
  Classifier Node     → Groq LLM classifies query as 'chat' or 'docs'
        ↓                        ↓
  ┌─────────────┐     ┌──────────────────┐
  │  CHAT MODE  │     │    DOCS MODE     │
  │             │     │                  │
  │  Groq LLM   │     │  DuckDuckGo      │
  │  streams    │     │  → top 3 URLs    │
  │  answer     │     │  → full HTML     │
  │  directly   │     │  fetched via     │
  └─────────────┘     │  requests        │
        ↓             │        ↓         │
       END            │  BeautifulSoup   │
                      │  strips scripts/ │
                      │  nav/footer      │
                      │        ↓         │
                      │  RecursiveChar   │
                      │  TextSplitter    │
                      │  chunk_size=1000 │
                      │  overlap=150     │
                      │        ↓         │
                      │  HuggingFace     │
                      │  Embeddings      │
                      │  (MiniLM-L6-v2)  │
                      │  cached locally  │
                      │        ↓         │
                      │  Chroma Vector   │
                      │  Store (persisted│
                      │  to disk)        │
                      │        ↓         │
                      │  Retriever       │
                      │  top-k=5 chunks  │
                      │        ↓         │
                      │  Groq LLM        │
                      │  streams grounded│
                      │  answer          │
                      └──────────────────┘
                               ↓
                              END
        ↓
  Streamlit UI        → Real-time pipeline step tracker (⬜ → ⏳ → ✅)
                      → Streaming token-by-token response with ▌ cursor
                      → Mode badge (💬 CHAT / 📄 DOCS)
                      → Clickable source URL cards
                      → Session stats (total / chat / docs counts)
                      → Full chat history with persistent session state
```

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| LangGraph | Agent pipeline orchestration |
| Groq (`llama-3.1-8b-instant`) | Query classification + answer generation |
| DuckDuckGo Search (`ddgs`) | Web search — top 3 URLs per query |
| `requests` + BeautifulSoup | Full HTML page fetching + cleaning |
| LangChain `RecursiveCharacterTextSplitter` | Chunking clean text (1000 chars, 150 overlap) |
| HuggingFace `all-MiniLM-L6-v2` | Local sentence embeddings (cached to disk) |
| Chroma (`langchain-chroma`) | Vector store with `persist_directory` |
| Streamlit | Immersive chat UI with real-time pipeline status |
| Python-dotenv | Environment variable management |

---

## 📂 Project Structure

```
DAY-2/
├── app.py              # Streamlit UI — streaming, pipeline tracker, chat history
├── DocuMind.py         # LangGraph backend — all nodes, graph, stream_pipeline()
├── chroma_store/       # Persisted Chroma vector DB (auto-created on first run)
├── model_cache/        # Cached HuggingFace embedding model (auto-created)
├── requirements.txt
├── .env                # API keys (not pushed)
└── README.md
```

---

## ⚙️ Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
```
GROQ_API_KEY=your_groq_key
```

3. Run the app:
```bash
streamlit run app.py
```

> **Note:** First run will download `all-MiniLM-L6-v2` (~90MB) into `model_cache/`. Every run after loads from disk instantly.

---

## 🖥 UI Features

- **Dual-mode chat** — same input box, AI decides chat vs docs automatically
- **Live pipeline tracker** — each step lights up in real time: Classifying → Fetching → Chunking → Retrieving → Generating
- **Token streaming** — answer appears word by word with a blinking `▌` cursor
- **Mode badges** — `💬 CHAT MODE` (green) or `📄 DOCS MODE` (blue) above every response
- **Source cards** — clickable URLs in a collapsible expander after every docs response
- **Session stats sidebar** — live count of total / chat / docs queries
- **Pipeline flow diagram** — visual graph in sidebar showing the LangGraph structure
- **Clear chat** — resets full history and stats in one click
- **Dark theme** — custom CSS with Inter font, gradient hero, styled bubbles

---

## 🪲 Challenges I Faced

**1. `from ddgs import DDGS` ImportError**
- Original code had `from duckduckgo_search import DDGS` — package was installed as `ddgs` in this environment
- Fix: Changed import to `from ddgs import DDGS` to match the installed package name

**2. LangGraph state not propagating between nodes**
- Was mutating state directly with `state["key"] = value` inside nodes — LangGraph treats state as immutable
- Changes made inside a node were lost by the time the next node ran
- Fix: Return `{**state, "key": value}` from every node — spread the existing state and override only changed keys

**3. `RetrievalQA` import path changed across LangChain versions**
- `from langchain_community.chains import RetrievalQA` raised `ImportError` — it moved packages
- Fix: `from langchain.chains import RetrievalQA` — lives in core `langchain`, not `langchain_community`

**4. Chroma import deprecated from `langchain_community`**
- `from langchain_community.vectorstores import Chroma` raised a deprecation warning and broke on newer versions
- Fix: `from langchain_chroma import Chroma` — use the dedicated `langchain-chroma` package

**5. Embedding model re-downloading on every run**
- `HuggingFaceEmbeddings` was downloading `all-MiniLM-L6-v2` fresh every time the script ran
- Fix: Added `cache_folder=os.path.join(os.path.dirname(__file__), "model_cache")` — model downloads once, loads from disk after

**6. HTML pages returning only a few words instead of full content**
- Original `docs_node` was truncating with `text[:500]` — only passing a fragment to the RAG pipeline
- Fix: Store the full `requests.get().text` (complete HTML) in `raw_html` state field, let `rag_node` handle all parsing

**7. Chroma not persisting between queries**
- `Chroma.from_documents()` was creating an in-memory store — lost after every query
- Fix: Added `persist_directory=CHROMA_DIR` pointing to `DAY-2/chroma_store/` — embeddings saved to disk

**8. `chunk_size=500` cutting sentences mid-word**
- Small chunks were splitting sentences in the middle, losing context and degrading retrieval quality
- Fix: Bumped to `chunk_size=1000, chunk_overlap=150` with `separators=["\n\n", "\n", " ", ""]` — splits on paragraphs first, then lines, then words

**9. Streaming not working in Streamlit**
- `pipeline.invoke()` returns only after the full response is ready — no streaming possible through LangGraph's compiled graph
- Fix: Built a `stream_pipeline()` generator that manually calls `classifier_node` → `docs_node` → RAG steps, yielding `(token, None)` during streaming and `(None, final_state)` at the end

**10. Pipeline status panel not updating in real time**
- Used separate `st.markdown()` calls for each step update — Streamlit renders them as new elements, not updates
- Fix: Used a single `st.empty()` placeholder and called `.markdown()` on it each time to replace content in place

**11. Classifier running twice (once for status, once in generator)**
- To show the mode badge before streaming started, the classifier was being called separately — then called again inside `stream_pipeline()`, doubling the API calls
- Fix: Called `classifier_node()` once in `app.py` to get the category for the UI, then passed the already-classified query into `stream_pipeline()` which skips re-classification

**12. `▌` cursor remaining after stream ends**
- The streaming bubble used `{full_reply}▌` — but the final render inside the loop still had the cursor
- Fix: After the generator exhausts, re-render the bubble once more without `▌` using `response_box.markdown()`
