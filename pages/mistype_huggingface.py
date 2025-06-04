import streamlit as st
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Cache model and tokenizer to avoid reloading on every interaction
@st.cache_resource
def load_spellchecker():
    model_name = "willwade/t5-small-spoken-typo"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_spellchecker()

def clean_user_input(text):
    # Your existing cleaning function
    # ... [keep original implementation] ...
    return text

def transformer_spellcheck(text, protected_names):
    """Use T5-small for context-aware spellchecking"""
    # Convert protected names to placeholders
    name_map = {name: f"__NAME_{i}__" for i, name in enumerate(protected_names)}
    for name, ph in name_map.items():
        text = text.replace(name, ph)
    
    # Add grammar correction prefix
    inputs = tokenizer("grammar: " + text, return_tensors="pt", max_length=512, truncation=True)
    
    # Generate correction
    outputs = model.generate(
        inputs.input_ids,
        max_length=512,
        num_beams=5,
        early_stopping=True
    )
    
    corrected = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Restore protected names
    for ph, name in name_map.items():
        corrected = corrected.replace(ph, name)
    
    return corrected

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Smart Text Processor")

user_input = st.text_area("Enter text:", height=150, value="John and Maria were exci-ted to meet François and Ahmed. Check D:\Documentsile.txt")

if st.button("Process Text"):
    # Step 1: Clean and protect names/paths
    cleaned = clean_user_input(user_input)
    
    # Step 2: Extract protected names (from your NER logic)
    # For this example, we'll use a simplified version
    protected_names = ["John", "Maria", "François", "Ahmed"]
    
    # Step 3: Apply transformer spellcheck
    corrected_text = transformer_spellcheck(cleaned, protected_names)
    
    # Display results
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Original Input")
        st.code(user_input)
    
    with col2:
        st.subheader("Cleaned Text")
        st.code(cleaned)
    
    with col3:
        st.subheader("Corrected Text")
        st.code(corrected_text)
