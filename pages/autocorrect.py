import streamlit as st
from autocorrect import Speller
import re
from transformers import pipeline

st.set_page_config(layout="wide")

# Initialize NER pipeline once (cached for performance)
@st.cache_resource
def load_ner_model():
    return pipeline("ner", 
                   model="Davlan/distilbert-base-multilingual-cased-ner-hrl",
                   aggregation_strategy="simple")


ner = load_ner_model()
spell = Speller(lang='en')

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



def spellcheck_and_correct(text, protected_names):
    """
    Spellcheck while preserving protected names using autocorrect.
    """
    # Build a map for placeholders to original names
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
            corrected = spell(token)
            if corrected != token:
                corrections[token] = corrected
            corrected_tokens.append(corrected)
        else:
            corrected_tokens.append(token)

    return ''.join(corrected_tokens), corrections

# Streamlit UI
st.title("Smart Text Processor")

st.markdown("""
| Step          | What Happens                                                                 |
|---------------|------------------------------------------------------------------------------|
| NER           | Finds and protects names with placeholders                                   |
| Cleaning      | Removes stray punctuation, protects quoted text and file paths               |
| Spellchecking | Corrects spelling, skips protected names, uses autocorrect module            |
| UI            | Lets user input text, shows results and corrections in a clear, structured way|
""")

st.markdown("""
**Test Sample:**  
Below are 10 examples to test the text cleaning, and also a paragraph containing 30 diverse names and 5 intentionally misspelled words. Try pasting this into the input box to see how the processor handles names and spelling errors.

**Test text cleaning and context preservation:**  
- exa,ple
- "This is important"
- C/file/pathdirectory
- He said, "exa,ple" is wrong
- test.ing
- Check this path: D:\Documents\\file.txt
- but\\this backslas\h shouldn't be here
- but/this backslas/h shouldn't be here
- Hello, world!
- Mistyped,word with, commas inside

---

**Example Text (30 names, mispelling, mistyping and :**  
John and Maria were exci-ted to meet their new classmates: François, Ahmed, Szymon, and Nguyen. Hyeon-woo and Xi arrived early, chatting with Barack and Jose about the upcomming project. Olamide, Svetlana, and Fatima joi'ned the group, soon followed by Yuki, Priya, and Lars. Anna and Soren brought snaks, while Mikhail and Isabella set up the presentation. Chinedu, Helena, and Rashid discussed their ideas with Leandro and Duong, as Aisha and Zeynep reviewed the scedule. Vladislav, Sara, and Laszlo made sure everyone felt welcome, ensuring the team was ready to collaborate on their assignment.
""")
user_input = st.text_area("Enter text:", height=150)


if st.button("Process Text"):
    # Step 1: Extract and protect names
    protected_text, protected_names = extract_and_protect_names(user_input)
    st.subheader("Names Detected & Protected")
    # st.write(protected_names)  # This will display the list of (placeholder, name) tuples
    if protected_names:
        names = [name for _, name in protected_names]
        n_cols = 6  # Adjust as needed
        rows = [names[i:i+n_cols] for i in range(0, len(names), n_cols)]
        for row in rows:
            cols = st.columns(len(row))
            for col, name in zip(cols, row):
                col.write(f"🔒 {name}")

    # Step 2: Clean text (with protected names)
    cleaned_text = clean_user_input(protected_text)
    
    # Step 3: Spellcheck (while preserving protected names)
    corrected_text, corrections = spellcheck_and_correct(cleaned_text, protected_names)

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
        if corrections:
            st.subheader("Spelling Corrections")
            for wrong, right in corrections.items():
                st.write(f"**{wrong}** → {right}")

