import streamlit as st
import requests
from db import setup_db, save_prompt_to_db, seed_original_prompts, SessionLocal, PromptEntry, seed_prompt_variants
import urllib.parse


setup_db()
seed_original_prompts()
seed_prompt_variants()

# ----------- PAGE CONFIG ------------
st.set_page_config(page_title="Differentiate Resource", layout="centered")

# Handle incoming query params
query_params = st.query_params
preloaded_category = query_params.get("category", [None])[0]
preloaded_prompt = query_params.get("prompt", [None])[0]



# ----------- STYLING ------------
st.markdown("""
    <style>
    .title-text {
        font-size: 2.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0.5em;
    }
    .subtitle-text {
        font-size: 1.1rem;
        color: #7f8c8d;
        margin-bottom: 1em;
    }
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .prompt-box {
        background-color: #f5f7fa;
        border-left: 5px solid #3498db;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1.5rem;
        white-space: pre-wrap;
    }
    .stMultiSelect>div>div>div {
        background-color: #ecf0f1;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------- PROMPT TEMPLATES ------------
prompt_templates = {
    "Simplified": "You are a teacher simplifying lesson content for a student with a reading age of 9 years. Rewrite the following resource using simpler vocabulary, shorter sentences, and clear structure while preserving meaning and core knowledge.\n\n{}",
    "Challenge Extension": "You are a gifted and talented coordinator. Extend the following task to provide a greater challenge for high-attaining students. Add one open-ended question, and one creative application or real-world connection.\n\n{}",
    "EAL Support": "You are an EAL support specialist. Modify the following resource to include sentence starters and a glossary of key terms with definitions in simple English.\n\n{}",
    "SEND Support": "You are a SEND teacher. Adapt this activity for students with moderate learning difficulties. Break the task into small, guided steps and use supportive language.\n\n{}",
    "Dyslexia-Friendly": "You are supporting students with dyslexia. Rewrite the following resource using short sentences and high-frequency words. Present content in readable chunks.\n\n{}",
    "Tiered": "You are creating a tiered version of this resource for a mixed-ability classroom. Provide:\n1. A simplified version\n2. A standard version\n3. A challenge version\n\n{}",
    "Sentence Starters": "You are helping students develop structured responses. Rewrite this worksheet to include sentence starters or writing frames for each question.\n\n{}",
}
# ----------- UI ELEMENTS ------------
st.markdown("<div class='title-text'>🧠 Differentiate Resource</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-text'>Paste your lesson content below and choose your differentiation type and prompting strategy.</div>", unsafe_allow_html=True)

subject_text = st.text_area(
    "Lesson Content / Worksheet", 
    height=250, 
    placeholder="Paste your worksheet, question, or task content here...", 
    value=preloaded_prompt if preloaded_prompt else ""
)

# --- Differentiation type (one only for now)
category = st.selectbox("What do your students need help with?", list(prompt_templates.keys()))

st.markdown("""
**What is this doing?**  
First, choose the type of support your students need (e.g., simplified task, scaffolded version).  
Then, choose how the AI will adapt the resource — using different prompting strategies (like role-based or few-shot prompting).
""")

# --- Strategy options from DB
session = SessionLocal()
variant_prompts = session.query(PromptEntry).filter(
    PromptEntry.category == category,
    PromptEntry.edited == False,
    PromptEntry.feedback_comment.like("Technique:%")
).all()
session.close()

# --- Show strategies
if variant_prompts:
    technique_options = [
        p.feedback_comment.replace("Technique: ", "") for p in variant_prompts
    ]
    selected_technique = st.selectbox("Choose Prompting Strategy:", technique_options)
    base_prompt_text = next(
        (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
        prompt_templates[category]  # fallback
    )
else:
    selected_technique = "Default Template"
    base_prompt_text = prompt_templates[category]

# Final prompt after inserting worksheet
raw_prompt = base_prompt_text.replace("[PASTE WORKSHEET HERE]", subject_text)

# Let user preview/edit the prompt
final_prompt = st.text_area(
    label="🔍 Preview & Edit Prompt to be Sent to the AI",
    value=raw_prompt,
    height=250
)

# ----------- SUBMIT ACTION ------------
if st.button("✨ Generate Differentiated Version"):
    if not subject_text.strip():
        st.warning("Please enter some lesson content.")
    else:
        with st.spinner(f"Generating {category} using {selected_technique} strategy..."):

            # Save prompt to DB
            save_prompt_to_db(
                category=category,
                prompt_text=final_prompt,
                edited=True
            )

            # Call LLM
            response = requests.post(
                "https://your-llm-api.com/generate",
                json={"prompt": final_prompt}
            )
            generated_text = response.json().get("text", "[No output returned]")

            # Show result
            st.markdown(f"### {category} – Strategy: {selected_technique}")
            st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

            # Rating & Feedback
            st.markdown("#### 💬 Rate this output")
            rating = st.slider("How helpful was this version?", 1, 5, key=f"rating_{category}")
            feedback = st.text_area("Any comments or suggestions?", key=f"feedback_{category}")

            if st.button(f"💾 Save Feedback for {category}"):
                save_prompt_to_db(
                    category=category,
                    prompt_text=final_prompt,
                    edited=True,
                    rating=rating,
                    feedback_comment=feedback
                )
                st.success("✅ Feedback saved!")


import pandas as pd
from io import StringIO

def download_prompt_csv():
    session = SessionLocal()
    prompts = session.query(PromptEntry).all()
    session.close()

    # Convert to DataFrame
    df = pd.DataFrame([{
        "Category": p.category,
        "Prompt Text": p.prompt_text,
        "Edited": p.edited,
        "Rating": p.rating,
        "Feedback": p.feedback_comment,
        "Created At": p.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for p in prompts])

    csv = StringIO()
    df.to_csv(csv, index=False)
    return csv.getvalue()

csv_data = download_prompt_csv()

st.download_button(
    label="⬇️ Download All Prompts as CSV",
    data=csv_data,
    file_name='differentiated_prompts.csv',
    mime='text/csv'
)
