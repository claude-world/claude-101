"""Project planning tool — WBS generation with realistic task estimation."""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Phase templates
# ---------------------------------------------------------------------------

_DEFAULT_PHASES = [
    {"name": "Planning", "percentage": 15},
    {"name": "Design", "percentage": 20},
    {"name": "Implementation", "percentage": 35},
    {"name": "Testing", "percentage": 20},
    {"name": "Launch", "percentage": 10},
]

_DOMAIN_TASKS: dict[str, dict[str, list[dict]]] = {
    "web": {
        "Planning": [
            {
                "name": "Define site map and information architecture",
                "priority": "high",
            },
            {"name": "Gather content requirements", "priority": "high"},
            {"name": "Identify third-party integrations", "priority": "medium"},
        ],
        "Design": [
            {"name": "Create wireframes for key pages", "priority": "high"},
            {"name": "Design responsive layouts", "priority": "high"},
            {
                "name": "Define component library and design system",
                "priority": "medium",
            },
            {"name": "Design navigation and user flows", "priority": "medium"},
        ],
        "Implementation": [
            {"name": "Set up project scaffolding and build tools", "priority": "high"},
            {"name": "Implement page templates and routing", "priority": "high"},
            {"name": "Build interactive components", "priority": "high"},
            {"name": "Integrate CMS or backend API", "priority": "medium"},
            {"name": "Implement SEO and meta tags", "priority": "medium"},
            {"name": "Add analytics tracking", "priority": "low"},
        ],
        "Testing": [
            {"name": "Cross-browser testing", "priority": "high"},
            {"name": "Mobile responsiveness testing", "priority": "high"},
            {"name": "Performance and Lighthouse audit", "priority": "medium"},
            {"name": "Accessibility (WCAG) audit", "priority": "medium"},
        ],
        "Launch": [
            {"name": "Configure DNS and SSL", "priority": "high"},
            {"name": "Deploy to production", "priority": "high"},
            {"name": "Monitor post-launch metrics", "priority": "medium"},
        ],
    },
    "api": {
        "Planning": [
            {"name": "Define API endpoints and resource model", "priority": "high"},
            {"name": "Write OpenAPI specification", "priority": "high"},
            {
                "name": "Plan authentication and authorization strategy",
                "priority": "high",
            },
        ],
        "Design": [
            {"name": "Design database schema", "priority": "high"},
            {"name": "Design request/response payloads", "priority": "high"},
            {"name": "Plan rate limiting and caching strategy", "priority": "medium"},
            {"name": "Define error handling conventions", "priority": "medium"},
        ],
        "Implementation": [
            {"name": "Set up project structure and dependencies", "priority": "high"},
            {"name": "Implement data models and migrations", "priority": "high"},
            {"name": "Build CRUD endpoints", "priority": "high"},
            {"name": "Implement authentication middleware", "priority": "high"},
            {"name": "Add input validation and serialization", "priority": "medium"},
            {"name": "Implement logging and monitoring", "priority": "medium"},
        ],
        "Testing": [
            {"name": "Write unit tests for business logic", "priority": "high"},
            {"name": "Write integration tests for endpoints", "priority": "high"},
            {"name": "Load testing and performance benchmarks", "priority": "medium"},
            {"name": "Security audit (OWASP top 10)", "priority": "high"},
        ],
        "Launch": [
            {"name": "Set up CI/CD pipeline", "priority": "high"},
            {"name": "Deploy to staging and production", "priority": "high"},
            {"name": "Publish API documentation", "priority": "medium"},
        ],
    },
    "mobile": {
        "Planning": [
            {"name": "Define target platforms (iOS/Android)", "priority": "high"},
            {
                "name": "Gather feature requirements and user stories",
                "priority": "high",
            },
            {"name": "Plan offline capabilities", "priority": "medium"},
        ],
        "Design": [
            {"name": "Create UI mockups for key screens", "priority": "high"},
            {"name": "Design navigation patterns", "priority": "high"},
            {
                "name": "Define platform-specific design guidelines",
                "priority": "medium",
            },
            {"name": "Design onboarding flow", "priority": "medium"},
        ],
        "Implementation": [
            {"name": "Set up mobile project and dependencies", "priority": "high"},
            {"name": "Implement core screens and navigation", "priority": "high"},
            {"name": "Build data layer and API integration", "priority": "high"},
            {"name": "Implement push notifications", "priority": "medium"},
            {"name": "Add local storage and caching", "priority": "medium"},
            {"name": "Implement analytics and crash reporting", "priority": "low"},
        ],
        "Testing": [
            {"name": "Device compatibility testing", "priority": "high"},
            {"name": "UI automation tests", "priority": "medium"},
            {"name": "Performance profiling", "priority": "medium"},
            {"name": "Beta testing with TestFlight/Play Console", "priority": "high"},
        ],
        "Launch": [
            {"name": "Prepare App Store/Play Store listings", "priority": "high"},
            {"name": "Submit for review", "priority": "high"},
            {"name": "Plan post-launch update cadence", "priority": "medium"},
        ],
    },
    "data": {
        "Planning": [
            {"name": "Define data sources and collection strategy", "priority": "high"},
            {"name": "Identify key metrics and KPIs", "priority": "high"},
            {"name": "Plan data governance and privacy compliance", "priority": "high"},
        ],
        "Design": [
            {"name": "Design data warehouse schema", "priority": "high"},
            {"name": "Design ETL/ELT pipeline architecture", "priority": "high"},
            {"name": "Define dashboard and report layouts", "priority": "medium"},
            {"name": "Plan data quality checks", "priority": "medium"},
        ],
        "Implementation": [
            {"name": "Set up data infrastructure", "priority": "high"},
            {"name": "Build data ingestion pipelines", "priority": "high"},
            {"name": "Implement data transformations", "priority": "high"},
            {"name": "Build dashboards and visualizations", "priority": "medium"},
            {
                "name": "Implement automated data quality monitoring",
                "priority": "medium",
            },
            {"name": "Set up alerting for pipeline failures", "priority": "low"},
        ],
        "Testing": [
            {"name": "Validate data accuracy against source", "priority": "high"},
            {"name": "Test pipeline fault tolerance", "priority": "high"},
            {
                "name": "Performance testing with production-scale data",
                "priority": "medium",
            },
            {"name": "User acceptance testing for dashboards", "priority": "medium"},
        ],
        "Launch": [
            {"name": "Migrate to production data sources", "priority": "high"},
            {"name": "Train stakeholders on dashboards", "priority": "high"},
            {"name": "Set up ongoing monitoring and SLAs", "priority": "medium"},
        ],
    },
    "generic": {
        "Planning": [
            {"name": "Define project scope and objectives", "priority": "high"},
            {
                "name": "Identify stakeholders and communication plan",
                "priority": "high",
            },
            {"name": "Gather and prioritize requirements", "priority": "high"},
        ],
        "Design": [
            {"name": "Create system architecture diagram", "priority": "high"},
            {"name": "Design user interface mockups", "priority": "high"},
            {"name": "Define technical specifications", "priority": "medium"},
            {
                "name": "Plan infrastructure and deployment strategy",
                "priority": "medium",
            },
        ],
        "Implementation": [
            {"name": "Set up development environment", "priority": "high"},
            {"name": "Implement core features", "priority": "high"},
            {"name": "Build integration layers", "priority": "high"},
            {"name": "Implement security controls", "priority": "medium"},
            {"name": "Add logging and observability", "priority": "medium"},
            {"name": "Write documentation", "priority": "low"},
        ],
        "Testing": [
            {"name": "Write and run unit tests", "priority": "high"},
            {"name": "Integration and end-to-end testing", "priority": "high"},
            {"name": "Performance testing", "priority": "medium"},
            {"name": "User acceptance testing", "priority": "medium"},
        ],
        "Launch": [
            {"name": "Prepare deployment runbook", "priority": "high"},
            {"name": "Deploy to production", "priority": "high"},
            {"name": "Post-launch monitoring and support", "priority": "medium"},
        ],
    },
}

