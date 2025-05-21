import streamlit as st
from db import setup_db, SessionLocal, PromptEntry
import urllib.parse
from datetime import datetime

# ---- DB INIT ----
setup_db()

st.set_page_config(page_title="Prompt History", layout="wide")
st.title("📚 Prompt History & Reuse")

session = SessionLocal()

# ---- FILTER OPTIONS ----
with st.sidebar:
    st.header("🔍 Filter Prompts")
    task_filter = st.selectbox("Task Name", ["All"] + sorted({p.task_name for p in session.query(PromptEntry).all()}))
    technique_filter = st.selectbox("Technique", ["All"] + sorted({
        p.feedback_comment.replace("Technique: ", "")
        for p in session.query(PromptEntry).filter(PromptEntry.feedback_comment.like("Technique:%"))
    }))
    edited_filter = st.radio("Prompt Type", ["All", "Original", "Edited"])
    min_rating = st.slider("Minimum Rating", 1, 5, 3)
    date_filter = st.date_input("From Date", value=datetime(2023, 1, 1))

# ---- FETCH PROMPTS ----
query = session.query(PromptEntry)
if task_filter != "All":
    query = query.filter(PromptEntry.task_name == task_filter)
if technique_filter != "All":
    query = query.filter(PromptEntry.feedback_comment == f"Technique: {technique_filter}")
if edited_filter == "Original":
    query = query.filter(PromptEntry.edited == False)
elif edited_filter == "Edited":
    query = query.filter(PromptEntry.edited == True)
query = query.filter((PromptEntry.rating >= min_rating) | (PromptEntry.rating == None))
query = query.filter(PromptEntry.created_at >= datetime.combine(date_filter, datetime.min.time()))
query = query.order_by(PromptEntry.created_at.desc())

results = query.all()

st.markdown(f"### Showing {len(results)} prompts")
for entry in results:
    st.markdown("---")
    badge = "🌱 Original" if not entry.edited else "✏️ Edited"
    st.markdown(f"**🗂️ Task:** {entry.task_name} &nbsp;&nbsp;&nbsp;&nbsp;{badge}")
    st.markdown(f"**🕒 Created:** {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    if entry.rating:
        st.markdown(f"**⭐ Rating:** {entry.rating}")
    if entry.feedback_comment:
        st.markdown(f"**💬 Feedback:** {entry.feedback_comment}")

    display_text = entry.prompt_text[:500] + "..." if len(entry.prompt_text) > 500 else entry.prompt_text
    st.code(display_text, language="markdown")

    if st.button(f"🧪 Try in App: {entry.task_name}", key=f"try_{entry.id}"):
        st.query_params.update({
            "task_name": entry.task_name,
            "prompt": entry.prompt_text
        })
        st.success("🔁 Head to the Home page to use this prompt!")

session.close()
