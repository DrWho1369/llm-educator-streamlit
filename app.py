import streamlit as st
import requests
from db import setup_db, save_prompt_to_db, seed_original_prompts, SessionLocal, PromptEntry, seed_prompt_variants, seed_lesson_plan_variants, seed_parent_comms_variants, seed_mcq_variants, seed_flashcard_variants, seed_group_task_variants
import urllib.parse
import pandas as pd
from io import StringIO


# ----------- INITIAL SETUP ------------
setup_db()
seed_original_prompts()
seed_prompt_variants()
seed_lesson_plan_variants()
seed_parent_comms_variants()
seed_mcq_variants()
seed_flashcard_variants()
seed_group_task_variants()

# ----------- PAGE CONFIG ------------
st.set_page_config(page_title="Differentiate Resource", layout="centered")

query_params = st.query_params
preloaded_task_name = query_params.get("task_name", [None])[0]
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
        color: #2c3e50;
    }
    .stMultiSelect>div>div>div {
        background-color: #ecf0f1;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)


# ----------- MAIN TASK SELECTOR ------------
task = st.selectbox("Choose a Teaching Task", [
    "Differentiate This",
    "Generate Lesson Plan + Resources",
    "Parent Comms Assistant",
    "Convert to MCQ",
    "Convert to Flashcards",
    "Convert to Group Task"
])





# ----------- STATIC TEMPLATE FALLBACKS ------------
prompt_templates = {
    "Simplified": "You are a teacher simplifying lesson content for a student with a reading age of 9 years. Rewrite the following resource using simpler vocabulary, shorter sentences, and clear structure while preserving meaning and core knowledge.\n\n{}",
    "Challenge Extension": "You are a gifted and talented coordinator. Extend the following task to provide a greater challenge for high-attaining students. Add one open-ended question, and one creative application or real-world connection.\n\n{}",
    "EAL Support": "You are an EAL support specialist. Modify the following resource to include sentence starters and a glossary of key terms with definitions in simple English.\n\n{}",
    "SEND Support": "You are a SEND teacher. Adapt this activity for students with moderate learning difficulties. Break the task into small, guided steps and use supportive language.\n\n{}",
    "Dyslexia-Friendly": "You are supporting students with dyslexia. Rewrite the following resource using short sentences and high-frequency words. Present content in readable chunks.\n\n{}",
    "Tiered": "You are creating a tiered version of this resource for a mixed-ability classroom. Provide:\n1. A simplified version\n2. A standard version\n3. A challenge version\n\n{}",
    "Sentence Starters": "You are helping students develop structured responses. Rewrite this worksheet to include sentence starters or writing frames for each question.\n\n{}",
}

# ----------- UI: MAIN FORM ------------
if task == "Differentiate This":
    st.markdown("<div class='title-text'>Differentiate Resource</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle-text'>Paste your lesson content below and choose your differentiation type and prompting strategy.</div>", unsafe_allow_html=True)

    subject_text = st.text_area(
        "Lesson Content / Worksheet",
        height=250,
        placeholder="Paste your worksheet, question, or task content here...",
        value=preloaded_prompt if preloaded_prompt else ""
    )

    task_name = st.selectbox("What do your students need help with?", list(prompt_templates.keys()))

    st.markdown("""
    **How should the Prompt be adapted to the content?**  
    Each strategy uses a different approach to tailoring the prompt — e.g., role-based, few-shot, scaffolded.
    """)

    session = SessionLocal()
    variant_prompts = session.query(PromptEntry).filter(
        PromptEntry.task_name == task_name,
        PromptEntry.edited == False,
        PromptEntry.feedback_comment.like("Technique:%")
    ).all()
    session.close()

    if variant_prompts:
        technique_options = [p.feedback_comment.replace("Technique: ", "") for p in variant_prompts]
        selected_technique = st.selectbox("Choose Prompting Strategy:", technique_options)
        base_prompt_text = next(
            (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
            prompt_templates[task_name]
        )
    else:
        selected_technique = "Default Template"
        base_prompt_text = prompt_templates[task_name]

    raw_prompt = base_prompt_text.replace("[PASTE WORKSHEET HERE]", subject_text)
    final_prompt = st.text_area("\U0001F50D Preview & Edit Prompt to be Sent to the AI", value=raw_prompt, height=250)

    if st.button("\u2728 Generate Differentiated Version"):
        if not subject_text.strip():
            st.warning("Please enter some lesson content.")
        else:
            with st.spinner(f"Generating {task_name} using {selected_technique} strategy..."):
                save_prompt_to_db(task_name=task_name, prompt_text=final_prompt, edited=True)

                response = requests.post(
                    "http://18.171.171.212:8080/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a helpful teaching assistant."},
                            {"role": "user", "content": final_prompt}
                        ]
                    }
                )
                st.write("Raw response:", response.text)

                try:
                    generated_text = response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Could not parse API response: {e}")
                    st.code(response.text)
                    generated_text = "[No output returned]"


                st.markdown(f"### {task_name} – Strategy: {selected_technique}")
                st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

                st.markdown("#### \U0001F4AC Rate this output")
                rating = st.slider("How helpful was this version?", 1, 5, key=f"rating_{task_name}")
                feedback = st.text_area("Any comments or suggestions?", key=f"feedback_{task_name}")

                if st.button(f"\U0001F4BE Save Feedback for {task_name}"):
                    save_prompt_to_db(
                        task_name=task_name,
                        prompt_text=final_prompt,
                        edited=True,
                        rating=rating,
                        feedback_comment=feedback
                    )
                    st.success("\u2705 Feedback saved!")

    def download_prompt_csv():
        session = SessionLocal()
        prompts = session.query(PromptEntry).all()
        session.close()

        df = pd.DataFrame([{
            "Task": p.task_name,
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
        label="\u2B07\uFE0F Download All Prompts as CSV",
        data=csv_data,
        file_name='differentiated_prompts.csv',
        mime='text/csv'
    )


elif task == "Generate Lesson Plan + Resources":
    st.markdown("###Generate a Lesson Plan + Supporting Materials")

    topic = st.text_input("🧠 Topic", placeholder="e.g. Photosynthesis")
    year_group = st.selectbox("📘 Year Group", [f"Year {i}" for i in range(1, 14)])
    duration = st.slider("⏱️ Lesson Duration (minutes)", min_value=20, max_value=120, value=50, step=5)
    lesson_text = st.text_area("📄 Paste Supporting Textbook/Chapter Content (optional)", height=200)

    # -- Fetch prompt variants for this task --
    session = SessionLocal()
    variant_prompts = session.query(PromptEntry).filter(
        PromptEntry.task_name == "Generate Lesson Plan + Resources",
        PromptEntry.edited == False,
        PromptEntry.feedback_comment.like("Technique:%")
    ).all()
    session.close()

    if variant_prompts:
        technique_options = [p.feedback_comment.replace("Technique: ", "") for p in variant_prompts]
        selected_technique = st.selectbox("🧠 Choose Prompting Strategy", technique_options)
        base_prompt_text = next(
            (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
            "You are a teacher generating a full lesson plan..."
        )
    else:
        selected_technique = "Default Template"
        base_prompt_text = "You are a teacher generating a full lesson plan..."

    # Format the prompt dynamically
    prompt_filled = base_prompt_text.replace("{topic}", topic)\
                                    .replace("{year_group}", year_group)\
                                    .replace("{duration}", str(duration))\
                                    .replace("{chapter_text}", lesson_text or "[No content provided]")

    final_prompt = st.text_area("🔍 Preview & Edit Prompt to be Sent to the AI", value=prompt_filled, height=250)

    if st.button("✨ Generate Lesson Plan"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating lesson plan..."):
                save_prompt_to_db(
                    task_name="Generate Lesson Plan + Resources",
                    prompt_text=final_prompt,
                    edited=True
                )

                response = requests.post(
                    "http://18.171.171.212:8080/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a helpful teaching assistant."},
                            {"role": "user", "content": final_prompt}
                        ]
                    }
                )
                try:
                    generated_text = response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Could not parse API response: {e}")
                    st.code(response.text)
                    generated_text = "[No output returned]"


                st.markdown("### 📋 Lesson Plan Output")
                st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

                st.markdown("#### 💬 Rate this output")
                rating = st.slider("How helpful was this lesson plan?", 1, 5, key="rating_lesson")
                feedback = st.text_area("Any comments or suggestions?", key="feedback_lesson")

                if st.button("💾 Save Feedback for Lesson Plan"):
                    save_prompt_to_db(
                        task_name="Generate Lesson Plan + Resources",
                        prompt_text=final_prompt,
                        edited=True,
                        rating=rating,
                        feedback_comment=feedback
                    )
                    st.success("✅ Feedback saved!")

elif task == "Parent Comms Assistant":
    st.markdown("###Generate a Parent Communication Message")

    concern = st.selectbox("📌 What’s the communication about?", ["Praise", "Missed Homework", "Behaviour Issue", "General Update"])
    tone = st.selectbox("🎙️ Preferred Tone", ["Supportive", "Neutral", "Firm but Constructive"])
    extra_note = st.text_area("📝 Optional Extra Info", placeholder="e.g. Jamie missed the last two homework deadlines.")

    # --- Load prompt strategies for this task ---
    session = SessionLocal()
    variant_prompts = session.query(PromptEntry).filter(
        PromptEntry.task_name == "Parent Comms Assistant",
        PromptEntry.edited == False,
        PromptEntry.feedback_comment.like("Technique:%")
    ).all()
    session.close()

    if variant_prompts:
        technique_options = [p.feedback_comment.replace("Technique: ", "") for p in variant_prompts]
        selected_technique = st.selectbox("🧠 Choose Prompting Strategy", technique_options)
        base_prompt_text = next(
            (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
            "You are a teacher writing a message to a parent..."
        )
    else:
        selected_technique = "Default Template"
        base_prompt_text = "You are a teacher writing a message to a parent..."

    # Format the prompt
    prompt_filled = base_prompt_text.replace("{concern}", concern)\
                                    .replace("{tone}", tone)\
                                    .replace("{note}", extra_note or "[No extra context provided]")

    final_prompt = st.text_area("🔍 Preview & Edit Prompt to be Sent to the AI", value=prompt_filled, height=250)

    if st.button("✨ Generate Message"):
        with st.spinner("Creating message..."):
            save_prompt_to_db(
                task_name="Parent Comms Assistant",
                prompt_text=final_prompt,
                edited=True
            )
            response = requests.post(
                "http://18.171.171.212:8080/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "You are a helpful teaching assistant."},
                        {"role": "user", "content": final_prompt}
                    ]
                }
            )
            try:
                generated_text = response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                st.error(f"❌ Could not parse API response: {e}")
                st.code(response.text)
                generated_text = "[No output returned]"


            st.markdown("### ✉️ Suggested Message to Parent")
            st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

            st.markdown("#### 💬 Rate this output")
            rating = st.slider("How helpful was this message?", 1, 5, key="rating_parent")
            feedback = st.text_area("Any comments or suggestions?", key="feedback_parent")

            if st.button("💾 Save Feedback for Parent Message"):
                save_prompt_to_db(
                    task_name="Parent Comms Assistant",
                    prompt_text=final_prompt,
                    edited=True,
                    rating=rating,
                    feedback_comment=feedback
                )
                st.success("✅ Feedback saved!")