_DOMAIN_RISKS: dict[str, list[dict]] = {
    "web": [
        {
            "risk": "Browser compatibility issues causing layout breaks",
            "impact": "medium",
            "mitigation": "Test on top 5 browsers early and use progressive enhancement",
        },
        {
            "risk": "Third-party API changes breaking integrations",
            "impact": "high",
            "mitigation": "Abstract API calls behind adapter layer with fallback handling",
        },
        {
            "risk": "Poor performance on mobile devices",
            "impact": "high",
            "mitigation": "Set performance budgets and test on low-end devices weekly",
        },
    ],
    "api": [
        {
            "risk": "Security vulnerabilities in authentication flow",
            "impact": "high",
            "mitigation": "Use battle-tested auth libraries and conduct security review before launch",
        },
        {
            "risk": "Database schema changes causing downtime",
            "impact": "high",
            "mitigation": "Use reversible migrations and blue-green deployment strategy",
        },
        {
            "risk": "API breaking changes affecting consumers",
            "impact": "medium",
            "mitigation": "Version the API from day one and maintain backward compatibility",
        },
    ],
    "mobile": [
        {
            "risk": "App store rejection delaying launch",
            "impact": "high",
            "mitigation": "Review store guidelines early and submit a pre-release for feedback",
        },
        {
            "risk": "Device fragmentation causing inconsistent behavior",
            "impact": "medium",
            "mitigation": "Define supported device matrix and test on physical devices",
        },
        {
            "risk": "Poor offline experience frustrating users",
            "impact": "medium",
            "mitigation": "Design offline-first with clear sync status indicators",
        },
    ],
    "data": [
        {
            "risk": "Data quality issues leading to incorrect insights",
            "impact": "high",
            "mitigation": "Implement automated data validation at each pipeline stage",
        },
        {
            "risk": "Pipeline failures during peak data volume",
            "impact": "high",
            "mitigation": "Load test with 2x expected volume and implement circuit breakers",
        },
        {
            "risk": "Regulatory non-compliance with data privacy laws",
            "impact": "high",
            "mitigation": "Conduct privacy impact assessment and implement data anonymization",
        },
    ],
    "generic": [
        {
            "risk": "Scope creep extending timeline beyond budget",
            "impact": "high",
            "mitigation": "Freeze scope at design phase and use change request process",
        },
        {
            "risk": "Key team member unavailability",
            "impact": "medium",
            "mitigation": "Document knowledge in shared wiki and cross-train team members",
        },
        {
            "risk": "Integration issues between components discovered late",
            "impact": "high",
            "mitigation": "Run integration tests in CI from week 2 onward",
        },
    ],
}


