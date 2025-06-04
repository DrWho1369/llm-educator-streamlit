import streamlit as st
import re
from spellchecker import SpellChecker
st.set_page_config(layout="wide")

def clean_user_input(text):
    protected = []  # List of tuples: (type, content)
    def protect_quotes(match):
        protected.append(('quote', match.group(0)))
        return f"__PROTECTED{len(protected)-1}__"
    def protect_paths(match):
        protected.append(('path', match.group(0)))
        return f"__PROTECTED{len(protected)-1}__"

    # Protect quoted text FIRST (so we don't protect paths inside quotes)
    text = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', protect_quotes, text)
    # Protect file paths with at least one internal slash/backslash
    text = re.sub(
        r'([A-Za-z]:[\\/](?:[^\s"\']+[\\/])+[^\s"\']+|[\\/](?:[^\s"\']+[\\/])+[^\s"\']+)',
        protect_paths,
        text
    )

    # Remove stray punctuation including backslash and forward slash inside words
    text = re.sub(r'(?<=\w)[,.;:!?\\\\/](?=\w)', '', text)

    # Restore protected content
    def restore(match):
        idx = int(match.group(1))
        typ, content = protected[idx]
        if typ == 'quote':
            # Recursively clean inside the quotes, but keep the quotes
            quote_char = content[0]
            inner = content[1:-1]
            cleaned_inner = clean_user_input(inner)
            return f"{quote_char}{cleaned_inner}{quote_char}"
        else:
            # For paths, just restore as-is
            return content

    text = re.sub(r'__PROTECTED(\d+)__', restore, text)
    return text

# Initialize spellchecker once
spell = SpellChecker(distance=1)

def spellcheck_and_correct(text):
    # Split into words and non-words (punctuation, whitespace)
    tokens = re.findall(r'\w+|[^\w\s]+|\s+', text)
    corrected_tokens = []
    corrections = {}
    for token in tokens:
        if token.strip() and token.isalpha():  # Only spellcheck alphabetic tokens
            if token.lower() in spell:
                corrected_tokens.append(token)
            else:
                correction = spell.correction(token)
                if correction and correction != token:
                    corrections[token] = correction
                    corrected_tokens.append(correction)
                else:
                    corrected_tokens.append(token)
        else:
            corrected_tokens.append(token)
    corrected_text = ''.join(corrected_tokens)
    return corrected_text, corrections

# Streamlit UI
st.title("Text Cleaner and Spellchecker")

user_input = st.text_area("Enter text:", height=150)

if st.button("Clean and Spellcheck"):
    cleaned = clean_user_input(user_input)
    corrected_text, corrections = spellcheck_and_correct(cleaned)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Original Input")
        st.write(user_input)
    
    with col2:
        st.subheader("1st Step - Clean")
        st.write(cleaned)
    
    with col3:
        st.subheader("2nd Step - Spellcheck")
        st.write(corrected_text)
        if corrections:
            st.subheader("Corrections Made:")
            for wrong, right in corrections.items():
                st.write(f"**{wrong}** → {right}")
        else:
            st.write("No spelling corrections needed.")
    
