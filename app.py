import streamlit as st
import requests

LLM_API_URL = st.secrets["LLM_API_URL"]

# --- Page Config ---
st.set_page_config(page_title="Prompt Tester", layout="centered")
st.title("OI-TA")
st.markdown("""
<div style="padding:0.5rem 1rem; background-color:#ecf0f1; border-left:5px solid #3498db; font-size:1rem; color:#2c3e50;">
    Empowering every teacher, AI-Powered Support for Educators.
</div>
""", unsafe_allow_html=True)
st.markdown("""
    <div style="margin-top:2rem;margin-bottom:1rem;border-bottom:2px solid #ccc;"></div>
""", unsafe_allow_html=True)
# --- Initialize state for task highlight ---
if "selected_task" not in st.session_state:
    st.session_state["selected_task"] = None

if "selected_subtask" not in st.session_state:
    st.session_state["selected_subtask"] = None

# --- User Input ---
st.subheader("Paste Your Content")
user_input = st.text_area("Add here your Lesson content, Parent update, or any material you wish to convert:", height=250)

# Track the warning state and input word count
word_count = len(user_input.strip().split())
warning_placeholder = st.empty()

# Only show warning if input is too short
if word_count < 10:
    warning_placeholder.warning("✏️ Please expand your input with more context so the AI can generate a meaningful response.")
else:
    warning_placeholder.empty()  # Clears the warning once the condition is met

# --- Task Selection Buttons ---
st.markdown("""
    <div style="margin-top:2rem;margin-bottom:1rem;border-bottom:2px solid #ccc;"></div>
""", unsafe_allow_html=True)
st.subheader("Choose a Task")

task_labels = [
    "Differentiate Resource",
    "Generate Parent Message",
    "Plan & Print",
    "Reformat & Repurpose Resource"
]

system_prompts = {
    "Differentiate Resource": """You are a specialist teaching assistant trained in curriculum adaptation. Your task is to differentiate the piece of educational content shared below under [USER INPUT] into three clearly labeled versions for different learner levels. 

If the user topic is very short (e.g. a single word like "Computers" or "Volcanoes"), you must:
1. Interpret the topic in a way that makes sense for educational purposes / curriculums,
2. Break it into logical, curriculum-appropriate subtopics,
3. Clearly define the scope of the user topic to yourself.

Otherwise, identify the core learning idea shared between the tags [USER INPUT START] and [USER INPUT END]. 

Then rewrite the content into three sections:

1. **Junior Level** – Use simple words, short playful sentences, and concrete metaphors familiar to young children. Make it friendly and engaging.

2. **Middle Level** – Use vocabulary and sentence structures suitable for middle school students. Include relevant examples and maintain educational depth while staying accessible.

3. **Advanced Level** – Assume prior knowledge. Use precise terminology, explore nuance, and add critical thinking prompts or real-world connections.

Each version should follow this structure:
- A heading (e.g., “Junior Level”)
- A one-sentence description of the version’s intent
- The rewritten version of the content

Use only the content provided between the tags [USER INPUT START] and [USER INPUT END] as your base material. Do not fabricate unrelated facts.
""",
   "Plan & Print": """You are an experienced teacher and curriculum designer.

Your task is to create a slide-based lesson plan using only the topic provided between the tags [USER INPUT START] and [USER INPUT END].

Use the provided age group and lesson duration below to guide the tone, depth, and length of the plan:
- Year group = {year_group}
- Duration = {duration} minutes

If the user topic is very short (e.g. a single word like "Computers" or "Volcanoes"), you must:
1. Interpret the topic in a way that makes sense for the age group,
2. Break it into logical, curriculum-appropriate subtopics,
3. Clearly define the scope of the lesson in Slide 1.

Include 6–10 slides covering:
1. Lesson Objectives  
2. Hook or Starter Activity  
3. Core Concept Explanation  
4. Guided Practice or Worked Example  
5. Student Activity Instructions  
6. Recap / Exit Task  
7. Optional Homework  

Include at least one interactive task (e.g. a pair discussion, mini-quiz, or real-world challenge).

Use clear, age-appropriate language. Tailor tone and depth of content to the year group specified.
Do not fabricate unrelated facts. Expand on the user topic only using general knowledge appropriate to the subject and level/year group.
Your output should read like the written content of a PowerPoint or Google Slides presentation.

Use this structure for each slide:
- Slide Title
- Slide Content (5 bullet points or short paragraphs)
- [Optional: Teacher Notes or Activity Instructions]

Return only the slide content as structured text.
"""
,
    "Generate Parent Message": """You are a compassionate and professional school teacher, skilled in communications. 
Given the student's situation defined between the tags [USER INPUT START] and [USER INPUT END], your task is to write a short message using the tone and context provided. 

Follow this structure:
1. Greeting
2. Main concern or praise
3. Optional context
4. Positive reinforcement and next step

Think step-by-step about how to reassure, inform, and motivate the parent. If tone is unclear, default to a supportive, respectful style.

Examples:
• Praise → Highlight achievement, thank parents, suggest continuation.
• Concern → Describe behaviour neutrally, offer solution, invite collaboration.

Finally check your message against these constraints:
1. Ensure the message is always addressed to the parent / guardian.
2. Only include a meeting or follow-up appointment if the user input explicitly requests it. If it’s not mentioned, do not include any reference to meetings or scheduling.
3. Use only the content provided between the tags [USER INPUT START] and [USER INPUT END] as your base material. Do not fabricate unrelated facts.
4. Keep the message short and professional (under 100 words) <max_output> = 100 tokens.

Return only the final message.
""",
    "Convert to MCQ": """You are an expert exam question writer designing multiple-choice questions. Based on the resource provided between the tags [USER INPUT START] and [USER INPUT END], create {num_mcq} MCQs to assess comprehension.

Each MCQ should follow this format:
Q: [Question]
A. Option 1  
B. Option 2  
C. Option 3  
D. Option 4  
Answer: [Correct Option Letter]

Use a mix of easy, medium, and hard questions to cover different cognitive levels, and lable the question with this level. Avoid ambiguous phrasing and ensure only one correct answer.

Example:
(EASY)
Q: What is the boiling point of water?  
A. 90°C  
B. 100°C  
C. 110°C  
D. 120°C  
Answer: B

Return only the MCQs.
""",
 "Convert to Flashcards": """You are an educational content designer creating flashcards to reinforce learning from the material between the tags [USER INPUT START] and [USER INPUT END]. 
 First break the resource into essential knowledge chunks and convert them into Q&A pairs.

Follow this step-by-step approach:
1. Identify key facts, terms, or concepts that should be retained.
2. For each, write a question that prompts recall or understanding.
3. Provide a concise and accurate answer.
4. Optionally use cloze-style (fill-in-the-blank) for variety.

Apply this structure:
**Q:** [Clear, focused question]  
**A:** [Direct answer]

Constraints:
- Use only information provided by the user. Do not invent content.
- Keep language age-appropriate but precise.
- Limit each answer to 1–2 sentences max.

Example flashcard:
Q: What is photosynthesis?  
A: It's the process by which green plants make food using sunlight.

Return {num_flashcards} flashcards. Clearly label each pair (Q/A).
""",

    "Group Discussion Task": """You are an expert teacher designing a collaborative classroom discussion task based on the resource provided between the tags [USER INPUT START] and [USER INPUT END]. 
    The goal is to spark thoughtful student dialogue and peer learning.

Step-by-step reasoning:
1. Extract the key concept or debate point from the material.
2. Pose one or more open-ended discussion questions.
3. Suggest clear roles or responsibilities for group members (e.g. facilitator, recorder, timekeeper).
4. Provide instructions that encourage active participation and critical thinking.

Use this format:
**Task Title:**  
**Overview:** [1–2 sentence explanation of the goal]  
**Group Roles:** [3–4 roles with simple descriptions]  
**Discussion Questions:** [1–3 questions]  
**Instructions:**  
- Step-by-step guidance on how to run the discussion  
- Include time guidance (e.g. “5 mins discussion, 3 mins summary”)  
- Encourage inclusive participation

Constraints:
- Use only the provided material
- Make the activity achievable in 15–20 minutes
- Avoid abstract questions unless clearly scaffolded

Return the full activity as structured text.
"""
}

