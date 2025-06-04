import streamlit as st
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

st.set_page_config(layout="wide")

# Initialize NER pipeline once (cached for performance)
@st.cache_resource
def load_ner_model():
    return pipeline("ner", 
                   model="Davlan/distilbert-base-multilingual-cased-ner-hrl",
                   aggregation_strategy="simple")


ner = load_ner_model()

def extract_and_protect_names(text):
    """Extract names and replace with placeholders"""
    entities = ner(text)
    protected = []
    protected_names = []
    
    # Sort entities by start position (reverse order for safe replacement)
    sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
    
    for i, entity in enumerate(sorted_entities):
        if entity['entity_group'] == 'PER':
            # Replace name with placeholder
            placeholder = f"__NAME_{i}__"
            text = text[:entity['start']] + placeholder + text[entity['end']:]
            protected_names.append((placeholder, entity['word']))
    
    return text, protected_names

# Cache model and tokenizer to avoid reloading on every interaction
@st.cache_resource
def load_spellchecker():
    model_name = "willwade/t5-small-spoken-typo"
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_spellchecker()

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
        r'([A-Za-z]:[\\/][^\s"\']+|[\\/](?:[^\s"\']+[\\/])+[^\s"\']+)',
        protect_paths,
        text
    )
    # Remove stray punctuation including backslash and forward slash inside words
    text = re.sub(r"(?<=\w)[,.;:!?\\\\/'-](?=\w)", '', text)

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
    protected_text, protected_names = extract_and_protect_names(user_input)
    
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
