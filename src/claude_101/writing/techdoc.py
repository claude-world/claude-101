"""Technical documentation scaffolding — templates for common doc types."""

from __future__ import annotations

import re

from .._utils import text_structure_check


def _parse_code_structure(code: str) -> dict:
    """Extract functions, classes, and imports from code."""
    if not code.strip():
        return {"functions": [], "classes": [], "imports": [], "line_count": 0}

    # Function patterns (Python, JS/TS, Go, Rust, Java)
    func_patterns = [
        r"(?:def|async def)\s+(\w+)\s*\(",  # Python
        r"(?:function|async function)\s+(\w+)\s*\(",  # JS
        r"(?:func)\s+(\w+)\s*\(",  # Go
        r"(?:fn)\s+(\w+)\s*\(",  # Rust
        r"(?:public|private|protected|static)?\s*\w+\s+(\w+)\s*\(",  # Java
    ]
    functions: list[str] = []
    for pat in func_patterns:
        functions.extend(re.findall(pat, code))

    # Class patterns
    class_patterns = [
        r"class\s+(\w+)",  # Python/JS/TS/Java
        r"struct\s+(\w+)",  # Go/Rust
        r"interface\s+(\w+)",  # TS/Java
    ]
    classes: list[str] = []
    for pat in class_patterns:
        classes.extend(re.findall(pat, code))

    # Import patterns
    import_patterns = [
        r"(?:from\s+\S+\s+)?import\s+(.+)",  # Python
        r'(?:import|require)\s*\(?["\'](.+?)["\']\)?',  # JS
    ]
    imports: list[str] = []
    for pat in import_patterns:
        imports.extend(re.findall(pat, code))

    lines = [ln for ln in code.splitlines() if ln.strip()]
    return {
        "functions": list(dict.fromkeys(functions)),
        "classes": list(dict.fromkeys(classes)),
        "imports": imports[:20],
        "line_count": len(lines),
    }


def _score_readme_completeness(content: str) -> dict:
    """Score a README for completeness of standard sections (0-100)."""
    if not content.strip():
        return {"score": 0, "found": [], "missing": []}

    sections = {
        "title": ["# "],
        "description": ["overview", "description", "about", "introduction"],
        "installation": ["install", "setup", "getting started", "quick start"],
        "usage": ["usage", "example", "how to use"],
        "api_reference": ["api", "reference", "documentation"],
        "contributing": ["contributing", "contribute", "development"],
        "license": ["license", "licence"],
        "tests": ["test", "testing"],
    }

    found_markers = text_structure_check(content, sections)
    found = [k for k, v in found_markers.items() if v]
    missing = [k for k, v in found_markers.items() if not v]
    score = round(len(found) / len(sections) * 100, 1)

    return {"score": score, "found": found, "missing": missing}


def _estimate_doc_effort(doc_type: str, section_count: int) -> dict:
    """Estimate documentation effort in hours."""
    # Base hours per section by doc type
    hours_per_section = {
        "readme": 0.5,
        "api": 1.0,
        "rfc": 1.5,
        "adr": 0.3,
        "runbook": 0.8,
        "changelog": 0.2,
        "contributing": 0.4,
        "architecture": 1.2,
    }
    base = hours_per_section.get(doc_type, 0.5)
    min_hours = round(section_count * base * 0.7, 1)
    max_hours = round(section_count * base * 1.3, 1)
    return {
        "min_hours": min_hours,
        "max_hours": max_hours,
        "per_section_estimate": base,
    }


def scaffold_tech_doc(
    doc_type: str,
    title: str,
    sections: str = "",
    content: str = "",
) -> dict:
    """Generate a structured technical document scaffold.

    Args:
        doc_type: One of readme, api, rfc, adr, runbook, changelog,
                  contributing, architecture.
        title: The document title.
        sections: Optional comma-separated section names to use instead
                  of defaults.
        content: Optional code or existing document text to analyze.
    """
    doc_type = doc_type.lower().strip()
    if doc_type not in _DOC_TYPES:
        doc_type = "readme"

    spec = _DOC_TYPES[doc_type]

    # Use custom sections if provided, otherwise use defaults
    if sections.strip():
        section_names = [s.strip() for s in sections.split(",") if s.strip()]
        section_list = [
            {"name": name, "description": f"Content for {name}", "required": True}
            for name in section_names
        ]
    else:
        section_list = spec["sections"]

    # --- Build template ---
    template = _build_template(doc_type, title, section_list, spec)

    # --- Estimate length ---
    section_count = len(section_list)
    if section_count <= 4:
        estimated_length = "short"
    elif section_count <= 8:
        estimated_length = "medium"
    else:
        estimated_length = "long"

    result = {
        "doc_type": doc_type,
        "title": title,
        "template": template,
        "sections": section_list,
        "best_practices": spec["best_practices"],
        "estimated_length": estimated_length,
        "effort_estimate": _estimate_doc_effort(doc_type, section_count),
    }

    if content.strip():
        analysis: dict = {}
        # Check if content looks like code
        code_indicators = [
            "def ",
            "function ",
            "class ",
            "import ",
            "const ",
            "var ",
            "let ",
            "fn ",
            "func ",
        ]
        is_code = any(ind in content for ind in code_indicators)
        if is_code:
            analysis["code_structure"] = _parse_code_structure(content)
        # If doc_type is readme, score completeness
        if doc_type == "readme":
            analysis["completeness"] = _score_readme_completeness(content)
        if analysis:
            result["analysis"] = analysis

    return result


