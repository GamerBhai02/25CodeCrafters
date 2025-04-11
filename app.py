import os
import json
import pandas as pd
import plotly.graph_objs as go
import streamlit as st

from fetch_fund_data import fetch_fund_data
from model_run import summarize, get_sentiment, extract_entities, match_fund  # You should have this from the previous script

# --- Load Fund Data ---
def load_fund_data(symbol):
    json_path = f"data/fund_data_{symbol}.json"

    if not os.path.exists(json_path):
        st.warning(f"Fetching live data for {symbol}...")
        fetch_fund_data(symbol, days=30)

    with open(json_path, "r") as f:
        raw_data = json.load(f)

    df = pd.DataFrame(raw_data)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    return df

# --- Plot Fund Chart ---
def plot_fund_data(symbol):
    df = load_fund_data(symbol)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f'{symbol} Fund Price Over Time',
                      xaxis_title='Date',
                      yaxis_title='Price (USD)')
    st.plotly_chart(fig)

# --- Load News ---
def load_news(symbol):
    news_path = f"data/news/news_{symbol}.json"
    if not os.path.exists(news_path):
        st.warning("No news found. Please scrape news first.")
        return []

    with open(news_path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    return articles

# --- UI Layout ---
st.title("📉 NewsSense: Why is My Fund Down?")

fund_choice = st.selectbox('Select a Fund', ['QQQ', 'VTI', 'SPY', 'ARKK'])

if st.button("🔄 Refresh Fund Data"):
    fetch_fund_data(fund_choice, days=30)
    st.success(f"Refreshed {fund_choice} data.")

plot_fund_data(fund_choice)

st.markdown("### 💬 Ask a Question")
user_question = st.text_input("Ask something like 'Why is QQQ down?' or 'What news affected SPY?'", value=f"Why is {fund_choice} down?")

if user_question:
    articles = load_news(fund_choice)

    if articles:
        st.markdown("### 🗞️ Relevant News & NLP Insights")

        for idx, article in enumerate(articles[:5]):
            st.markdown(f"**{article['title']}**")
            st.markdown(f"[Read Full Article]({article['link']})")

            summary = summarize(article['summary'])
            sentiment = get_sentiment(article['summary'])
            entities = extract_entities(article['summary'])
            matched = match_news_to_fund(article, fund_choice)

            st.write(f"**Summary:** {summary}")
            st.write(f"**Sentiment Score:** {sentiment:.2f}")
            st.write(f"**Entities:** {entities}")
            st.write(f"**Matched Holdings/Keywords:** {matched}")
            st.markdown("---")
    else:
        st.warning("No articles found. Please run the news scraper.")

