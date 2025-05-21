import streamlit as st
import pandas as pd
from db import SessionLocal, PromptEntry

st.set_page_config(page_title="Prompt Performance Dashboard", layout="wide")
st.title("📊 Prompt Performance Dashboard")

session = SessionLocal()
data = session.query(PromptEntry).all()
session.close()

# Convert to DataFrame
df = pd.DataFrame([{
    "Task": p.task_name,
    "Prompt Text": p.prompt_text,
    "Technique": p.feedback_comment.replace("Technique: ", "") if p.feedback_comment and "Technique:" in p.feedback_comment else "Manual Edit" if p.edited else "System Seed",
    "Rating": p.rating,
    "User Feedback": p.feedback_comment if p.rating is not None and "Technique:" not in p.feedback_comment else None,
    "Created": p.created_at.strftime('%Y-%m-%d %H:%M:%S')
} for p in data])

rated_df = df[df["Rating"].notnull()]

# ---------- SECTION 1: Ratings Summary ----------
if not rated_df.empty:
    st.subheader("📌 Average Ratings by Task")
    avg_task_ratings = rated_df.groupby("Task")["Rating"].mean().sort_values(ascending=False)
    st.bar_chart(avg_task_ratings)
else:
    st.info("No ratings available yet. Try generating and rating some prompts!")

# ---------- SECTION 2: Technique Breakdown ----------
if not rated_df.empty:
    st.subheader("🧠 Average Rating by Technique (per Task)")
    task_options = df["Task"].unique()
    selected_task = st.selectbox("Choose a Task", task_options)

    task_df = rated_df[rated_df["Task"] == selected_task]
    technique_avg = task_df.groupby("Technique")["Rating"].mean().sort_values(ascending=False)

    st.table(technique_avg)

# ---------- SECTION 3: Feedback Explorer ----------
st.subheader("💬 Browse Feedback")

if st.checkbox("Show only rows with written feedback"):
    feedback_df = rated_df[rated_df["User Feedback"].notnull()]
else:
    feedback_df = rated_df

st.dataframe(
    feedback_df[["Task", "Technique", "Rating", "User Feedback", "Prompt Text", "Created"]],
    use_container_width=True
)

# ---------- SECTION 4: Download ----------
st.subheader("⬇️ Download Full Prompt + Feedback Data")
csv = df.to_csv(index=False)
st.download_button("Download CSV", csv, "prompt_feedback_export.csv", mime="text/csv")