# ---------------------------------------------------------------------------
# Document type specifications
# ---------------------------------------------------------------------------

_DOC_TYPES: dict[str, dict] = {
    "readme": {
        "sections": [
            {
                "name": "Title & Badges",
                "description": "Project name, version badge, CI status, license badge",
                "required": True,
            },
            {
                "name": "Overview",
                "description": "One-paragraph description of what the project does and who it's for",
                "required": True,
            },
            {
                "name": "Features",
                "description": "Bulleted list of key features and capabilities",
                "required": True,
            },
            {
                "name": "Quick Start",
                "description": "Minimal steps to get running (install + first command)",
                "required": True,
            },
            {
                "name": "Installation",
                "description": "Detailed installation instructions for all platforms",
                "required": True,
            },
            {
                "name": "Usage",
                "description": "Common usage examples with code blocks",
                "required": True,
            },
            {
                "name": "Configuration",
                "description": "Available config options, environment variables, config files",
                "required": False,
            },
            {
                "name": "API Reference",
                "description": "Link to full API docs or inline summary",
                "required": False,
            },
            {
                "name": "Contributing",
                "description": "How to contribute, link to CONTRIBUTING.md",
                "required": True,
            },
            {
                "name": "License",
                "description": "License type and link to LICENSE file",
                "required": True,
            },
        ],
        "best_practices": [
            "Lead with a clear one-line description of what the project does",
            "Include a Quick Start that works in under 60 seconds",
            "Add badges for build status, version, and license",
            "Provide copy-pasteable code examples",
            "Keep the README under 500 lines — link to docs for details",
            "Include a screenshot or GIF for visual projects",
        ],
    },
    "api": {
        "sections": [
            {
                "name": "Overview",
                "description": "API purpose, base URL, versioning strategy",
                "required": True,
            },
            {
                "name": "Authentication",
                "description": "Auth methods (API key, OAuth, JWT), token format, examples",
                "required": True,
            },
            {
                "name": "Rate Limiting",
                "description": "Rate limits, headers, retry strategy",
                "required": True,
            },
            {
                "name": "Endpoints",
                "description": "Grouped endpoint documentation with methods, params, responses",
                "required": True,
            },
            {
                "name": "Request Format",
                "description": "Content types, headers, pagination parameters",
                "required": True,
            },
            {
                "name": "Response Format",
                "description": "Response envelope structure, status codes, pagination",
                "required": True,
            },
            {
                "name": "Error Handling",
                "description": "Error codes, error response format, common errors",
                "required": True,
            },
            {
                "name": "Examples",
                "description": "Complete request/response examples for common workflows",
                "required": True,
            },
            {
                "name": "SDKs & Libraries",
                "description": "Official and community client libraries",
                "required": False,
            },
            {
                "name": "Changelog",
                "description": "API version history and breaking changes",
                "required": False,
            },
        ],
        "best_practices": [
            "Document every endpoint with method, path, params, and response",
            "Include curl examples that can be copy-pasted and run",
            "List all possible error codes with descriptions",
            "Show complete request/response bodies, not fragments",
            "Version your API docs alongside the API itself",
            "Document rate limits prominently",
        ],
    },
    "rfc": {
        "sections": [
            {
                "name": "Title & Metadata",
                "description": "RFC number, title, author, date, status (draft/accepted/rejected)",
                "required": True,
            },
            {
                "name": "Summary",
                "description": "One-paragraph summary of the proposal",
                "required": True,
            },
            {
                "name": "Motivation",
                "description": "Why this change is needed, what problem it solves",
                "required": True,
            },
            {
                "name": "Detailed Design",
                "description": "Technical design with diagrams, interfaces, data flow",
                "required": True,
            },
            {
                "name": "Alternatives Considered",
                "description": "Other approaches evaluated and why they were rejected",
                "required": True,
            },
            {
                "name": "Migration Plan",
                "description": "How to roll out the change, backward compatibility",
                "required": True,
            },
            {
                "name": "Drawbacks",
                "description": "Known limitations, trade-offs, risks",
                "required": True,
            },
            {
                "name": "Unresolved Questions",
                "description": "Open questions to resolve during implementation",
                "required": False,
            },
            {
                "name": "References",
                "description": "Related RFCs, external resources, prior art",
                "required": False,
            },
        ],
        "best_practices": [
            "Write the Summary so someone can decide whether to read further",
            "Be honest about Drawbacks — credibility matters",
            "Include at least 2 Alternatives Considered",
            "Separate the problem statement from the solution",
            "Get feedback on the Motivation section first before detailing design",
            "Include diagrams for complex data or control flow",
        ],
    },
    "adr": {
        "sections": [
            {
                "name": "Title",
                "description": "ADR number and short descriptive title",
                "required": True,
            },
            {
                "name": "Status",
                "description": "Proposed, Accepted, Deprecated, Superseded",
                "required": True,
            },
            {
                "name": "Context",
                "description": "The situation and forces at play (technical, political, social)",
                "required": True,
            },
            {
                "name": "Decision",
                "description": "The change being proposed or decided",
                "required": True,
            },
            {
                "name": "Consequences",
                "description": "What happens as a result — both positive and negative",
                "required": True,
            },
        ],
        "best_practices": [
            "Keep ADRs short (1-2 pages) — they should be quick to write and read",
            "Focus on WHY, not just WHAT",
            "Record the decision even if it seems obvious now",
            "Link to related ADRs when superseding or extending",
            "Write in present tense: 'We decide to...' not 'We decided to...'",
        ],
    },
    "runbook": {
        "sections": [
            {
                "name": "Overview",
                "description": "What this runbook covers, when to use it, severity level",
                "required": True,
            },
            {
                "name": "Prerequisites",
                "description": "Required access, tools, permissions, dashboards",
                "required": True,
            },
            {
                "name": "Detection",
                "description": "How to detect the issue — alerts, metrics, symptoms",
                "required": True,
            },
            {
                "name": "Diagnosis",
                "description": "Step-by-step diagnostic commands and what to look for",
                "required": True,
            },
            {
                "name": "Remediation",
                "description": "Step-by-step fix instructions with rollback plan",
                "required": True,
            },
            {
                "name": "Verification",
                "description": "How to verify the fix worked — checks, metrics, tests",
                "required": True,
            },
            {
                "name": "Escalation",
                "description": "When and how to escalate, contact information",
                "required": True,
            },
            {
                "name": "Post-Incident",
                "description": "Follow-up tasks, post-mortem template link",
                "required": False,
            },
        ],
        "best_practices": [
            "Write for the on-call engineer at 3 AM — be explicit and step-by-step",
            "Include exact commands, not descriptions of commands",
            "Always include a rollback plan for every remediation step",
            "Link to relevant dashboards and monitoring tools",
            "Test the runbook by having someone unfamiliar follow it",
            "Include expected output for diagnostic commands",
        ],
    },
    "changelog": {
        "sections": [
            {
                "name": "Header",
                "description": "Project name, changelog format note, link conventions",
                "required": True,
            },
            {
                "name": "Unreleased",
                "description": "Changes not yet in a release",
                "required": True,
            },
            {
                "name": "Version Entry",
                "description": "Version number, date, grouped changes (Added/Changed/Deprecated/Removed/Fixed/Security)",
                "required": True,
            },
        ],
        "best_practices": [
            "Follow Keep a Changelog format (keepachangelog.com)",
            "Group changes: Added, Changed, Deprecated, Removed, Fixed, Security",
            "Write for humans, not machines — explain the impact",
            "Include links to issues/PRs for each entry",
            "Put the most recent version at the top",
            "Use semantic versioning (semver.org)",
        ],
    },
    "contributing": {
        "sections": [
            {
                "name": "Welcome",
                "description": "Thank contributors, link to Code of Conduct",
                "required": True,
            },
            {
                "name": "Getting Started",
                "description": "Dev environment setup, fork/clone/branch workflow",
                "required": True,
            },
            {
                "name": "Development Workflow",
                "description": "Build, test, lint commands, pre-commit hooks",
                "required": True,
            },
            {
                "name": "Pull Request Process",
                "description": "PR requirements, review process, merge criteria",
                "required": True,
            },
            {
                "name": "Code Style",
                "description": "Formatting, naming conventions, linting rules",
                "required": True,
            },
            {
                "name": "Issue Guidelines",
                "description": "Bug report template, feature request process",
                "required": True,
            },
            {
                "name": "Community",
                "description": "Communication channels, meetings, decision process",
                "required": False,
            },
        ],
        "best_practices": [
            "Make the first contribution as easy as possible",
            "Include exact commands for setup, not just descriptions",
            "Label 'good first issue' tickets for newcomers",
            "Respond to PRs within 48 hours",
            "Be explicit about code style — automate with linters",
            "Thank every contributor, regardless of contribution size",
        ],
    },
    "architecture": {
        "sections": [
            {
                "name": "Overview",
                "description": "System purpose, high-level architecture diagram",
                "required": True,
            },
            {
                "name": "Design Principles",
                "description": "Core principles guiding architectural decisions",
                "required": True,
            },
            {
                "name": "System Components",
                "description": "Major components/services and their responsibilities",
                "required": True,
            },
            {
                "name": "Data Flow",
                "description": "How data moves through the system, data models",
                "required": True,
            },
            {
                "name": "Infrastructure",
                "description": "Deployment architecture, cloud services, networking",
                "required": True,
            },
            {
                "name": "Security",
                "description": "Auth, encryption, access control, threat model",
                "required": True,
            },
            {
                "name": "Scalability",
                "description": "Scaling strategy, bottlenecks, capacity planning",
                "required": False,
            },
            {
                "name": "Observability",
                "description": "Logging, metrics, tracing, alerting strategy",
                "required": False,
            },
            {
                "name": "Decision Log",
                "description": "Key architectural decisions with rationale (link to ADRs)",
                "required": False,
            },
        ],
        "best_practices": [
            "Include a high-level diagram on the first page",
            "Use C4 model levels (Context, Container, Component, Code)",
            "Document the WHY behind architectural choices",
            "Keep it updated — stale architecture docs are worse than none",
            "Link to ADRs for detailed decision rationale",
            "Include failure modes and disaster recovery strategy",
        ],
    },
}


