# 🧠 NewSense – Why Is My Fund Down?

NewSense is an AI-powered explanation system that helps investors understand **why mutual funds or ETFs are falling** by analyzing performance trends and scraping relevant real-world news. It uses NLP to summarize news articles, detect sentiment, highlight key entities, and match them with the fund's major holdings.

---

## 🚀 Features

- 🔍 **Ticker Detection** from natural language queries (e.g., "Why is QQQ down?")
- 📉 **Fund Performance Visualization** with Plotly
- 📰 **Dynamic News Scraping** based on ticker and keywords (no API dependency)
- 🧠 **AI Summarization** using NLP model
- 😃 **Sentiment Analysis** of scraped articles
- 🔎 Named Entity Recognition (NER) for companies, people, organizations, etc.
- 🎯 Matching News to Fund Holdings for better insights

---

## 🛠️ Tech Stack

- Python
- Streamlit (for the UI)
- Plotly (for charts)
- NLTK (for text processing)
- BeautifulSoup + Requests (for news scraping)
- Sentence-Transformers + FAISS (for semantic search)
- OpenAI / Transformers (optional: for summarization)

---

## 🖥️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/news-sense.git
cd news-sense
```

### 2. Create virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK data (optional: handled in app)

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## ▶️ Running the App

```bash
streamlit run app.py
```
Then open in browser: http://localhost:8501

## 📁 Project Structure

```bash
.
├── app.py                  # Main Streamlit app
├── fetch_fund_data.py      # Pulls mutual fund data via Alpha Vantage API
├── news_scraper.py         # Custom Bing/Google news scraper
├── model_run.py            # NLP pipeline (summarization, sentiment, NER)
├── data/
│   ├── fund_data_<TICKER>.json
│   └── news/news_<TICKER>.json
├── requirements.txt
└── README.md
```

## 💡 Example Queries

"Why is QQQ falling?"

"What’s affecting SPY today?"

"News around SBI mutual fund"

"Why is the tech sector down?"

## 🙌 Credits

Built by Team NewsSense at the "Why Is My Fund Down?" Hackathon Challenge 🧠
Big thanks to open-source libraries and APIs used.

## 📄 License

MIT License – free to use, modify, and share.

```yaml
---
Let me know if you want a version that includes screenshots, GitHub badges, or OpenAI API setup instructions.
```
