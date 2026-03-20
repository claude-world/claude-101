"""Architecture Decision Record (ADR) generator — Michael Nygard format."""

from __future__ import annotations

from datetime import date
from typing import Any


# ── Trade-off criteria ───────────────────────────────────────────────────────

_DEFAULT_CRITERIA = ["Performance", "Maintainability", "Cost", "Complexity", "Risk"]

# ── Technology knowledge base ────────────────────────────────────────────────
# Maps well-known technology names to their known characteristics so that
# the trade-off matrix contains *real*, differentiated values instead of
# generic "medium" for every option.

_TECH_PROFILES: dict[str, dict[str, str]] = {
    # Message queues
    "rabbitmq": {
        "performance": "high",
        "cost": "low",
        "complexity": "medium",
        "scalability": "medium",
        "maturity": "high",
    },
    "kafka": {
        "performance": "very_high",
        "cost": "medium",
        "complexity": "high",
        "scalability": "very_high",
        "maturity": "high",
    },
    "sqs": {
        "performance": "high",
        "cost": "low",
        "complexity": "low",
        "scalability": "very_high",
        "maturity": "high",
    },
    "redis": {
        "performance": "very_high",
        "cost": "low",
        "complexity": "low",
        "scalability": "medium",
        "maturity": "high",
    },
    # Databases
    "postgresql": {
        "performance": "high",
        "cost": "low",
        "complexity": "medium",
        "scalability": "medium",
        "maturity": "very_high",
    },
    "mysql": {
        "performance": "high",
        "cost": "low",
        "complexity": "low",
        "scalability": "medium",
        "maturity": "very_high",
    },
    "mongodb": {
        "performance": "high",
        "cost": "medium",
        "complexity": "low",
        "scalability": "high",
        "maturity": "high",
    },
    "dynamodb": {
        "performance": "very_high",
        "cost": "variable",
        "complexity": "medium",
        "scalability": "very_high",
        "maturity": "high",
    },
    "sqlite": {
        "performance": "medium",
        "cost": "free",
        "complexity": "very_low",
        "scalability": "low",
        "maturity": "very_high",
    },
    "cassandra": {
        "performance": "very_high",
        "cost": "high",
        "complexity": "high",
        "scalability": "very_high",
        "maturity": "high",
    },
    # Web frameworks
    "express": {
        "performance": "medium",
        "cost": "low",
        "complexity": "low",
        "scalability": "medium",
        "maturity": "very_high",
    },
    "fastapi": {
        "performance": "high",
        "cost": "low",
        "complexity": "low",
        "scalability": "high",
        "maturity": "medium",
    },
    "django": {
        "performance": "medium",
        "cost": "low",
        "complexity": "medium",
        "scalability": "medium",
        "maturity": "very_high",
    },
    "flask": {
        "performance": "medium",
        "cost": "low",
        "complexity": "low",
        "scalability": "medium",
        "maturity": "high",
    },
    "spring": {
        "performance": "high",
        "cost": "low",
        "complexity": "high",
        "scalability": "high",
        "maturity": "very_high",
    },
    "nextjs": {
        "performance": "high",
        "cost": "low",
        "complexity": "medium",
        "scalability": "high",
        "maturity": "medium",
    },
    # Cloud providers
    "aws": {
        "performance": "very_high",
        "cost": "variable",
        "complexity": "high",
        "scalability": "very_high",
        "maturity": "very_high",
    },
    "gcp": {
        "performance": "very_high",
        "cost": "variable",
        "complexity": "high",
        "scalability": "very_high",
        "maturity": "high",
    },
    "azure": {
        "performance": "very_high",
        "cost": "variable",
        "complexity": "high",
        "scalability": "very_high",
        "maturity": "high",
    },
    "vercel": {
        "performance": "high",
        "cost": "low",
        "complexity": "very_low",
        "scalability": "high",
        "maturity": "medium",
    },
    "cloudflare": {
        "performance": "very_high",
        "cost": "low",
        "complexity": "low",
        "scalability": "very_high",
        "maturity": "medium",
    },
    # Frontend frameworks
    "react": {
        "performance": "medium",
        "cost": "low",
        "complexity": "medium",
        "scalability": "high",
        "maturity": "very_high",
    },
    "vue": {
        "performance": "high",
        "cost": "low",
        "complexity": "low",
        "scalability": "high",
        "maturity": "high",
    },
    "svelte": {
        "performance": "very_high",
        "cost": "low",
        "complexity": "low",
        "scalability": "medium",
        "maturity": "medium",
    },
    "angular": {
        "performance": "medium",
        "cost": "low",
        "complexity": "high",
        "scalability": "high",
        "maturity": "very_high",
    },
}