# ---------------------------------------------------------------------------
# Template builder
# ---------------------------------------------------------------------------


def _build_template(
    doc_type: str,
    title: str,
    section_list: list[dict],
    spec: dict,
) -> str:
    """Build a full Markdown template with placeholders."""
    lines: list[str] = []

    # Header varies by doc type
    if doc_type == "rfc":
        lines.append(f"# RFC: {title}")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        lines.append(f"| **Title** | {title} |")
        lines.append("| **Author** | [Your Name] |")
        lines.append("| **Date** | [YYYY-MM-DD] |")
        lines.append("| **Status** | Draft |")
        lines.append("")

    elif doc_type == "adr":
        lines.append(f"# ADR-NNN: {title}")
        lines.append("")
        lines.append("**Status:** Proposed")
        lines.append("")
        lines.append("**Date:** [YYYY-MM-DD]")
        lines.append("")

    elif doc_type == "changelog":
        lines.append(f"# Changelog — {title}")
        lines.append("")
        lines.append(
            "All notable changes to this project will be documented in this file."
        )
        lines.append("")
        lines.append(
            "The format is based on [Keep a Changelog](https://keepachangelog.com/),"
        )
        lines.append(
            "and this project adheres to [Semantic Versioning](https://semver.org/)."
        )
        lines.append("")

    elif doc_type == "readme":
        lines.append(f"# {title}")
        lines.append("")
        lines.append("<!-- badges -->")
        lines.append("![License](https://img.shields.io/badge/license-MIT-blue)")
        lines.append("")

    else:
        lines.append(f"# {title}")
        lines.append("")

    # Sections
    for sec in section_list:
        name = sec["name"]
        desc = sec["description"]
        required = sec.get("required", True)

        # Special handling for changelog version entries
        if doc_type == "changelog" and name == "Version Entry":
            lines.append("## [1.0.0] - YYYY-MM-DD")
            lines.append("")
            lines.append("### Added")
            lines.append("- [Describe new features]")
            lines.append("")
            lines.append("### Changed")
            lines.append("- [Describe changes to existing functionality]")
            lines.append("")
            lines.append("### Fixed")
            lines.append("- [Describe bug fixes]")
            lines.append("")
            continue

        if doc_type == "changelog" and name == "Unreleased":
            lines.append("## [Unreleased]")
            lines.append("")
            lines.append("### Added")
            lines.append("- ")
            lines.append("")
            continue

        if doc_type == "changelog" and name == "Header":
            # Already handled above
            continue

        # Title & Badges already handled for readme
        if doc_type == "readme" and name == "Title & Badges":
            continue

        marker = "" if required else " *(optional)*"
        lines.append(f"## {name}{marker}")
        lines.append("")
        lines.append(f"<!-- {desc} -->")
        lines.append("")
        lines.append(f"[Write {name.lower()} content here]")
        lines.append("")

    return "\n".join(lines)
