import streamlit as st
import requests
import PyPDF2
from pdf_summariser import summarize_uploaded_pdf
from prompts.py import *

# --- Set API call URL ---
LLM_API_URL = st.secrets["LLM_API_URL"]

# --- Page Config ---
st.set_page_config(page_title="Prompt Tester", layout="centered")

st.title("OI-TA")

# --- INITAL TASK BUTTONS  ---

# Define task buttons names and hover descriptions
task_labels = [
    "Differentiate Resource",
    "Generate Parent Message",
    "Plan & Print",
    "Reformat & Repurpose Resource",
    "Emotion Check-in Templates"
]

task_descriptions = {
    "Differentiate Resource": "Tailor a teaching resource into 3 ability levels",
    "Generate Parent Message": "Create a message to update parents",
    "Plan & Print": "Generate lesson plan + printable resources",
    "Reformat & Repurpose Resource": "Convert into flashcards, MCQs, etc.",
    "Emotion Check-in Templates": "Create easy-to-use mood check-in templates."
}

st.subheader("Choose a task:")

# --- Initialise state for task highlight ---
if "selected_task" not in st.session_state:
    st.session_state["selected_task"] = None

if "selected_subtask" not in st.session_state:
    st.session_state["selected_subtask"] = None

# --- Generating the actual buttons ---
cols_per_row = 4
for i, label in enumerate(task_labels):
    if i % cols_per_row == 0:
        cols = st.columns(cols_per_row)
    with cols[i % cols_per_row]:
        button_class = "task-button-selected" if st.session_state["selected_task"] == label else "task-button"
        if st.button(f"{label}", key=label, help=task_descriptions[label]):
            st.session_state["selected_task"] = label
            st.session_state["selected_subtask"] = None

# --- Adding HTML/CSS button styling ---
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

# Forcefully update the style of the selected button using JavaScript
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

# --- UI to show nothing else until a task is selected ---
if not st.session_state["selected_task"]:
    st.stop()

# --- Show content input only if a task is selected ---

# --- Functionality for PDF upload or Text Generation
if st.session_state["selected_task"]:
    selected_task = st.session_state["selected_task"]
    st.markdown(f"### Task Selected: {selected_task}")

    allow_pdf_upload = selected_task in [
        "Differentiate Resource",
        "Plan & Print",
        "Reformat & Repurpose Resource",
    ]

    # — Initialize shared variables —
    input_method = None
    user_input = ""
    uploaded_file = None
    pdf_text = None

    # — Let user pick input method if PDF is allowed —
    if allow_pdf_upload:
        input_method = st.radio("Choose input method:", ["Text Input", "Upload PDF"])
    else:
        input_method = "Text Input"

    # — Handle PDF upload path —
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload a PDF", type="pdf", key="pdf_upload")
        if uploaded_file:
            summarized_chunks = summarize_uploaded_pdf(uploaded_file, LLM_API_URL)
            summarized_text = "\n".join(summarized_chunks)
            st.text_area("Summarized PDF Text", value=summarized_text, height=300)
            user_input = summarized_text


    # — Handle text input path —
    elif input_method == "Text Input":
        if st.session_state.get("selected_task") != "Emotion Check-in Templates":
            user_input = st.text_area("Paste lesson content, parent update, etc:", height=250)
            word_count = len(user_input.split())
            if word_count < 10:
                st.warning("✏️ Try to expand your input so the AI can generate a meaningful response.")
        else:
            user_input = ""
    


# Handle Reformat & Repurpose subtasks
selected_task = st.session_state["selected_task"]
selected_subtask = st.session_state["selected_subtask"]


if selected_task == "Reformat & Repurpose Resource":
    st.markdown("#### Choose how to repurpose the content:")
    subtask_cols = st.columns(3)
    with subtask_cols[0]:
        if st.button("Convert to MCQ"):
            st.session_state["selected_subtask"] = "Convert to MCQ"
    with subtask_cols[1]:
        if st.button("Convert to Flashcards"):
            st.session_state["selected_subtask"] = "Convert to Flashcards"
    with subtask_cols[2]:
        if st.button("Group Discussion Task"):
            st.session_state["selected_subtask"] = "Group Discussion Task"

