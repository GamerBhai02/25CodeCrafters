# For plotting graphs
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime
import os

DB_NAME = os.path.join("db", "fund_data.db")

def plot_fund(symbol):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, close FROM fund_data
        WHERE symbol = ?
        ORDER BY date ASC
    """, (symbol,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"⚠️ No data to plot for {symbol}")
        return

    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in rows]
    closes = [row[1] for row in rows]

    os.makedirs("plots", exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(dates, closes, marker='o')
    plt.title(f"{symbol} Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Close Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    filename = f"plots/{symbol}_close_plot.png"
    plt.savefig(filename)
    print(f"📈 Plot saved as {filename}")