elif task == "Convert to MCQ":
    st.markdown("###Convert Resource into Multiple-Choice Questions")

    mcq_text = st.text_area("📄 Paste Your Resource", height=250, placeholder="e.g. a passage, worksheet, or topic summary")

    num_questions = st.slider("🔢 Number of MCQs to Generate", 1, 10, 5)

    # --- Load MCQ prompt variants from DB ---
    session = SessionLocal()
    variant_prompts = session.query(PromptEntry).filter(
        PromptEntry.task_name == "Convert to MCQ",
        PromptEntry.edited == False,
        PromptEntry.feedback_comment.like("Technique:%")
    ).all()
    session.close()

    if variant_prompts:
        technique_options = [p.feedback_comment.replace("Technique: ", "") for p in variant_prompts]
        selected_technique = st.selectbox("🧠 Choose Prompting Strategy", technique_options)
        base_prompt_text = next(
            (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
            "Convert the following content into multiple-choice questions."
        )
    else:
        selected_technique = "Default Template"
        base_prompt_text = "Convert the following content into multiple-choice questions."

    # Replace placeholders
    prompt_filled = base_prompt_text.replace("{text}", mcq_text)\
                                    .replace("{num}", str(num_questions))

    final_prompt = st.text_area("🔍 Preview & Edit Prompt to be Sent to the AI", value=prompt_filled, height=250)

    if st.button("✨ Generate MCQs"):
        if not mcq_text.strip():
            st.warning("Please paste a resource.")
        else:
            with st.spinner("Generating MCQs..."):
                save_prompt_to_db(
                    task_name="Convert to MCQ",
                    prompt_text=final_prompt,
                    edited=True
                )

                response = requests.post(
                    "http://18.171.171.212:8080/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a helpful teaching assistant."},
                            {"role": "user", "content": final_prompt}
                        ]
                    }
                )
                try:
                    generated_text = response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Could not parse API response: {e}")
                    st.code(response.text)
                    generated_text = "[No output returned]"


                st.markdown("### 🧪 Generated MCQs")
                st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

                st.markdown("#### 💬 Rate this output")
                rating = st.slider("How helpful were the MCQs?", 1, 5, key="rating_mcq")
                feedback = st.text_area("Any comments or suggestions?", key="feedback_mcq")

                if st.button("💾 Save Feedback for MCQs"):
                    save_prompt_to_db(
                        task_name="Convert to MCQ",
                        prompt_text=final_prompt,
                        edited=True,
                        rating=rating,
                        feedback_comment=feedback
                    )
                    st.success("✅ Feedback saved!")