# Mapping from profile trait names to ADR criteria names so we can translate
# a profile entry into the standard criteria used in the trade-off matrix.
_PROFILE_TO_CRITERIA: dict[str, str] = {
    "performance": "performance",
    "cost": "cost",
    "complexity": "complexity",
    "scalability": "maintainability",  # scalability is the best proxy we have
    "maturity": "risk",  # high maturity → low risk, handled below
}

# Maturity-to-risk inversion: higher maturity means lower risk.
_MATURITY_TO_RISK: dict[str, str] = {
    "very_high": "low",
    "high": "low",
    "medium": "medium",
    "low": "high",
    "very_low": "high",
}


def _lookup_tech_profile(name: str) -> dict[str, str] | None:
    """Fuzzy-match *name* against ``_TECH_PROFILES`` keys.

    Matching strategy (in order):
    1. Exact match after lower-casing and stripping whitespace.
    2. Check whether any profile key is *contained* in *name* (handles cases
       like "Use PostgreSQL" or "PostgreSQL 16").
    3. Check whether *name* is contained in any profile key.
    """
    normalised = name.lower().strip()
    # 1. Exact match
    if normalised in _TECH_PROFILES:
        return _TECH_PROFILES[normalised]
    # 2. Profile key contained in name
    for key, profile in _TECH_PROFILES.items():
        if key in normalised:
            return profile
    # 3. Name contained in profile key
    for key, profile in _TECH_PROFILES.items():
        if normalised in key:
            return profile
    return None


def _assess_option(option_name: str, criteria: list[str]) -> dict[str, str]:
    """Auto-generate a trade-off assessment for an option.

    First attempts to match the option name against ``_TECH_PROFILES`` for
    real, differentiated values.  Falls back to keyword-based heuristics when
    no profile is found, and appends a note for unknown technologies.

    Heuristic fallback patterns:
    - Options mentioning "simple", "existing", "monolith" → lower complexity, higher maintainability
    - Options mentioning "new", "custom", "build" → higher complexity, higher performance
    - Options mentioning "cloud", "managed", "saas" → lower complexity, higher cost
    - Options mentioning "open-source", "free" → lower cost
    """
    # ── 1. Try technology knowledge base ──────────────────────────────────
    profile = _lookup_tech_profile(option_name)
    if profile is not None:
        assessment: dict[str, str] = {}
        for criterion in criteria:
            crit_lower = criterion.lower()
            if crit_lower == "performance":
                assessment[criterion] = profile.get("performance", "medium")
            elif crit_lower == "cost":
                assessment[criterion] = profile.get("cost", "medium")
            elif crit_lower == "complexity":
                assessment[criterion] = profile.get("complexity", "medium")
            elif crit_lower == "maintainability":
                # Use scalability as a proxy; higher scalability → easier to maintain at scale.
                assessment[criterion] = profile.get("scalability", "medium")
            elif crit_lower == "risk":
                # Invert maturity: very_high maturity → low risk.
                maturity = profile.get("maturity", "medium")
                assessment[criterion] = _MATURITY_TO_RISK.get(maturity, "medium")
            else:
                assessment[criterion] = "medium"
        return assessment

    # ── 2. Keyword-based heuristic fallback ───────────────────────────────
    name_lower = option_name.lower()
    assessment = {}

    for criterion in criteria:
        crit_lower = criterion.lower()

        if crit_lower == "performance":
            if any(
                kw in name_lower
                for kw in ("custom", "optimized", "native", "rust", "go", "c++")
            ):
                assessment[criterion] = "high"
            elif any(kw in name_lower for kw in ("simple", "basic", "script")):
                assessment[criterion] = "low"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "maintainability":
            if any(
                kw in name_lower
                for kw in ("standard", "existing", "managed", "saas", "convention")
            ):
                assessment[criterion] = "high"
            elif any(kw in name_lower for kw in ("custom", "complex", "novel")):
                assessment[criterion] = "low"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "cost":
            if any(
                kw in name_lower
                for kw in ("free", "open-source", "oss", "existing", "self-host")
            ):
                assessment[criterion] = "low"
            elif any(
                kw in name_lower
                for kw in ("cloud", "managed", "saas", "enterprise", "commercial")
            ):
                assessment[criterion] = "high"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "complexity":
            if any(
                kw in name_lower
                for kw in ("simple", "existing", "monolith", "basic", "standard")
            ):
                assessment[criterion] = "low"
            elif any(
                kw in name_lower
                for kw in ("microservice", "distributed", "custom", "novel")
            ):
                assessment[criterion] = "high"
            else:
                assessment[criterion] = "medium"

        elif crit_lower == "risk":
            if any(
                kw in name_lower
                for kw in ("proven", "standard", "existing", "stable", "managed")
            ):
                assessment[criterion] = "low"
            elif any(
                kw in name_lower
                for kw in ("new", "experimental", "alpha", "beta", "novel", "custom")
            ):
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
        pros.extend(
            [
                "Low learning curve",
                "Already integrated with existing systems",
                "Minimal migration effort",
            ]
        )
        cons.extend(
            [
                "May not scale well",
                "Limited feature set",
                "Technical debt may accumulate",
            ]
        )

    # Cloud / managed
    elif any(kw in name_lower for kw in ("cloud", "managed", "saas", "serverless")):
        pros.extend(
            [
                "No infrastructure management",
                "Built-in scaling",
                "Vendor-provided reliability",
            ]
        )
        cons.extend(
            ["Vendor lock-in risk", "Ongoing costs may grow", "Limited customization"]
        )

    # Open source
    elif any(kw in name_lower for kw in ("open-source", "oss", "open source")):
        pros.extend(
            [
                "No licensing costs",
                "Community support",
                "Full source access for customization",
            ]
        )
        cons.extend(
            [
                "Maintenance burden on team",
                "Community support may be inconsistent",
                "Security patches are team's responsibility",
            ]
        )

    # Custom / build
    elif any(kw in name_lower for kw in ("custom", "build", "in-house", "homegrown")):
        pros.extend(
            [
                "Tailored to exact requirements",
                "Full control over implementation",
                "No external dependencies",
            ]
        )
        cons.extend(
            [
                "High development effort",
                "Ongoing maintenance burden",
                "Risk of reinventing the wheel",
            ]
        )

    # Microservice
    elif any(
        kw in name_lower for kw in ("microservice", "distributed", "event-driven")
    ):
        pros.extend(
            ["Independent scaling", "Technology diversity per service", "Team autonomy"]
        )
        cons.extend(
            [
                "Operational complexity",
                "Network latency overhead",
                "Distributed debugging difficulty",
            ]
        )

    # Monolith
    elif any(kw in name_lower for kw in ("monolith", "monolithic", "unified")):
        pros.extend(
            [
                "Simple deployment",
                "Easy debugging",
                "No network overhead between components",
            ]
        )
        cons.extend(
            ["Scaling constraints", "Technology lock-in", "Deployment coupling"]
        )

    # Generic fallback
    else:
        pros.extend(
            ["Addresses the stated requirements", "Feasible with current resources"]
        )
        cons.extend(
            ["Trade-offs need further evaluation", "May require additional research"]
        )

    return pros, cons


