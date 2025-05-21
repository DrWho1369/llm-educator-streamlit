import streamlit as st
import pandas as pd
from db import SessionLocal, PromptEntry

st.set_page_config(page_title="Top-Rated Prompts", layout="wide")
st.title("🏆 Top-Rated Prompts Per Task & Strategy")

# --- Load Data ---
session = SessionLocal()
data = session.query(PromptEntry).filter(PromptEntry.rating.isnot(None)).all()
session.close()

df = pd.DataFrame([{
    "Task": p.task_name,
    "Prompt Text": p.prompt_text,
    "Technique": p.feedback_comment.replace("Technique: ", "") if p.feedback_comment and "Technique:" in p.feedback_comment else "Manual Edit" if p.edited else "System Seed",
    "Rating": p.rating,
    "Created": p.created_at.strftime('%Y-%m-%d %H:%M:%S')
} for p in data])

if df.empty:
    st.warning("No rated prompts yet. Once you start saving feedback, the top-rated prompts will appear here.")
    st.stop()

# --- Get Top-Rated Prompt per (Task + Technique) ---
top_prompts = df.sort_values("Rating", ascending=False).groupby(["Task", "Technique"]).first().reset_index()

# --- Section 1: Chart of Top 5 Prompts Overall ---
st.subheader("📈 Top 5 Highest Rated Prompts (All Tasks)")
top5 = df.sort_values("Rating", ascending=False).head(5)
chart_data = top5[["Task", "Technique", "Rating"]].copy()
chart_data["Label"] = chart_data["Task"] + " / " + chart_data["Technique"]
chart_data = chart_data.set_index("Label")
st.bar_chart(chart_data[["Rating"]])

# --- Section 2: Summary Table ---
st.subheader("📊 Summary Table (All Top-Rated Prompts)")
styled_df = top_prompts.copy()
styled_df["Highlight"] = styled_df["Rating"].apply(lambda x: "⭐" if x > 5 else "")
styled_df_display = styled_df[["Task", "Technique", "Rating", "Created", "Highlight"]]
st.dataframe(styled_df_display, use_container_width=True)

# --- Section 3: Prompt Viewer ---
st.subheader("🔍 View Top Prompt Text")
selected_task = st.selectbox("Select a Task", sorted(df["Task"].unique()))
filtered = top_prompts[top_prompts["Task"] == selected_task]

if filtered.empty:
    st.info("No techniques rated yet for this task.")
    st.stop()

selected_technique = st.selectbox("Select a Technique", sorted(filtered["Technique"].unique()))
prompt_row = filtered[filtered["Technique"] == selected_technique].iloc[0]

# Highlight prompt box if rated > 5
highlight = prompt_row["Rating"] > 5
rating_display = f"**⭐ Rating:** {prompt_row['Rating']}" if not highlight else f"<span style='color:green;font-weight:bold'>🌟 Rating: {prompt_row['Rating']}</span>"

st.markdown(f"**📘 Task:** {selected_task}  \n**🧠 Technique:** {selected_technique}", unsafe_allow_html=True)
st.markdown(rating_display, unsafe_allow_html=True)

st.text_area("📝 Top-Rated Prompt", prompt_row["Prompt Text"], height=300)

# Streamlit Button: Load this prompt in app
if st.button("🧪 Try This Prompt in the App"):
    st.query_params.update({
        "task_name": selected_task,
        "prompt": prompt_row["Prompt Text"]
    })
    st.success("✅ Prompt loaded! Go to the Home page to try it.")

# --- Section 4: Download Top Prompts ---
csv = top_prompts.to_csv(index=False)
st.download_button("⬇️ Download Top-Rated Prompts", csv, "top_rated_prompts.csv", mime="text/csv")
