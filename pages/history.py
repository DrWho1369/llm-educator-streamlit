import streamlit as st
from db import setup_db, seed_original_prompts, SessionLocal, PromptEntry
import urllib.parse

setup_db()
seed_original_prompts()

st.set_page_config(page_title="Prompt History", layout="wide")
st.title("📚 Prompt History & Reuse")

session = SessionLocal()

# ---- FILTER OPTIONS ----
with st.sidebar:
    st.header("🔍 Filter Prompts")
    category_filter = st.selectbox("Category", ["All"] + sorted({p.category for p in session.query(PromptEntry).all()}))
    min_rating = st.slider("Minimum Rating", 1, 5, 3)

# ---- FETCH PROMPTS ----
query = session.query(PromptEntry)
if category_filter != "All":
    query = query.filter(PromptEntry.category == category_filter)
query = query.filter((PromptEntry.rating >= min_rating) | (PromptEntry.rating == None))
query = query.order_by(PromptEntry.created_at.desc())

results = query.all()

st.markdown(f"### Showing {len(results)} prompts")
for entry in results:
    st.markdown("---")
    badge = "🌱 Original" if not entry.edited else "✏️ Edited"
    st.markdown(f"**🗂️ Category:** {entry.category} &nbsp;&nbsp;&nbsp;&nbsp;{badge}")
    st.markdown(f"**🕒 Created:** {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    if entry.rating:
        st.markdown(f"**⭐ Rating:** {entry.rating}")
    if entry.feedback_comment:
        st.markdown(f"**💬 Feedback:** {entry.feedback_comment}")

    # Show truncated version in UI (for readability)
    display_text = entry.prompt_text[:500] + "..." if len(entry.prompt_text) > 500 else entry.prompt_text
    st.code(display_text, language="markdown")

    # Use a button to update query params instead of encoding long prompt into a URL
    if st.button(f"🧪 Try in App: {entry.category}", key=f"try_{entry.id}"):
        st.query_params.update({
            "category": entry.category,
            "prompt": entry.prompt_text
        })
        st.success("🔁 Head to the Home page to use this prompt!")

session.close()
