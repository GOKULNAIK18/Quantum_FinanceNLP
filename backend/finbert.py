from dataclasses import dataclass
from typing import List
from transformers import pipeline

_pipe = None

def _get_pipe():
    global _pipe
    if _pipe is None:
        _pipe = pipeline("text-classification", model="ProsusAI/finbert", top_k=3)
    return _pipe

@dataclass
class Sentiment:
    score: int
    label: str
    positive: int
    negative: int
    neutral: int

def analyze_headlines(headlines: List[str]) -> Sentiment:
    pipe = _get_pipe()
    positive = negative = neutral = 0.0

    for headline in headlines:
        results = pipe(headline[:512])[0]
        for r in results:
            lbl = r["label"].lower()
            if lbl == "positive":
                positive += r["score"]
            elif lbl == "negative":
                negative += r["score"]
            else:
                neutral += r["score"]

    total = positive + negative + neutral or 1
    pos_norm = positive / total
    neg_norm = negative / total
    neu_norm = neutral / total

    score = round((pos_norm - neg_norm + 1) / 2 * 100)

    if pos_norm > neg_norm and pos_norm > neu_norm:
        label = "Bullish"
    elif neg_norm > pos_norm and neg_norm > neu_norm:
        label = "Bearish"
    else:
        label = "Neutral"

    return Sentiment(
        score=score,
        label=label,
        positive=round(pos_norm * 100),
        negative=round(neg_norm * 100),
        neutral=round(neu_norm * 100),
    )