elif task == "Convert to Flashcards":
    st.markdown("###Convert Resource into Flashcards")

    flashcard_text = st.text_area("📄 Paste Your Resource", height=250, placeholder="e.g. topic summary, glossary, article")

    # --- Load prompt strategies for flashcard task ---
    session = SessionLocal()
    variant_prompts = session.query(PromptEntry).filter(
        PromptEntry.task_name == "Convert to Flashcards",
        PromptEntry.edited == False,
        PromptEntry.feedback_comment.like("Technique:%")
    ).all()
    session.close()

    if variant_prompts:
        technique_options = [p.feedback_comment.replace("Technique: ", "") for p in variant_prompts]
        selected_technique = st.selectbox("🧠 Choose Prompting Strategy", technique_options)
        base_prompt_text = next(
            (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
            "Convert the following content into flashcards."
        )
    else:
        selected_technique = "Default Template"
        base_prompt_text = "Convert the following content into flashcards."

    prompt_filled = base_prompt_text.replace("{text}", flashcard_text)
    final_prompt = st.text_area("🔍 Preview & Edit Prompt to be Sent to the AI", value=prompt_filled, height=250)

    if st.button("✨ Generate Flashcards"):
        if not flashcard_text.strip():
            st.warning("Please paste a resource.")
        else:
            with st.spinner("Generating flashcards..."):
                save_prompt_to_db("Convert to Flashcards", final_prompt, edited=True)

                response = requests.post(
                    "http://18.171.171.212:8080/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a helpful teaching assistant."},
                            {"role": "user", "content": final_prompt}
                        ]
                    }
                )
                try:
                    generated_text = response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Could not parse API response: {e}")
                    st.code(response.text)
                    generated_text = "[No output returned]"

                st.markdown("### 📇 Flashcards")
                st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

                rating = st.slider("How helpful were the flashcards?", 1, 5, key="rating_flash")
                feedback = st.text_area("Any comments or suggestions?", key="feedback_flash")

                if st.button("💾 Save Feedback for Flashcards"):
                    save_prompt_to_db("Convert to Flashcards", final_prompt, edited=True, rating=rating, feedback_comment=feedback)
                    st.success("✅ Feedback saved!")


