# Handles API requests + saves to JSON and SQLite
from datetime import datetime
import requests, sqlite3, json, os

API_KEY = "M8DT2DY9V611F9BF"
DB_NAME = os.path.join("db", "fund_data.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            percent_change REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(symbol, records):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for record in records:
        cursor.execute('''
            INSERT OR REPLACE INTO fund_data (symbol, date, open, high, low, close, volume, percent_change)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            record["date"],
            record["open"],
            record["high"],
            record["low"],
            record["close"],
            record["volume"],
            record["percent_change"]
        ))
    conn.commit()
    conn.close()

def fetch_fund_data(symbol, days=5, save_json=True):
    print(f"🔄 Fetching data for {symbol}...")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        print(f"⚠️ No time series data found for {symbol}. Response: {data}")
        return []

    parsed = []
    for date_str, values in list(data["Time Series (Daily)"].items())[:days]:
        open_price = float(values["1. open"])
        close_price = float(values["4. close"])
        percent_change = round(((close_price - open_price) / open_price) * 100, 2)
        parsed.append({
            "date": date_str,
            "symbol": symbol,
            "open": open_price,
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": close_price,
            "volume": int(values["5. volume"]),
            "percent_change": percent_change
        })

    if save_json:
        os.makedirs("data", exist_ok=True)
        with open(f"data/fund_data_{symbol}.json", "w") as f:
            json.dump({symbol: parsed}, f, indent=2)

    save_to_db(symbol, parsed)
    return parsed

