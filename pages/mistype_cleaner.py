import streamlit as st
import re
from transformers import pipeline
from spellchecker import SpellChecker

st.set_page_config(layout="wide")

# Initialize NER pipeline once (cached for performance)
@st.cache_resource
def load_ner_model():
    return pipeline("ner", 
                   model="Davlan/distilbert-base-multilingual-cased-ner-hrl",
                   aggregation_strategy="simple")

# Initialize spellchecker once
@st.cache_resource
def load_spellchecker():
    return SpellChecker()

ner = load_ner_model()
spell = load_spellchecker()

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



# # Cache the model and tokenizer to avoid reloading on every rerun
# @st.cache_resource
# def load_t5_spellchecker():
#     tokenizer = AutoTokenizer.from_pretrained("Bhuvana/t5-base-spellchecker")
#     model = AutoModelForSeq2SeqLM.from_pretrained("Bhuvana/t5-base-spellchecker")
#     return tokenizer, model

# tokenizer, model = load_t5_spellchecker()

# def t5_spellcheck(text):
#     input_ids = tokenizer.encode(text, return_tensors='pt')
#     with torch.no_grad():
#         sample_output = model.generate(
#             input_ids,
#             do_sample=True,
#             max_length=100,
#             top_p=0.99,
#             num_return_sequences=1
#         )
#     result = tokenizer.decode(sample_output[0], skip_special_tokens=True)
#     return result
def spellcheck_and_correct(text, protected_names):
    """Spellcheck while preserving protected names"""
    # Convert protected names to dict for lookup
    name_map = {ph: name for ph, name in protected_names}
    
    # Split into tokens (words and non-words)
    tokens = re.findall(r'\w+|[^\w\s]+|\s+', text)
    
    corrected_tokens = []
    corrections = {}
    
    for token in tokens:
        if token in name_map:
            # Restore protected names
            corrected_tokens.append(name_map[token])
        elif token.isalpha():
            # Spellcheck normal words
            if spell.unknown([token]):
                correction = spell.correction(token)
                if correction and correction != token:
                    corrections[token] = correction
                    corrected_tokens.append(correction)
                else:
                    corrected_tokens.append(token)
            else:
                corrected_tokens.append(token)
        else:
            corrected_tokens.append(token)
    
    return ''.join(corrected_tokens), corrections

# Streamlit UI
st.title("Smart Text Processor")

st.subheader("Here is a test sample with 30 names, and 5 Misspelled words to test:

exci-ted → excited

upcomming → upcoming

joi'ned → joined

snaks → snacks

scedule → schedule")

st.text("John and Maria were exci-ted to meet their new classmates: François, Ahmed, Szymon, and Nguyen. Hyeon-woo and Xi arrived early, chatting with Barack and Jose about the upcomming project. Olamide, Svetlana, and Fatima joi'ned the group, soon followed by Yuki, Priya, and Lars. Anna and Soren brought snaks, while Mikhail and Isabella set up the presentation. Chinedu, Helena, and Rashid discussed their ideas with Leandro and Duong, as Aisha and Zeynep reviewed the scedule. Vladislav, Sara, and Laszlo made sure everyone felt welcome, ensuring the team was ready to collaborate on their assignment.")
user_input = st.text_area("Enter text:", height=150)

if st.button("Process Text"):
    # Step 1: Extract and protect names
    protected_text, protected_names = extract_and_protect_names(user_input)
    st.subheader("Debug: Protected Names")
    st.write(protected_names)  # This will display the list of (placeholder, name) tuples
    # Step 2: Clean text (with protected names)
    cleaned_text = clean_user_input(protected_text)
    
    # Step 3: Spellcheck (while preserving protected names)
    corrected_text, corrections = spellcheck_and_correct(cleaned_text, protected_names)

    # corrected_text = t5_spellcheck(cleaned)
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     st.subheader("Original Input")
    #     st.write(user_input)
    # with col2:
    #     st.subheader("Cleaned Text")
    #     st.write(cleaned)
    # with col3:
    #     st.subheader("Corrected Text")
    #     st.write(corrected_text)
    # Display results

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Original Input")
        st.write(user_input)
    
    with col2:
        st.subheader("Cleaned Text")
        st.write(cleaned_text)
    
    with col3:
        st.subheader("Final Output")
        st.write(corrected_text)
        if protected_names:
            st.markdown("**Protected Names:**")
            for ph, name in protected_names:
                st.write(f"🔒 {name}")
        if corrections:
            st.subheader("Spelling Corrections")
            for wrong, right in corrections.items():
                st.write(f"**{wrong}** → {right}")


# # Initialize spellchecker once
# spell = SpellChecker(distance=1)

# def spellcheck_and_correct(text):
#     # Split into words and non-words (punctuation, whitespace)
#     tokens = re.findall(r'\w+|[^\w\s]+|\s+', text)
#     corrected_tokens = []
#     corrections = {}
#     for token in tokens:
#         if token.strip() and token.isalpha():  # Only spellcheck alphabetic tokens
#             if token.lower() in spell:
#                 corrected_tokens.append(token)
#             else:
#                 correction = spell.correction(token)
#                 if correction and correction != token:
#                     corrections[token] = correction
#                     corrected_tokens.append(correction)
#                 else:
#                     corrected_tokens.append(token)
#         else:
#             corrected_tokens.append(token)
#     corrected_text = ''.join(corrected_tokens)
#     return corrected_text, corrections

# # Streamlit UI
# st.title("Text Cleaner and Spellchecker")

# user_input = st.text_area("Enter text:", height=150)

# if st.button("Clean and Spellcheck"):
#     cleaned = clean_user_input(user_input)
#     corrected_text, corrections = spellcheck_and_correct(cleaned)
    
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         st.subheader("Original Input")
#         st.write(user_input)
    
#     with col2:
#         st.subheader("1st Step - Clean")
#         st.write(cleaned)
    
#     with col3:
#         st.subheader("2nd Step - Spellcheck")
#         st.write(corrected_text)
#         if corrections:
#             st.subheader("Corrections Made:")
#             for wrong, right in corrections.items():
#                 st.write(f"**{wrong}** → {right}")
#         else:
#             st.write("No spelling corrections needed.")
    
