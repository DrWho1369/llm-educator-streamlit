import streamlit as st
import requests
import re

LLM_API_URL = st.secrets["LLM_API_URL"]
revised_functional_lit_prompt = '''
You are a literacy support teacher who creates scaffolded, real-world reading and writing activities to help students build functional literacy skills.

Your task is to design a detailed, practical literacy activity based on the user input below. The activity should be age-appropriate and focused on real-life reading or writing tasks.

---

### Output Format (Use This Exactly):

Objective:
[One clear sentence describing the learning objective]

Activity:
[A detailed description of the activity, including any materials, instructions, or examples]

Support Prompt:
[A sentence stem, example, or scaffold to help the student begin or understand the task]

---

### Guidelines:

- Use the user input as the main focus for the activity.
- Include clear, student-friendly instructions.
- Provide detailed, practical tasks such as reading schedules, writing emails, following instructions, etc.
- Do not invent unrelated facts or overly abstract tasks.
- Do not include markdown or extra commentary in the output.

---

### Examples:

Objective:
Practice reading and understanding a simple school timetable.

Activity:
Read the timetable and answer the questions:
Monday Timetable:
9:00 – 9:30 → Registration
9:30 – 10:30 → English
10:30 – 11:00 → Break
11:00 – 12:00 → Maths
12:00 – 1:00 → Lunch
1:00 – 2:00 → Art
Questions:
What time does break start? ______________
What lesson is after lunch? ______________
How long is the English lesson? ______________

Support Prompt:
What time does break start? What lesson is after lunch?

---

Objective:
Learn to write a basic email to a teacher.

Activity:
Fill in the blanks to complete the email:
To: mr.jones@school.org
Subject: I will be late today
Email Body:
Hello Mr. Jones,
I will be late to school today because ______________________.
I will arrive at ____________.
Thank you.
From,

Support Prompt:
To: mr.jones@school.org
Subject: I will be late today
Hello Mr. Jones, I will be late to school today because _______. I will arrive at _______.

---

Objective:
Understand and follow step-by-step written directions.

Activity:
Read the instructions and put them in the correct order by numbering them (1–5):
___ Spread butter on the toast.
___ Put the bread in the toaster.
___ Plug in the toaster.
___ Take the toast out carefully.
___ Press the lever down.

Support Prompt:
Number the steps in the correct order.

---

User input starts in below :
###
'''


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
    obj = re.search(r'Objective:\s*(.+?)(?:\n|$)', output_text, re.DOTALL)
    act = re.search(r'Activity:\s*(.+?)(?:\nSupport Prompt:|$)', output_text, re.DOTALL)
    sup = re.search(r'Support Prompt:\s*(.+)', output_text, re.DOTALL)
    objective = obj.group(1).strip() if obj else ""
    activity = act.group(1).strip() if act else ""
    support = sup.group(1).strip() if sup else ""
    return objective, activity, support

st.set_page_config(page_title="Functional Literacy Activities", layout="centered")
st.title("📝 Functional Literacy Activity Generator")
st.write(
    "Describe a real-world literacy scenario or skill. This tool will generate a scaffolded, practical activity for your students."
)

user_input = st.text_area("Describe the literacy scenario or skill (e.g., 'writing a shopping list', 'reading a bus timetable'):", height=150)

if st.button("Generate Activity"):
    with st.spinner("Generating..."):
        prompt = revised_functional_lit_prompt + user_input
        output = call_llm(prompt)
        objective, activity, support_prompt = parse_functional_lit_output(output)

    st.markdown("#### Objective")
    st.success(objective if objective else "Not found.")

    st.markdown("#### Activity")
    st.info(activity if activity else "Not found.")

    st.markdown("#### Support Prompt")
    st.info(support_prompt if support_prompt else "Not found.")


    st.download_button("Download Activity", data=output, file_name="functional_literacy_activity.txt")

st.markdown("---")
st.info(
    "Tip: Try tasks like 'writing a thank you note', 'reading a recipe', or 'filling out a form'."
)
