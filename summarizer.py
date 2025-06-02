import re
import base64
from collections import Counter
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# --- Regex-based tokenizers ---

def regex_sent_tokenize(text):
    pattern = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    return [s.strip() for s in pattern.split(text.strip()) if s.strip()]

def regex_word_tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

# --- Stopwords (simple static list) ---

STOPWORDS = set("""
    a about above after again against all am an and any are aren't as at be because been
    before being below between both but by can can't cannot could couldn't did didn't do
    does doesn't doing don't down during each few for from further had hadn't has hasn't
    have haven't having he he'd he'll he's her here here's hers herself him himself his
    how how's i i'd i'll i'm i've if in into is isn't it it's its itself let's me more
    most mustn't my myself no nor not of off on once only or other ought our ours
    ourselves out over own same shan't she she'd she'll she's should shouldn't so some
    such than that that's the their theirs them themselves then there there's these they
    they'd they'll they're they've this those through to too under until up very was
    wasn't we we'd we'll we're we've were weren't what what's when when's where where's
    which while who who's whom why why's with won't would wouldn't you you'd you'll you're
    you've your yours yourself yourselves
""".split())

# --- Keyword Extraction Methods ---

def extract_keywords_freq(text, num_keywords=10):
    words = regex_word_tokenize(text)
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(num_keywords)]

def extract_keywords_tfidf(text, num_keywords=10):
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    ranked = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    return [term for term, _ in ranked[:num_keywords]]

def extract_noun_phrases(text, top_n=10):
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer(ngram_range=(2, 2), stop_words='english')
    X = vectorizer.fit_transform([text])
    freqs = zip(vectorizer.get_feature_names_out(), X.toarray()[0])
    sorted_phrases = sorted(freqs, key=lambda x: x[1], reverse=True)
    return [phrase for phrase, count in sorted_phrases[:top_n]]

def text_summarize(text, num_sentences=3):
    sentences = regex_sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])

    words = regex_word_tokenize(text)
    filtered = [w for w in words if w not in STOPWORDS]

    word_freq = Counter(filtered)
    sentence_scores = {}

    for i, sent in enumerate(sentences):
        sent_words = regex_word_tokenize(sent)
        score = sum(word_freq[word] for word in sent_words if word in word_freq)
        sentence_scores[i] = score

    # Get the indices of the top-ranked sentences
    top_indices = sorted(
        [i for i, _ in sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]]
    )

    # Return the top sentences in their original order, each numbered
    return "\n".join([f"{j+1}. {sentences[i]}" for j, i in enumerate(top_indices)])

# --- Word Cloud Generation ---
def word_cloud(text):
    wc = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS)
    wc.generate(text)
    buffer = BytesIO()
    wc.to_image().save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return encoded

# --- Main Analysis Function ---
def analyze_pdf(text, num_keywords=10):
    num_keywords = int(num_keywords)  # ✅ Force type conversion
    summary = text_summarize(text)
    keywords = {
        "TF-IDF": extract_keywords_tfidf(text, num_keywords),
        "Frequency": extract_keywords_freq(text, num_keywords),
        "Noun Phrases": extract_noun_phrases(text, num_keywords)
    }
    wordcloud_img = word_cloud(text)

    return {
        "summary": summary,
        "keywords": keywords,
        "wordcloud": wordcloud_img
    }
