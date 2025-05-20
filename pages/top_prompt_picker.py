import streamlit as st
import pandas as pd
from db import SessionLocal, PromptEntry

st.set_page_config(page_title="Top-Rated Prompts", layout="wide")
st.title("🏆 Top-Rated Prompts Per Task & Strategy")

session = SessionLocal()
data = session.query(PromptEntry).filter(PromptEntry.rating.isnot(None)).all()
session.close()

# Convert to DataFrame
df = pd.DataFrame([{
    "Task": p.task_name,
    "Prompt Text": p.prompt_text,
    "Technique": p.feedback_comment.replace("Technique: ", "") if p.feedback_comment and "Technique:" in p.feedback_comment else "Edited" if p.edited else "Original",
    "Rating": p.rating,
    "Created": p.created_at.strftime('%Y-%m-%d %H:%M:%S')
} for p in data])

# Group by Task and Technique, pick prompt with highest rating
top_prompts = df.sort_values("Rating", ascending=False).groupby(["Task", "Technique"]).first().reset_index()

# Show summary table
st.subheader("📊 Summary Table")
st.dataframe(top_prompts[["Task", "Technique", "Rating", "Created"]], use_container_width=True)

# Let user view full prompt text
st.subheader("🔍 View Top Prompt Text")
selected_task = st.selectbox("Select a Task", sorted(df["Task"].unique()))
filtered = top_prompts[top_prompts["Task"] == selected_task]

selected_technique = st.selectbox("Select a Technique", sorted(filtered["Technique"].unique()))
prompt_row = filtered[(filtered["Technique"] == selected_technique)].iloc[0]

st.markdown(f"**📘 Task:** {selected_task}  \n**🧠 Technique:** {selected_technique}  \n**⭐ Rating:** {prompt_row['Rating']}")
st.text_area("📝 Top-Rated Prompt", prompt_row["Prompt Text"], height=300)
