import streamlit as st
from db import setup_db, SessionLocal, PromptEntry

setup_db()

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
query = query.filter(PromptEntry.rating >= min_rating).order_by(PromptEntry.created_at.desc())

results = query.all()

st.markdown(f"### Showing {len(results)} prompts")
for entry in results:
    st.markdown(f"---")
    st.markdown(f"**🗂️ Category:** {entry.category}")
    st.markdown(f"**🕒 Created:** {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**⭐ Rating:** {entry.rating or '—'}")
    if entry.feedback_comment:
        st.markdown(f"**💬 Feedback:** {entry.feedback_comment}")
    st.code(entry.prompt_text, language="markdown")
    st.button("📋 Copy this prompt", key=f"copy_{entry.id}")

session.close()
