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
    "Differentiate Resource": "You are a specialist teaching assistant trained in curriculum adaptation. Your role is to adjust educational content to suit different learner levels.",
    "Plan & Print": "You are an experienced teacher and curriculum designer. Your role is to generate engaging, age-appropriate slide-based lesson plans.",
    "Generate Parent Message": "You are a compassionate and professional school teacher writing an email to parents.",
    "Convert to MCQ": "You are an expert exam question writer who designs age-appropriate high-quality multiple-choice questions for students.",
    "Convert to Flashcards": "You are an expert educational content designer who creates age-appropriate flashcards to support student learning.",
    "Group Discussion Task": "You are an expert classroom teacher who designs age-appropriate collaborative discussion tasks for students based on curriculum-aligned resources."
}


user_prompts = {
    "Differentiate Resource": """Your task is to differentiate the following content into three versions for different ability levels.

Use only the content provided between the tags here: 
[USER INPUT START] 
{user_input}
[USER INPUT END] 
as your source material.

If the input topic is very short (e.g. "Computers" or "Volcanoes"), do the following:
1. Interpret the topic logically within an educational curriculum.
2. Break it into curriculum-appropriate subtopics.
3. Clearly define your interpreted scope before rewriting.

Write 3 versions:
1. **Advanced Level** – Assume prior knowledge. Use precise terminology, explore nuance, and include real-world or critical-thinking prompts.
2. **Middle Level** – Use accessible language for middle-year learners. Explain key ideas with examples.
3. **Junior Level** – Use playful, simple language and concrete examples familiar to young children.

Each version must include:
- A clear heading
- A one-sentence description of the intent
- The adapted content

Return the three sections in this order:  
1. Advanced Level  
2. Middle Level  
3. Junior Level
""",
   "Plan & Print": """
Create a slide-based lesson plan based on the topic provided between the tags below.

- Year group: {year_group}
- Duration: {duration} minutes

Use only the topic between the tags here 
[USER INPUT START] 
{user_input}
[USER INPUT END] to build your slides. Do not make up unrelated content.

If the topic is very short (e.g. just one word), you must interpret the topic in a way that fits the curriculum for the specified year group.

Then:
1. Break it into logical subtopics.
2. Tailor tone, depth, and content to {year_group}.
3. Clearly define the lesson’s focus in the first slide.

Your lesson should include 6–10 slides that guide learners through a complete journey. Typical slides include:
- Lesson objectives
- Hook or starter
- Core explanation
- Guided or worked example
- Student task instructions
- Recap / Exit task
- Optional homework

Each slide should follow this format:
- Slide Title (specific to the content)
- Slide Content (5 bullet points or short paragraphs)
- [Optional: Teacher Notes]

Always start your reply with:
Slide 1
""",
    "Generate Parent Message": """
Your task is to write a short, supportive message from the teacher to the student’s parent or guardian.

Context about the praise or concern is provided between the tags here: 
[USER INPUT START] 
{user_input}
[USER INPUT END].

Guidelines:
- The message should be in first person (from the teacher’s perspective).
- Address the parent as “Dear Parent/Guardian” unless a name is explicitly provided.
- Do not repeat the input text verbatim.
- Do not suggest a meeting unless the input specifically asks for one.
- Keep the tone respectful, encouraging, and professional.
- Keep the message concise (under 100 words).

Tone examples:
- Praise → Highlight achievement, thank the parent, suggest continued support at home.
- Concern → Describe behaviour factually, invite the parent’s perspective, suggest next steps only if appropriate.

Follow this message structure:
1. Greeting
2. Main praise or concern
3. Encouragement or next steps

Start your output: 
Dear Parent/Guardian,
""",

    "Convert to MCQ": """
Create {num_mcq} multiple-choice questions for the target audience: {year_group} students, based only on the educational content between the tags here: 
[USER INPUT START]  
{user_input}
[USER INPUT END].

If the user input is very short (e.g. just one word), you must interpret the topic in a way that fits the curriculum for the specified year group.

Instructions:
- Ensure each question tests understanding of the input content.
- Include a mix of easy, medium, and hard difficulty levels.
- Avoid ambiguous phrasing or trick questions.

Each question should follow this format:
Q: [Question]
A. Option 1  
B. Option 2  
C. Option 3  
D. Option 4  
Answer: [Correct Option Letter]

""",

"Convert to Flashcards": """
Create exactly {num_flashcards} flashcards appropriate for the target audience: {year_group} students based only on the educational content provided between the tags here:
[USER INPUT START] 
{user_input}
[USER INPUT END].

If the user input is very short (e.g. just one word), you must interpret the topic in a way that fits the curriculum for the specified year group.

Instructions:
1. Identify key facts, terms, definitions, or concepts relevant to {year_group}.
2. For each, write a clear and focused question to prompt understanding.
3. Provide a concise and accurate answer (1–2 sentences max).
4. Optionally include 1–2 cloze-style questions (fill-in-the-blank), but no more than 20%.

If the educational content provided between the tags [USER INPUT START] and [USER INPUT END] is very short (e.g., just a word like “Volcanoes” or “Photosynthesis”):
- Define the topic scope based on typical curriculum expectations for {year_group}.
- Break it into logical subtopics before generating flashcards.

Use this format for every flashcard:
**Q:** [Question]  
**A:** [Answer]

Return {num_flashcards} flashcards formatted exactly as above.

""",
    "Group Discussion Task": """
Design a classroom group discussion task appropriate for the audience: {year_group} students, using only the material provided between the tags here:
[USER INPUT START]
{user_input}
[USER INPUT END].
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

cols = st.columns(4)
for i, label in enumerate(task_labels):
    with cols[i]:
        button_class = "task-button-selected" if st.session_state["selected_task"] == label else "task-button"
        if st.button(f"{label}", key=label, help=task_descriptions[label]):
            st.session_state["selected_task"] = label
            st.session_state["selected_subtask"] = None

# Forcefully update the style of the selected button using JavaScript
if st.session_state["selected_task"]:
    st.markdown(f"""
    <script>
    const buttons = window.parent.document.querySelectorAll('button[kind="secondary"]');
    buttons.forEach(btn => {{
        if (btn.innerText === "{st.session_state['selected_task']}") {{
            btn.classList.add("selected");
        }}
    }});
    </script>
    """, unsafe_allow_html=True)

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

    user_prompt_template = user_prompts[task_key]
    user_prompt = user_prompt_template.format(
        user_input=user_input.strip(),
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
        st.code(f"[System Prompt]\n{system_prompt}\n\n[User Prompt]\n{user_prompt}", language="markdown")

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

