# For querying fund data (used by other members)
import sqlite3
import os

DB_NAME = os.path.join("db", "fund_data.db")

def get_fund_data(symbol, days=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, open, close, volume, percent_change
        FROM fund_data
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT ?
    """, (symbol, days))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "date": row[0],
            "open": row[1],
            "close": row[2],
            "volume": row[3],
            "percent_change": row[4]
        }
        for row in rows
    ]

