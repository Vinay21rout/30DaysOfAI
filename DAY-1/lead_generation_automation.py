from typing import TypedDict, Union
from langgraph.graph import StateGraph, END
import pandas as pd
import os
import requests
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

llm_groq = ChatGroq(model="llama-3.1-8b-instant")

class LeadState(TypedDict):
    category: str
    max_places: int
    csv_path: str
    parsed_path: str
    lead: dict
    email: str

def scraper_agent(state: LeadState) -> LeadState:
    APIFY_TOKEN = os.getenv("APIFY_API_KEY")
    ACTOR_ID = "compass~crawler-google-places"
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items?token={APIFY_TOKEN}"
    payload = {"searchStringsArray": [state["category"]], "maxCrawledPlaces": state["max_places"], "language": "en"}
    response = requests.post(url, json=payload)
    raw = response.json()
    if isinstance(raw, dict) and "error" in raw:
        raise RuntimeError(f"Apify error: {raw['error']}")
    if not isinstance(raw, list) or len(raw) == 0:
        raise RuntimeError("No leads returned")
    csv_path = os.path.join(os.path.dirname(__file__), "leads.csv")
    pd.DataFrame(raw).to_csv(csv_path, index=False)
    return {**state, "csv_path": csv_path}

def parser_agent(state: LeadState) -> LeadState:
    csv_path = state.get("csv_path", "")
    if not csv_path or not os.path.exists(csv_path):
        raise RuntimeError("leads.csv not found")
    df = pd.read_csv(csv_path)
    parsed = []
    for _, row in df.iterrows():
        parsed.append({
            "name":     row["title"]     if "title"        in row and pd.notna(row["title"])        else None,
            "category": row["categoryName"] if "categoryName" in row and pd.notna(row["categoryName"]) else None,
            "address":  row["address"]   if "address"      in row and pd.notna(row["address"])      else None,
            "phone":    row["phone"]     if "phone"        in row and pd.notna(row["phone"])        else None,
            "email":    row["email"]     if "email"        in row and pd.notna(row["email"])        else None,
            "website":  row["website"]   if "website"      in row and pd.notna(row["website"])      else None,
            "rating":   row["totalScore"] if "totalScore"  in row and pd.notna(row["totalScore"])   else None,
        })
    parsed_path = os.path.join(os.path.dirname(__file__), "parsed_leads.csv")
    pd.DataFrame(parsed).to_csv(parsed_path, index=False)
    return {**state, "parsed_path": parsed_path, "lead": parsed[0]}

def email_writer_agent(state: LeadState) -> LeadState:
    df = pd.read_csv(state["parsed_path"])

    prompt = """You are an outreach email writer. Write a professional cold email to {{NAME}}, who runs a {{CATEGORY}} located at {{ADDRESS}}.
Explain how a simple website can help attract more customers.
Keep it concise, well structured with subject line, body, and sign-off.
Use exactly these placeholders in the email: {{NAME}}, {{CATEGORY}}, {{ADDRESS}}.
Do not replace them — keep them as-is. Mark the draft as 'Pending Approval'.

Sign off with:
Best regards,
Vinay
LeadGen
Phone: +91 8709265396
Email: routvinay83@gmail.com"""

    template = llm_groq.invoke(prompt).content

    emails = []
    for _, row in df.iterrows():
        has_website = pd.notna(row["website"]) and str(row["website"]).strip() not in ["", "nan", "None"]
        if has_website:
            emails.append(None)
            continue
        name     = str(row["name"])     if pd.notna(row["name"])     else "Business Owner"
        category = str(row["category"]) if pd.notna(row["category"]) else "business"
        address  = str(row["address"])  if pd.notna(row["address"])  else "your location"
        emails.append(template.replace("{{NAME}}", name).replace("{{CATEGORY}}", category).replace("{{ADDRESS}}", address))

    df["email_draft"] = emails
    df.to_csv(state["parsed_path"], index=False)

    first_email = next((e for e in emails if e is not None), "")
    return {**state, "email": first_email}

workflow = StateGraph(LeadState)
workflow.add_node("scraper", scraper_agent)
workflow.add_node("parser", parser_agent)
workflow.add_node("email_writer", email_writer_agent)
workflow.add_edge("scraper", "parser")
workflow.add_edge("parser", "email_writer")
workflow.add_edge("email_writer", END)
workflow.set_entry_point("scraper")
pipeline = workflow.compile()

def run_pipeline(category: str, max_places: int) -> tuple[pd.DataFrame, str]:
    result = pipeline.invoke({"category": category, "max_places": max_places, "csv_path": "", "parsed_path": "", "lead": {}, "email": ""})
    parsed_path = result.get("parsed_path", "")
    if not parsed_path or not os.path.exists(parsed_path):
        raise RuntimeError(f"parsed_leads.csv not created. Pipeline state: {result}")
    df = pd.read_csv(parsed_path)  # all leads
    return df, result["email"]

if __name__ == "__main__":
    df, email = run_pipeline("restaurants in Raigarh", 10)
    print(df)
    print(email)
