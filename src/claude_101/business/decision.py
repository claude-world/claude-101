"""Decision evaluation tool — weighted scoring matrix with sensitivity analysis."""

from __future__ import annotations

from .._utils import _normalize_weights


def _parse_scores(
    scores_str: str, options: list[str], criteria: list[str]
) -> dict[str, dict[str, float]]:
    """Parse scores from format: 'opt1:c1=8,c2=7;opt2:c1=6,c2=9'.

    Returns a nested dict: {option: {criterion: score}}.
    Missing entries get None.
    """
    result: dict[str, dict[str, float | None]] = {
        opt: {crit: None for crit in criteria} for opt in options
    }

    if not scores_str.strip():
        return result  # type: ignore[return-value]

    # Split by semicolons to get per-option blocks
    option_blocks = [b.strip() for b in scores_str.split(";") if b.strip()]

    for block in option_blocks:
        # Split on first colon to get option name and scores
        if ":" not in block:
            continue
        opt_part, scores_part = block.split(":", 1)
        opt_name = opt_part.strip()

        # Find matching option (case-insensitive, partial match)
        matched_opt = _find_match(opt_name, options)
        if matched_opt is None:
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
                result[matched_opt][matched_crit] = score_val
            except ValueError:
                pass

    return result  # type: ignore[return-value]


def _find_match(query: str, candidates: list[str]) -> str | None:
    """Find the best match for a query string in a list of candidates.

    Tries exact match first, then case-insensitive, then prefix match.
    """
    # Exact match
    if query in candidates:
        return query

    # Case-insensitive
    lower_query = query.lower()
    for c in candidates:
        if c.lower() == lower_query:
            return c

    # Prefix match (case-insensitive)
    for c in candidates:
        if c.lower().startswith(lower_query):
            return c

    # Substring match
    for c in candidates:
        if lower_query in c.lower():
            return c

    return None


def _compute_weighted_scores(
    scores: dict[str, dict[str, float | None]],
    weights: dict[str, float],
    criteria: list[str],
) -> dict[str, float | None]:
    """Compute weighted score for each option.

    Returns None for options with any missing score.
    """
    result: dict[str, float | None] = {}

    for option, crit_scores in scores.items():
        missing = any(crit_scores.get(c) is None for c in criteria)
        if missing:
            result[option] = None
        else:
            weighted = sum(
                crit_scores[c] * weights[c]  # type: ignore[operator]
                for c in criteria
            )
            result[option] = round(weighted, 4)

    return result


def _compute_rankings(
    weighted_scores: dict[str, float | None],
) -> list[dict]:
    """Rank options by weighted score (descending)."""
    # Filter out options with no score
    scorable = [
        (opt, score) for opt, score in weighted_scores.items() if score is not None
    ]

    if not scorable:
        return []

    # Sort by score descending
    sorted_opts = sorted(scorable, key=lambda x: x[1], reverse=True)  # type: ignore[arg-type,return-value]

    rankings: list[dict] = []
    for rank, (opt, score) in enumerate(sorted_opts, 1):
        rankings.append(
            {
                "option": opt,
                "weighted_score": score,
                "rank": rank,
            }
        )

    return rankings


def _compute_winner(rankings: list[dict]) -> dict | None:
    """Identify the winner and margin over second place."""
    if not rankings:
        return None

    winner = rankings[0]
    if len(rankings) >= 2:
        margin = round(winner["weighted_score"] - rankings[1]["weighted_score"], 4)
    else:
        margin = winner["weighted_score"]

    return {
        "option": winner["option"],
        "score": winner["weighted_score"],
        "margin": margin,
    }


