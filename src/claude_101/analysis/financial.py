"""Financial analysis tool — real margin, growth, and burn-rate calculations."""

from __future__ import annotations

from claude_101._utils import parse_csv


def _to_float(value: str) -> float | None:
    """Try converting a string to float, stripping $, commas, and whitespace."""
    cleaned = value.strip().replace("$", "").replace(",", "").replace(" ", "")
    if not cleaned or cleaned == "-":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _growth_rates(values: list[float]) -> list[float | None]:
    """Calculate period-over-period growth rates."""
    rates: list[float | None] = []
    for i in range(1, len(values)):
        if values[i - 1] != 0:
            rates.append(round((values[i] - values[i - 1]) / abs(values[i - 1]) * 100, 2))
        else:
            rates.append(None)
    return rates


def _trend(values: list[float]) -> str:
    """Detect trend from the last two values."""
    if len(values) < 2:
        return "insufficient_data"
    diff = values[-1] - values[-2]
    pct = abs(diff / values[-2]) * 100 if values[-2] != 0 else 100
    if pct < 2:
        return "stable"
    return "up" if diff > 0 else "down"


def _margins(numerators: list[float], denominators: list[float]) -> list[float | None]:
    """Calculate margin percentages."""
    result: list[float | None] = []
    for n, d in zip(numerators, denominators):
        if d != 0:
            result.append(round(n / d * 100, 2))
        else:
            result.append(None)
    return result


def _find_metric_row(
    row_labels: list[str],
    rows_data: dict[str, list[float]],
    *candidates: str,
) -> list[float] | None:
    """Find a metric row by trying multiple name candidates (case-insensitive)."""
    for candidate in candidates:
        cl = candidate.lower()
        for label in row_labels:
            if cl in label.lower():
                return rows_data[label]
    return None


def analyze_financials(data: str, period: str = "quarterly") -> dict:
    """Analyze financial data with real calculations.

    Expects CSV where:
    - First column contains metric names (Revenue, COGS, Operating Expenses, etc.)
    - Subsequent columns are period values (Q1, Q2, ... or Year 1, Year 2, ...)

    Args:
        data: CSV string with financial data.
        period: Period type — "quarterly", "monthly", or "annual".

    Returns:
        Dictionary with metrics, ratios, burn rate, and summary.
    """
    headers, rows = parse_csv(data)
    if not headers or not rows:
        return {"period": period, "periods_analyzed": 0, "metrics": {}}

    period_headers = headers[1:]  # Skip the metric-name column
    num_periods = len(period_headers)

    # ── Parse rows into metric -> values mapping ───────────────
    row_labels: list[str] = []
    rows_data: dict[str, list[float]] = {}
    for row in rows:
        if not row:
            continue
        label = row[0].strip()
        if not label:
            continue
        values: list[float] = []
        for cell in row[1:]:
            v = _to_float(cell)
            values.append(v if v is not None else 0.0)
        # Pad to match period count
        while len(values) < num_periods:
            values.append(0.0)
        values = values[:num_periods]
        row_labels.append(label)
        rows_data[label] = values

    # ── Identify key metrics ───────────────────────────────────
    revenue = _find_metric_row(
        row_labels, rows_data, "revenue", "sales", "income", "total revenue",
    )
    cogs = _find_metric_row(
        row_labels, rows_data, "cogs", "cost of goods", "cost of revenue",
        "cost of sales", "direct costs",
    )
    opex = _find_metric_row(
        row_labels, rows_data, "operating expenses", "opex", "operating costs",
        "total expenses", "expenses",
    )
    net_income = _find_metric_row(
        row_labels, rows_data, "net income", "net profit", "profit",
        "net earnings", "bottom line",
    )

    # ── Derived metrics ─────────────────────────────────────────
    if revenue is None:
        revenue = [0.0] * num_periods

    # Gross profit = Revenue - COGS
    if cogs is not None:
        gross_profit = [r - c for r, c in zip(revenue, cogs)]
    else:
        gross_profit = list(revenue)  # If no COGS, gross = revenue

    # Total costs = COGS + OPEX (or just whichever is available)
    costs: list[float] = [0.0] * num_periods
    if cogs is not None:
        costs = [c + o for c, o in zip(costs, cogs)]
    if opex is not None:
        costs = [c + o for c, o in zip(costs, opex)]

    # Operating profit = Revenue - total costs
    operating_profit = [r - c for r, c in zip(revenue, costs)]

    # Net profit: use provided or fall back to operating profit
    if net_income is None:
        net_income = operating_profit

    # ── Ratios ──────────────────────────────────────────────────
    gross_margins = _margins(gross_profit, revenue)
    operating_margins = _margins(operating_profit, revenue)
    profit_margins = _margins(net_income, revenue)

    # ── Growth rates ────────────────────────────────────────────
    revenue_growth = _growth_rates(revenue)
    cost_growth = _growth_rates(costs)
    _growth_rates(net_income)  # computed for completeness

    # ── Burn rate (applicable when costs > revenue) ─────────────
    burn_rate_result: dict = {}
    if num_periods > 0:
        latest_revenue = revenue[-1]
        latest_costs = costs[-1]
        if latest_costs > latest_revenue:
            monthly_burn = latest_costs - latest_revenue
            if period == "quarterly":
                monthly_burn = monthly_burn / 3
            elif period == "annual":
                monthly_burn = monthly_burn / 12
            # Estimate runway: assume some cash reserve (sum of all revenues as proxy)
            total_cash = sum(max(0, r - c) for r, c in zip(revenue, costs))
            runway = round(total_cash / monthly_burn, 1) if monthly_burn > 0 else 0
            burn_rate_result = {
                "monthly": round(monthly_burn, 2),
                "runway_months": runway,
            }

    # ── Trend detection ─────────────────────────────────────────
    rev_trend = _trend(revenue)
    margin_trend = "stable"
    valid_margins = [m for m in profit_margins if m is not None]
    if len(valid_margins) >= 2:
        margin_trend = _trend(valid_margins)

    # Key concern
    key_concern = "None identified"
    if rev_trend == "down":
        key_concern = "Revenue is declining"
    elif margin_trend == "down":
        key_concern = "Profit margins are shrinking"
    elif burn_rate_result:
        runway = burn_rate_result.get("runway_months", 0)
        if runway < 12:
            key_concern = f"Burn rate high — estimated {runway} months runway"

    return {
        "period": period,
        "periods_analyzed": num_periods,
        "metrics": {
            "revenue": {
                "values": revenue,
                "growth_rates": revenue_growth,
                "trend": rev_trend,
            },
            "costs": {
                "values": costs,
                "growth_rates": cost_growth,
            },
            "profit": {
                "values": [round(v, 2) for v in net_income],
                "margins": profit_margins,
            },
        },
        "ratios": {
            "gross_margin": gross_margins,
            "operating_margin": operating_margins,
            "profit_margin": profit_margins,
        },
        "burn_rate": burn_rate_result,
        "summary": {
            "revenue_trend": rev_trend,
            "margin_trend": margin_trend,
            "key_concern": key_concern,
        },
    }
