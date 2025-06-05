import streamlit as st
import requests
from modules.summarizer import analyze_pdf
from modules.pdf_extractor import extract_text_from_pdf
from modules.prompts import user_prompts

# --- Set API call URL ---
LLM_API_URL = st.secrets["LLM_API_URL"]

st.set_page_config(page_title="Differentiate Resource", layout="centered")
st.title("Differentiate Resource")

# --- Input method selection ---
input_method = st.radio("Choose input method:", ["Text Input", "Upload PDF"])
user_input = ""

if input_method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)
            result_data = analyze_pdf(text)
            keywords = result_data.get("keywords", {})
            flat_keywords = [word for group in keywords.values() for word in group]
            user_input = "\n\n[Extracted Keywords]\n" + ", ".join(flat_keywords) if flat_keywords else text
else:
    user_input = st.text_area("Paste lesson content or resource:", height=250)

# --- Prompt Chaining Logic ---
def call_llm(prompt, user_input):
    response = requests.post(
        LLM_API_URL,
        json={
            "messages": [
                {"role": "system", "content": prompt.strip()},
                {"role": "user", "content": user_input.strip()},
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

def differentiate_resource_chain(user_input):
    # Step 1: Analysis
    analysis_prompt = (
        "Analyze the following teaching resource content for subject, topic, and complexity. "
        "If the input is vague or short, infer a likely classroom topic and scope. "
        "Output as: Subject: ...; Topic: ...; Complexity: ..."
    )
    analysis_output = call_llm(analysis_prompt, user_input)

    # Step 2: Differentiation
    combined_input = f"{analysis_output}\n\n{user_input}"
    differentiation_prompt = user_prompts["Differentiate Resource"]
    differentiated_output = call_llm(differentiation_prompt, combined_input)

    return analysis_output, differentiated_output

# --- Generate Button ---
if st.button("🚀 Generate Differentiated Resource"):
    if not user_input.strip():
        st.warning("⚠️ Please enter some content or upload a PDF above.")
    else:
        with st.spinner("Generating differentiated resource..."):
            analysis, output = differentiate_resource_chain(user_input)
        st.markdown("#### 🔍 **Analysis Output**")
        st.code(analysis, language="markdown")
        st.markdown("#### 📝 **Differentiated Resource Output**")
        st.markdown(f"<div class='prompt-box'>{output}</div>", unsafe_allow_html=True)
        st.download_button("Download Output", data=output, file_name="differentiated_resource.txt")
