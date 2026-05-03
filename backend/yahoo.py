import yfinance as yf
from dataclasses import dataclass
from typing import List

@dataclass
class Quote:
    company_name: str
    currency: str
    price: float
    change: float
    change_percent: float
    volume: int
    high_52w: float
    low_52w: float
    market_cap: float
    sector: str
    industry: str

@dataclass
class NewsItem:
    title: str
    publisher: str
    link: str

_SUFFIXES = ["", ".NS", ".BO", ".L", ".AX", ".TO", ".HK", ".SS", ".SZ"]

def _resolve_ticker(ticker: str):
    """Try ticker as-is, then common exchange suffixes until we get real price data."""
    candidates = [ticker] if "." in ticker else [ticker + s for s in _SUFFIXES]
    for sym in candidates:
        info = yf.Ticker(sym).info
        if info.get("currentPrice") or info.get("regularMarketPrice"):
            return sym, info
    # Return bare ticker info as last resort
    return ticker, yf.Ticker(ticker).info

_CURRENCY_MAP = {
    ".NS": "INR", ".BO": "INR",
    ".L":  "GBP",
    ".AX": "AUD",
    ".TO": "CAD",
    ".HK": "HKD",
    ".SS": "CNY", ".SZ": "CNY",
}

def get_quote(ticker: str) -> Quote:
    resolved, info = _resolve_ticker(ticker)
    price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", price)
    change = price - prev_close
    change_percent = (change / prev_close) if prev_close else 0

    suffix = next((s for s in _CURRENCY_MAP if resolved.endswith(s)), "")
    currency = info.get("currency") or _CURRENCY_MAP.get(suffix, "USD")

    return Quote(
        company_name=info.get("longName") or info.get("shortName") or ticker,
        currency=currency,
        price=price,
        change=change,
        change_percent=change_percent,
        volume=info.get("regularMarketVolume") or info.get("volume", 0),
        high_52w=info.get("fiftyTwoWeekHigh", 0),
        low_52w=info.get("fiftyTwoWeekLow", 0),
        market_cap=info.get("marketCap", 0),
        sector=info.get("sector", "N/A"),
        industry=info.get("industry", "N/A"),
    )

def get_news(ticker: str) -> List[NewsItem]:
    resolved, _ = _resolve_ticker(ticker)
    t = yf.Ticker(resolved)
    news = t.news[:5]
    items = []
    for n in news:
        content = n.get("content", {})
        title = content.get("title") or n.get("title", "")
        publisher = content.get("provider", {}).get("displayName") or n.get("publisher", "")
        link = content.get("canonicalUrl", {}).get("url") or n.get("link", "")
        if title:
            items.append(NewsItem(title=title, publisher=publisher, link=link))
    return items

def get_peers(ticker: str) -> List[str]:
    resolved, info = _resolve_ticker(ticker)
    try:
        t = yf.Ticker(resolved)
        recs = t.recommendations
        if recs is not None and not recs.empty and recs.index.dtype == object:
            return list(recs.index[:4])
    except Exception:
        pass
    # Fallback: return common peers based on sector
    sector = info.get("sector", "")
    # Use exchange-aware peer tickers for Indian stocks
    suffix = ".NS" if resolved.endswith(".NS") else (".BO" if resolved.endswith(".BO") else "")
    def s(t): return t + suffix

    fallbacks = {
        "Technology": [s("INFY"), s("TCS"), s("WIPRO"), s("HCLTECH")] if suffix else ["MSFT", "GOOGL", "META", "NVDA"],
        "Industrials": [s("HAL"), s("BDL"), s("BEML"), s("MIDHANI")] if suffix else ["HON", "GE", "MMM", "RTX"],
        "Financial Services": [s("HDFCBANK"), s("ICICIBANK"), s("SBIN"), s("KOTAKBANK")] if suffix else ["JPM", "BAC", "GS", "MS"],
        "Consumer Cyclical": [s("MARUTI"), s("TATAMOTORS"), s("M&M"), s("BAJAJ-AUTO")] if suffix else ["AMZN", "TSLA", "NKE", "MCD"],
        "Healthcare": [s("SUNPHARMA"), s("DRREDDY"), s("CIPLA"), s("DIVISLAB")] if suffix else ["JNJ", "PFE", "UNH", "ABBV"],
        "Energy": [s("RELIANCE"), s("ONGC"), s("IOC"), s("BPCL")] if suffix else ["XOM", "CVX", "COP", "SLB"],
        "Basic Materials": [s("TATASTEEL"), s("JSWSTEEL"), s("HINDALCO"), s("VEDL")] if suffix else ["LIN", "APD", "ECL", "SHW"],
        "Communication Services": [s("BHARTIARTL"), s("IDEA"), s("TATACOMM"), s("MTNL")] if suffix else ["GOOGL", "META", "NFLX", "DIS"],
    }
    default = [s("NIFTY50"), s("SENSEX"), "SPY", "QQQ"] if suffix else ["SPY", "QQQ", "DIA", "IWM"]
    return [p for p in fallbacks.get(sector, default) if p != resolved][:4]
