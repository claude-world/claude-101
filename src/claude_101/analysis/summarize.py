"""Document summarization tool — real extractive summarization."""

from __future__ import annotations

import re

from .._utils import (
    flesch_score,
    flesch_grade,
    keyword_frequency,
    reading_time,
    sentence_tokenize,
    word_count,
)


def _score_sentence(
    sentence: str,
    position: int,
    total_sentences: int,
    keyword_set: set[str],
    paragraph_boundaries: set[int],
) -> float:
    """Score a sentence for extractive summarization.

    Factors:
        - Position: first and last sentences in text get a boost;
          first/last sentences of each paragraph get a smaller boost.
        - Keyword density: ratio of keywords present in the sentence.
        - Length preference: prefer medium-length sentences (10-30 words).
    """
    score = 0.0

    # ── Position score (0–3) ────────────────────────────────────
    if position == 0:
        score += 3.0  # Very first sentence
    elif position == total_sentences - 1:
        score += 2.0  # Very last sentence
    elif position in paragraph_boundaries:
        score += 1.5  # First sentence of a paragraph
    elif (position + 1) in paragraph_boundaries or position == total_sentences - 1:
        score += 1.0  # Last sentence of a paragraph

    # ── Keyword density (0–3) ──────────────────────────────────
    words = re.findall(r"\b[a-zA-Z]{3,}\b", sentence.lower())
    if words:
        kw_count = sum(1 for w in words if w in keyword_set)
        density = kw_count / len(words)
        score += density * 3.0

    # ── Length preference (0–2) ─────────────────────────────────
    wc = len(sentence.split())
    if 10 <= wc <= 30:
        score += 2.0  # Ideal length
    elif 6 <= wc <= 40:
        score += 1.0  # Acceptable
    # Very short or very long sentences get no length bonus

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

    # ── Score sentences ─────────────────────────────────────────
    scored: list[dict] = []
    for i, sent in enumerate(sentences):
        s = _score_sentence(sent, i, sc, keyword_set, paragraph_boundaries)
        scored.append({"sentence": sent, "position": i, "score": s})

    # Select top sentences, preserve original order
    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:max_sentences]
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
