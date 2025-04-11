import os
import json
import re
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
import string
from openai import OpenAI
from fetch_fund_data import fetch_fund_data
from news_scraper import scrape_news_for_query
from model_run import analyze_news_articles

client = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    api_key="8b10e507d0ae4eeb9c591d3da3273e22",    
)

st.set_page_config(layout="wide")

def load_fund_data(symbol):
    filepath = f"data/fund_data_{symbol}.json"

    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return pd.DataFrame()

    with open(filepath, 'r') as f:
        json_data = json.load(f)

    if symbol not in json_data:
        print(f"❌ Symbol {symbol} not found in file.")
        return pd.DataFrame()

    df = pd.DataFrame(json_data[symbol])

    if 'date' not in df.columns:
        print(f"❌ 'date' column missing in {symbol} data.")
        print("Available columns:", df.columns.tolist())
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])
    return df

def plot_fund_data(symbol):
    df = load_fund_data(symbol)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f'{symbol} Fund Price Over Time', xaxis_title='Date', yaxis_title='Price (USD)')
    st.plotly_chart(fig)

def load_news(symbol):
    news_path = f"data/news/news_{symbol}.json"
    if os.path.exists(news_path):
        with open(news_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def extract_ticker(text):
    match = re.findall(r"\b[A-Z]{2,5}\b", text)
    return match[0] if match else None

def extract_keywords(text):
    stopwords = {
        "is", "what", "why", "who", "how", "the", "a", "an", "and", "or", "on",
        "in", "for", "of", "to", "with", "at", "from", "by", "as", "it", "this"
    }
    tokens = text.lower().translate(str.maketrans('', '', string.punctuation)).split()
    return [word for word in tokens if word not in stopwords]

FUND_HOLDINGS = {
    "QQQ": ["Apple", "Amazon", "NVIDIA", "Tesla"],
    "VTI": ["Berkshire", "Johnson & Johnson", "Microsoft"],
    "SPY": ["Meta", "Google", "ExxonMobil"]
}

st.title("🧠 NewsSense: Why Is My Fund Down?")

user_input = st.text_input("Ask anything like 'Why is QQQ falling?' or 'What affected SPY?'")

if user_input:
    st.markdown("#### ✅ Step 1: Extract Ticker from Question")
    ticker = extract_ticker(user_input)

    if ticker:
        st.success(f"Found ticker: {ticker}")

        with st.spinner("📈 Fetching fund data..."):
            fetch_fund_data(ticker, days=30)
        plot_fund_data(ticker)

        keywords = extract_keywords(user_input)
        st.markdown(f"#### 🔍 Step 2: Scraping news for **{ticker}** using keywords: `{keywords}`")

        with st.spinner("📰 Scraping relevant news..."):
            scrape_news_for_query(ticker=ticker, extra_keywords=keywords)

        articles = load_news(ticker)
        if not articles:
            st.warning("No articles found.")
        else:
            st.markdown("### 🧠 Step 3: AI-Powered Explanation")

            results = analyze_news_articles(articles, FUND_HOLDINGS, query=user_input)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant who knows only about stock market, finance, mutual funds and ETFs."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    },
                ],
            )
            message = response.choices[0].message.content
            st.markdown("### 📌 AI Analysis")
            st.write(message)
            st.markdown("---")
    else:
        st.error("❌ Could not find a valid ticker in your query.")
