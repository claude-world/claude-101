"""Shared utilities for Claude 101 tools."""

from __future__ import annotations

import re
from collections import Counter


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def reading_time(text: str, wpm: int = 238) -> float:
    """Estimate reading time in minutes."""
    return round(word_count(text) / wpm, 1)


def flesch_score(text: str) -> float:
    """Calculate Flesch Reading Ease score (0-100, higher = easier)."""
    sentences = sentence_tokenize(text)
    words = text.split()
    if not sentences or not words:
        return 0.0
    syllables = sum(_count_syllables(w) for w in words)
    asl = len(words) / len(sentences)
    asw = syllables / len(words)
    score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(max(0.0, min(100.0, score)), 1)


def flesch_grade(score: float) -> str:
    """Convert Flesch score to readability grade."""
    if score >= 90:
        return "Very Easy (5th grade)"
    if score >= 80:
        return "Easy (6th grade)"
    if score >= 70:
        return "Fairly Easy (7th grade)"
    if score >= 60:
        return "Standard (8th-9th grade)"
    if score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    if score >= 30:
        return "Difficult (College)"
    return "Very Difficult (Graduate)"


def sentence_tokenize(text: str) -> list[str]:
    """Split text into sentences."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in parts if s.strip()]


def keyword_frequency(text: str, top_n: int = 10) -> list[tuple[str, int]]:
    """Extract top-N keywords by frequency (excluding stopwords)."""
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "it",
        "that",
        "this",
        "was",
        "are",
        "be",
        "has",
        "have",
        "had",
        "not",
        "as",
        "we",
        "they",
        "you",
        "i",
        "he",
        "she",
        "its",
        "my",
        "your",
        "our",
        "their",
        "can",
        "will",
        "do",
        "does",
        "did",
        "been",
        "being",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "about",
        "up",
        "out",
        "if",
        "so",
        "no",
        "than",
        "too",
        "very",
        "just",
        "also",
        "more",
        "some",
        "any",
        "all",
        "each",
        "every",
        "both",
        "few",
        "most",
        "other",
        "into",
        "over",
        "such",
        "after",
        "before",
        "between",
        "through",
        "during",
        "what",
        "which",
        "who",
        "whom",
        "how",
        "when",
        "where",
        "why",
        "these",
        "those",
        "then",
        "there",
        "here",
        "only",
        "own",
        "same",
        "while",
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    filtered = [w for w in words if w not in stopwords]
    return Counter(filtered).most_common(top_n)


def _count_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower().strip(".,!?;:'\"")
    if not word:
        return 0
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and not word.endswith("le"):
        count -= 1
    return max(1, count)


def parse_csv(data: str) -> tuple[list[str], list[list[str]]]:
    """Parse CSV string into headers and rows."""
    import csv
    import io

    reader = csv.reader(io.StringIO(data.strip()))
    rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def parse_json_data(data: str) -> list[dict]:
    """Parse JSON string into list of dicts."""
    import json

    parsed = json.loads(data)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    return []


def basic_stats(values: list[float]) -> dict:
    """Calculate basic statistics for a list of numbers."""
    import statistics

    if not values:
        return {"count": 0}
    result = {
        "count": len(values),
        "mean": round(statistics.mean(values), 4),
        "median": round(statistics.median(values), 4),
        "min": min(values),
        "max": max(values),
    }
    if len(values) >= 2:
        result["stdev"] = round(statistics.stdev(values), 4)
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        result["p25"] = sorted_vals[n // 4]
        result["p75"] = sorted_vals[(3 * n) // 4]
        q1, q3 = result["p25"], result["p75"]
        iqr = q3 - q1
        result["outliers"] = [
            v for v in values if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr
        ]
    return result


def formality_score(text: str) -> float:
    """Compute a formality score for text (0-100, higher = more formal).

    Factors: formal/informal marker ratio, average sentence length, syllable density.
    """
    if not text.strip():
        return 50.0

    _FORMAL_MARKERS = [
        "regarding",
        "furthermore",
        "consequently",
        "therefore",
        "sincerely",
        "respectfully",
        "accordingly",
        "henceforth",
        "pursuant",
        "hereby",
        "please",
        "kindly",
        "appreciate",
        "acknowledge",
        "endeavor",
        "facilitate",
        "commence",
        "subsequent",
        "aforementioned",
        "notwithstanding",
    ]
    _INFORMAL_MARKERS = [
        "hey",
        "gonna",
        "wanna",
        "gotta",
        "kinda",
        "sorta",
        "yeah",
        "yep",
        "nope",
        "cool",
        "awesome",
        "stuff",
        "thing",
        "ok",
        "lol",
        "omg",
        "btw",
        "tbh",
        "imo",
        "fyi",
    ]
    _CONTRACTION_RE = re.compile(
        r"\b(?:don'?t|can'?t|won'?t|isn'?t|aren'?t|wasn'?t|weren'?t|"
        r"wouldn'?t|couldn'?t|shouldn'?t|hasn'?t|haven'?t|hadn'?t|"
        r"doesn'?t|didn'?t|i'?m|i'?ll|i'?d|i'?ve|"
        r"he'?s|she'?s|it'?s|we'?re|they'?re|that'?s|"
        r"let'?s|who'?s|what'?s|there'?s|here'?s)\b",
        re.IGNORECASE,
    )

    lower = text.lower()
    words = text.split()
    if not words:
        return 50.0

    formal_count = sum(1 for m in _FORMAL_MARKERS if m in lower)
    informal_count = sum(1 for m in _INFORMAL_MARKERS if m in lower)
    contraction_count = len(_CONTRACTION_RE.findall(text))
    informal_count += contraction_count

    # Marker ratio component (0-40 points)
    total_markers = formal_count + informal_count
    if total_markers > 0:
        marker_score = (formal_count / total_markers) * 40
    else:
        marker_score = 20.0  # neutral

    # Sentence length component (0-30 points)
    sentences = sentence_tokenize(text)
    if sentences:
        avg_sent_len = len(words) / len(sentences)
        # Longer sentences → more formal (clamp 5-30 words → 0-30 points)
        sent_score = min(30.0, max(0.0, (avg_sent_len - 5) / 25 * 30))
    else:
        sent_score = 15.0

    # Syllable density component (0-30 points)
    total_syllables = sum(_count_syllables(w) for w in words)
    avg_syllables = total_syllables / len(words) if words else 1.0
    # Higher syllable count → more formal (clamp 1.0-2.5 → 0-30 points)
    syl_score = min(30.0, max(0.0, (avg_syllables - 1.0) / 1.5 * 30))

    score = marker_score + sent_score + syl_score
    return round(max(0.0, min(100.0, score)), 1)


def detect_named_entities(text: str) -> list[str]:
    """Extract probable named entities (capitalized multi-word sequences).

    Uses simple heuristics: looks for sequences of capitalized words
    not at sentence start, filters common false positives.
    """
    _SKIP_WORDS = {
        "The",
        "This",
        "That",
        "There",
        "They",
        "Then",
        "When",
        "Where",
        "What",
        "Which",
        "However",
        "Also",
        "Meanwhile",
        "After",
        "Before",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
        "I",
        "He",
        "She",
        "It",
        "We",
        "You",
        "But",
        "And",
        "Or",
        "So",
        "If",
        "Not",
        "For",
        "Yet",
        "Because",
        "Since",
        "While",
        "Although",
    }

    # Find capitalized word sequences
    candidates = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text)
    # Also single capitalized words that appear mid-sentence
    sentences = sentence_tokenize(text)
    for sent in sentences:
        words = sent.split()
        for i, w in enumerate(words):
            if i > 0 and re.match(r"^[A-Z][a-z]+$", w) and w not in _SKIP_WORDS:
                candidates.append(w)

    # Deduplicate preserving order, filter skip words
    seen: set[str] = set()
    result: list[str] = []
    for c in candidates:
        if c not in seen and c not in _SKIP_WORDS:
            seen.add(c)
            result.append(c)
    return result


def count_pattern_matches(text: str, patterns: list[str]) -> int:
    """Count total keyword matches with word boundary matching (case-insensitive)."""
    total = 0
    for pattern in patterns:
        total += len(
            re.findall(r"\b" + re.escape(pattern) + r"\b", text, re.IGNORECASE)
        )
    return total


def text_structure_check(text: str, markers: dict[str, list[str]]) -> dict[str, bool]:
    """Check if text contains any of the patterns for each marker group.

    Args:
        text: Text to check.
        markers: ``{marker_name: [pattern1, pattern2, ...]}``

    Returns:
        ``{marker_name: True/False}``
    """
    lower = text.lower()
    return {
        name: any(p.lower() in lower for p in patterns)
        for name, patterns in markers.items()
    }


def _normalize_weights(raw: list[float]) -> list[float]:
    """Normalize a list of weights so they sum to 1.0."""
    total = sum(raw)
    if total == 0:
        n = len(raw)
        return [round(1.0 / n, 4)] * n if n else []
    return [round(w / total, 4) for w in raw]


def infer_column_type(values: list[str]) -> str:
    """Infer the type of a column from its values."""
    numeric = 0
    for v in values:
        try:
            float(v.replace(",", ""))
            numeric += 1
        except (ValueError, AttributeError):
            pass
    if numeric > len(values) * 0.8:
        return "numeric"
    date_pattern = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}")
    if sum(1 for v in values if date_pattern.match(str(v))) > len(values) * 0.8:
        return "date"
    return "text"
