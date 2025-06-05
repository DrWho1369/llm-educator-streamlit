import streamlit as st
import requests
import re

# --- LLM API endpoint (replace with your actual endpoint) ---
LLM_API_URL = st.secrets["LLM_API_URL"]

st.set_page_config(page_title="Behavior Reflection Sheet", layout="centered")
st.title("📝 Behavior Reflection Sheet Generator")
st.write(
    "Describe the situation or student need below. This tool will generate a structured reflection sheet with questions and calming strategies."
)

user_input = st.text_area("Describe the situation or context (optional):", height=150)

# --- Prompt with few-shot examples and strict format ---
reflection_prompt = """
You are a school counselor creating a Behavior Reflection Sheet for students. 
Your task is to generate a list of 4–6 reflection questions and 2–3 calming strategies, formatted as shown.

Instructions:
- Use age-appropriate, clear language.
- Number each question.
- After the questions, add a section titled "Calming Strategies" with tick-boxes.
- Do not add extra commentary or sections.

Example 1:

1. What happened?
2. How did you feel?
3. What could you do differently next time?
4. Who can help you next time?

Calming Strategies:
[ ] Take three deep breaths
[ ] Count to ten slowly
[ ] Talk to a teacher

Example 2:

1. What was your choice?
2. How did your choice affect others?
3. What would be a better choice next time?
4. Who can you ask for help?

Calming Strategies:
[ ] Take a short walk
[ ] Draw or color quietly
[ ] Listen to calming music

---

Now, using the following information, generate a new reflection sheet in the same format:

Student details/context:
{user_input}
"""

# --- LLM call helper ---
def call_llm(prompt):
    response = requests.post(
        LLM_API_URL,
        json={
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0  # Deterministic output
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# --- Output parsing function ---
def parse_reflection_sheet(output_text):
    # Split by "Calming Strategies:"
    parts = re.split(r'Calming Strategies:', output_text, flags=re.IGNORECASE)
    questions_text = parts[0].strip() if len(parts) > 0 else ''
    strategies_text = parts[1].strip() if len(parts) > 1 else ''

    # Extract numbered questions
    question_pattern = re.compile(r'^\s*\d+\.\s*(.*)$', re.MULTILINE)
    questions = question_pattern.findall(questions_text)

    # Extract calming strategies (tick-box items)
    strategy_pattern = re.compile(r'^\s*\[\s*\]\s*(.*)$', re.MULTILINE)
    strategies = strategy_pattern.findall(strategies_text)

    return questions, strategies

# --- UI: Generate button ---
if st.button("Generate Reflection Sheet"):
    with st.spinner("Generating..."):
        output = call_llm(reflection_prompt.format(user_input=user_input))
        questions, strategies = parse_reflection_sheet(output)

    st.markdown("#### Raw Reflection Sheet Output")
    st.code(output, language="markdown")

    st.markdown("#### Parsed Reflection Questions")
    if questions:
        for i, q in enumerate(questions, 1):
            st.write(f"{i}. {q}")
    else:
        st.warning("No questions detected. Please check the output or prompt.")

    st.markdown("#### Parsed Calming Strategies")
    if strategies:
        for s in strategies:
            st.write(f"- {s}")
    else:
        st.warning("No calming strategies detected. Please check the output or prompt.")

    # Download option
    st.download_button("Download Sheet", data=output, file_name="reflection_sheet.txt")

st.markdown("---")
st.info(
    "Tip: Leave the context blank for a generic sheet, or specify details (e.g., 'Year 4 student, playground conflict') for a tailored version."
)
