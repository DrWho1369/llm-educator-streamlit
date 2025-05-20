import streamlit as st
import requests

# ----------- PAGE CONFIG ------------
st.set_page_config(page_title="Differentiate Resource", layout="centered")

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
st.markdown("<div class='subtitle-text'>Paste your lesson content below and select one or more learning needs to instantly adapt it.</div>", unsafe_allow_html=True)

subject_text = st.text_area("Lesson Content / Worksheet", height=250, placeholder="Paste your worksheet, question, or task content here...")

options = st.multiselect(
    "Select differentiation needs:",
    list(prompt_templates.keys()),
    help="Choose one or more support types to adapt the content accordingly."
)

# ----------- SUBMIT ACTION ------------
if st.button("✨ Generate Differentiated Versions"):
    if not subject_text.strip():
        st.warning("Please enter some lesson content.")
    elif not options:
        st.warning("Please select at least one differentiation type.")
    else:
        for opt in options:
            with st.spinner(f"Generating {opt} version..."):
                prompt = prompt_templates[opt].format(subject_text)

                # --- Replace with your LLM API ---
                # Example placeholder response
                response = requests.post(
                    "https://your-llm-api.com/generate",
                    json={"prompt": prompt}
                )
                generated_text = response.json().get("text", "[No output returned]")
                # ---------------------------------

                st.markdown(f"### {opt} Version")
                st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)