selected_subtask = st.session_state["selected_subtask"]
# Inputs for Plan & Print only
if selected_task == "Plan & Print":
    year_group = st.selectbox("Age Category", [
        "Early Years / KS1 (4–7)",
        "Lower KS2 (7–9)",
        "Upper KS2 (9–11)",
        "KS3 / Lower Secondary (11–14)",
        "KS4 / GCSE (14–16)",
        "Post-16 / A-Level (16–18)"
    ])
    duration = st.slider("Lesson Duration (minutes)", min_value=15, max_value=60, value=30)

# Inputs for Reformat & Repurpose subtasks only (no duration)
if selected_task == "Reformat & Repurpose Resource" and selected_subtask in [
    "Convert to MCQ", "Convert to Flashcards", "Group Discussion Task"
]:
    year_group = st.selectbox("Age Category", [
        "Early Years / KS1 (4–7)",
        "Lower KS2 (7–9)",
        "Upper KS2 (9–11)",
        "KS3 / Lower Secondary (11–14)",
        "KS4 / GCSE (14–16)",
        "Post-16 / A-Level (16–18)"
    ])

# MCQ item count (only for MCQ and Flashcards)
if selected_task == "Reformat & Repurpose Resource" and selected_subtask in ["Convert to MCQ", "Convert to Flashcards"]:
    num_mcq = st.slider("Number of Items to Generate", 1, 20, value=10)

if st.session_state.get("selected_task") == "Emotion Check-in Templates":
    num_templates = st.slider("Number of check-in templates to generate", 1, 10, value=3)
else:
    num_templates = 0  # fallback to avoid errors in other prompt templates

#--- Generation Button ---
st.markdown("""
    <div style="margin-top:2rem;margin-bottom:1rem;border-bottom:2px solid #ccc;"></div>
""", unsafe_allow_html=True)
st.markdown("### Now Generate the Output")
generate_col = st.container()
with generate_col:
    st.markdown("""
        <style>
        .generate-btn button {
            background-color: #2ecc71 !important;
            color: white !important;
            font-size: 1.1rem !important;
            font-weight: bold;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)
    generate_now = st.button("🚀 Generate Output", key="generate_btn", help="Send your content to the AI for generation")
    st.markdown('<div class="generate-btn"></div>', unsafe_allow_html=True)


if selected_task and generate_now:
    task_key = selected_subtask if selected_task == "Reformat & Repurpose Resource" else selected_task
    system_prompt = system_prompts[task_key] 

    user_input = f"User Input: {user_input}"

    user_prompt_template = user_prompts[task_key]
    user_prompt = user_prompt_template.format(
        year_group=year_group if 'year_group' in user_prompt_template else "",
        duration=duration if 'duration' in user_prompt_template else "",
        num_mcq=num_mcq if 'num_mcq' in user_prompt_template else "",
        num_flashcards=num_mcq if 'num_flashcards' in user_prompt_template else "",
        num_templates=num_templates if 'num_templates' in user_prompt_template else ""
    )

    if not user_input.strip():
        st.warning("⚠️ Please enter some content above.")
    else:
        with st.spinner(f"Generating output for: {selected_task}..."):
            response = requests.post(
                LLM_API_URL,
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt.strip()},
                        {"role": "user", "content": user_input.strip()},
                        {"role": "user", "content": user_prompt.strip()}
                    ]
                }
            )



            try:
                output = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                st.error(f"❌ Failed to parse API response: {e}")
                st.code(response.text)
                output = "[No output returned]"

        st.markdown(f"### AI Output")
        st.markdown(f"<div class='prompt-box'>{output}</div>", unsafe_allow_html=True)
        st.download_button("Copy/Download Output", data=output, file_name="output.txt")

        st.markdown(f"### Prompt Sent to AI")
        st.code(f"[System Prompt]\n{system_prompt}\n\n[User Input]\n{user_input.strip()}\n\n[User Prompt]\n{user_prompt}", language="markdown")

# --- Styling ---
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
