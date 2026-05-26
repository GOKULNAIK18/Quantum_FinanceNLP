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

from functools import lru_cache
import hashlib

_cache = {}

def analyze_headlines(headlines: list) -> 'Sentiment':
    key = hashlib.md5('|'.join(headlines[:3]).encode()).hexdigest()
    if key in _cache:
        return _cache[key]
    pipe = _get_pipe()
    positive = negative = neutral = 0.0
    for headline in headlines[:3]:  # only first 3 to stay under timeout
        results = pipe(headline[:256])[0]  # truncate to 256 chars
        for r in results:
            lbl = r['label'].lower()
            if lbl == 'positive': positive += r['score']
            elif lbl == 'negative': negative += r['score']
            else: neutral += r['score']
    total = positive + negative + neutral or 1
    pos_norm = positive / total
    neg_norm = negative / total
    neu_norm = neutral / total
    score = round((pos_norm - neg_norm + 1) / 2 * 100)
    if pos_norm > neg_norm and pos_norm > neu_norm: label = 'Bullish'
    elif neg_norm > pos_norm and neg_norm > neu_norm: label = 'Bearish'
    else: label = 'Neutral'
    result = Sentiment(
        score=score, label=label,
        positive=round(pos_norm * 100),
        negative=round(neg_norm * 100),
        neutral=round(neu_norm * 100),
    )
    _cache[key] = result
    return result
