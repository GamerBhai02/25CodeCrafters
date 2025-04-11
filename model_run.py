import re
import spacy
import json
import faiss
import numpy as np
from textblob import TextBlob
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# Load models once
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization", model="t5-small")
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- Preprocessing ----------
def clean_html(text):
    return re.sub(r"<[^>]+>", "", text)

def preprocess_article(article):
    text = f"{article.get('title', '')}. {article.get('summary', '')}"
    text = clean_html(text)
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

def preprocess_articles(articles):
    return [preprocess_article(a) for a in articles]

# ---------- NLP Tasks ----------
def summarize(text):
    if len(text.split()) < 50:
        return text
    max_len = min(50, len(text.split()) // 2)
    return summarizer(text, max_length=max_len, min_length=10, do_sample=False)[0]['summary_text']

def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# ---------- Fund Matcher ----------
def match_fund(article_text, fund_holdings):
    matches = []
    for fund, holdings in fund_holdings.items():
        for holding in holdings:
            if holding.lower() in article_text.lower():
                matches.append(fund)
                break
    return matches

# ---------- Semantic Search ----------
def build_faiss_index(docs):
    embeddings = model.encode(docs)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, embeddings

def search(query, docs, index, embeddings, top_k=3):
    q_embed = model.encode([query])
    D, I = index.search(q_embed, k=top_k)
    return [docs[i] for i in I[0]], I[0]  # Return both text results and indices

# ---------- Core Runner ----------
def analyze_news_articles(articles, fund_holdings, query="Why is my fund down?"):
    preprocessed = preprocess_articles(articles)

    summaries = [summarize(text) for text in preprocessed]
    sentiments = [get_sentiment(text) for text in preprocessed]
    entities = [extract_entities(text) for text in preprocessed]
    matched_funds = [match_fund(text, fund_holdings) for text in preprocessed]

    index, embeddings = build_faiss_index(preprocessed)
    top_results, top_indices = search(query, preprocessed, index, embeddings)

    results = []
    for i, idx in enumerate(top_indices):
        article = articles[idx]
        results.append({
            "original_title": article.get("title", "")[:150],
            "summary": summaries[idx],
            "sentiment": sentiments[idx],
            "entities": entities[idx],
            "matched_funds": matched_funds[idx]
        })
    return results
