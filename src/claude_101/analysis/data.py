"""Data analysis tool — CSV/JSON parsing with real statistics."""

from __future__ import annotations

import math
from collections import Counter

from claude_101._utils import (
    basic_stats,
    infer_column_type,
    parse_csv,
    parse_json_data,
)


def _pearson_correlation(xs: list[float], ys: list[float]) -> float:
    """Calculate Pearson correlation coefficient between two lists."""
    n = len(xs)
    if n < 3:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    std_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if std_x == 0 or std_y == 0:
        return 0.0
    return round(cov / (std_x * std_y), 4)


def _to_float(value: str) -> float | None:
    """Try converting a string to float, stripping commas."""
    try:
        return float(value.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def analyze_data(
    data: str,
    format: str = "csv",
    operations: str = "summary",
) -> dict:
    """Analyze CSV or JSON data with real statistics.

    Args:
        data: Raw data string (CSV or JSON).
        format: Data format — "csv" or "json".
        operations: Comma-separated list of operations:
            "summary" (default), "correlations", "outliers", "all".

    Returns:
        Dictionary with column analysis, correlations, outliers, etc.
    """
    ops = {o.strip().lower() for o in operations.split(",")}
    if "all" in ops:
        ops = {"summary", "correlations", "outliers"}

    # ── Parse data ──────────────────────────────────────────────
    if format.lower() == "json":
        records = parse_json_data(data)
        if not records:
            return {"format": "json", "row_count": 0, "column_count": 0, "columns": []}
        headers = list(records[0].keys())
        rows = [[str(r.get(h, "")) for h in headers] for r in records]
    else:
        headers, rows = parse_csv(data)
        if not headers:
            return {"format": "csv", "row_count": 0, "column_count": 0, "columns": []}

    row_count = len(rows)
    col_count = len(headers)

    # ── Per-column analysis ─────────────────────────────────────
    columns_info: list[dict] = []
    numeric_columns: dict[str, list[float]] = {}

    for col_idx, col_name in enumerate(headers):
        raw_values = [row[col_idx] if col_idx < len(row) else "" for row in rows]
        non_empty = [v for v in raw_values if v.strip()]
        missing_count = row_count - len(non_empty)
        col_type = infer_column_type(non_empty) if non_empty else "text"

        col_info: dict = {
            "name": col_name,
            "type": col_type,
            "sample_values": raw_values[:5],
            "missing_count": missing_count,
        }

        if col_type == "numeric":
            float_vals = [v for v in (_to_float(s) for s in non_empty) if v is not None]
            stats = basic_stats(float_vals)
            col_info["stats"] = stats
            numeric_columns[col_name] = float_vals
        else:
            counter = Counter(non_empty)
            col_info["stats"] = {
                "unique_count": len(counter),
                "most_common": counter.most_common(5),
            }

        columns_info.append(col_info)

    result: dict = {
        "format": format.lower(),
        "row_count": row_count,
        "column_count": col_count,
        "columns": columns_info,
        "operations_performed": sorted(ops),
    }

    # ── Correlations ────────────────────────────────────────────
    correlations: list[dict] = []
    if "correlations" in ops or "summary" in ops:
        num_cols = list(numeric_columns.keys())
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                col_a, col_b = num_cols[i], num_cols[j]
                vals_a, vals_b = numeric_columns[col_a], numeric_columns[col_b]
                # Align lengths (use minimum)
                min_len = min(len(vals_a), len(vals_b))
                if min_len >= 3:
                    r = _pearson_correlation(vals_a[:min_len], vals_b[:min_len])
                    correlations.append({
                        "column_a": col_a,
                        "column_b": col_b,
                        "pearson_r": r,
                        "strength": (
                            "strong" if abs(r) >= 0.7
                            else "moderate" if abs(r) >= 0.4
                            else "weak"
                        ),
                    })
    result["correlations"] = correlations

    # ── Outliers ────────────────────────────────────────────────
    outliers: dict[str, list] = {}
    if "outliers" in ops or "summary" in ops:
        for col_name, float_vals in numeric_columns.items():
            stats = basic_stats(float_vals)
            if "outliers" in stats and stats["outliers"]:
                outliers[col_name] = stats["outliers"]
    result["outliers"] = outliers

    return result
