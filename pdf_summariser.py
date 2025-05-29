# pdf_summarizer.py

import fitz  # PyMuPDF
import tiktoken
import requests

CHUNK_TOKEN_LIMIT = 1000
OVERLAP_TOKENS = 100

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

        if tokens > chunk_token_limit:
            # Split large paragraph into smaller chunks
            words = paragraph.split()
            sub_chunk = ""
            sub_tokens = 0
            for word in words:
                word_tokens = count_tokens(word)
                if sub_tokens + word_tokens > chunk_token_limit:
                    chunks.append(sub_chunk.strip())
                    sub_chunk = word + " "
                    sub_tokens = word_tokens
                else:
                    sub_chunk += word + " "
                    sub_tokens += word_tokens
            if sub_chunk:
                chunks.append(sub_chunk.strip())
            continue

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

def call_llm_api(prompt, api_url):
    payload = {
        "messages": [
            {"role": "system", "content": "You are an assistant summarizing educational content for teachers."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as req_err:
        return f"⚠️ Request error: {req_err}"
    except (KeyError, IndexError) as parse_err:
        return f"⚠️ Parsing error: {parse_err}\n{response.text if 'response' in locals() else ''}"

def summarize_uploaded_pdf(uploaded_file, api_url):
    paragraphs = extract_pdf_text(uploaded_file)
    if not paragraphs:
        return ["⚠️ No text found in uploaded PDF."]

    chunks = chunk_text(paragraphs)
    prompts = prepare_prompts(chunks)

    summaries = []
    for prompt in prompts:
        summary = call_llm_api(prompt, api_url)
        summaries.append(summary)
    return summaries
# pdf_summarizer.py

import fitz  # PyMuPDF
import tiktoken
import requests

CHUNK_TOKEN_LIMIT = 1000
OVERLAP_TOKENS = 100

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

        if tokens > chunk_token_limit:
            # Split large paragraph into smaller chunks
            words = paragraph.split()
            sub_chunk = ""
            sub_tokens = 0
            for word in words:
                word_tokens = count_tokens(word)
                if sub_tokens + word_tokens > chunk_token_limit:
                    chunks.append(sub_chunk.strip())
                    sub_chunk = word + " "
                    sub_tokens = word_tokens
                else:
                    sub_chunk += word + " "
                    sub_tokens += word_tokens
            if sub_chunk:
                chunks.append(sub_chunk.strip())
            continue

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

def call_llm_api(prompt, api_url):
    payload = {
        "messages": [
            {"role": "system", "content": "You are an assistant summarizing educational content for teachers."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as req_err:
        return f"⚠️ Request error: {req_err}"
    except (KeyError, IndexError) as parse_err:
        return f"⚠️ Parsing error: {parse_err}\n{response.text if 'response' in locals() else ''}"

def summarize_uploaded_pdf(uploaded_file, api_url):
    paragraphs = extract_pdf_text(uploaded_file)
    if not paragraphs:
        return ["⚠️ No text found in uploaded PDF."]

    chunks = chunk_text(paragraphs)
    prompts = prepare_prompts(chunks)

    summaries = []
    for prompt in prompts:
        summary = call_llm_api(prompt, api_url)
        summaries.append(summary)
    return summaries
