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
Your task is to help students reflect on their actions in a supportive, restorative, and non-judgmental way.

Instructions:
- Use age-appropriate, clear language.
- Number each question.
- After the questions, add a section titled "Calming Strategies" with tick-boxes.
- Do NOT condone or encourage negative behaviors.
- Focus on helping the student understand why the behavior was not appropriate and how to make better choices next time.

---------
Example 1 (negative behavior):

Student details/context: Hitting another student

1. What happened before you decided to hit?
2. How did you and the other student feel?
3. What could you have done instead of hitting?
4. Who can help you make better choices next time?

Calming Strategies:
[ ] Take three deep breaths
[ ] Walk away and talk to an adult
[ ] Squeeze a stress ball

---------
Example 2 (neutral behavior):

Student details/context: Not completing homework

1. What happened that made it hard to finish your homework?
2. How did you feel about not completing it?
3. What could you do differently next time?
4. Who can help you stay on track?

Calming Strategies:
[ ] Make a homework plan with a teacher
[ ] Take a short break before starting homework
[ ] Ask for help if you’re stuck

---------
Example 3 (positive behavior):

Student details/context: Helping a classmate

1. What did you do to help your classmate?
2. How did your actions make you and your classmate feel?
3. Why is it important to help others?
4. What could you do to help someone again?

Calming Strategies:
[ ] Take three deep breaths
[ ] Give yourself a compliment
[ ] Share your experience with the class

-------

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


if st.button("Generate Reflection Sheets"):
    # Clear previous results
    st.session_state.generated_sheets = []
    previous_outputs = ""  # Holds all previous outputs as context

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_sheets):
        try:
            status_text.text(f"Generating sheet {i+1}/{num_sheets}...")

            # Build a context-aware prompt for each sheet
            if i == 0:
                prompt = reflection_prompt.format(user_input=user_input)
            else:
                prompt = (
                    reflection_prompt
                    + f"\n---\nHere are the reflection sheets previously generated, ensure you generate a new, different reflection sheet for the same context:\n{previous_outputs}\n"
                )

            output = call_llm(prompt)
            questions, strategies = parse_reflection_sheet(output)

            st.session_state.generated_sheets.append({
                "raw": output,
                "questions": questions,
                "strategies": strategies
            })

            # Add this output to the context for the next sheet
            previous_outputs += f"\n--- Sheet {i+1} ---\n{output}\n"

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
                        st.markdown(f"{i+1}. {q}")
            
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
