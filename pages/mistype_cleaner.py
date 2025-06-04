import streamlit as st
import re

def clean_user_input(text):
    # Step 1: Protect quoted text and file paths by replacing them with placeholders
    protected = []
    def protect(match):
        protected.append(match.group(0))
        return f"__PROTECTED{len(protected)-1}__"
    
    # Protect quoted text (handles "..." and '...')
    text = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', protect, text)
    # Protect file paths (simple heuristic: sequences with / or \ and no whitespace)
    text = re.sub(r'([A-Za-z]:[\\/][^\s"\']+|[\\/][^\s"\']+)', protect, text)
    
    # Step 2: Remove stray punctuation inside words (e.g., "exa,ple" -> "example")
    text = re.sub(r'(?<=\w)[,.;:!?](?=\w)', '', text)
    
    # Step 3: Restore protected content
    def restore(match):
        idx = int(match.group(1))
        return protected[idx]
    text = re.sub(r'__PROTECTED(\d+)__', restore, text)
    
    return text

# Streamlit UI
st.title("Intelligent Mistype Cleaner")
st.write("Enter your text below. The app will clean common mistypes while preserving important context (quotes, file paths, etc).")

user_input = st.text_area("Your input:", height=150)

if st.button("Clean Text"):
    cleaned = clean_user_input(user_input)
    st.subheader("Cleaned Output:")
    st.code(cleaned, language="markdown")
