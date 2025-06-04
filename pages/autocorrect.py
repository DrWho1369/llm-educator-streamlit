import streamlit as st
from autocorrect import Speller

spell = Speller(lang='en')

st.title("Autocorrect Spellchecker Demo")
user_input = st.text_area("Enter text:", height=150)
if st.button("Spellcheck"):
    corrected = spell(user_input)
    st.subheader("Corrected Text")
    st.write(corrected)
