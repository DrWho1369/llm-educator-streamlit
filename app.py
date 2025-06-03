import streamlit as st
import requests
from summarizer import analyze_pdf 
from pdf_extractor import extract_text_from_pdf
from prompts import user_prompts

import re

def clean_user_input(text):
    return re.sub(r"[^\w\s.,?!-]", "", text)

def extract_flashcards(text):
    lines = text.strip().split("\n")
    cards = []
    question, answer = "", ""
    for line in lines:
        if line.strip().startswith("Q:"):
            question = line.strip()[2:].strip()
        elif line.strip().startswith("A:"):
            answer = line.strip()[2:].strip()
            if question and answer:
                cards.append((question, answer))
                question, answer = "", ""
    return cards

def render_flashcard_grid(flashcards):
    st.markdown("""
        <style>
        .flashcard-box {
            background-color: #f9f9f9;
            border: 2px solid #3498db;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .flashcard-question {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        .flashcard-answer {
            color: #34495e;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🃏 Flashcard View")

    cols = st.columns(2)
    for idx, (q, a) in enumerate(flashcards):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="flashcard-box">
                    <div class="flashcard-question">Q: {q}</div>
                    <div class="flashcard-answer">A: {a}</div>
                </div>
            """, unsafe_allow_html=True)

# --- Set API call URL ---
LLM_API_URL = st.secrets["LLM_API_URL"]

# --- Page Config ---
st.set_page_config(page_title="Prompt Tester", layout="centered")
st.title("OI-TA")

# --- TASK BUTTONS  ---
task_labels = [
    "Differentiate Resource",
    "Generate Parent Message",
    "Plan & Print",
    "Reformat & Repurpose Resource",
    "Emotion Check-in Templates",
    "Simplified Instruction Scripts",
    "Functional Literacy Activities",
    "Behavior Reflection Sheets"
]


task_descriptions = {
    "Differentiate Resource": "Tailor a teaching resource into 3 ability levels",
    "Generate Parent Message": "Create a message to update parents",
    "Plan & Print": "Generate lesson plan + printable resources",
    "Reformat & Repurpose Resource": "Convert into flashcards, MCQs, etc.",
    "Emotion Check-in Templates": "Create easy-to-use mood check-in templates.",
    "Simplified Instruction Scripts": "Turn routines into simple, repeatable step-by-step instructions.",
    "Functional Literacy Activities": "Design life-skills literacy tasks like reading signs or writing lists.",
    "Behavior Reflection Sheets": "Generate student-friendly prompts to reflect on behavior."
}

st.subheader("Choose a task:")

if "selected_task" not in st.session_state:
    st.session_state["selected_task"] = None

if "selected_subtask" not in st.session_state:
    st.session_state["selected_subtask"] = None

cols_per_row = 4
for i, label in enumerate(task_labels):
    if i % cols_per_row == 0:
        cols = st.columns(cols_per_row)
    with cols[i % cols_per_row]:
        button_class = "task-button-selected" if st.session_state["selected_task"] == label else "task-button"
        if st.button(f"{label}", key=label, help=task_descriptions[label]):
            st.session_state["selected_task"] = label
            st.session_state["selected_subtask"] = None

# --- STYLE ---
st.markdown("""
<style>
.task-button {
    background-color: #f0f0f0;
    border: 2px solid #ccc;
    border-radius: 8px;
    padding: 0.5rem;
    text-align: center;
    font-weight: bold;
    cursor: pointer;
}
.task-button:hover {
    background-color: #e0e0e0;
}
.task-button-selected {
    background-color: #3498db !important;
    color: white !important;
    border: 2px solid #2980b9;
}
</style>
""", unsafe_allow_html=True)


if st.session_state["selected_task"]:
    st.markdown(f"""
    <script>
    const buttons = window.parent.document.querySelectorAll('button[kind="secondary"]');
    buttons.forEach(btn => {{
        if (btn.innerText === '{st.session_state['selected_task']}') {{
            btn.classList.add("selected");
        }}
    }});
    </script>
    """, unsafe_allow_html=True)

if not st.session_state["selected_task"]:
    st.stop()

selected_task = st.session_state.get("selected_task")

allow_pdf_upload = selected_task in [
        "Differentiate Resource",
        "Plan & Print",
        "Reformat & Repurpose Resource",
    ]

input_method = None
user_input = ""
uploaded_file = None
keywords = {}

if allow_pdf_upload:
    st.subheader("Choose input method:")
    input_method = st.radio("", ["Text Input", "Upload PDF"])
else:
    input_method = "Text Input"

if input_method == "Upload PDF":
    st.subheader("Upload a PDF")
    uploaded_file = st.file_uploader("", type="pdf", key="pdf_upload")

    if uploaded_file:
        # Only run analysis if the file is newly uploaded
        if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
            with st.spinner("Analyzing PDF..."):
                text = extract_text_from_pdf(uploaded_file)
                result_data = analyze_pdf(text)

                # Save results in session state
                st.session_state["extracted_keywords"] = result_data["keywords"]
                st.session_state["user_input"] = (
                    "\n\n[Extracted Keywords]\n" +
                    "\n".join(", ".join(words) for words in result_data["keywords"].values())
                )
                st.session_state["img_base64"] = result_data["wordcloud"]
                st.session_state["last_uploaded_filename"] = uploaded_file.name

        # Always show the results from session state
        if st.session_state.get("img_base64"):
            st.subheader("Generated Word Cloud")
            st.image(f"data:image/png;base64,{st.session_state['img_base64']}")


        st.markdown("### 🧠 Extracted Keywords")
        st.markdown(st.session_state.get("user_input", "_No keywords found._"))

