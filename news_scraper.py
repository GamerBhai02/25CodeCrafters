import os
import re
import json
import requests
from bs4 import BeautifulSoup
import spacy
from transformers import pipeline
from textblob import TextBlob
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import subprocess

try:
    nlp = spacy.load("en_core_web_sm")
except:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Load models once
nlp = spacy.load("en_core_web_sm")
summarizer = pipeline("summarization", model="t5-small")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Fund Holdings for matching
fund_holdings = {
    "QQQ": ["Apple", "Amazon", "NVIDIA", "Tesla"],
    "VTI": ["Berkshire", "Johnson & Johnson", "Microsoft"],
    "SPY": ["Meta", "Alphabet", "ExxonMobil", "Pfizer"]
}

# 🧠 NLP Functions
def summarize(text):
    if len(text.split()) < 50:
        return text
    max_len = min(50, len(text.split()) // 2)
    return summarizer(text, max_length=max_len, min_length=10, do_sample=False)[0]['summary_text']

def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def match_news_to_fund(article, ticker):
    text = article.get("title", "") + " " + article.get("summary", "")
    matches = []
    for holding in fund_holdings.get(ticker, []):
        if holding.lower() in text.lower():
            matches.append(holding)
    return matches

# 🔍 Clean HTML
def clean_html(text):
    return re.sub(r"<[^>]+>", "", text)

# 🔄 Preprocess article for embeddings
def preprocess_article(article):
    text = f"{article['title']}. {article['summary']}"
    text = clean_html(text)
    doc = nlp(text)
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

# 🔎 Semantic Search Engine
def build_faiss_index(docs):
    embeddings = model.encode(docs)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, embeddings

def search(query, docs, index, embeddings):
    q_embed = model.encode([query])
    D, I = index.search(q_embed, k=3)
    return [docs[i] for i in I[0]]

# 📰 DYNAMIC Scraper for News
def scrape_news_for_query(ticker, extra_keywords=[]):
    query = f"{ticker} {' '.join(extra_keywords)}"
    search_url = f"https://www.bing.com/news/search?q={query}&FORM=HDRSC6"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        articles = []
        for card in soup.select("div.news-card") + soup.select("div.t_t") + soup.select("div.news-card-news"):
            title = card.find("a")
            if not title: continue
            title_text = title.get_text()
            link = title["href"]
            summary = card.get_text(separator=" ").strip()

            if title_text and link:
                articles.append({
                    "title": title_text,
                    "link": link,
                    "summary": summary,
                })

        # Fallback if none of the selectors worked
        if not articles:
            for a_tag in soup.select("a.title"):
                title_text = a_tag.get_text()
                link = a_tag.get("href")
                snippet = a_tag.find_next("div")
                summary = snippet.get_text() if snippet else ""

                if title_text and link:
                    articles.append({
                        "title": title_text,
                        "link": link,
                        "summary": summary
                    })

        os.makedirs("data/news", exist_ok=True)
        json.dump(articles, open(f"data/news/news_{ticker}.json", "w", encoding="utf-8"), indent=2)
        print(f"[✔] Scraped and saved {len(articles)} articles for {ticker}")
        return articles

    except Exception as e:
        print(f"[❌] Failed to scrape news for {ticker}: {e}")
        return []

# 🔬 Analyzer for CLI (optional)
def analyze_news(news_file):
    with open(news_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    docs = [preprocess_article(a) for a in articles]
    summaries = [summarize(a['summary']) for a in articles]
    sentiments = [get_sentiment(a['summary']) for a in articles]
    entities = [extract_entities(a['summary']) for a in articles]
    matched_funds = [match_news_to_fund(a, "QQQ") for a in articles]

    index, embeddings = build_faiss_index(docs)
    query = "Why did QQQ drop?"
    results = search(query, docs, index, embeddings)

    for idx, res in enumerate(results):
        print(f"\n🔍 Match {idx + 1}:\n{res[:250]}")
        print("Summary:", summaries[idx])
        print("Sentiment:", sentiments[idx])
        print("Entities:", entities[idx])
        print("Matched:", matched_funds[idx])

if __name__ == "__main__":
    scrape_news_for_query("QQQ", ["earnings", "market"])
    analyze_news("data/news/news_QQQ.json")
