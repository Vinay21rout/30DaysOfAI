import streamlit as st
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

@st.cache_resource
def load_pipeline():
    from lead_generation_automation import run_pipeline
    return run_pipeline

run_pipeline = load_pipeline()

st.set_page_config(page_title="Lead Gen Automation", page_icon="🤖", layout="wide")
st.title("🤖 AI Lead Generation Automation")
st.caption("Powered by Apify + LangGraph + Groq LLM")

# ── Session state init ────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "current_df" not in st.session_state:
    st.session_state.current_df = None
if "current_email" not in st.session_state:
    st.session_state.current_email = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    search_query = st.text_input("Search Query", placeholder="e.g. restaurants in Raigarh")
    max_places = st.slider("Max Places to Scrape", 5, 100, 20)
    run_btn = st.button("🚀 Run Automation", use_container_width=True, type="primary")
    st.divider()
    st.markdown("**Workflow Steps**")
    step1 = st.empty()
    step2 = st.empty()
    step3 = st.empty()

def render_step(placeholder, label, status):
    icons = {"pending": "⬜", "running": "🔄", "done": "✅", "error": "❌"}
    placeholder.markdown(f"{icons[status]} **{label}**")

render_step(step1, "Scraper Agent", "pending")
render_step(step2, "Parser Agent", "pending")
render_step(step3, "Email Writer Agent", "pending")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Leads Table", "✉️ Email Draft", "📁 Export", "🕓 History"])

if run_btn:
    if not search_query:
        st.warning("Please enter a search query.")
    else:
        try:
            render_step(step1, "Scraper Agent", "running")
            render_step(step2, "Parser Agent", "running")
            render_step(step3, "Email Writer Agent", "running")

            with st.spinner("⚙️ Running automation pipeline..."):
                df_result, email_draft = run_pipeline(search_query, max_places)
                st.session_state.current_df = df_result
                st.session_state.current_email = email_draft

            render_step(step1, "Scraper Agent", "done")
            render_step(step2, "Parser Agent", "done")
            render_step(step3, "Email Writer Agent", "done")

            # ── Save to history (no duplicates for same query) ────────────────────
            existing_queries = [h["query"] for h in st.session_state.history]
            if search_query not in existing_queries:
                st.session_state.history.append({
                    "query": search_query,
                    "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "count": len(df_result),
                    "df": df_result,
                    "email": email_draft,
                })
            else:
                for h in st.session_state.history:
                    if h["query"] == search_query:
                        h.update({"time": datetime.now().strftime("%d %b %Y, %I:%M %p"), "count": len(df_result), "df": df_result, "email": email_draft})

        except Exception as e:
            render_step(step1, "Scraper Agent", "error")
            st.error(f"Pipeline failed: {e}")
            st.exception(e)

# ── Always render tabs from session state ─────────────────────────────────────
df = st.session_state.current_df

with tab1:
    if df is not None:
        st.success(f"✅ {len(df)} leads scraped successfully!")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Leads", len(df))
        col2.metric("With Phone", df["phone"].notna().sum())
        col3.metric("Targets (No Website)", df["email_draft"].notna().sum())
        st.dataframe(df, use_container_width=True, height=450)
    else:
        st.info("Run the automation to see leads here.")

with tab2:
    if df is not None:
        st.caption("1 API call used · emails drafted only for leads without a website")
        df_targets = df[df["email_draft"].notna()].reset_index(drop=True)
        if df_targets.empty:
            st.warning("No leads without a website found.")
        else:
            lead_names = df_targets["name"].fillna("Unknown").tolist()
            selected = st.selectbox("Select a lead to view email", lead_names)
            idx = lead_names.index(selected)
            draft = df_targets["email_draft"].iloc[idx]
            st.subheader(f"📧 Draft for: {selected}")
            st.info(draft)
            st.download_button("⬇️ Download this Email", draft, file_name=f"email_{idx+1}.txt")
            all_emails = "\n\n" + "="*60 + "\n\n".join(
                [f"Lead {i+1}: {df_targets['name'].iloc[i]}\n\n{df_targets['email_draft'].iloc[i]}" for i in range(len(df_targets))]
            )
            st.download_button("⬇️ Download All Emails", all_emails, file_name="all_emails.txt")
    else:
        st.info("Run the automation to see email drafts here.")

with tab3:
    if df is not None:
        st.subheader("📁 Export Leads")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download leads.csv", csv, file_name="leads.csv", mime="text/csv")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Run the automation to export leads.")

# ── History Tab ───────────────────────────────────────────────────────────────
with tab4:
    if not st.session_state.history:
        st.info("No runs yet. Run the automation to see history here.")
    else:
        st.subheader(f"🕓 Run History ({len(st.session_state.history)} unique queries)")
        for i, h in enumerate(reversed(st.session_state.history)):
            with st.expander(f"🔍 {h['query']}  ·  {h['count']} leads  ·  {h['time']}"):
                st.dataframe(h["df"], use_container_width=True)
                csv = h["df"].to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download CSV",
                    csv,
                    file_name=f"{h['query'].replace(' ', '_')}.csv",
                    mime="text/csv",
                    key=f"hist_dl_{i}"
                )
