import os
import requests
from dataclasses import dataclass
from typing import List

HF_API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
HF_TOKEN = os.getenv("HF_TOKEN", "")

@dataclass
class Sentiment:
    score: int
    label: str
    positive: int
    negative: int
    neutral: int

_cache = {}

def analyze_headlines(headlines: List[str]) -> Sentiment:
    key = '|'.join(headlines[:3])
    if key in _cache:
        return _cache[key]

    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    positive = negative = neutral = 0.0

    for headline in headlines[:3]:
        try:
            res = requests.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": headline[:256]},
                timeout=10,
            )
            if res.status_code == 200:
                results = res.json()
                if isinstance(results, list) and isinstance(results[0], list):
                    results = results[0]
                for r in results:
                    lbl = r.get("label", "").lower()
                    score = r.get("score", 0)
                    if lbl == "positive": positive += score
                    elif lbl == "negative": negative += score
                    else: neutral += score
        except Exception:
            neutral += 1.0

    total = positive + negative + neutral or 1
    pos_norm = positive / total
    neg_norm = negative / total
    neu_norm = neutral / total
    score = round((pos_norm - neg_norm + 1) / 2 * 100)

    if pos_norm > neg_norm and pos_norm > neu_norm: label = "Bullish"
    elif neg_norm > pos_norm and neg_norm > neu_norm: label = "Bearish"
    else: label = "Neutral"

    result = Sentiment(
        score=score, label=label,
        positive=round(pos_norm * 100),
        negative=round(neg_norm * 100),
        neutral=round(neu_norm * 100),
    )
    _cache[key] = result
    return result

# Keep for compatibility
def _get_pipe():
    pass
