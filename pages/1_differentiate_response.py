import streamlit as st
import requests

# --- API endpoint (replace with your actual endpoint) ---
LLM_API_URL = st.secrets["LLM_API_URL"]

st.set_page_config(page_title="Differentiate Resource", layout="centered")
st.title("🧠 Differentiate Resource")
st.write(
    "Paste lesson content, worksheet, or a question below. This tool will instantly adapt it for different ability levels: "
    "a challenge version, a scaffolded version, and a simplified version."
)

# --- User input ---
user_input = st.text_area("Paste your lesson content or resource here:", height=250)

# --- Prompt templates ---
analysis_prompt = """
Analyze the following teaching resource content. Output as:
Subject: ...
Topic: ...
Complexity: ...
If the input is vague or short, infer a likely classroom topic and scope.

Content:
{user_input}
"""

challenge_prompt = """
Create a Challenge Version for high-attaining students.
- Use academic language.
- Encourage critical thinking or real-world application.
- Include 2–3 stretch questions if appropriate.

Format:
### Challenge Version
[Your content here]

---

Analysis:
{analysis}

Content:
{user_input}
"""


scaffolded_prompt = """
Create a Scaffolded Version of the provided educational content for students needing extra support (e.g., EAL, SEND).
- Provide 2–3 sentence starters.
- Include a vocabulary box with 5–10 key terms and definitions.
- Keep the structure clear and logical.

Format:
### Scaffolded Version
Sentence starters:
- ...
- ...
Vocabulary:
- ...
- ...
[Your scaffolded content here]

---

Analysis:
{analysis}

Content:
{user_input}
"""


simplified_prompt = """
Create a Simplified Version of the provided educational content for students with low reading levels or cognitive difficulties.
- Use simple vocabulary and short sentences.
- Remove complex phrasing and abstract ideas.

Format:
### Simplified Version
[Your simplified content here]

---

Analysis:
{analysis}

Content:
{user_input}
"""


# --- LLM call helper ---
def call_llm(prompt):
    response = requests.post(
        LLM_API_URL,
        json={"messages": [{"role": "user", "content": prompt}]}
    )
    return response.json()["choices"][0]["message"]["content"]

# --- Differentiation workflow ---
def differentiate_resource_chain(user_input):
    # Step 1: Analysis
    analysis = call_llm(analysis_prompt.format(user_input=user_input))
    # Step 2: Challenge
    challenge = call_llm(challenge_prompt.format(analysis=analysis, user_input=user_input))
    # Step 3: Scaffolded
    scaffolded = call_llm(scaffolded_prompt.format(analysis=analysis, user_input=user_input))
    # Step 4: Simplified
    simplified = call_llm(simplified_prompt.format(analysis=analysis, user_input=user_input))
    return analysis, challenge, scaffolded, simplified

# --- UI: Generate button ---
if st.button("🚀 Differentiate Resource"):
    if not user_input.strip():
        st.warning("Please enter some lesson content.")
    else:
        with st.spinner("Generating differentiated versions..."):
            analysis, challenge, scaffolded, simplified = differentiate_resource_chain(user_input)
       
        st.markdown("#### 🏆 **Challenge Version**")
        st.markdown(challenge)
        st.markdown("---")
        st.markdown("#### 🛠️ **Scaffolded Version**")
        st.markdown(scaffolded)
        st.markdown("---")
        st.markdown("#### 🌱 **Simplified Version**")
        st.markdown(simplified)
        # Download all versions as a text file
        all_outputs = (
            "Analysis:\n" + analysis +
            "\n\n" + challenge +
            "\n\n" + scaffolded +
            "\n\n" + simplified
        )
        st.download_button("Download All Versions", data=all_outputs, file_name="differentiated_resource.txt")

st.markdown("---")
st.info(
    "Tip: Try both long lesson texts and short prompts (like 'Photosynthesis' or 'Causes of climate change') to test how the tool adapts."
)
