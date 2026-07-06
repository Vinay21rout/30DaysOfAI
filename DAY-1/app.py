import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(__file__))

@st.cache_resource
def load_pipeline():
    from lead_generation_automation import run_pipeline
    return run_pipeline

run_pipeline = load_pipeline()

st.set_page_config(page_title="Lead Gen Automation", page_icon="🤖", layout="wide")
st.title("🤖 AI Lead Generation Automation")
st.caption("Powered by Apify + LangGraph + Groq LLM")

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
tab1, tab2, tab3 = st.tabs(["📊 Leads Table", "✉️ Email Draft", "📁 Export"])

if run_btn:
    if not search_query:
        st.warning("Please enter a search query.")
        st.stop()

    try:
        render_step(step1, "Scraper Agent", "running")
        render_step(step2, "Parser Agent", "running")
        render_step(step3, "Email Writer Agent", "running")

        with st.spinner("⚙️ Running automation pipeline..."):
            df, email_draft = run_pipeline(search_query, max_places)

        render_step(step1, "Scraper Agent", "done")
        render_step(step2, "Parser Agent", "done")
        render_step(step3, "Email Writer Agent", "done")

        # ── Leads Table ───────────────────────────────────────────────────────
        with tab1:
            st.success(f"✅ {len(df)} leads scraped successfully!")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", len(df))
            col2.metric("With Phone", df["phone"].notna().sum())
            col3.metric("With Website", df["website"].notna().sum())
            st.dataframe(df, use_container_width=True, height=450)

        # ── Email Draft ───────────────────────────────────────────────────────
        with tab2:
            first_name = df["name"].iloc[0] if not df.empty else "Lead"
            st.subheader(f"📧 Draft for: {first_name}")
            st.info(email_draft)
            st.download_button("⬇️ Download Email Draft", email_draft, file_name="email_draft.txt")

        # ── Export ────────────────────────────────────────────────────────────
        with tab3:
            st.subheader("📁 Export Leads")
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download leads.csv", csv, file_name="leads.csv", mime="text/csv")
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        render_step(step1, "Scraper Agent", "error")
        st.error(f"Pipeline failed: {e}")
        st.exception(e)
