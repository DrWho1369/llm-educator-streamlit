import streamlit as st
import requests
import PyPDF2
from pdf_summariser import summarize_uploaded_pdf

LLM_API_URL = st.secrets["LLM_API_URL"]

# --- Page Config ---
st.set_page_config(page_title="Prompt Tester", layout="centered")

st.title("OI-TA")

# Define task labels and descriptions
task_labels = [
    "Differentiate Resource",
    "Generate Parent Message",
    "Plan & Print",
    "Reformat & Repurpose Resource"
]

task_descriptions = {
    "Differentiate Resource": "Tailor a teaching resource into 3 ability levels",
    "Generate Parent Message": "Create a message to update parents",
    "Plan & Print": "Generate lesson plan + printable resources",
    "Reformat & Repurpose Resource": "Convert into flashcards, MCQs, etc."
}

st.subheader("Choose a task:")
cols = st.columns(4)
for i, label in enumerate(task_labels):
    with cols[i]:
        button_class = "task-button-selected" if st.session_state.get("selected_task") == label else "task-button"
        if st.button(f"{label}", key=label, help=task_descriptions[label]):
            st.session_state["selected_task"] = label
            st.session_state["selected_subtask"] = None

# Display buttons in columns

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


# --- Initialize state for task highlight ---
if "selected_task" not in st.session_state:
    st.session_state["selected_task"] = None

if "selected_subtask" not in st.session_state:
    st.session_state["selected_subtask"] = None



# Show nothing else if no task is selected yet
if not st.session_state["selected_task"]:
    st.stop()


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

# Show content input only if a task is selected

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
        user_input = st.text_area("Enter your input text here:", height=300)

    # From here on, use `user_input` for word counts, validation, and final API call
    word_count = len(user_input.split())
    if word_count < 10:
        st.warning("✏️ Try to expand your input so the AI can generate a meaningful response.")

# --- Task Selection Buttons ---
st.markdown("""
    <div style="margin-top:2rem;margin-bottom:1rem;border-bottom:2px solid #ccc;"></div>
""", unsafe_allow_html=True)
st.subheader("Choose a Task")


system_prompts = {
    "Differentiate Resource": "You are a specialist teaching assistant trained in adaptive instruction. Your job is to rewrite classroom materials in three distinct formats: simplified, scaffolded, and challenge versions. You always follow the teacher’s original intent and never add unrelated content.",
    "Plan & Print": "You are an expert curriculum designer who creates age-appropriate lesson materials. Your task is to help teachers prepare for a topic by generating a topic guide, a structured lesson plan, and a slide-based presentation.",
    "Generate Parent Message": "You are a compassionate and professional school teacher writing a message to parents or guardians. Maintain a respectful, human tone that suits the nature of the user input message (positive or negative).",
    "Convert to MCQ": "You are an expert exam question writer who designs age-appropriate high-quality multiple-choice questions for students. You will always create num_mcq questions",
    "Convert to Flashcards": "You are an expert educational content designer who creates age-appropriate flashcards to support student learning.",
    "Group Discussion Task": "You are an expert classroom teacher who designs age-appropriate collaborative discussion tasks for students based on curriculum-aligned resources."
}


