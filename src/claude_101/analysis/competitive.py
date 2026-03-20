"""Competitive analysis tool — structured comparison matrix builder."""

from __future__ import annotations

from .._utils import _normalize_weights


def _identify_critical_weights(
    weights: dict[str, float],
    delta: float = 0.20,
) -> list[str]:
    """Identify weights where a +/-20% change could flip rankings.

    A weight is "critical" if it is close enough to another weight that
    a 20% swing would make it larger/smaller than its neighbor. This is
    a heuristic for sensitivity analysis.
    """
    items = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
    critical: list[str] = []
    for i in range(len(items) - 1):
        name_a, w_a = items[i]
        name_b, w_b = items[i + 1]
        # If reducing w_a by delta makes it smaller than w_b (or vice-versa)
        if w_a * (1 - delta) < w_b * (1 + delta):
            if name_a not in critical:
                critical.append(name_a)
            if name_b not in critical:
                critical.append(name_b)
    return critical


def _parse_scores(
    scores_str: str, items: list[str], criteria: list[str]
) -> dict[str, dict[str, float | None]]:
    """Parse scores from format: 'item1:c1=8,c2=7;item2:c1=6,c2=9'.

    Returns a nested dict: {item: {criterion: score}}.
    Missing entries get None.
    """
    result: dict[str, dict[str, float | None]] = {
        item: {crit: None for crit in criteria} for item in items
    }

    if not scores_str.strip():
        return result

    # Split by semicolons to get per-item blocks
    item_blocks = [b.strip() for b in scores_str.split(";") if b.strip()]

    for block in item_blocks:
        if ":" not in block:
            continue
        item_part, scores_part = block.split(":", 1)
        item_name = item_part.strip()

        # Find matching item (case-insensitive, partial match)
        matched_item = _find_match(item_name, items)
        if matched_item is None:
            continue

        # Parse individual criterion scores
        score_pairs = [p.strip() for p in scores_part.split(",") if p.strip()]
        for pair in score_pairs:
            if "=" not in pair:
                continue
            crit_part, val_part = pair.split("=", 1)
            crit_name = crit_part.strip()
            matched_crit = _find_match(crit_name, criteria)
            if matched_crit is None:
                continue
            try:
                score_val = float(val_part.strip())
                result[matched_item][matched_crit] = score_val
            except ValueError:
                pass

    return result


def _find_match(query: str, candidates: list[str]) -> str | None:
    """Find the best match for a query string in a list of candidates.

    Tries exact match first, then case-insensitive, then prefix match.
    """
    if query in candidates:
        return query
    lower_query = query.lower()
    for c in candidates:
        if c.lower() == lower_query:
            return c
    for c in candidates:
        if c.lower().startswith(lower_query):
            return c
    for c in candidates:
        if lower_query in c.lower():
            return c
    return None


def _compute_weighted_scores(
    scores: dict[str, dict[str, float | None]],
    weights: dict[str, float],
    criteria: list[str],
) -> dict[str, float | None]:
    """Compute weighted score for each item.

    Returns None for items with any missing score.
    """
    result: dict[str, float | None] = {}
    for item, crit_scores in scores.items():
        missing = any(crit_scores.get(c) is None for c in criteria)
        if missing:
            result[item] = None
        else:
            weighted = sum(
                crit_scores[c] * weights[c]  # type: ignore[operator]
                for c in criteria
            )
            result[item] = round(weighted, 4)
    return result


def _compute_rankings(
    weighted_scores: dict[str, float | None],
) -> list[dict]:
    """Rank items by weighted score (descending)."""
    scorable = [
        (item, score) for item, score in weighted_scores.items() if score is not None
    ]
    if not scorable:
        return []
    sorted_items = sorted(scorable, key=lambda x: x[1], reverse=True)  # type: ignore[arg-type,return-value]
    rankings: list[dict] = []
    for rank, (item, score) in enumerate(sorted_items, 1):
        rankings.append({"item": item, "weighted_score": score, "rank": rank})
    return rankings


def build_comparison_matrix(
    items: str,
    criteria: str,
    weights: str = "",
    scores: str = "",
) -> dict:
    """Build a structured comparison matrix for competitive analysis.

    Args:
        items: Comma-separated list of items to compare (e.g. "Product A, Product B").
        criteria: Comma-separated list of criteria (e.g. "Price, Quality, Support").
        weights: Optional comma-separated numeric weights for each criterion.
            If empty, equal weights are assigned.
        scores: Optional scores in format "Item1:Crit1=8,Crit2=7;Item2:Crit1=6,Crit2=9".
            If empty, returns framework with empty score slots.

    Returns:
        Dictionary with matrix structure, weight analysis, rankings, and sensitivity framework.
    """
    item_list = [i.strip() for i in items.split(",") if i.strip()]
    criteria_list = [c.strip() for c in criteria.split(",") if c.strip()]

    # ── Weights ─────────────────────────────────────────────────
    if weights.strip():
        raw_weights: list[float] = []
        for w in weights.split(","):
            try:
                raw_weights.append(float(w.strip()))
            except ValueError:
                raw_weights.append(1.0)
        # Pad or truncate to match criteria count
        while len(raw_weights) < len(criteria_list):
            raw_weights.append(1.0)
        raw_weights = raw_weights[: len(criteria_list)]
    else:
        raw_weights = [1.0] * len(criteria_list)

    normalized = _normalize_weights(raw_weights)
    weights_map = {c: w for c, w in zip(criteria_list, normalized)}

    # ── Parse scores ────────────────────────────────────────────
    score_matrix = _parse_scores(scores, item_list, criteria_list)

    # ── Build display matrix ────────────────────────────────────
    matrix: dict[str, dict] = {}
    for item in item_list:
        matrix[item] = {}
        for criterion in criteria_list:
            matrix[item][criterion] = {
                "score": score_matrix[item][criterion],
                "max_score": 10,
            }

    # ── Compute weighted scores and rankings ────────────────────
    weighted_scores = _compute_weighted_scores(score_matrix, weights_map, criteria_list)
    rankings = _compute_rankings(weighted_scores)

    # ── Winner ──────────────────────────────────────────────────
    winner = None
    if rankings:
        w = rankings[0]
        margin = (
            round(w["weighted_score"] - rankings[1]["weighted_score"], 4)
            if len(rankings) >= 2
            else w["weighted_score"]
        )
        winner = {"item": w["item"], "score": w["weighted_score"], "margin": margin}

    # ── Sensitivity framework ───────────────────────────────────
    critical = _identify_critical_weights(weights_map)

    result: dict = {
        "items": item_list,
        "criteria": criteria_list,
        "weights": weights_map,
        "matrix": matrix,
        "rankings": rankings,
        "ranking_formula": "weighted_sum = sum(score_i * weight_i)",
        "sensitivity_framework": {
            "description": "Change each weight by +/-20% and re-rank",
            "critical_weights": critical,
        },
    }
    if winner is not None:
        result["winner"] = winner

    return result