# ---------------------------------------------------------------------------
# Domain detection
# ---------------------------------------------------------------------------


def _detect_domain(description: str) -> str:
    """Detect project domain from description keywords."""
    lower = description.lower()

    domain_keywords = {
        "web": [
            "website",
            "web app",
            "webapp",
            "landing page",
            "frontend",
            "html",
            "css",
            "react",
            "vue",
            "angular",
            "next.js",
            "nuxt",
            "astro",
            "wordpress",
            "shopify",
            "ecommerce",
            "e-commerce",
        ],
        "api": [
            "api",
            "rest",
            "graphql",
            "backend",
            "microservice",
            "endpoint",
            "server",
            "webhook",
            "grpc",
            "service layer",
        ],
        "mobile": [
            "mobile",
            "ios",
            "android",
            "react native",
            "flutter",
            "swift",
            "kotlin",
            "app store",
            "play store",
            "cordova",
        ],
        "data": [
            "data",
            "analytics",
            "dashboard",
            "etl",
            "pipeline",
            "machine learning",
            "ml",
            "ai model",
            "warehouse",
            "visualization",
            "bi",
            "reporting",
        ],
    }

    scores: dict[str, int] = {}
    for domain, keywords in domain_keywords.items():
        scores[domain] = sum(1 for kw in keywords if kw in lower)

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    if scores[best] == 0:
        return "generic"
    return best


# ---------------------------------------------------------------------------
# Task hour estimation
# ---------------------------------------------------------------------------


