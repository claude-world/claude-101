"""Architecture Decision Record (ADR) generator — Michael Nygard format."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any


# ── Trade-off criteria ───────────────────────────────────────────────────────

_DEFAULT_CRITERIA = ["Performance", "Maintainability", "Cost", "Complexity", "Risk"]


def _assess_option(option_name: str, criteria: list[str]) -> dict[str, str]:
    """Auto-generate a trade-off assessment for an option.

    Uses simple heuristics based on common option name patterns:
    - Options mentioning "simple", "existing", "monolith" → lower complexity, higher maintainability
    - Options mentioning "new", "custom", "build" → higher complexity, higher performance
    - Options mentioning "cloud", "managed", "saas" → lower complexity, higher cost
    - Options mentioning "open-source", "free" → lower cost
    """
    name_lower = option_name.lower()
    assessment: dict[str, str] = {}

    for criterion in criteria:
        crit_lower = criterion.lower()

        if crit_lower == "performance":
            if any(kw in name_lower for kw in ("custom", "optimized", "native", "rust", "go", "c++")):
                assessment[criterion] = "high"
            elif any(kw in name_lower for kw in ("simple", "basic", "script")):
                assessment[criterion] = "low"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "maintainability":
            if any(kw in name_lower for kw in ("standard", "existing", "managed", "saas", "convention")):
                assessment[criterion] = "high"
            elif any(kw in name_lower for kw in ("custom", "complex", "novel")):
                assessment[criterion] = "low"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "cost":
            if any(kw in name_lower for kw in ("free", "open-source", "oss", "existing", "self-host")):
                assessment[criterion] = "low"
            elif any(kw in name_lower for kw in ("cloud", "managed", "saas", "enterprise", "commercial")):
                assessment[criterion] = "high"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "complexity":
            if any(kw in name_lower for kw in ("simple", "existing", "monolith", "basic", "standard")):
                assessment[criterion] = "low"
            elif any(kw in name_lower for kw in ("microservice", "distributed", "custom", "novel")):
                assessment[criterion] = "high"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "risk":
            if any(kw in name_lower for kw in ("proven", "standard", "existing", "stable", "managed")):
                assessment[criterion] = "low"
            elif any(kw in name_lower for kw in ("new", "experimental", "alpha", "beta", "novel", "custom")):
                assessment[criterion] = "high"
            else:
                assessment[criterion] = "medium"

        else:
            assessment[criterion] = "medium"

    return assessment


def _generate_pros_cons(option_name: str) -> tuple[list[str], list[str]]:
    """Auto-generate pros and cons based on option name heuristics."""
    name_lower = option_name.lower()
    pros: list[str] = []
    cons: list[str] = []

    # Simple / existing
    if any(kw in name_lower for kw in ("simple", "existing", "current")):
        pros.extend(["Low learning curve", "Already integrated with existing systems", "Minimal migration effort"])
        cons.extend(["May not scale well", "Limited feature set", "Technical debt may accumulate"])

    # Cloud / managed
    elif any(kw in name_lower for kw in ("cloud", "managed", "saas", "serverless")):
        pros.extend(["No infrastructure management", "Built-in scaling", "Vendor-provided reliability"])
        cons.extend(["Vendor lock-in risk", "Ongoing costs may grow", "Limited customization"])

    # Open source
    elif any(kw in name_lower for kw in ("open-source", "oss", "open source")):
        pros.extend(["No licensing costs", "Community support", "Full source access for customization"])
        cons.extend(["Maintenance burden on team", "Community support may be inconsistent", "Security patches are team's responsibility"])

    # Custom / build
    elif any(kw in name_lower for kw in ("custom", "build", "in-house", "homegrown")):
        pros.extend(["Tailored to exact requirements", "Full control over implementation", "No external dependencies"])
        cons.extend(["High development effort", "Ongoing maintenance burden", "Risk of reinventing the wheel"])

    # Microservice
    elif any(kw in name_lower for kw in ("microservice", "distributed", "event-driven")):
        pros.extend(["Independent scaling", "Technology diversity per service", "Team autonomy"])
        cons.extend(["Operational complexity", "Network latency overhead", "Distributed debugging difficulty"])

    # Monolith
    elif any(kw in name_lower for kw in ("monolith", "monolithic", "unified")):
        pros.extend(["Simple deployment", "Easy debugging", "No network overhead between components"])
        cons.extend(["Scaling constraints", "Technology lock-in", "Deployment coupling"])

    # Generic fallback
    else:
        pros.extend([f"Addresses the stated requirements", "Feasible with current resources"])
        cons.extend([f"Trade-offs need further evaluation", "May require additional research"])

    return pros, cons


def _infer_consequences(options: list[dict[str, Any]], decision: str) -> dict[str, list[str]]:
    """Infer consequences based on the selected option."""
    positive: list[str] = []
    negative: list[str] = []
    neutral: list[str] = []

    # Find the selected option
    selected = None
    for opt in options:
        if decision and opt["name"].lower() in decision.lower():
            selected = opt
            break
    if selected is None and options:
        selected = options[0]

    if selected:
        positive = [p for p in selected.get("pros", [])[:2]]
        negative = [c for c in selected.get("cons", [])[:2]]
    else:
        positive = ["Addresses the identified need"]
        negative = ["Requires implementation effort"]

    neutral.append("Team will need to adapt to the chosen approach")
    neutral.append("Documentation and training may be required")

    return {"positive": positive, "negative": negative, "neutral": neutral}


# ── Markdown generation ──────────────────────────────────────────────────────

def _generate_markdown(
    title: str,
    today: str,
    status: str,
    context: str,
    options: list[dict[str, Any]],
    decision: str,
    consequences: dict[str, list[str]],
    trade_off_matrix: dict[str, Any],
) -> str:
    """Generate a full ADR in standard markdown format (Michael Nygard template)."""
    lines: list[str] = [
        f"# ADR: {title}",
        "",
        f"**Date**: {today}",
        "",
        f"**Status**: {status.capitalize()}",
        "",
        "## Context",
        "",
        context,
        "",
        "## Options Considered",
        "",
    ]

    for i, opt in enumerate(options, 1):
        lines.append(f"### Option {i}: {opt['name']}")
        lines.append("")
        if opt.get("pros"):
            lines.append("**Pros:**")
            for pro in opt["pros"]:
                lines.append(f"- {pro}")
            lines.append("")
        if opt.get("cons"):
            lines.append("**Cons:**")
            for con in opt["cons"]:
                lines.append(f"- {con}")
            lines.append("")

    # Trade-off matrix
    criteria = trade_off_matrix.get("criteria", [])
    opt_scores = trade_off_matrix.get("options", {})
    if criteria and opt_scores:
        lines.append("## Trade-off Matrix")
        lines.append("")
        header = "| Option | " + " | ".join(criteria) + " |"
        separator = "|--------|" + "|".join("-------" for _ in criteria) + "|"
        lines.append(header)
        lines.append(separator)
        for opt_name, scores in opt_scores.items():
            row_values = [scores.get(c, "medium") for c in criteria]
            lines.append(f"| {opt_name} | " + " | ".join(row_values) + " |")
        lines.append("")

    # Decision
    lines.append("## Decision")
    lines.append("")
    if decision:
        lines.append(decision)
    else:
        lines.append("*No decision has been made yet. This ADR is in proposed status.*")
    lines.append("")

    # Consequences
    lines.append("## Consequences")
    lines.append("")
    if consequences.get("positive"):
        lines.append("### Positive")
        for c in consequences["positive"]:
            lines.append(f"- {c}")
        lines.append("")
    if consequences.get("negative"):
        lines.append("### Negative")
        for c in consequences["negative"]:
            lines.append(f"- {c}")
        lines.append("")
    if consequences.get("neutral"):
        lines.append("### Neutral")
        for c in consequences["neutral"]:
            lines.append(f"- {c}")
        lines.append("")

    return "\n".join(lines)


# ── Public API ───────────────────────────────────────────────────────────────

def create_adr(
    title: str,
    context: str,
    options: str,
    decision: str = "",
) -> dict:
    """Generate an Architecture Decision Record.

    Args:
        title: ADR title (e.g. "Choose database engine").
        context: Problem context and background.
        options: Comma-separated list of options (e.g. "PostgreSQL, MongoDB, DynamoDB").
        decision: The chosen option and rationale. If empty, status is "proposed".

    Returns:
        Dictionary with the ADR structure, trade-off matrix, and markdown.
    """
    today = date.today().isoformat()
    status = "accepted" if decision.strip() else "proposed"

    # Parse options from comma-separated string
    raw_options = [o.strip() for o in options.split(',') if o.strip()]
    if not raw_options:
        raw_options = ["Option A", "Option B"]

    parsed_options: list[dict[str, Any]] = []
    for opt_name in raw_options:
        pros, cons = _generate_pros_cons(opt_name)
        parsed_options.append({
            "name": opt_name,
            "pros": pros,
            "cons": cons,
        })

    # Trade-off matrix
    criteria = list(_DEFAULT_CRITERIA)
    opt_assessments: dict[str, dict[str, str]] = {}
    for opt in parsed_options:
        opt_assessments[opt["name"]] = _assess_option(opt["name"], criteria)

    trade_off_matrix = {
        "criteria": criteria,
        "options": opt_assessments,
    }

    # Consequences
    consequences = _infer_consequences(parsed_options, decision)

    # Generate markdown
    markdown = _generate_markdown(
        title, today, status, context,
        parsed_options, decision, consequences, trade_off_matrix,
    )

    return {
        "adr": {
            "title": title,
            "date": today,
            "status": status,
            "context": context,
            "options": parsed_options,
            "decision": decision or "",
            "consequences": consequences,
        },
        "trade_off_matrix": trade_off_matrix,
        "markdown": markdown,
    }
