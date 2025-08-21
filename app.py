from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

def fetch_stock_data(ticker):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_KEY,
        "outputsize": "compact"
    }

    # Retry up to 3 times with 5-second timeout
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "Time Series (Daily)" not in data:
                return {"ticker": ticker, "error": data.get("Note") or data.get("Error Message") or "No data available"}
            break
        except requests.exceptions.RequestException:
            if attempt == 2:
                return {"ticker": ticker, "error": "Network/SSL error"}
            time.sleep(1)

    ts = data["Time Series (Daily)"]
    sorted_dates = sorted(ts.keys())
    latest = ts[sorted_dates[-1]]

    history = []
    for date in sorted_dates[-30:]:
        day = ts[date]
        history.append({
            "date": date,
            "price": float(day["1. open"]),
            "high": float(day["2. high"]),
            "low": float(day["3. low"]),
            "close": float(day["4. close"]),
            "volume": int(day["6. volume"])
        })

    return {
        "ticker": ticker,
        "price": float(latest["1. open"]),
        "high": float(latest["2. high"]),
        "low": float(latest["3. low"]),
        "previous_close": float(latest["4. close"]),
        "source": "Alpha Vantage",
        "history": history
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stocks")
def get_stocks():
    tickers = request.args.get("tickers", "").upper().split(",")
    results = []
    for ticker in tickers:
        ticker = ticker.strip()
        if not ticker:
            continue
        results.append(fetch_stock_data(ticker))
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)