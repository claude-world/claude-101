"""Document summarization tool — real extractive summarization."""

from __future__ import annotations

import re
import statistics

from .._utils import (
    flesch_score,
    flesch_grade,
    keyword_frequency,
    reading_time,
    sentence_tokenize,
    word_count,
)


def _keyword_density(sentence: str, keyword_set: set[str]) -> float:
    """Return raw keyword density for a sentence (0.0–1.0)."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
    if not words:
        return 0.0
    kw_count = sum(1 for w in words if w in keyword_set)
    return kw_count / len(words)


def _score_sentence(
    sentence: str,
    position: int,
    total_sentences: int,
    keyword_set: set[str],
    paragraph_boundaries: set[int],
    max_keyword_density: float,
) -> float:
    """Score a sentence for extractive summarization.

    Factors:
        - Position: strong bonus for first and last sentences only;
          modest bonus for paragraph-opening sentences.
        - Keyword density: normalized relative to the densest sentence
          so only genuinely keyword-rich sentences score high.
        - Length preference: aggressive penalty for very short sentences;
          mild penalty for very long ones; sweet spot 10-30 words.
    """
    score = 0.0

    # ── Position score (0–3) ────────────────────────────────────
    # Only the very first and very last sentences get a strong boost.
    if position == 0:
        score += 3.0
    elif position == total_sentences - 1:
        score += 2.0
    elif position in paragraph_boundaries:
        score += 0.5  # Modest boost for paragraph openers
    # No bonus for other positions.

    # ── Keyword density (0–3), normalized ───────────────────────
    raw_density = _keyword_density(sentence, keyword_set)
    if max_keyword_density > 0:
        normalized = raw_density / max_keyword_density
    else:
        normalized = 0.0
    score += normalized * 3.0

    # ── Length preference (−2 to +2) ────────────────────────────
    wc = len(sentence.split())
    if wc < 4:
        score -= 2.0  # Aggressively penalize very short fragments
    elif wc < 8:
        score -= 1.0  # Penalize short sentences
    elif 10 <= wc <= 30:
        score += 2.0  # Ideal length
    elif 8 <= wc < 10 or 30 < wc <= 40:
        score += 0.5  # Acceptable
    # wc > 40 gets no bonus (0)

    return round(score, 4)


def summarize_document(text: str, max_sentences: int = 5) -> dict:
    """Produce an extractive summary with readability metrics.

    Args:
        text: Document text to summarize.
        max_sentences: Maximum number of key sentences to extract.

    Returns:
        Dictionary with word count, readability, key sentences, keywords, etc.
    """
    sentences = sentence_tokenize(text)
    wc = word_count(text)
    sc = len(sentences)

    # ── Readability ─────────────────────────────────────────────
    f_score = flesch_score(text)
    f_grade = flesch_grade(f_score)

    # ── Keywords ────────────────────────────────────────────────
    kw_list = keyword_frequency(text, top_n=15)
    keyword_set = {w for w, _ in kw_list}

    # ── Identify paragraph boundaries ──────────────────────────
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraph_boundaries: set[int] = set()
    sent_idx = 0
    for para in paragraphs:
        paragraph_boundaries.add(sent_idx)
        para_sents = sentence_tokenize(para)
        sent_idx += len(para_sents)

    # ── Compute max keyword density across all sentences ───────
    densities = [_keyword_density(s, keyword_set) for s in sentences]
    max_kw_density = max(densities) if densities else 0.0

    # ── Score sentences ─────────────────────────────────────────
    scored: list[dict] = []
    for i, sent in enumerate(sentences):
        s = _score_sentence(
            sent,
            i,
            sc,
            keyword_set,
            paragraph_boundaries,
            max_kw_density,
        )
        scored.append({"sentence": sent, "position": i, "score": s})

    # ── Filter by median threshold ──────────────────────────────
    # Only sentences scoring above the median are candidates for
    # the summary, so low-value sentences never appear even if
    # max_sentences is generous.
    all_scores = [entry["score"] for entry in scored]
    if len(all_scores) >= 2:
        median_score = statistics.median(all_scores)
    else:
        median_score = 0.0

    above_median = [entry for entry in scored if entry["score"] > median_score]

    # If nothing is above median (e.g. all identical scores), fall
    # back to all sentences so we still return something.
    candidates = above_median if above_median else scored

    # Select top sentences (capped by max_sentences), preserve
    # original document order.
    top = sorted(candidates, key=lambda x: x["score"], reverse=True)[:max_sentences]
    key_sentences = sorted(top, key=lambda x: x["position"])

    # ── Summary ratio ──────────────────────────────────────────
    summary_words = sum(word_count(s["sentence"]) for s in key_sentences)
    summary_ratio = round(summary_words / wc, 4) if wc > 0 else 0.0

    return {
        "word_count": wc,
        "sentence_count": sc,
        "reading_time_minutes": reading_time(text),
        "flesch_score": f_score,
        "flesch_grade": f_grade,
        "key_sentences": key_sentences,
        "keywords": [{"word": w, "count": c} for w, c in kw_list[:10]],
        "summary_ratio": summary_ratio,
    }
