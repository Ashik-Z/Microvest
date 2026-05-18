import requests
from datetime import datetime, timedelta
from typing import Optional


_cache: dict = {}
CACHE_TTL_SECONDS = 3600


def _is_valid(key: str) -> bool:
    if key not in _cache:
        return False
    return datetime.now() < _cache[key]["expired_at"]


def _store(key: str, data):
    _cache[key] = {
        "data": data,
        "expired_at": datetime.now() + timedelta(seconds=CACHE_TTL_SECONDS)
    }


def fetch_exchange_rates() -> Optional[dict]:
    key = "exchange_rates"
    if _is_valid(key):
        return _cache[key]["data"]
    try:
        response = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=BDT,EUR,GBP,JPY,CNY,INR,RUB,TRY",
            timeout=8
        )
        data = response.json()
        rates = data.get("rates", {})
        result = {
            "BDT": round(rates.get("BDT", 0), 2),
            "EUR": round(rates.get("EUR", 0), 4),
            "GBP": round(rates.get("GBP", 0), 4),
            "JPY": round(rates.get("JPY", 0), 2),
            "CNY": round(rates.get("CNY", 0), 4),
            "INR": round(rates.get("INR", 0), 4),
            "RUB": round(rates.get("RUB", 0), 4),
            "TRY": round(rates.get("TRY", 0), 4),
        }
        _store(key, result)
        return result
    except Exception:
        return None
    

def fetch_inflation_rates() -> list[dict]:
    key = "inflation_rates"
    if _is_valid(key):
        return _cache[key]["data"]
    
    countries = {
        "BD": "Bangladesh",
        "US": "United States",
        "GB": "United Kingdom",
        "CN": "China",
        "IN": "India",
        "JP": "Japan",
        "DE": "Germany",
        "FR": "France",
        "TR": "Turkey",
        "RU": "Russia",
    }

    result = []
    for code, name in countries.items():
        try:
            url = (
                f"https://api.worldbank.org/v2/country/{code}/indicator/FP.CPI.TOTL.ZG"
                f"?format=json&mrnev=1"
            )
            resp = requests.get(url, timeout=8)
            data = resp.json()
            entries = data[1] if data and len(data) > 1 else []
            if entries and entries[0].get("value") is not None:
                result.append({
                    "country": name,
                    "code": code,
                    "rate": round(entries[0]["value"], 2),
                    "year": entries[0]["date"],
                })
        except Exception:
            continue

    _store(key, result)
    return result


def fetch_commodity_prices() -> Optional[dict]:
    key = "commodities"
    if _is_valid(key):
        return _cache[key]["data"]

    try:
        import yfinance as yf
        tickers = yf.download(
            ["GC=F", "CL=F", "KOL=F"],
            period="5d",
            auto_adjust=True,
            progress=False
        )
        closes = tickers["Close"]

        gold_series = closes["GC=F"].dropna()
        oil_series = closes["CL=F"].dropna()
        coal_series = closes["KOL=F"].dropna()

        if gold_series.empty or oil_series.empty or coal_series.empty:
            return None

        gold_now = round(float(gold_series.iloc[-1]), 2)
        gold_prev = round(float(gold_series.iloc[-2]), 2) if len(gold_series) > 1 else gold_now
        oil_now = round(float(oil_series.iloc[-1]), 2)
        oil_prev = round(float(oil_series.iloc[-2]), 2) if len(oil_series) > 1 else oil_now
        coal_now = round(float(coal_series.iloc[-1]), 2)
        coal_prev = round(float(coal_series.iloc[-2]), 2) if len(coal_series) > 1 else coal_now


        def pct(now, prev):
            return round(((now - prev) / prev) * 100, 2) if prev != 0 else 0

        result = {
            "gold": {
                "price": gold_now,
                "change_pct": pct(gold_now, gold_prev),
            },
            "oil": {
                "price": oil_now,
                "change_pct": pct(oil_now, oil_prev),
            },
            "coal": {
                "price": coal_now,
                "change_pct": pct(coal_now, coal_prev),
            }
        }
        _store(key, result)
        return result
    except Exception:
        return None


def calculate_real_returns(positions: list[dict], inflation_rate: float) -> list[dict]:
    results = []
    for pos in positions:
        nominal_pnl_pct = pos.get("change_pct") or pos.get("pnl_pct") or 0
        real_return = round(nominal_pnl_pct - inflation_rate, 2)
        results.append({
            "ticker": pos.get("ticker"),
            "name": pos.get("name", pos.get("ticker")),
            "nominal_pct": round(nominal_pnl_pct, 2),
            "inflation_rate": inflation_rate,
            "real_return": real_return,
            "beating_inflation": real_return > 0,
        })
    return results