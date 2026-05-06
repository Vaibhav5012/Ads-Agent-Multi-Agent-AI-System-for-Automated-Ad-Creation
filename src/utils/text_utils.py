# ═══════════════════════════════════
# FILE: src/utils/text_utils.py
# PURPOSE: Text processing — cleaning, duration estimation, sentence splitting
# ═══════════════════════════════════

from __future__ import annotations

import re
import math
from typing import List


# Average speaking rate in words per second (conversational pace)
WORDS_PER_SECOND = 2.5


def clean_text(text: str) -> str:
    """Remove extra whitespace, control characters, and normalise quotes."""
    if not text:
        return ""
    # Replace smart quotes with straight quotes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    # Collapse multiple spaces / newlines
    text = re.sub(r"\s+", " ", text).strip()
    return text


def estimate_duration(text: str, wps: float = WORDS_PER_SECOND) -> float:
    """Estimate spoken duration in seconds for *text*."""
    word_count = len(text.split())
    return round(word_count / wps, 2)


def split_sentences(text: str) -> List[str]:
    """Split *text* into sentences using basic punctuation rules."""
    if not text:
        return []
    # Split on sentence-ending punctuation followed by space or end-of-string
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]


def word_count(text: str) -> int:
    """Return the number of words in *text*."""
    return len(text.split())


def truncate_text(text: str, max_words: int = 160) -> str:
    """Truncate *text* to at most *max_words* words."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def calculate_word_timings(
    text: str,
    total_duration_ms: int,
) -> list[dict]:
    """
    Return per-word timing dicts: ``[{start_ms, end_ms, word}, ...]``.

    Words are spread evenly across *total_duration_ms*.
    """
    words = text.split()
    if not words:
        return []
    ms_per_word = total_duration_ms / len(words)
    timings = []
    for i, word in enumerate(words):
        timings.append(
            {
                "start_ms": round(i * ms_per_word),
                "end_ms": round((i + 1) * ms_per_word),
                "word": word,
            }
        )
    return timings
