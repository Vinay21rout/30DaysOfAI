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
            "name":     row.get("title"),
            "category": row.get("categoryName"),
            "address":  row.get("address"),
            "phone":    row.get("phone"),
            "email":    row.get("email"),
            "website":  row.get("website"),
            "rating":   row.get("totalScore"),
        })
    parsed_path = os.path.join(os.path.dirname(__file__), "parsed_leads.csv")
    pd.DataFrame(parsed).to_csv(parsed_path, index=False)
    return {**state, "parsed_path": parsed_path, "lead": parsed[0]}

def email_writer_agent(state: LeadState) -> LeadState:
    lead = state["lead"]
    name     = lead.get("name")     or "the business owner"
    category = lead.get("category") or "business"
    address  = lead.get("address")  or ""
    prompt = f"You are an outreach email writer. Write a professional but friendly cold email to {name}, who runs a {category}"
    if address:
        prompt += f" located at {address}."
    prompt += " Explain how a simple website can help attract more customers. Keep it concise and end with a clear call to action. Do not invent missing details. Mark the draft as 'Pending Approval'."
    prompt += """

Sign off the email with:
Best regards,
Vinay
LeadGen
Phone: +91 8709265396
Email: routvinay83@gmail.com"""
    return {**state, "email": llm_groq.invoke(prompt).content}

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
    df = pd.read_csv(parsed_path)
    return df, result["email"]

if __name__ == "__main__":
    df, email = run_pipeline("restaurants in Raigarh", 10)
    print(df)
    print(email)
