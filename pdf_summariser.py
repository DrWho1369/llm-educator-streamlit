# pdf_summarizer.py

import fitz  # PyMuPDF
import tiktoken
import requests

CHUNK_TOKEN_LIMIT = 1000
OVERLAP_TOKENS = 100
LLM_API_URL =  st.secrets["LLM_API_URL"]  

def count_tokens(text, model="gpt-3.5-turbo"):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def extract_pdf_text(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    paragraphs = []
    for page in doc:
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: b[1])
        for b in blocks:
            text = b[4].strip()
            if text:
                paragraphs.append(text)
    return paragraphs

def chunk_text(paragraphs, chunk_token_limit=CHUNK_TOKEN_LIMIT, overlap_tokens=OVERLAP_TOKENS):
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for paragraph in paragraphs:
        tokens = count_tokens(paragraph)
        if current_tokens + tokens > chunk_token_limit:
            chunks.append(current_chunk.strip())
            overlap_words = current_chunk.split()[-overlap_tokens:]
            current_chunk = " ".join(overlap_words) + " " + paragraph
            current_tokens = count_tokens(current_chunk)
        else:
            current_chunk += " " + paragraph
            current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def prepare_prompts(chunks):
    prompts = []
    for i, chunk in enumerate(chunks):
        prompt = f"""You are an assistant summarizing educational material for teachers.
Summarize the following extract from an educational PDF, focusing on:
- learning objectives
- key concepts
- topic structure

Return a concise bullet point list. Use the author’s wording where possible.

Extract {i+1}:
\"\"\"
{chunk}
\"\"\"
"""
        prompts.append(prompt)
    return prompts

def call_llm_api(prompt):
    response = requests.post(LLM_API_URL, json={"prompt": prompt})
    return response.json().get("summary", "⚠️ Error: No summary returned.")

def summarize_uploaded_pdf(uploaded_file):
    paragraphs = extract_pdf_text(uploaded_file)
    chunks = chunk_text(paragraphs)
    prompts = prepare_prompts(chunks)

    summaries = []
    for prompt in prompts:
        summary = call_llm_api(prompt)
        summaries.append(summary)
    return summaries
