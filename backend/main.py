import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import asyncio
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from yahoo import get_quote, get_news, get_peers
from finbert import analyze_headlines, _get_pipe
from quantum import run_quantum_circuit
from gemini import get_peers_and_alternative

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _get_pipe)
    # warm up with a dummy inference so first real request is fast
    await loop.run_in_executor(_executor, analyze_headlines, ["market update"])
    yield

app = FastAPI(title="Quantum Finance API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
    allow_credentials=False,
)

class NewsItem(BaseModel):
    title: str
    publisher: str
    link: str

class Sentiment(BaseModel):
    score: int
    label: str
    positive: int
    negative: int
    neutral: int

class QuantumMetrics(BaseModel):
    qubit_states: List[str]
    entanglement_score: int
    superposition_stability: int
    decoherence_risk: str
    probabilities: List[float]

class Peer(BaseModel):
    ticker: str
    quantum_score: int

class TopAlternative(BaseModel):
    ticker: str
    reasoning: str

class AnalysisResult(BaseModel):
    ticker: str
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
    headlines: List[NewsItem]
    sentiment: Sentiment
    quantum_metrics: QuantumMetrics
    peers: List[Peer]
    top_alternative: TopAlternative

_executor = ThreadPoolExecutor()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/analyze/{ticker}", response_model=AnalysisResult)
async def analyze(ticker: str):
    loop = asyncio.get_event_loop()
    ticker = ticker.upper()

    try:
        quote, news, peer_tickers = await asyncio.gather(
            loop.run_in_executor(_executor, get_quote, ticker),
            loop.run_in_executor(_executor, get_news, ticker),
            loop.run_in_executor(_executor, get_peers, ticker),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Yahoo Finance error: {e}")

    try:
        sentiment = await loop.run_in_executor(_executor, analyze_headlines, [n.title for n in news])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"FinBERT error: {e}")

    week52_position = (
        (quote.price - quote.low_52w) / (quote.high_52w - quote.low_52w)
        if quote.high_52w > quote.low_52w else 0.5
    )
    volume_ratio = min(quote.volume / (quote.volume * 0.7 + 1), 3.0) if quote.volume > 0 else 1.0

    quantum_metrics = run_quantum_circuit(
        change_percent=quote.change_percent,
        volume_ratio=volume_ratio,
        week52_position=week52_position,
        sentiment_score=sentiment.score,
    )

    try:
        peers, top_alternative = await loop.run_in_executor(
            _executor, get_peers_and_alternative, ticker, quote.sector, sentiment.label, peer_tickers
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini error: {e}")

    return AnalysisResult(
        ticker=ticker,
        company_name=quote.company_name,
        currency=quote.currency,
        price=quote.price,
        change=quote.change,
        change_percent=quote.change_percent,
        volume=quote.volume,
        high_52w=quote.high_52w,
        low_52w=quote.low_52w,
        market_cap=quote.market_cap,
        sector=quote.sector,
        industry=quote.industry,
        headlines=[NewsItem(title=n.title, publisher=n.publisher, link=n.link) for n in news],
        sentiment=Sentiment(
            score=sentiment.score,
            label=sentiment.label,
            positive=sentiment.positive,
            negative=sentiment.negative,
            neutral=sentiment.neutral,
        ),
        quantum_metrics=QuantumMetrics(
            qubit_states=quantum_metrics.qubit_states,
            entanglement_score=quantum_metrics.entanglement_score,
            superposition_stability=quantum_metrics.superposition_stability,
            decoherence_risk=quantum_metrics.decoherence_risk,
            probabilities=quantum_metrics.probabilities,
        ),
        peers=[Peer(ticker=p.ticker, quantum_score=p.quantum_score) for p in peers],
        top_alternative=TopAlternative(
            ticker=top_alternative.ticker,
            reasoning=top_alternative.reasoning,
        ),
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
