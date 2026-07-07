import os
from typing import TypedDict
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from ddgs import DDGS
from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph
load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_store")

llm = ChatGroq(model="llama-3.1-8b-instant", streaming=True)

# ── State ─────────────────────────────────────────────────────────────────────
class DocuState(TypedDict):
    user_input: str
    category: str
    urls: list
    raw_html: list   # full HTML string per URL — fed into RAG agents downstream
    chunks: list     # clean text chunks from all pages
    response: str

# ── Nodes ─────────────────────────────────────────────────────────────────────
def classifier_node(state: DocuState) -> DocuState:
    prompt = f"""You are a query router. Classify the query into exactly one category:

- 'docs'  → technical questions, how-to guides, library/framework/API usage, code examples,
             error messages, installation, configuration, concepts, tools, documentation search,
             anything that benefits from searching real up-to-date sources on the web.
- 'chat'  → casual conversation, greetings, opinions, simple math, general knowledge
             that does NOT need live web sources.

Query: "{state['user_input']}"

When in doubt, choose 'docs'. Only return the single word: docs or chat."""
    result = llm.invoke(prompt).content.strip().lower()
    category = "docs" if "docs" in result else "chat"
    return {**state, "category": category}

def chat_node(state: DocuState) -> DocuState:
    reply = ""
    for chunk in llm.stream(state["user_input"]):
        reply += chunk.content
    return {**state, "response": reply}

def docs_node(state: DocuState) -> DocuState:
    query = state["user_input"]
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    urls = [r["href"] for r in results]

    raw_html = []
    for url in urls:
        try:
            html = requests.get(url, timeout=10).text  # full HTML, no truncation
            raw_html.append(html)
        except Exception as e:
            raw_html.append(f"<!-- FAILED: {url} | {e} -->")

    return {**state, "urls": urls, "raw_html": raw_html, "response": f"Fetched {len(urls)} pages. Ready for RAG pipeline."}

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    cache_folder=os.path.join(os.path.dirname(__file__), "model_cache")
)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", " ", ""]
)

def rag_node(state: DocuState) -> DocuState:
    # parse all HTML pages into clean text
    all_text = []
    for html in state["raw_html"]:
        if html.startswith("<!-- FAILED"):
            continue
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        all_text.append(soup.get_text(separator=" ", strip=True))

    if not all_text:
        return {**state, "chunks": [], "response": "Could not retrieve any content."}

    chunks = splitter.create_documents(all_text)
    vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    context = "\n\n".join([d.page_content for d in retriever.invoke(state["user_input"])])
    prompt = f"""You are DocuMind — an expert technical documentation assistant with superpowers.
You have just scraped and indexed real web pages to answer this question with precision.

Rules:
- Answer ONLY from the context below. Do NOT hallucinate or use prior knowledge.
- Be specific, detailed, and structured. Use bullet points, code blocks, or steps where helpful.
- If the context contains partial info, say what you found and what's missing.
- If the context has NO relevant info, say: "The fetched pages did not contain enough information. Try rephrasing."

Context (from live web sources):
{context}

Question: {state['user_input']}

Answer:"""
    reply = ""
    for chunk in llm.stream(prompt):
        reply += chunk.content
    return {**state, "chunks": [d.page_content for d in chunks], "response": reply}

# ── Router ────────────────────────────────────────────────────────────────────
def route(state: DocuState) -> str:
    return state["category"]

# ── Build Graph ───────────────────────────────────────────────────────────────
graph = StateGraph(DocuState)
graph.add_node("classifier", classifier_node)
graph.add_node("chat", chat_node)
graph.add_node("docs", docs_node)
graph.add_node("rag", rag_node)

graph.add_edge(START, "classifier")
graph.add_conditional_edges("classifier", route, {"chat": "chat", "docs": "docs"})
graph.add_edge("chat", END)
graph.add_edge("docs", "rag")
graph.add_edge("rag", END)

pipeline = graph.compile()

def run_pipeline(user_input: str) -> dict:
    safe_input = user_input[:500].replace("\n", " ").replace("\r", " ")
    return pipeline.invoke({"user_input": safe_input, "category": "", "urls": [], "raw_html": [], "chunks": [], "response": ""})

def stream_pipeline(user_input: str):
    """Yields (token, final_result) — token is str while streaming, None when done with result dict."""
    safe_input = user_input[:500].replace("\n", " ").replace("\r", " ")
    state = {"user_input": safe_input, "category": "", "urls": [], "raw_html": [], "chunks": [], "response": ""}

    # classify first
    state = classifier_node(state)

    if state["category"] == "chat":
        reply = ""
        for chunk in llm.stream(safe_input):
            yield chunk.content, None
            reply += chunk.content
        state["response"] = reply
        yield None, state
    else:
        # docs: fetch + RAG (blocking), then stream the answer
        state = docs_node(state)
        all_text = []
        for html in state["raw_html"]:
            if html.startswith("<!-- FAILED"):
                continue
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            all_text.append(soup.get_text(separator=" ", strip=True))

        if not all_text:
            state["response"] = "Could not retrieve any content."
            yield None, state
            return

        chunks = splitter.create_documents(all_text)
        vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
        context = "\n\n".join([d.page_content for d in retriever.invoke(safe_input)])
        prompt = f"""You are DocuMind — an expert technical documentation assistant with superpowers.
You have just scraped and indexed real web pages to answer this question with precision.

Rules:
- Answer ONLY from the context below. Do NOT hallucinate or use prior knowledge.
- Be specific, detailed, and structured. Use bullet points, code blocks, or steps where helpful.
- If the context contains partial info, say what you found and what's missing.
- If the context has NO relevant info, say: "The fetched pages did not contain enough information. Try rephrasing."

Context (from live web sources):
{context}

Question: {safe_input}

Answer:"""
        reply = ""
        for chunk in llm.stream(prompt):
            yield chunk.content, None
            reply += chunk.content
        state["response"] = reply
        state["chunks"] = [d.page_content for d in chunks]
        yield None, state


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    while True:
        user_input = input("USER: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["bye", "q"]:
            print("GoodBye👋")
            break

        print("\nDocuMind AI😊: ", end="", flush=True)
        final = None
        for token, result in stream_pipeline(user_input):
            if token:
                print(token, end="", flush=True)
            else:
                final = result
        print()
        if final and final["category"] == "docs":
            print(f"🔗 Sources: {final['urls']}")
        print("----------------------------------<-*-*-*->----------------------------------")
        print()
