import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Prompt Engineering Research", layout="wide")
st.title("📘 Prompt Engineering Research")

st.markdown("""
## Objective  
This page presents deep research into prompt engineering strategies for improving LLM performance in education-focused tasks.  
""")

# --- Summary Section ---
st.header("Summary of Prompt Engineering Techniques")
st.markdown("""
Prompt engineering techniques can be grouped into several categories:

### 🔹 **Instruction-based Techniques**
- Clear role assignment (e.g., “You are a helpful teaching assistant…”)
- Task decomposition (multi-step instructions)
- Output formatting (e.g., bullet points, markdown)

### 🔹 **Cognitive Scaffolding Techniques**
- **Chain-of-Thought prompting** – Encourage step-by-step reasoning
- Socratic-style prompting – Have the LLM generate clarifying questions
- Self-evaluation prompting – Ask the LLM to assess or reflect on its own response

### 🔹 **Few-shot / Zero-shot Prompting**
- Provide examples (few-shot)
- Rely on generalization (zero-shot)

### 🔹 **Role & Persona Conditioning**
- Give the model a professional identity (e.g., teacher, examiner)
- Aligns tone and vocabulary to the user’s expectations

### 🔹 **Constraint-based Prompting**
- Define output structure, tone, or style strictly
- Limit responses (e.g., “no more than 100 words”, “bullet points only”)
""")

# --- Top 5 Table ---
st.header("Top 5 Techniques to Use in Prompts")

top5 = [
    ["1", "**Explicit Role Assignment**", "Define who the model is (e.g., teacher, coach)", "Improves context relevance and tone"],
    ["2", "**Step-by-Step Instructions**", "Break the task into clear steps", "Boosts clarity and task adherence"],
    ["3", "**Structured Output Format**", "Specify headers, slides, bullet points, etc.", "Delivers predictable, usable outputs"],
    ["4", "**Chain-of-Thought Prompting**", "Encourage multi-step reasoning", "Improves logic and content generation"],
    ["5", "**Variable Injection**", "Insert user-defined info like `{year_group}`", "Personalizes outputs and increases accuracy"]
]

st.markdown("### Summary Table")
st.table(top5)

# --- Optional Export ---
with st.expander("📄 Download as Markdown"):
    markdown_export = """
# Prompt Engineering Research Summary

## 🧠 Prompt Techniques Overview

### Instruction-Based
- Clear role assignment  
- Step-by-step decomposition  
- Output format guidance  

### Cognitive Scaffolding
- Chain-of-thought  
- Socratic prompting  
- Self-evaluation  

### Few-shot & Zero-shot
- Use of example inputs  
- Generalized task specification  

### Role Conditioning
- Assign persona (e.g. 'You are an examiner')  
- Align tone with audience  

### Constraints
- Word limits, style limits  
- Required sections / formatting  

## 🏆 Top 5 Prompt Techniques

| Rank | Technique                  | Description                                         | Why It's Effective                            |
|------|----------------------------|-----------------------------------------------------|------------------------------------------------|
| 1    | Explicit Role Assignment   | Set identity of the model                          | Aligns language, reduces ambiguity             |
| 2    | Step-by-Step Instructions | Provide clear ordered steps                        | Improves structure and focus                   |
| 3    | Structured Output Format   | Require specific formatting (e.g. slides)          | Makes output easier to use or copy             |
| 4    | Chain-of-Thought Prompting | Ask the LLM to reason through steps                | Helps with logical consistency and accuracy    |
| 5    | Variable Injection         | Insert custom info like age or topic               | Tailors outputs directly to user needs         |
    """
    st.download_button("📥 Download Markdown", data=markdown_export.strip(), file_name="prompt_research.md")

