import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd



_cache: dict = {}
CACHE_TTL_SECONDS = 60


def _is_cache_valid(ticker: str) -> bool:
    if ticker not in _cache:
        return False
    return datetime.now() < _cache[ticker]["expires_at"]


def fetch_stock_data(ticker: str) -> Optional[dict]:
    ticker = ticker.upper().strip()

    if _is_cache_valid(ticker):
        return _cache[ticker]["data"]
    
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="5d")

        if data.empty:
            return None
        
        row = data.iloc[-1]
        price = row["Close"]
        high = row["High"]
        low = row["Low"]
        volume = row["Volume"]

        info = stock.info
        prev_close = info.get("previousClose", price)
        name = info.get("shortName", ticker)

        change = price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
        date_time = pd.Timestamp(data.index[-1]).strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "ticker": ticker,
            "name": name,
            "price": round(price, 2),
            "date_time": date_time,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "volume": f"{int(volume):,}",
            "prev_close": round(prev_close, 2),
        }

        # Store in cache
        _cache[ticker] = {
            "data": result,
            "expires_at": datetime.now() + timedelta(seconds=CACHE_TTL_SECONDS)
        }

        return result
    
    except Exception:
        return None
    

def fetch_multiple(tickers: list[str]):
    results = []
    for ticker in tickers:
        data = fetch_stock_data(ticker)
        if data:
            results.append(data)
    return results


POPULAR_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "HPCL", "BIDU", "FRAWZZX", "XIACF", "POAHY", "SQURPHARMA",
    "TSLA", "META", "NFLX", "AMD", "INTC", "DELL", "LNVGY", "NSUG", "AUDVF", "BMW", "TM"
]


def fetch_popular():
    return fetch_multiple(POPULAR_TICKERS)