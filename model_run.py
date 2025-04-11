import json
import re
import spacy
from transformers import pipeline
from textblob import TextBlob
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Load necessary models
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization", model="t5-small")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Preprocessing function to clean HTML and tokenize
def clean_html(text):
    return re.sub(r"<[^>]+>", "", text)

def preprocess_article(article):
    text = f"{article['title']}. {article['summary']}"
    text = clean_html(text)
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

def preprocess_news_file(news_file):
    with open(news_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
    return [preprocess_article(a) for a in articles]

# NLP Tasks
def summarize(text):
    return summarizer(text, max_length=50, min_length=15, do_sample=False)[0]['summary_text']

def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Range: -1 to +1

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

# Match news articles with fund holdings
fund_holdings = {
    "QQQ": ["Apple", "Amazon", "NVIDIA", "Tesla"],
    "VTI": ["Berkshire", "Johnson & Johnson", "Microsoft"]
}

def match_fund(article_text, fund_holdings):
    matches = []
    for fund, holdings in fund_holdings.items():
        for holding in holdings:
            if holding.lower() in article_text.lower():
                matches.append(fund)
                break
    return matches

# Build FAISS Index for semantic search
def build_faiss_index(docs):
    embeddings = model.encode(docs)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, embeddings

# Search function to match query with the top N results
def search(query, docs, index, embeddings):
    q_embed = model.encode([query])
    D, I = index.search(q_embed, k=3)
    return [docs[i] for i in I[0]]

# Main function to process and analyze news
def analyze_news(news_file):
    # Preprocess articles
    articles = preprocess_news_file(news_file)
    
    # NLP Tasks
    summaries = [summarize(a) for a in articles]
    sentiments = [get_sentiment(a) for a in articles]
    entities = [extract_entities(a) for a in articles]

    # Match news to funds
    matched_funds = [match_fund(a, fund_holdings) for a in articles]

    # Semantic search setup
    index, embeddings = build_faiss_index(articles)

    # Example Query
    query = "Why did QQQ drop?"
    search_results = search(query, articles, index, embeddings)

    # Display results
    for idx, result in enumerate(search_results):
        print(f"🔍 Result {idx + 1}:")
        print("Article:", result[:200])  # First 200 chars for preview
        print("Summary:", summaries[idx])
        print("Sentiment:", sentiments[idx])
        print("Entities:", entities[idx])
        print("Matched Funds:", matched_funds[idx])
        print("\n")

if __name__ == "__main__":
    # Example file path (make sure the file exists in this location)
    news_file = "data/news/news_QQQ.json"
    analyze_news(news_file)
