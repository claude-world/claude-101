"""Survey analysis tool — real response statistics and NPS calculation."""

from __future__ import annotations

import statistics
from collections import Counter

from .._utils import parse_csv


def _to_int(value: str) -> int | None:
    """Try converting a string to int."""
    try:
        return int(float(value.strip()))
    except (ValueError, TypeError):
        return None


def _is_id_column(header: str, values: list[str]) -> bool:
    """Heuristic: column is a respondent ID if header suggests it or all values unique."""
    id_keywords = {"id", "respondent", "resp", "participant", "user", "uid", "#"}
    if header.strip().lower() in id_keywords:
        return True
    # All unique non-empty values suggest an ID column
    non_empty = [v for v in values if v.strip()]
    return len(non_empty) == len(set(non_empty)) and len(non_empty) > 1


def _compute_nps(all_scores: list[int], scale_max: int) -> dict:
    """Compute Net Promoter Score.

    For scale_max=5:  promoters=5, passives=4, detractors=1-3
    For scale_max=10: promoters=9-10, passives=7-8, detractors=0-6
    """
    if not all_scores:
        return {
            "score": 0.0,
            "promoters": 0,
            "passives": 0,
            "detractors": 0,
            "promoter_pct": 0.0,
            "detractor_pct": 0.0,
        }

    promoters = 0
    passives = 0
    detractors = 0

    for s in all_scores:
        if scale_max <= 5:
            if s >= 5:
                promoters += 1
            elif s == 4:
                passives += 1
            else:
                detractors += 1
        else:  # scale_max >= 6 (typically 10)
            if s >= 9:
                promoters += 1
            elif s >= 7:
                passives += 1
            else:
                detractors += 1

    total = len(all_scores)
    promoter_pct = round(promoters / total * 100, 1)
    detractor_pct = round(detractors / total * 100, 1)

    return {
        "score": round(promoter_pct - detractor_pct, 1),
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "promoter_pct": promoter_pct,
        "detractor_pct": detractor_pct,
    }


def analyze_survey(data: str, scale_max: int = 5) -> dict:
    """Analyze survey response data.

    Args:
        data: CSV string where first row = headers (question names),
            subsequent rows = responses. First column may be respondent ID.
        scale_max: Maximum value on the Likert scale (5 or 10).

    Returns:
        Dictionary with per-question stats, distributions, NPS, and overall
        satisfaction.
    """
    headers, rows = parse_csv(data)
    if not headers or not rows:
        return {"response_count": 0, "questions": []}

    # Detect and skip ID column
    col_values = {
        i: [row[i] if i < len(row) else "" for row in rows] for i in range(len(headers))
    }
    question_indices = [
        i for i in range(len(headers)) if not _is_id_column(headers[i], col_values[i])
    ]

    response_count = len(rows)
    midpoint = scale_max / 2.0

    # ── Identify the NPS / recommend question column ────────────
    nps_keywords = {"recommend", "nps", "likelihood", "refer"}
    nps_col_idx: int | None = None
    for col_idx in question_indices:
        if any(kw in headers[col_idx].strip().lower() for kw in nps_keywords):
            nps_col_idx = col_idx
            break
    # Fallback: use the last numeric question column (common convention)
    if nps_col_idx is None and question_indices:
        # We'll resolve this after identifying numeric columns below
        pass

    questions_result: list[dict] = []
    all_scores: list[int] = []
    numeric_question_indices: list[int] = []

    for col_idx in question_indices:
        question_name = headers[col_idx]
        raw_values = col_values[col_idx]
        int_values = [v for v in (_to_int(s) for s in raw_values) if v is not None]

        if not int_values:
            # Non-numeric question — skip for stats
            continue

        # Clamp to valid scale range
        int_values = [max(1, min(scale_max, v)) for v in int_values]
        all_scores.extend(int_values)
        numeric_question_indices.append(col_idx)

        float_vals = [float(v) for v in int_values]
        mean = round(statistics.mean(float_vals), 2)
        median = round(statistics.median(float_vals), 2)
        stdev = round(statistics.stdev(float_vals), 2) if len(float_vals) >= 2 else 0.0

        # Distribution: count per scale point
        counter = Counter(int_values)
        distribution = {str(k): counter.get(k, 0) for k in range(1, scale_max + 1)}

        # Satisfaction: % scoring above midpoint
        above_mid = sum(1 for v in int_values if v > midpoint)
        satisfaction_pct = round(above_mid / len(int_values) * 100, 1)

        questions_result.append(
            {
                "question": question_name,
                "stats": {"mean": mean, "median": median, "stdev": stdev},
                "distribution": distribution,
                "satisfaction_pct": satisfaction_pct,
            }
        )

    # ── NPS ─────────────────────────────────────────────────────
    # Use only the identified recommend/NPS column, or fall back to the last
    # numeric question column.
    if nps_col_idx is None and numeric_question_indices:
        nps_col_idx = numeric_question_indices[-1]

    nps_scores: list[int] = []
    if nps_col_idx is not None:
        raw_nps = col_values[nps_col_idx]
        nps_scores = [v for v in (_to_int(s) for s in raw_nps) if v is not None]
        nps_scores = [max(1, min(scale_max, v)) for v in nps_scores]

    nps = _compute_nps(nps_scores, scale_max)

    # ── Overall satisfaction ────────────────────────────────────
    overall_satisfaction = 0.0
    if all_scores:
        above_mid_total = sum(1 for s in all_scores if s > midpoint)
        overall_satisfaction = round(above_mid_total / len(all_scores) * 100, 1)

    return {
        "response_count": response_count,
        "questions": questions_result,
        "nps": nps,
        "overall_satisfaction": overall_satisfaction,
        "cross_tab_framework": "Group by [demographic column] to compare segments",
    }
