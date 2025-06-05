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
# --- Add number input widget ---
num_sheets = st.number_input(
    "Number of reflection sheets to generate",
    min_value=1,
    max_value=5,  # Limit to prevent abuse
    value=1,
    step=1
)
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


# --- Modified generation logic ---
if st.button("Generate Reflection Sheets"):
    if 'generated_sheets' in st.session_state:
        del st.session_state.generated_sheets  # Clear previous results
    
    st.session_state.generated_sheets = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(num_sheets):
        try:
            status_text.text(f"Generating sheet {i+1}/{num_sheets}...")
            output = call_llm(reflection_prompt.format(user_input=user_input))
            questions, strategies = parse_reflection_sheet(output)
            
            st.session_state.generated_sheets.append({
                "raw": output,
                "questions": questions,
                "strategies": strategies
            })
            
            progress_bar.progress((i+1)/num_sheets)
        
        except Exception as e:
            st.error(f"Error generating sheet {i+1}: {str(e)}")
            break
    
    progress_bar.empty()
    status_text.empty()

# --- Display generated sheets ---
if 'generated_sheets' in st.session_state and st.session_state.generated_sheets:
    st.markdown("---")
    st.subheader(f"Generated Reflection Sheets ({len(st.session_state.generated_sheets)} total)")
    
    # Combine all raw outputs for download
    all_outputs = []
    
    for idx, sheet in enumerate(st.session_state.generated_sheets, 1):
        with st.expander(f"Reflection Sheet #{idx}", expanded=(idx==1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Reflection Questions")
                if sheet['questions']:
                    for i, q in enumerate(sheet['questions']):
                        st.checkbox(f"{i+1}. {q}", key=f"q_{idx}_{i}")
            
            with col2:
                st.markdown("#### Calming Strategies")
                if sheet['strategies']:
                    for i, s in enumerate(sheet['strategies']):
                        st.checkbox(s, key=f"s_{idx}_{i}")
            
            st.markdown("##### Raw Output")
            st.code(sheet['raw'], language="markdown")
            
            all_outputs.append(f"--- Sheet {idx} ---\n{sheet['raw']}\n")
    
    # Download all sheets combined
    st.download_button(
        label="Download All Sheets",
        data="\n\n".join(all_outputs),
        file_name="multiple_reflection_sheets.txt"
    )
