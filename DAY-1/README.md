# 🤖 Day 01 – AI Lead Generation Automation

## 📌 What It Does
An agentic pipeline that scrapes business leads from Google Maps, parses the relevant info, and auto-generates personalized cold emails — all triggered from a Streamlit UI.

---

## 🔁 Workflow

```
User Input (search query)
        ↓
  Scraper Agent       → hits Apify Google Maps API → saves leads.csv
        ↓
  Parser Agent        → reads leads.csv row by row → saves parsed_leads.csv
        ↓
  Email Writer Agent  → reads first parsed lead → generates cold email via Groq LLM
        ↓
  Streamlit UI        → displays leads table + email draft + export options
```

---

## 🛠 Tech Stack

| Tool | Purpose |
|------|---------|
| LangGraph | Agent workflow orchestration |
| Apify (`compass~crawler-google-places`) | Google Maps scraping |
| Groq (`llama-3.1-8b-instant`) | Cold email generation |
| Streamlit | UI + workflow tracker |
| Pandas | CSV handling |
| Python-dotenv | Environment variable management |

---

## 📂 Project Structure

```
DAY-1/
├── app.py                        # Streamlit UI
├── lead_generation_automation.py # LangGraph pipeline (backend)
├── requirements.txt
├── .env                          # API keys (not pushed)
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
APIFY_API_KEY=your_apify_token
GROQ_API_KEY=your_groq_key
```

3. Run the app:
```bash
streamlit run app.py
```

---

## 🖥 UI Features
- Search query input + max places slider
- Live workflow step tracker (⬜ → 🔄 → ✅)
- Leads table with metrics (total, with phone, with website)
- Generated cold email draft with download button
- Export leads as CSV

---

## 🪲 Challenges I Faced

This was not a smooth build. Here's every real issue I hit and how I fixed it:

**1. Wrong Apify Actor ID**
- Used `apify~google-maps-scraper` → got `actor-not-found` error
- Then tried `compass/google-maps-scraper` (with `/`) → got `page-not-found` error
- Fix: Apify actor IDs use `~` not `/` — correct ID is `compass~crawler-google-places`

**2. `.env` file not loading**
- `load_dotenv()` was silently failing because the `.env` was inside `DAY-1/` but the script was run from the root folder
- Fix: Used `load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))` to always resolve relative to the file location

**3. LangGraph state mutation bug**
- Was doing `state["key"] = value` inside agents — LangGraph uses immutable state so changes were lost between agents
- Scraper ran fine but parser received empty `raw_leads` because the update never propagated
- Fix: Return `{**state, "key": value}` from every agent instead of mutating in place

**4. Backend code mixed into `app.py`**
- Initially had all API calls, LLM logic, and LangGraph pipeline inside the Streamlit file
- Fix: Separated into `lead_generation_automation.py` (backend) and `app.py` (UI only), exposing a clean `run_pipeline()` function

**5. Python can't import files with hyphens**
- File was named `lead-generation-automation.py` — Python module imports don't support hyphens
- Fix: Renamed to `lead_generation_automation.py` (underscores)

**6. Apify returning valid data but triggering error**
- Was checking `if response.status_code != 200` — Apify sometimes returns non-200 status even with valid data in the body
- The actual lead data was showing up inside the error message itself
- Fix: Removed status code check, parse JSON directly, only raise if response is an error dict `{"error": ...}`

**7. LangGraph pipeline rebuilding on every Streamlit rerun**
- Every button click caused Streamlit to re-import the module, rebuilding the entire LangGraph graph
- Fix: Wrapped the import in `@st.cache_resource` so the pipeline is compiled once and reused

**8. `LeadState` type mismatch**
- Defined `lead: dict` in TypedDict but scraper was setting it to a `list` of all leads, then parser set it back to a `dict` of one lead
- Fix: Separated concerns — scraper saves to `leads.csv`, parser reads it and saves `parsed_leads.csv`, state only carries file paths between agents