def _estimate_hours(
    task_count: int,
    phase_hours: float,
    team_size: int,
) -> list[float]:
    """Distribute phase hours across tasks with some variance.

    Earlier tasks (higher priority) get slightly more hours.
    """
    if task_count == 0:
        return []
    # Give first task ~30% more than average, last task ~30% less
    weights = [
        1.0 + 0.3 * (1 - 2 * i / max(task_count - 1, 1)) for i in range(task_count)
    ]
    total_weight = sum(weights)
    hours = [round(w / total_weight * phase_hours, 1) for w in weights]
    return hours


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def plan_project(
    description: str,
    team_size: int = 1,
    duration_weeks: int = 4,
) -> dict:
    """Generate a WBS and project plan from a description.

    Args:
        description: Natural-language description of the project.
        team_size: Number of people on the team.
        duration_weeks: Total project duration in weeks.

    Returns:
        Dictionary with phases, tasks, milestones, critical path,
        risks, and resource allocation.
    """
    team_size = max(1, team_size)
    duration_weeks = max(1, duration_weeks)

    total_hours = round(team_size * duration_weeks * 40 * 0.7, 1)
    buffer_hours = round(total_hours * 0.10, 1)
    available_hours = total_hours - buffer_hours

    domain = _detect_domain(description)
    domain_tasks = _DOMAIN_TASKS.get(domain, _DOMAIN_TASKS["generic"])

    # ── Build phases ─────────────────────────────────────────────
    phases: list[dict] = []
    cumulative_weeks = 0.0

    for phase_def in _DEFAULT_PHASES:
        pct = phase_def["percentage"]
        phase_weeks = round(duration_weeks * pct / 100, 2)
        phase_hours = round(available_hours * pct / 100, 1)
        tasks_templates = domain_tasks.get(phase_def["name"], [])

        task_hours = _estimate_hours(len(tasks_templates), phase_hours, team_size)

        tasks: list[dict] = []
        for idx, tmpl in enumerate(tasks_templates):
            # Dependencies: each task depends on previous task in same phase
            deps = [tasks_templates[idx - 1]["name"]] if idx > 0 else []
            tasks.append(
                {
                    "name": tmpl["name"],
                    "estimated_hours": task_hours[idx] if idx < len(task_hours) else 0,
                    "priority": tmpl["priority"],
                    "dependencies": deps,
                }
            )

        phases.append(
            {
                "name": phase_def["name"],
                "percentage": pct,
                "duration_weeks": phase_weeks,
                "tasks": tasks,
            }
        )
        cumulative_weeks += phase_weeks

    # ── Milestones ───────────────────────────────────────────────
    milestones: list[dict] = []
    week_cursor = 0.0
    milestone_defs = [
        ("Planning Complete", "Approved project scope and requirements document"),
        ("Design Complete", "Finalized designs and technical specifications"),
        ("Feature Complete", "All features implemented and code-complete"),
        ("Testing Complete", "All tests passed and defects resolved"),
        ("Launch", "Production deployment and go-live"),
    ]
    for phase, (m_name, m_deliverable) in zip(phases, milestone_defs):
        week_cursor += phase["duration_weeks"]
        milestones.append(
            {
                "name": m_name,
                "week": round(week_cursor, 1),
                "deliverable": m_deliverable,
            }
        )

    # ── Critical path ────────────────────────────────────────────
    # The critical path follows the highest-priority task in each phase
    critical_path: list[str] = []
    for phase in phases:
        high_prio = [t for t in phase["tasks"] if t["priority"] == "high"]
        if high_prio:
            critical_path.append(high_prio[0]["name"])
        elif phase["tasks"]:
            critical_path.append(phase["tasks"][0]["name"])

    # ── Risks ────────────────────────────────────────────────────
    risks = list(_DOMAIN_RISKS.get(domain, _DOMAIN_RISKS["generic"]))

    # Add team-size-specific risks
    if team_size == 1:
        risks.append(
            {
                "risk": "Single point of failure — no backup if developer is unavailable",
                "impact": "high",
                "mitigation": "Document decisions and maintain clear commit history for hand-off",
            }
        )
    elif team_size > 4:
        risks.append(
            {
                "risk": "Communication overhead increasing with team size",
                "impact": "medium",
                "mitigation": "Use daily standups, clear ownership, and async updates",
            }
        )

    # Add tight-timeline risk
    hours_per_person_per_week = available_hours / (team_size * duration_weeks)
    if hours_per_person_per_week > 30:
        risks.append(
            {
                "risk": "Aggressive timeline may lead to burnout and quality shortcuts",
                "impact": "high",
                "mitigation": "Prioritize ruthlessly and cut scope before cutting quality",
            }
        )

    # ── Resource allocation ──────────────────────────────────────
    resource_allocation = {
        "planning": round(available_hours * 0.15, 1),
        "execution": round(available_hours * 0.55, 1),
        "testing": round(available_hours * 0.20, 1),
        "buffer": buffer_hours,
    }

    return {
        "description": description,
        "team_size": team_size,
        "duration_weeks": duration_weeks,
        "total_hours": total_hours,
        "phases": phases,
        "milestones": milestones,
        "critical_path": critical_path,
        "risks": risks,
        "resource_allocation": resource_allocation,
    }
