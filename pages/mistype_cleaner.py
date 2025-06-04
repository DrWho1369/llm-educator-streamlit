import streamlit as st
import re

def clean_user_input(text):
    protected = []
    def protect(match):
        protected.append(match.group(0))
        return f"__PROTECTED{len(protected)-1}__"
    
    # Protect quoted text
    text = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', protect, text)
    # Protect file paths
    text = re.sub(r'([A-Za-z]:[\\/][^\s"\']+|[\\/][^\s"\']+)', protect, text)
    
    # Remove stray punctuation including backslash inside words
    text = re.sub(r'(?<=\w)[,.;:!?\\\\](?=\w)', '', text)
    
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
