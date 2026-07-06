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