def _sensitivity_analysis(
    scores: dict[str, dict[str, float | None]],
    weights: dict[str, float],
    criteria: list[str],
    rankings: list[dict],
) -> list[dict]:
    """For each criterion, compute how much the weight would need to change
    to flip the winner.

    This uses a linear search approach: for the top-ranked option and the
    second-ranked option, we compute the weight delta needed on each
    criterion to make the second option's weighted score exceed the first's.
    """
    if len(rankings) < 2:
        return []

    first = rankings[0]
    second = rankings[1]

    first_scores = scores[first["option"]]
    second_scores = scores[second["option"]]

    # Check if any scores are missing
    for c in criteria:
        if first_scores.get(c) is None or second_scores.get(c) is None:
            return [
                {
                    "criterion": c,
                    "weight_change_to_flip": None,
                    "description": "Cannot compute — scores are missing",
                }
                for c in criteria
            ]

    analysis: list[dict] = []

    for crit in criteria:
        score_diff = first_scores[crit] - second_scores[crit]  # type: ignore[operator]

        if score_diff == 0:
            # This criterion doesn't differentiate the top two
            analysis.append(
                {
                    "criterion": crit,
                    "weight_change_to_flip": None,
                    "description": f"Both options score equally on '{crit}' — changing its weight has no effect on the ranking",
                }
            )
            continue

        # Current weighted advantage of first over second
        current_gap = first["weighted_score"] - second["weighted_score"]

        # The advantage from this criterion alone:
        # advantage_from_crit = weights[crit] * score_diff
        # If score_diff > 0 (first scores higher on this criterion),
        # reducing the weight would hurt first's lead.
        # We need: new_gap = current_gap - delta_w * score_diff <= 0
        # => delta_w >= current_gap / score_diff

        if score_diff > 0:
            # First option scores higher: need to reduce this weight
            delta_needed = current_gap / score_diff
            direction = "decrease"
        else:
            # Second option scores higher: need to increase this weight
            delta_needed = current_gap / abs(score_diff)
            direction = "increase"

        delta_needed = round(delta_needed, 4)

        # Express as percentage of current weight
        current_weight = weights[crit]
        if current_weight > 0:
            pct_change = round(delta_needed / current_weight * 100, 1)
            description = (
                f"Would need to {direction} the weight of '{crit}' by {delta_needed:.4f} "
                f"({pct_change}% of current weight {current_weight:.4f}) to flip "
                f"'{first['option']}' and '{second['option']}'"
            )
        else:
            description = f"Weight is currently 0; would need to set it to {delta_needed:.4f} to flip the ranking"

        analysis.append(
            {
                "criterion": crit,
                "weight_change_to_flip": delta_needed,
                "description": description,
            }
        )

    return analysis


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def evaluate_decision(
    options: str,
    criteria: str,
    weights: str = "",
    scores: str = "",
) -> dict:
    """Evaluate a decision using weighted scoring with sensitivity analysis.

    Args:
        options: Comma-separated list of options to evaluate.
        criteria: Comma-separated list of evaluation criteria.
        weights: Optional comma-separated numeric weights for each criterion.
            If empty, equal weights are assigned.
        scores: Optional scores in format 'opt1:c1=8,c2=7;opt2:c1=6,c2=9'.
            If empty, returns framework with empty score slots.

    Returns:
        Dictionary with options, criteria, weights, score matrix,
        rankings, winner, and sensitivity analysis.
    """
    option_list = [o.strip() for o in options.split(",") if o.strip()]
    criteria_list = [c.strip() for c in criteria.split(",") if c.strip()]

    if not option_list:
        option_list = ["Option A", "Option B"]
    if not criteria_list:
        criteria_list = ["Cost", "Quality", "Timeline"]

    # ── Parse and normalize weights ──────────────────────────────
    if weights.strip():
        raw_weights: list[float] = []
        for w in weights.split(","):
            try:
                raw_weights.append(float(w.strip()))
            except ValueError:
                raw_weights.append(1.0)
        # Pad or truncate
        while len(raw_weights) < len(criteria_list):
            raw_weights.append(1.0)
        raw_weights = raw_weights[: len(criteria_list)]
    else:
        raw_weights = [1.0] * len(criteria_list)

    normalized = _normalize_weights(raw_weights)
    weights_map = {c: w for c, w in zip(criteria_list, normalized)}

    # ── Parse scores ─────────────────────────────────────────────
    score_matrix = _parse_scores(scores, option_list, criteria_list)

    # ── Compute weighted scores and rankings ─────────────────────
    weighted_scores = _compute_weighted_scores(score_matrix, weights_map, criteria_list)
    rankings = _compute_rankings(weighted_scores)
    winner = _compute_winner(rankings)

    # ── Sensitivity analysis ─────────────────────────────────────
    sensitivity = _sensitivity_analysis(
        score_matrix, weights_map, criteria_list, rankings
    )

    return {
        "options": option_list,
        "criteria": criteria_list,
        "weights": weights_map,
        "scores": score_matrix,
        "rankings": rankings,
        "winner": winner,
        "sensitivity_analysis": sensitivity,
    }
