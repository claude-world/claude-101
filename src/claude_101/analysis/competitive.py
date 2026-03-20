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


def build_comparison_matrix(
    items: str,
    criteria: str,
    weights: str = "",
) -> dict:
    """Build a structured comparison matrix for competitive analysis.

    Args:
        items: Comma-separated list of items to compare (e.g. "Product A, Product B").
        criteria: Comma-separated list of criteria (e.g. "Price, Quality, Support").
        weights: Optional comma-separated numeric weights for each criterion.
            If empty, equal weights are assigned.

    Returns:
        Dictionary with matrix structure, weight analysis, and sensitivity framework.
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

    # ── Score matrix (empty slots) ──────────────────────────────
    matrix: dict[str, dict] = {}
    for item in item_list:
        matrix[item] = {}
        for criterion in criteria_list:
            matrix[item][criterion] = {"score": None, "max_score": 10}

    # ── Sensitivity framework ───────────────────────────────────
    critical = _identify_critical_weights(weights_map)

    return {
        "items": item_list,
        "criteria": criteria_list,
        "weights": weights_map,
        "matrix": matrix,
        "ranking_formula": "weighted_sum = sum(score_i * weight_i)",
        "sensitivity_framework": {
            "description": "Change each weight by +/-20% and re-rank",
            "critical_weights": critical,
        },
    }