task_descriptions = {
    "Differentiate Resource": "Adapt learning materials into 3 versions for junior, middle, and advanced learners.",
    "Generate Parent Message": "Draft a short, professional message to communicate with parents.",
    "Plan & Print": "Create a detailed, slide-style lesson plan tailored to age and duration.",
    "Reformat & Repurpose Resource": "Convert a resource into MCQs, flashcards, or a group task."
}

# Create button layout and track which was clicked
cols = st.columns(4)
for i, label in enumerate(task_labels):
    with cols[i % 4]:
        btn_style = f"background-color: #3498db; color: white;" if st.session_state["selected_task"] == label else ""
        if st.button(label, key=label, help=task_descriptions[label]):
            st.session_state["selected_task"] = label
            st.session_state["selected_subtask"] = None 

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
    duration = st.slider("Lesson Duration (minutes)", min_value=20, max_value=120, value=45)

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


# --- Perform Prompt if Task Selected ---
if selected_task and generate_now:
    task_key = selected_subtask if selected_task == "Reformat & Repurpose Resource" else selected_task
    system_prompt = system_prompts[task_key]

    if task_key == "Plan & Print":
        system_prompt = system_prompt.format(
            year_group=year_group if year_group else "Year 6",
            duration=duration if duration else 45
        )
    elif task_key == "Convert to MCQ":
        system_prompt = system_prompt.replace("{num_mcq}", str(num_mcq if num_mcq else 5))

    elif task_key == "Convert to Flashcards":
        system_prompt = system_prompt.replace("{num_flashcards}", str(num_mcq if num_mcq else 10))

    if not user_input.strip():
        st.warning("⚠️ Please enter some content above.")
    else:
        with st.spinner(f"Generating output for: {selected_task}..."):
            response = requests.post(
                LLM_API_URL,
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"[USER INPUT START]\n{user_input.strip()}\n[USER INPUT END]"}
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
        st.code(f"[System Prompt]\n{system_prompt}\n\n[USER INPUT START]\n{user_input.strip()}\n[USER INPUT END]", language="markdown")

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

