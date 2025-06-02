import fitz  # PyMuPDF
import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import hdbscan
from keybert import KeyBERT
import umap
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from sklearn.metrics.pairwise import cosine_similarity


# --- PDF Theme Extraction Functions ---

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return " ".join([page.get_text() for page in doc])

def extract_sentences(text):
    return sent_tokenize(text, language="english")

def embed_sentences(sentences):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(sentences)

def cluster_embeddings(embeddings, min_cluster_size=3):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    return clusterer.fit_predict(embeddings)

def extract_cluster_keywords(sentences, labels):
    keyword_model = KeyBERT()
    clusters = {}
    for label in set(labels):
        if label == -1:
            continue
        cluster_sentences = [s for s, l in zip(sentences, labels) if l == label]
        joined = " ".join(cluster_sentences)
        keywords = keyword_model.extract_keywords(joined, top_n=3)
        clusters[label] = {
            "keywords": [kw[0] for kw in keywords],
            "examples": cluster_sentences[:3]
        }
    return clusters

def plot_clusters(embeddings, labels):
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, metric='cosine')
    reduced = reducer.fit_transform(embeddings)
    fig, ax = plt.subplots(figsize=(10, 6))
    unique_labels = set(labels)
    for label in unique_labels:
        idxs = [i for i, l in enumerate(labels) if l == label]
        x = reduced[idxs, 0]
        y = reduced[idxs, 1]
        ax.scatter(x, y, label=f"Cluster {label}" if label != -1 else "Noise", alpha=0.7)
    ax.legend()
    ax.set_title("Sentence Clusters (UMAP)")
    ax.set_xlabel("UMAP-1")
    ax.set_ylabel("UMAP-2")
    ax.grid(True)
    return fig

def process_uploaded_pdf(file):
    pdf_text = extract_text_from_pdf(file.read())
    sentences = extract_sentences(pdf_text)
    embeddings = embed_sentences(sentences)
    labels = cluster_embeddings(embeddings)
    themes = extract_cluster_keywords(sentences, labels)
    fig = plot_clusters(embeddings, labels)

    # Convert plot to base64 image
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()

    # Convert themes into readable summaries
    summarized_chunks = []
    for cluster_id, info in themes.items():
        summary = f"Cluster {cluster_id} — Keywords: {', '.join(info['keywords'])}\n"
        for ex in info['examples']:
            summary += f"  → {ex}\n"
        summarized_chunks.append(summary.strip())

    return summarized_chunks, img_base64
