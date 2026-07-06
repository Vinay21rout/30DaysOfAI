# 🤖 Day 01 – AI Lead Generation Automation

## 📌 What It Does
An agentic pipeline that scrapes business leads from Google Maps, parses the relevant info, and auto-generates personalized cold emails — all triggered from a Streamlit UI.

---

## 🔁 Workflow

```
User Input (search query + max places)
        ↓
  Scraper Agent       → hits Apify Google Maps API → saves all raw data to leads.csv
        ↓
  Parser Agent        → reads leads.csv row by row → extracts relevant fields → saves parsed_leads.csv
        ↓
  Email Writer Agent  → 1 Groq API call generates a template with {{NAME}} {{CATEGORY}} {{ADDRESS}}
                      → replaces placeholders for every lead WITHOUT a website (0 extra API calls)
                      → leads WITH a website get email_draft = None (skipped)
                      → saves email_draft column back to parsed_leads.csv
        ↓
  Streamlit UI        → Leads Table: shows ALL leads (with + without website)
                      → Email Draft: selectbox shows only no-website leads with their drafts
                      → Export: full CSV with email_draft column
                      → History: every unique query stored in session, no duplicates
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
- Leads Table: all scraped leads with metrics (total, targets without website, with phone)
- Email Draft: selectbox per lead — only no-website leads shown, 1 API call for all
- Export: download full CSV including email drafts
- History Panel: every unique query stored with timestamp, lead count, and CSV download — no duplicates

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

**9. Email generated only for first lead**
- Initially the email writer only processed `leads[0]` and returned a single draft
- Fix: Generate one LLM template with `{{NAME}}`, `{{CATEGORY}}`, `{{ADDRESS}}` placeholders, then do string `.replace()` for every lead — 1 API call total regardless of lead count

**10. Leads with websites being excluded from the table**
- Wanted all leads in the table but emails only for those without websites
- First attempt filtered the entire df to no-website leads only — so leads with websites disappeared everywhere
- Fix: Return all leads from `run_pipeline`, filter to no-website only inside the Email Draft tab in the UI

**11. `row.get()` silently returning None on pandas Series**
- Was using `row.get("website")` inside `iterrows()` — pandas Series does have `.get()` but it behaves differently from dict `.get()` and was returning `None` for all website values
- This caused the website filter to treat every lead as having no website
- Fix: Use direct `row["column"]` with explicit `pd.notna()` check instead

**12. Results disappearing when switching tabs or selecting a different lead**
- Streamlit reruns the entire script on every interaction — clicking a selectbox or switching tabs reset `run_btn` to `False`, wiping all results
- Fix: Store results in `st.session_state.current_df` after pipeline runs, render all tabs from session state outside the `if run_btn:` block

**13. `st.stop()` blocking tab rendering**
- Had `st.stop()` after the empty query warning — this halted the entire script so tabs never rendered on rerun
- Fix: Replaced with `else:` block so warning shows but tabs still render below

**14. `st.cache_resource.clear()` wiping cache on every rerun**
- Added it to force fresh imports but it was clearing the cached pipeline on every single Streamlit rerun, defeating the purpose
- Fix: Removed it — just do a full Streamlit restart (`Ctrl+C` + rerun) when backend code changes