elif task == "Convert to Group Task":
    st.markdown("###Convert Resource into a Group Task")

    group_text = st.text_area("📄 Paste Resource", height=250, placeholder="e.g. article, worksheet, problem prompt")

    session = SessionLocal()
    variant_prompts = session.query(PromptEntry).filter(
        PromptEntry.task_name == "Convert to Group Task",
        PromptEntry.edited == False,
        PromptEntry.feedback_comment.like("Technique:%")
    ).all()
    session.close()

    if variant_prompts:
        technique_options = [p.feedback_comment.replace("Technique: ", "") for p in variant_prompts]
        selected_technique = st.selectbox("🧠 Choose Prompting Strategy", technique_options)
        base_prompt_text = next(
            (p.prompt_text for p in variant_prompts if selected_technique in p.feedback_comment),
            "Convert the content into a collaborative group task."
        )
    else:
        selected_technique = "Default Template"
        base_prompt_text = "Convert the content into a collaborative group task."

    prompt_filled = base_prompt_text.replace("{text}", group_text)
    final_prompt = st.text_area("🔍 Preview & Edit Prompt", value=prompt_filled, height=250)

    if st.button("✨ Generate Group Task"):
        if not group_text.strip():
            st.warning("Please paste a resource.")
        else:
            with st.spinner("Generating group activity..."):
                save_prompt_to_db("Convert to Group Task", final_prompt, edited=True)

                response = requests.post(
                    "http://18.171.171.212:8080/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a helpful teaching assistant."},
                            {"role": "user", "content": final_prompt}
                        ]
                    }
                )
                try:
                    generated_text = response.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Could not parse API response: {e}")
                    st.code(response.text)
                    generated_text = "[No output returned]"

                st.markdown("### 🤝 Group Activity Output")
                st.markdown(f"<div class='prompt-box'>{generated_text}</div>", unsafe_allow_html=True)

                rating = st.slider("How useful is this task?", 1, 5, key="rating_group")
                feedback = st.text_area("Any comments or suggestions?", key="feedback_group")

                if st.button("💾 Save Feedback for Group Task"):
                    save_prompt_to_db("Convert to Group Task", final_prompt, edited=True, rating=rating, feedback_comment=feedback)
                    st.success("✅ Feedback saved!")
