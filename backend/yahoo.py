import yfinance as yf
from dataclasses import dataclass
from typing import List

@dataclass
class Quote:
    company_name: str
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

def get_quote(ticker: str) -> Quote:
    t = yf.Ticker(ticker)
    info = t.info
    price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", price)
    change = price - prev_close
    change_percent = (change / prev_close) if prev_close else 0

    return Quote(
        company_name=info.get("longName") or info.get("shortName") or ticker,
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
    t = yf.Ticker(ticker)
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
    try:
        t = yf.Ticker(ticker)
        recs = t.recommendations
        if recs is not None and not recs.empty:
            return list(recs.index[:4]) if recs.index.dtype == object else []
    except Exception:
        pass
    # Fallback: return common peers based on sector
    t = yf.Ticker(ticker)
    info = t.info
    sector = info.get("sector", "")
    fallbacks = {
        "Technology": ["MSFT", "GOOGL", "META", "NVDA"],
        "Consumer Cyclical": ["AMZN", "TSLA", "NKE", "MCD"],
        "Financial Services": ["JPM", "BAC", "GS", "MS"],
        "Healthcare": ["JNJ", "PFE", "UNH", "ABBV"],
        "Energy": ["XOM", "CVX", "COP", "SLB"],
    }
    return [p for p in fallbacks.get(sector, ["SPY", "QQQ", "DIA", "IWM"]) if p != ticker][:4]