def _infer_consequences(
    options: list[dict[str, Any]], decision: str
) -> dict[str, list[str]]:
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
        # Render notes for unknown technologies
        tm_notes = trade_off_matrix.get("notes", {})
        if tm_notes:
            for opt_name, note in tm_notes.items():
                lines.append(f"*{opt_name}: {note}*")
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
    raw_options = [o.strip() for o in options.split(",") if o.strip()]
    if not raw_options:
        raw_options = ["Option A", "Option B"]

    parsed_options: list[dict[str, Any]] = []
    for opt_name in raw_options:
        pros, cons = _generate_pros_cons(opt_name)
        parsed_options.append(
            {
                "name": opt_name,
                "pros": pros,
                "cons": cons,
            }
        )

    # Trade-off matrix
    criteria = list(_DEFAULT_CRITERIA)
    opt_assessments: dict[str, dict[str, str]] = {}
    notes: dict[str, str] = {}
    for opt in parsed_options:
        opt_assessments[opt["name"]] = _assess_option(opt["name"], criteria)
        # If the option did not match any known tech profile, record a note
        if _lookup_tech_profile(opt["name"]) is None:
            notes[opt["name"]] = "unknown technology \u2014 using default values"

    trade_off_matrix: dict[str, Any] = {
        "criteria": criteria,
        "options": opt_assessments,
    }
    if notes:
        trade_off_matrix["notes"] = notes

    # Consequences
    consequences = _infer_consequences(parsed_options, decision)

    # Generate markdown
    markdown = _generate_markdown(
        title,
        today,
        status,
        context,
        parsed_options,
        decision,
        consequences,
        trade_off_matrix,
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
