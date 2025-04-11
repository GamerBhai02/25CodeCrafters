import os
import json
import re
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from fetch_fund_data import fetch_fund_data
from news_scraper import scrape_news_for_query
from model_run import analyze_news_articles

st.set_page_config(layout="wide")

# Load Fund Data
def load_fund_data(symbol):
    json_path = f"data/fund_data_{symbol}.json"
    if not os.path.exists(json_path):
        fetch_fund_data(symbol, days=30)
    with open(json_path, "r") as f:
        raw_data = json.load(f)
    df = pd.DataFrame(raw_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    return df

# Plot Fund Chart
def plot_fund_data(symbol):
    df = load_fund_data(symbol)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f'{symbol} Fund Price Over Time', xaxis_title='Date', yaxis_title='Price (USD)')
    st.plotly_chart(fig)

# Load News Data
def load_news(symbol):
    news_path = f"data/news/news_{symbol}.json"
    if os.path.exists(news_path):
        with open(news_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Extract ticker from user input
def extract_ticker(text):
    match = re.findall(r"\b[A-Z]{2,5}\b", text)
    return match[0] if match else None

# Extract keywords from query
def extract_keywords(text):
    tokens = word_tokenize(text)
    return [word for word in tokens if word.isalnum() and word.lower() not in stopwords.words('english')]

# Dummy Fund Holdings (can be loaded from a JSON/db)
FUND_HOLDINGS = {
    "QQQ": ["Apple", "Amazon", "NVIDIA", "Tesla"],
    "VTI": ["Berkshire", "Johnson & Johnson", "Microsoft"],
    "SPY": ["Meta", "Google", "ExxonMobil"]
}

# Main Streamlit App
st.title("🧠 NewsSense: Why Is My Fund Down?")

user_input = st.text_input("Ask anything like 'Why is QQQ falling?' or 'What affected SPY?'")

if user_input:
    st.markdown("#### 🧩 Step 1: Extract Ticker from Question")
    ticker = extract_ticker(user_input)
    
    if ticker:
        st.success(f"Found ticker: {ticker}")

        # Fetch and plot fund data
        with st.spinner("📈 Fetching fund data..."):
            fetch_fund_data(ticker, days=30)
        plot_fund_data(ticker)

        # Extract keywords
        keywords = extract_keywords(user_input)
        st.markdown(f"#### 🔍 Step 2: Scraping news for **{ticker}** using keywords: `{keywords}`")

        # Scrape News
        with st.spinner("📰 Scraping relevant news..."):
            scrape_news_for_query(ticker=ticker, extra_keywords=keywords)

        # Load and analyze articles
        articles = load_news(ticker)
        if not articles:
            st.warning("No articles found.")
        else:
            st.markdown("### 🧠 Step 3: AI-Powered Explanation")

            results = analyze_news_articles(articles, FUND_HOLDINGS, query=user_input)

            for i, r in enumerate(results):
                st.markdown(f"**🧾 Result {i+1}: {r['original_title']}**")
                st.write(f"**📝 Summary:** {r['summary']}")
                st.write(f"**📊 Sentiment Score:** {r['sentiment']:.2f}")
                st.write(f"**🔍 Entities:** {r['entities']}")
                st.write(f"**🎯 Matched Holdings:** {r['matched_funds']}")
                st.markdown("---")
    else:
        st.error("❌ Could not find a valid ticker in your query.")