user_prompts = {
"Differentiate Resource": """Your task is to transform the previous teaching content input message into **three differentiated versions**, each tailored to a different student need:

1. **Simplified Version**  
   - Use **simpler vocabulary**, shorter sentences, and direct language.  
   - Aim for a **lower reading age**.  
   - Remove complex or abstract phrasing.  

2. **Scaffolded Version**  
   - Keep the original vocabulary, but **add sentence starters**, **guiding questions**, and a **vocabulary box**.  
   - The goal is to support students who benefit from extra structure.

3. **Challenge Version**  
   - Expand on the original ideas to encourage **critical thinking** or **real-world application**.  
   - Include **stretch questions**, comparisons, or deeper analysis.  
   - Use more **sophisticated vocabulary** and academic tone.

---

**Important Guidelines:**
- Use only the content provided in the input — **do not add unrelated facts**.
- If the input is vague or very short, infer a suitable topic and scope (e.g., “Volcanoes” → types, causes, effects).
- Format each version using this structure:

### [Version Name]

**Intent:** One sentence summary of how this version supports learners.

**Teacher Summary:**
- Bullet points describing how and why the version was adapted.
- Highlight key features, vocabulary, or focus.

**Student-Facing Version:**
[Rewritten content suitable for students.]

---

Return the versions in this exact order:   
1. Challenge Version
2. Scaffolded Version 
3. Simplified Version  
"""
,
   "Plan & Print": """You are helping a teacher prepare a full lesson plan and slides based on a single topic. Use the information in the user inpput message to design the lesson plan and student slides.

Topic: see user input message before

Year Group: {year_group}  
Duration: {duration} minutes

Follow these steps to create your output:
1. **Define the Lesson Scope:** If the topic is broad or vague, interpret it appropriately for the age group and specify your focus in Slide 1.
2. **Create a Teacher Guide:** Start your output with a brief topic overview and 4–6 key terms or learning objectives.
3. **Write a Lesson Plan Outline:** Include a short paragraph for the teacher explaining how the lesson will flow.
4. **Generate Slides:** Create 6–10 slides following this structure:
   - Slide Title (specific and relevant to the topic)
   - Slide Content (5 bullet points or short paragraphs)
   - [Optional: Teacher Notes or Activity Instructions]

Typical slides might include:
- Lesson Objectives  
- Hook or Starter  
- Core Explanation  
- Guided Example or Modelled Task  
- Student Activity Instructions  
- Recap or Exit Task  
- Optional Homework

Use age-appropriate, accurate language. Do **not** fabricate facts or examples. Focus only on the provided topic.

Always contain in your output:
A. The lesson scope
B. Teacher Guide
C. Lesson Plan Outline
D. Full complete slide deck for lesson
""",
   "Generate Parent Message": """
Your task is to write an email to the student’s parent or guardian based entirely on your personal notes written above in the "user input" message.

Guidelines:
- First person (“I” or “We”), from the teacher’s perspective.
- Do not invent or infer any information not in the input message.
- Use a respectful and appropriate tone:
    • If input message = Praise → warm and thankful.
    • If input message = Concern → factual, supportive and collaborative, without sugarcoating.

---
**Email Structure:**
1. Greeting — Start with “Dear Parent/Guardian”
2. Main message — Focused on describing the context in the user input message over 2 paragraphs
3. Always conclude with positive reinforcement / encouraging actions that the parent can do at home
---

- Keep the email under 100 words.
- Return only the final email.
""",

    "Convert to MCQ": """
Create num_mcq = {num_mcq} multiple-choice questions for the target audience: {year_group} students, based only on the educational content shared in the user input message before.

If the user input is very short (e.g. just one word), you must interpret the topic in a way that fits the curriculum for the specified target audience: {year_group} students.

Instructions:
- Create {num_mcq} multiple choice questions.
- Ensure each question tests understanding of the input content.
- Include a mix of easy, medium, and hard difficulty levels.
- Avoid ambiguous phrasing or trick questions.

--------
**Question format:**
Question Number
Q: [Question]
A. Option 1  
B. Option 2  
C. Option 3  
D. Option 4  
Answer: [Correct Option Letter]
-------

Return {num_mcq} Multiple Choice Questions
""",

"Convert to Flashcards": """
Create exactly {num_flashcards} flashcards appropriate for the target audience: {year_group} students based only on the educational content provided in the user input message before.

If the user input is very short (e.g. just one word), you must interpret the topic in a way that fits the curriculum for the specified year group.

Instructions:
1. Identify key facts, terms, definitions, or concepts relevant to {year_group}.
2. For each, write a clear and focused question to prompt understanding.
3. Provide a concise and accurate answer (1–2 sentences max).

-------
**Use this format for everyone of the {num_flashcards} flashcards:**
Flashcard Number
Q: Question  
A: Full Answer
-------

Remember to create {num_flashcards} flashcards formatted exactly as above.
""",
    "Group Discussion Task": """
Design a classroom group discussion task appropriate for the audience: {year_group} students, using only the material provided in the user input message before

If the user input is very short (e.g. just one word), you must interpret the topic in a way that fits the curriculum for the specified year group.

Goal: Spark thoughtful peer dialogue and cooperative learning. The activity should be achievable in 15–20 minutes.

Instructions:
1. Identify a key idea, theme, or concept from the material.
2. Pose 1–3 open-ended discussion questions.
3. Define group roles (e.g. facilitator, recorder, timekeeper).
4. Write step-by-step instructions that promote active participation and critical thinking.

Format your output using this structure:
**Task Title:**  
**Overview:** [1–2 sentence summary of the purpose and age-appropriateness]  
**Group Roles:** [3–4 clearly described roles]  
**Discussion Questions:** [1–3 open-ended questions]  
**Instructions:**  
- [Clear, sequenced steps]
- Include time guidance (e.g. “5 min discussion, 3 min summary”)
- Encourage inclusive discussion

Constraints:
- Ensure task and tone match the developmental level of {year_group}
- Avoid overly abstract or unsupported questions
- Do not fabricate facts not found in the provided material

Return only the full activity as structured text.
"""
}

task_descriptions = {
    "Differentiate Resource": "Adapt learning materials into 3 versions for junior, middle, and advanced learners.",
    "Generate Parent Message": "Draft a short, professional message to communicate with parents.",
    "Plan & Print": "Create a detailed, slide-style lesson plan tailored to age and duration.",
    "Reformat & Repurpose Resource": "Convert a resource into MCQs, flashcards, or a group task."
}


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