# — Handle text input path —
elif input_method == "Text Input":
    if st.session_state.get("selected_task") != "Emotion Check-in Templates":
        user_input = st.text_area("Paste lesson content, parent update, etc:", height=250)
        word_count = len(user_input.split())

        if word_count < 10:
            st.warning("✏️ Try to expand your input so the AI can generate a meaningful response.")
        
        # ✅ Save to session_state
        st.session_state["user_input"] = user_input

    else:
        user_input = st.text_area("Optional: Add context or focus area for the templates", height=150)
        st.session_state["user_input"] = ""  # Emotion Check-in generates content without needing input

    

selected_task = st.session_state["selected_task"]
selected_subtask = st.session_state["selected_subtask"]

if selected_task == "Reformat & Repurpose Resource":
    st.markdown("#### Choose how to repurpose the content:")
    subtask_cols = st.columns(3)
    with subtask_cols[0]:
        if st.button("Convert to MCQ"):
            st.session_state["selected_subtask"] = "Convert to MCQ"
            st.rerun()
    with subtask_cols[1]:
        if st.button("Convert to Flashcards"):
            st.session_state["selected_subtask"] = "Convert to Flashcards"
            st.rerun()
    with subtask_cols[2]:
        if st.button("Group Discussion Task"):
            st.session_state["selected_subtask"] = "Group Discussion Task"
            st.rerun()

if selected_task == "Plan & Print" or selected_task == "Behavior Reflection Sheets" or (selected_task == "Reformat & Repurpose Resource" and selected_subtask):
    st.subheader("Age Category")
    year_group = st.selectbox("", [
        "Early Years / KS1 (4–7)", "Lower KS2 (7–9)", "Upper KS2 (9–11)",
        "KS3 / Lower Secondary (11–14)", "KS4 / GCSE (14–16)", "Post-16 / A-Level (16–18)"
    ])

if selected_task == "Reformat & Repurpose Resource" and selected_subtask in ["Convert to MCQ", "Convert to Flashcards"]:
    st.subheader("Number of Items to Generate")
    num_mcq = st.slider("", 1, 20, value=10)
else:
    num_mcq = 0

if selected_task == "Emotion Check-in Templates":
    st.subheader("Number of check-in templates to generate")
    num_templates = st.slider("", 1, 10, value=3)
else:
    num_templates = 0

#--- Generation Button ---
st.markdown("""
    <div style="margin-top:2rem;margin-bottom:1rem;border-bottom:2px solid #ccc;"></div>
""", unsafe_allow_html=True)
st.markdown("### Now Generate the Output")

if st.button("🚀 Generate Output", key="generate_btn"):
    task_key = selected_subtask if selected_task == "Reformat & Repurpose Resource" else selected_task

    # --- Determine user_input based on method ---
    if input_method == "Upload PDF":
        user_input = "[Text extracted from uploaded PDF]"
    else:
        user_input = st.session_state.get("user_input", "").strip()
        user_input = clean_user_input(user_input)

    
    # --- Get extracted keywords from session ---
    keywords = st.session_state.get("extracted_keywords", {})
    keyword_summary = ""
    if keywords:
        # Flatten all keyword lists into one combined list
        flat_keywords = []
        for word_list in keywords.values():
            flat_keywords.extend(word_list)
    
        # Deduplicate and trim
        unique_keywords = list(dict.fromkeys(flat_keywords))[:250] 
        keyword_summary = "\n\n" + ", ".join(unique_keywords)

    full_input = f"User Input: {user_input}{keyword_summary}"

    user_prompt_template = user_prompts[task_key]
    user_prompt = user_prompt_template.format(
        year_group=year_group if 'year_group' in user_prompt_template else "",
        duration=duration if 'duration' in locals() else "",
        num_mcq=num_mcq,
        num_flashcards=num_mcq,
        num_templates=num_templates
    )

    if selected_task != "Emotion Check-in Templates" and not user_input.strip():
        st.warning("⚠️ Please enter some content or upload a PDF above.")

    else:
        with st.spinner(f"Generating output for: {selected_task}..."):
            response = requests.post(
                LLM_API_URL,
                json={
                    "messages": [
                        {"role": "system", "content": user_prompt.strip()},
                        {"role": "user", "content": full_input.strip()},
                    ]
                }
            )

            try:
                output = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                st.error(f"❌ Failed to parse API response: {e}")
                st.code(response.text)
                output = "[No output returned]"

        
        if selected_task == "Reformat & Repurpose Resource" and selected_subtask == "Convert to Flashcards":
            flashcards = extract_flashcards(output)
            if flashcards:
                render_flashcard_grid(flashcards)
            else:
                st.markdown("❗ Could not extract flashcards. Displaying raw output below:")
        st.markdown(f"### Raw AI Output")
        st.markdown(f"<div class='prompt-box'>{output}</div>", unsafe_allow_html=True)
        st.download_button("Copy/Download Output", data=output, file_name="output.txt")
        st.markdown(f"### Prompt Sent to AI")
        st.code(f"[System Prompt]\n{user_prompt}\n\n[User Input]\n{full_input.strip()}\n\n", language="markdown")
        st.session_state["extracted_keywords"] = {}

st.markdown("""
<style>
.prompt-box {
    background-color: #f5f7fa;
    border-left: 5px solid #3498db;
    padding: 1rem;
    border-radius: 8px;
    white-space: pre-wrap;
    color: #2c3e50;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)
