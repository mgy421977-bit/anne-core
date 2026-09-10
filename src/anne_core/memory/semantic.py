"""Lightweight, offline semantic approximation for cognitive memory.

This module deliberately does not call the result an embedding model. It uses
normalized character n-grams and cosine similarity to tolerate paraphrases
while remaining deterministic, dependency-free, and offline.
"""

from __future__ import annotations

import math
import re
from collections import Counter

_WORD_RE = re.compile(r"[\w]+", re.UNICODE)
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "the", "to", "what",
    "why", "with", "which", "this", "that", "these", "those",
}


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text) if t.lower() not in _STOPWORDS]


def _features(text: str) -> Counter[str]:
    tokens = _tokens(text)
    features: Counter[str] = Counter(tokens)
    # Character trigrams make the approximation robust to inflection and
    # small wording changes without pretending to understand semantics.
    normalized = " ".join(tokens)
    padded = f"  {normalized}  "
    for i in range(max(0, len(padded) - 2)):
        features[f"c:{padded[i:i+3]}"] += 0.35
    return features


def cosine_similarity(left: str, right: str) -> float:
    """Return deterministic cosine similarity in [0, 1]."""
    a = _features(left)
    b = _features(right)
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0.0) for key, value in a.items())
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if not norm_a or not norm_b:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


class LightweightSemanticMatcher:
    """Rank text candidates with an offline semantic approximation."""

    def __init__(self, threshold: float = 0.42) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def score(self, query: str, candidate: str) -> float:
        return cosine_similarity(query, candidate)

    def rank(self, query: str, candidates: list[tuple[str, str]]) -> list[tuple[str, float]]:
        scored = [(identifier, self.score(query, text)) for identifier, text in candidates]
        return sorted(scored, key=lambda item: item[1], reverse=True)

    def is_relevant(self, score: float) -> bool:
        return score >= self.threshold
