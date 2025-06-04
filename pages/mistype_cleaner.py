import streamlit as st
import re
from spellchecker import SpellChecker

# Your existing cleaning function (with protection and punctuation removal)
def clean_user_input(text):
    protected = []
    def protect(match):
        protected.append(match.group(0))
        return f"__PROTECTED{len(protected)-1}__"
    
    # Protect quoted text
    text = re.sub(r'(["\'])(?:(?=(\\?))\2.)*?\1', protect, text)
    
    # Protect file paths with internal slashes/backslashes
    text = re.sub(
        r'([A-Za-z]:[\\/](?:[^\s"\']+[\\/])+[^\s"\']+|[\\/](?:[^\s"\']+[\\/])+[^\s"\']+)', 
        protect, 
        text
    )
    
    # Remove stray punctuation including backslash and forward slash inside words
    text = re.sub(r'(?<=\w)[,.;:!?\\/](?=\w)', '', text)
    
    def restore(match):
        idx = int(match.group(1))
        return protected[idx]
    text = re.sub(r'__PROTECTED(\d+)__', restore, text)
    
    return text

# Initialize spellchecker once
spell = SpellChecker(distance=1)

def spellcheck_and_correct(text):
    words = text.split()
    misspelled = spell.unknown(words)
    corrections = {}
    corrected_words = []
    for word in words:
        if word in misspelled:
            correction = spell.correction(word)
            corrections[word] = correction
            corrected_words.append(correction)
        else:
            corrected_words.append(word)
    corrected_text = ' '.join(corrected_words)
    return corrected_text, corrections

# Streamlit UI
st.title("Text Cleaner and Spellchecker")

user_input = st.text_area("Enter text:", height=150)

if st.button("Clean and Spellcheck"):
    cleaned = clean_user_input(user_input)
    corrected_text, corrections = spellcheck_and_correct(cleaned)
    
    st.subheader("Cleaned Text")
    st.write(cleaned)
    
    st.subheader("Spellchecked and Corrected Text")
    st.write(corrected_text)
    
    if corrections:
        st.subheader("Corrections Made")
        for wrong, right in corrections.items():
            st.write(f"**{wrong}** → {right}")
    else:
        st.write("No spelling corrections needed.")
