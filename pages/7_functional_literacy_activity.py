import streamlit as st
import requests
import re

LLM_API_URL = st.secrets["LLM_API_URL"]
functional_lit_prompt = """
You are a literacy support teacher who creates scaffolded, real-world reading and writing activities to help students build functional literacy skills.

Your task is to design a **short literacy activity** based on the user input below. The activity should be **practical**, age-appropriate for the learner, and focused on **real-life reading or writing**.

---

### Output Format (Use This Exactly):

Task Instruction:  
[One clear sentence explaining the real-life literacy task the student should complete]

Support Prompt:  
[One sentence stem or short sample answer that helps the student begin or understand the task]

---

### Guidelines:

- Focus on **practical tasks** like lists, notes, forms, schedules, directions, etc.  
- Use **clear, student-friendly instructions**.  
- If the input is vague, interpret it as a life-skills-based task.  
- Do **not** invent unrelated facts or overly abstract tasks.  
- Do **not** include headings, markdown, or extra commentary.  
- Return only the formatted activity below.

---

### Examples:

Task Instruction:
Write a short note to your teacher explaining why you were late.

Support Prompt:
I was late because...

Task Instruction:
Read the shopping list and circle the items you can buy at a fruit shop.

Support Prompt:
Example: apples, bananas, oranges

Task Instruction:
Fill in the blanks to complete the email to your teacher.

Support Prompt:
To: teacher@school.org
Subject: I will be late today
Hello Teacher, I will be late to school today because _______. I will arrive at _______.

Task Instruction:
Read the timetable and answer the questions about it.

Support Prompt:
What time does break start? What lesson is after lunch?

---

User input starts in the next message:
###
"""

def call_llm(prompt):
    response = requests.post(
        LLM_API_URL,
        json={
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
    )
    return response.json()["choices"][0]["message"]["content"]

def parse_functional_lit_output(output_text):
    # Look for the two labeled sections
    task_match = re.search(r'Task Instruction:\s*(.+?)(?:\n|$)', output_text, re.DOTALL)
    support_match = re.search(r'Support Prompt:\s*(.+)', output_text, re.DOTALL)

    task_instruction = task_match.group(1).strip() if task_match else ""
    support_prompt = support_match.group(1).strip() if support_match else ""

    return task_instruction, support_prompt

st.set_page_config(page_title="Functional Literacy Activities", layout="centered")
st.title("📝 Functional Literacy Activity Generator")
st.write(
    "Describe a real-world literacy scenario or skill. This tool will generate a scaffolded, practical activity for your students."
)

user_input = st.text_area("Describe the literacy scenario or skill (e.g., 'writing a shopping list', 'reading a bus timetable'):", height=150)

if st.button("Generate Activity"):
    with st.spinner("Generating..."):
        prompt = functional_lit_prompt.format(user_input=user_input)
        output = call_llm(prompt)
        task_instruction, support_prompt = parse_functional_lit_output(output)

    st.markdown("#### Task Instruction")
    st.success(task_instruction if task_instruction else "Not found.")
    st.markdown("#### Support Prompt")
    st.info(support_prompt if support_prompt else "Not found.")
    st.markdown("#### Raw Output")
    st.code(output, language="markdown")

    st.download_button("Download Activity", data=output, file_name="functional_literacy_activity.txt")

st.markdown("---")
st.info(
    "Tip: Try tasks like 'writing a thank you note', 'reading a recipe', or 'filling out a form'."
)
