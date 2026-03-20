"""PRD scaffolding tool — structured product requirements document generator."""

from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# PRD section templates
# ---------------------------------------------------------------------------

_PRD_SECTIONS: list[dict] = [
    {
        "name": "Overview",
        "description": "High-level product summary and vision",
        "template": (
            "## 1. Overview\n\n"
            "**Product Name:** {product_name}\n"
            "**Version:** 1.0\n"
            "**Last Updated:** [Date]\n"
            "**Author:** [Name]\n"
            "**Status:** Draft\n\n"
            "### Vision\n"
            "[One sentence describing the product vision]\n\n"
            "### Elevator Pitch\n"
            "For [target users] who [have this problem], "
            "[product name] is a [product category] that [key benefit]. "
            "Unlike [alternatives], our product [key differentiator]."
        ),
    },
    {
        "name": "Problem Statement",
        "description": "Clear articulation of the problem being solved",
        "template": (
            "## 2. Problem Statement\n\n"
            "{problem}\n\n"
            "### Who is affected?\n"
            "[Describe the users experiencing this problem]\n\n"
            "### Current workarounds\n"
            "- [How users currently solve this problem]\n"
            "- [Limitations of current solutions]\n\n"
            "### Impact of not solving\n"
            "[Quantify the cost or impact of the status quo]"
        ),
    },
    {
        "name": "Target Users",
        "description": "User personas and segments",
        "template": (
            "## 3. Target Users\n\n"
            "{user_personas}\n\n"
            "### User Segmentation\n"
            "| Segment | Description | Priority |\n"
            "|---------|-------------|----------|\n"
            "| [Primary] | [description] | P0 |\n"
            "| [Secondary] | [description] | P1 |"
        ),
    },
    {
        "name": "Goals and Non-Goals",
        "description": "What the product will and will not do",
        "template": (
            "## 4. Goals and Non-Goals\n\n"
            "### Goals\n"
            "1. [Goal aligned with solving the stated problem]\n"
            "2. [Goal for user experience or adoption]\n"
            "3. [Goal for business metrics]\n\n"
            "### Non-Goals\n"
            "1. [Explicitly out of scope for this version]\n"
            "2. [Feature or behavior that might be assumed but is not included]\n"
            "3. [Adjacent problem that will not be addressed yet]"
        ),
    },
    {
        "name": "Features",
        "description": "Detailed feature descriptions organized by priority",
        "template": (
            "## 5. Features\n\n"
            "### P0 — Must Have\n"
            "| Feature | Description | Acceptance Criteria |\n"
            "|---------|-------------|--------------------|\n"
            "| [Feature 1] | [description] | [criteria] |\n\n"
            "### P1 — Should Have\n"
            "| Feature | Description | Acceptance Criteria |\n"
            "|---------|-------------|--------------------|\n"
            "| [Feature 2] | [description] | [criteria] |\n\n"
            "### P2 — Nice to Have\n"
            "| Feature | Description | Acceptance Criteria |\n"
            "|---------|-------------|--------------------|\n"
            "| [Feature 3] | [description] | [criteria] |"
        ),
    },
    {
        "name": "User Stories",
        "description": "User stories in standard format with acceptance criteria",
        "template": (
            "## 6. User Stories\n\n"
            "{user_stories}\n\n"
            "### Acceptance Criteria Format\n"
            "{acceptance_criteria}"
        ),
    },
    {
        "name": "Technical Requirements",
        "description": "Non-functional requirements and constraints",
        "template": (
            "## 7. Technical Requirements\n\n"
            "### Performance\n"
            "- Page load time: [target]\n"
            "- API response time: [target]\n"
            "- Concurrent users: [target]\n\n"
            "### Security\n"
            "- Authentication: [method]\n"
            "- Authorization: [model]\n"
            "- Data encryption: [at rest / in transit]\n\n"
            "### Compatibility\n"
            "- Browsers: [list]\n"
            "- Mobile: [iOS/Android versions]\n"
            "- Accessibility: [WCAG level]\n\n"
            "### Infrastructure\n"
            "- Hosting: [platform]\n"
            "- Database: [type]\n"
            "- Third-party services: [list]"
        ),
    },
    {
        "name": "Success Metrics",
        "description": "How product success will be measured",
        "template": (
            "## 8. Success Metrics\n\n"
            "{success_metrics}"
        ),
    },
    {
        "name": "Timeline",
        "description": "High-level release timeline",
        "template": (
            "## 9. Timeline\n\n"
            "| Milestone | Target Date | Description |\n"
            "|-----------|-------------|-------------|\n"
            "| Alpha | [date] | Core features complete, internal testing |\n"
            "| Beta | [date] | Feature complete, limited external testing |\n"
            "| GA | [date] | Production release |\n\n"
            "### Dependencies\n"
            "- [External dependency 1]\n"
            "- [External dependency 2]"
        ),
    },
    {
        "name": "Risks and Mitigations",
        "description": "Known risks and mitigation strategies",
        "template": (
            "## 10. Risks and Mitigations\n\n"
            "| Risk | Likelihood | Impact | Mitigation |\n"
            "|------|-----------|--------|------------|\n"
            "| [Risk 1] | [H/M/L] | [H/M/L] | [Strategy] |\n"
            "| [Risk 2] | [H/M/L] | [H/M/L] | [Strategy] |"
        ),
    },
]


# ---------------------------------------------------------------------------
# Problem-based keyword detection for user stories
# ---------------------------------------------------------------------------

_PROBLEM_KEYWORDS: dict[str, list[dict]] = {
    "search": [
        {"action": "search for items using keywords", "benefit": "I can quickly find what I need"},
        {"action": "filter search results by category", "benefit": "I can narrow down results efficiently"},
        {"action": "save my search queries", "benefit": "I can re-run frequent searches without retyping"},
    ],
    "auth": [
        {"action": "create an account with my email", "benefit": "I can access personalized features"},
        {"action": "log in securely", "benefit": "my data is protected"},
        {"action": "reset my password", "benefit": "I can regain access if I forget my credentials"},
    ],
    "payment": [
        {"action": "add items to a shopping cart", "benefit": "I can purchase multiple items at once"},
        {"action": "check out with my preferred payment method", "benefit": "the purchase process is convenient"},
        {"action": "view my order history", "benefit": "I can track my past purchases"},
    ],
    "dashboard": [
        {"action": "view key metrics on a single dashboard", "benefit": "I can quickly assess performance"},
        {"action": "customize which metrics are displayed", "benefit": "I see the most relevant data for my role"},
        {"action": "export dashboard data", "benefit": "I can share reports with stakeholders"},
    ],
    "collaboration": [
        {"action": "share documents with my team", "benefit": "we can collaborate in real time"},
        {"action": "leave comments on shared items", "benefit": "I can provide feedback asynchronously"},
        {"action": "track changes made by team members", "benefit": "I know who changed what and when"},
    ],
    "notification": [
        {"action": "receive notifications for important events", "benefit": "I stay informed without checking constantly"},
        {"action": "customize my notification preferences", "benefit": "I only receive relevant alerts"},
        {"action": "view a history of past notifications", "benefit": "I can catch up on missed updates"},
    ],
    "content": [
        {"action": "create and publish content", "benefit": "I can share information with my audience"},
        {"action": "edit content with a rich text editor", "benefit": "my content looks professional"},
        {"action": "schedule content for future publication", "benefit": "I can plan my content calendar"},
    ],
    "profile": [
        {"action": "update my profile information", "benefit": "my account reflects my current details"},
        {"action": "upload a profile picture", "benefit": "others can recognize me"},
        {"action": "manage my privacy settings", "benefit": "I control what others can see about me"},
    ],
}

_DEFAULT_STORIES = [
    {"action": "complete the primary workflow", "benefit": "I achieve my main goal efficiently"},
    {"action": "undo my last action", "benefit": "I can recover from mistakes"},
    {"action": "access the product on my mobile device", "benefit": "I can use it on the go"},
    {"action": "get help when I am stuck", "benefit": "I can resolve issues without external support"},
    {"action": "customize my experience", "benefit": "the product fits my personal workflow"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_target_users(target_users: str) -> list[str]:
    """Parse target users from comma-separated string."""
    if not target_users.strip():
        return ["General User"]
    return [u.strip() for u in target_users.split(",") if u.strip()]


def _detect_problem_domains(problem: str) -> list[str]:
    """Detect which problem domains are relevant from the problem description."""
    lower = problem.lower()
    detected: list[str] = []

    domain_detection: dict[str, list[str]] = {
        "search": ["search", "find", "discover", "browse", "lookup", "filter", "query"],
        "auth": ["login", "sign up", "register", "authenticate", "password", "account", "sso"],
        "payment": ["pay", "purchase", "buy", "checkout", "cart", "order", "billing", "subscription"],
        "dashboard": ["dashboard", "analytics", "metrics", "report", "kpi", "monitor", "visualize"],
        "collaboration": ["collaborate", "team", "share", "comment", "review", "real-time", "workspace"],
        "notification": ["notify", "alert", "notification", "remind", "update", "email", "push"],
        "content": ["content", "publish", "blog", "article", "cms", "editor", "post", "write"],
        "profile": ["profile", "settings", "preferences", "customize", "personal", "avatar"],
    }

    for domain, keywords in domain_detection.items():
        if any(kw in lower for kw in keywords):
            detected.append(domain)

    return detected


def _generate_user_stories(
    problem: str,
    personas: list[str],
) -> list[dict]:
    """Generate user stories based on problem domains and personas."""
    domains = _detect_problem_domains(problem)
    story_templates: list[dict] = []

    # Gather stories from detected domains
    for domain in domains:
        story_templates.extend(_PROBLEM_KEYWORDS.get(domain, []))

    # Fill with defaults if not enough
    if len(story_templates) < 3:
        for default in _DEFAULT_STORIES:
            if len(story_templates) >= 5:
                break
            if default not in story_templates:
                story_templates.append(default)

    # Limit to 5 stories
    story_templates = story_templates[:5]

    # Assign personas round-robin
    stories: list[dict] = []
    for i, tmpl in enumerate(story_templates):
        persona = personas[i % len(personas)] if personas else "User"
        story = {
            "persona": persona,
            "action": tmpl["action"],
            "benefit": tmpl["benefit"],
            "format": f"As a {persona}, I want to {tmpl['action']}, so that {tmpl['benefit']}",
        }
        stories.append(story)

    return stories


def _generate_acceptance_criteria(stories: list[dict]) -> dict:
    """Generate acceptance criteria format with examples."""
    template = "Given [context], When [action], Then [expected result]"

    examples: list[str] = []
    for story in stories[:3]:
        action_short = story["action"].split()[0:4]
        action_str = " ".join(action_short)
        examples.append(
            f"Given I am a logged-in {story['persona']}, "
            f"When I {action_str}, "
            f"Then the system should confirm the action was successful"
        )

    return {
        "template": template,
        "examples": examples,
    }


def _generate_success_metrics(problem: str, personas: list[str]) -> list[dict]:
    """Generate success metrics based on problem context."""
    base_metrics: list[dict] = [
        {
            "metric": "User Adoption Rate",
            "target": "1,000 active users within 3 months of launch",
            "measurement": "Count of users who complete onboarding and perform the core action at least once",
        },
        {
            "metric": "Task Completion Rate",
            "target": "85% of users complete the primary workflow without errors",
            "measurement": "Funnel analysis of primary user flow from start to completion",
        },
        {
            "metric": "User Satisfaction (NPS)",
            "target": "NPS score of 40+",
            "measurement": "In-app NPS survey sent 14 days after sign-up",
        },
    ]

    # Add problem-specific metrics
    lower = problem.lower()

    if any(w in lower for w in ["slow", "performance", "speed", "fast", "efficient"]):
        base_metrics.append({
            "metric": "Time to Complete Primary Task",
            "target": "50% reduction from current baseline",
            "measurement": "Average time from task start to completion, measured via event tracking",
        })

    if any(w in lower for w in ["error", "bug", "reliable", "crash", "fail"]):
        base_metrics.append({
            "metric": "Error Rate",
            "target": "Less than 1% of user sessions encounter an error",
            "measurement": "Error logging and monitoring dashboard",
        })

    if any(w in lower for w in ["engage", "retention", "return", "daily", "active"]):
        base_metrics.append({
            "metric": "Weekly Active Users (WAU) / Monthly Active Users (MAU)",
            "target": "WAU/MAU ratio above 40%",
            "measurement": "Analytics dashboard tracking unique active users per period",
        })

    if any(w in lower for w in ["revenue", "monetize", "conversion", "purchase", "subscribe"]):
        base_metrics.append({
            "metric": "Conversion Rate",
            "target": "3% free-to-paid conversion within 30 days",
            "measurement": "Funnel analysis from sign-up to first purchase/subscription",
        })

    if any(w in lower for w in ["support", "help", "ticket", "complaint"]):
        base_metrics.append({
            "metric": "Support Ticket Reduction",
            "target": "30% reduction in support tickets related to this problem area",
            "measurement": "Compare ticket volume before and after launch, filtered by category",
        })

    return base_metrics


def _build_persona_sections(personas: list[str], problem: str) -> str:
    """Build persona description sections."""
    if len(personas) == 1 and personas[0] == "General User":
        return (
            "### Primary Persona: General User\n"
            "- **Description:** [Describe the typical user]\n"
            "- **Goals:** [What they want to achieve]\n"
            "- **Pain Points:** [Current frustrations related to the problem]\n"
            "- **Technical Proficiency:** [Low/Medium/High]"
        )

    sections: list[str] = []
    for i, persona in enumerate(personas):
        priority = "Primary" if i == 0 else "Secondary"
        sections.append(
            f"### {priority} Persona: {persona}\n"
            f"- **Description:** [Describe a typical {persona}]\n"
            f"- **Goals:** [What a {persona} wants to achieve]\n"
            f"- **Pain Points:** [Current frustrations for {persona}]\n"
            f"- **Technical Proficiency:** [Low/Medium/High]"
        )

    return "\n\n".join(sections)


def _check_requirements_completeness(
    problem: str, personas: list[str], stories: list[dict],
) -> dict:
    """Check requirements completeness with gap analysis."""
    issues: list[str] = []
    score = 100

    # Check problem statement quality
    if len(problem.split()) < 10:
        issues.append("Problem statement is too brief — aim for 2+ sentences")
        score -= 15
    if not any(w in problem.lower() for w in ["need", "struggle", "lack", "cannot", "difficult", "slow", "no way"]):
        issues.append("Problem statement lacks pain language — quantify the user pain")
        score -= 10

    # Check persona coverage
    if len(personas) <= 1 and personas[0] == "General User":
        issues.append("No specific personas defined — identify at least 2 user types")
        score -= 15

    # Check story coverage
    if len(stories) < 3:
        issues.append(f"Only {len(stories)} user stories — aim for 5+ to cover core workflows")
        score -= 10

    # Check if all personas have stories
    personas_with_stories = {s.get("persona") for s in stories}
    for p in personas:
        if p not in personas_with_stories:
            issues.append(f"Persona '{p}' has no user stories")
            score -= 5

    # Check for measurable goals
    measurable_words = ["increase", "decrease", "reduce", "improve", "achieve", "%", "number", "rate"]
    if not any(w in problem.lower() for w in measurable_words):
        issues.append("No measurable goals detected — add quantifiable success criteria")
        score -= 10

    return {"score": max(0, score), "issues": issues}


def _validate_user_story_quality(stories: list[dict]) -> dict:
    """Validate each user story for completeness and specificity."""
    results: list[dict] = []
    total_score = 0

    for story in stories:
        issues: list[str] = []
        story_score = 100

        persona = story.get("persona", "")
        action = story.get("action", "")
        benefit = story.get("benefit", "")

        # Check persona specificity
        if persona.lower() in ("user", "general user", ""):
            issues.append("Persona is too generic — use specific role names")
            story_score -= 20

        # Check action specificity
        if len(action.split()) < 3:
            issues.append("Action is too vague — describe the specific interaction")
            story_score -= 20

        # Check benefit clarity
        if len(benefit.split()) < 3:
            issues.append("Benefit is too vague — quantify the value")
            story_score -= 20

        # Check for acceptance-criteria-ready language
        if not any(w in action.lower() for w in ["create", "view", "update", "delete", "search", "filter", "submit", "select", "upload", "download", "share", "export"]):
            issues.append("Action may be hard to turn into acceptance criteria — use specific verbs")
            story_score -= 10

        total_score += max(0, story_score)
        results.append({
            "story": story.get("format", ""),
            "score": max(0, story_score),
            "issues": issues,
        })

    avg = round(total_score / len(stories), 1) if stories else 0
    return {"stories": results, "average_score": avg}


def _detect_feature_dependencies(stories: list[dict]) -> list[dict]:
    """Detect likely dependencies between user stories based on domain rules."""
    dependency_rules = {
        "auth": {
            "keywords": ["log in", "sign up", "register", "authenticate", "account", "password"],
            "blocks": ["payment", "dashboard", "profile", "settings", "share", "collaborate"],
        },
        "data_model": {
            "keywords": ["create", "add", "define", "set up"],
            "blocks": ["view", "filter", "search", "export", "report", "dashboard", "analytics"],
        },
        "profile": {
            "keywords": ["profile", "account", "settings"],
            "blocks": ["customize", "preference", "notification settings"],
        },
    }

    dependencies: list[dict] = []
    for rule_name, rule in dependency_rules.items():
        prereq_stories = []
        dependent_stories = []
        for i, story in enumerate(stories):
            action = story.get("action", "").lower()
            if any(kw in action for kw in rule["keywords"]):
                prereq_stories.append(i)
            if any(kw in action for kw in rule["blocks"]):
                dependent_stories.append(i)

        for dep in dependent_stories:
            for pre in prereq_stories:
                if dep != pre:
                    dependencies.append({
                        "rule": rule_name,
                        "prerequisite": f"US-{pre + 1}",
                        "dependent": f"US-{dep + 1}",
                    })

    return dependencies


def _compute_moscow_scores(stories: list[dict], domains: list[str]) -> dict:
    """Assign MoSCoW priorities based on domain relevance."""
    must_have: list[str] = []
    should_have: list[str] = []
    could_have: list[str] = []
    wont_have: list[str] = []

    for i, story in enumerate(stories):
        action = story.get("action", "").lower()
        label = f"US-{i + 1}: {story.get('action', '')}"

        if any(kw in action for kw in ["log in", "sign up", "create", "search", "pay", "checkout"]):
            must_have.append(label)
        elif any(kw in action for kw in ["filter", "view", "track", "update"]):
            should_have.append(label)
        elif any(kw in action for kw in ["customize", "export", "share", "schedule"]):
            could_have.append(label)
        else:
            should_have.append(label)  # default to should-have

    return {
        "must_have": must_have,
        "should_have": should_have,
        "could_have": could_have,
        "wont_have": wont_have,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scaffold_prd(
    product_name: str,
    problem: str,
    target_users: str = "",
) -> dict:
    """Generate a structured PRD scaffold with user stories and prioritization.

    Args:
        product_name: Name of the product.
        problem: Problem statement the product addresses.
        target_users: Comma-separated list of target user types/personas.

    Returns:
        Dictionary with PRD sections, user stories, acceptance criteria,
        MoSCoW prioritization framework, and success metrics.
    """
    personas = _parse_target_users(target_users)
    user_stories = _generate_user_stories(problem, personas)
    acceptance_criteria = _generate_acceptance_criteria(user_stories)
    success_metrics = _generate_success_metrics(problem, personas)

    # ── Format user stories for template ─────────────────────────
    stories_text = "\n\n".join(
        f"**US-{i+1}:** {s['format']}"
        for i, s in enumerate(user_stories)
    )

    ac_examples_text = "\n".join(
        f"- {ex}" for ex in acceptance_criteria["examples"]
    )
    ac_text = (
        f"**Template:** {acceptance_criteria['template']}\n\n"
        f"**Examples:**\n{ac_examples_text}"
    )

    # ── Format success metrics for template ──────────────────────
    metrics_text = (
        "| Metric | Target | Measurement |\n"
        "|--------|--------|-------------|\n"
    )
    for m in success_metrics:
        metrics_text += f"| {m['metric']} | {m['target']} | {m['measurement']} |\n"

    # ── Build persona text ───────────────────────────────────────
    persona_text = _build_persona_sections(personas, problem)

    # ── Build sections ───────────────────────────────────────────
    sections: list[dict] = []
    for sec in _PRD_SECTIONS:
        template = sec["template"]

        # Perform template substitutions
        template = template.replace("{product_name}", product_name)
        template = template.replace("{problem}", problem)
        template = template.replace("{user_personas}", persona_text)
        template = template.replace("{user_stories}", stories_text)
        template = template.replace("{acceptance_criteria}", ac_text)
        template = template.replace("{success_metrics}", metrics_text)

        sections.append({
            "name": sec["name"],
            "description": sec["description"],
            "template": template,
        })

    # ── MoSCoW prioritization (computed) ─────────────────────────
    domains = _detect_problem_domains(problem)
    moscow = _compute_moscow_scores(user_stories, domains)
    prioritization = {
        "framework": "MoSCoW",
        "categories": moscow,
    }

    # ── Requirements analysis ────────────────────────────────────
    completeness = _check_requirements_completeness(problem, personas, user_stories)
    story_quality = _validate_user_story_quality(user_stories)
    dependencies = _detect_feature_dependencies(user_stories)

    return {
        "product_name": product_name,
        "problem_statement": problem,
        "target_users": personas,
        "sections": sections,
        "user_stories": user_stories,
        "acceptance_criteria_format": acceptance_criteria,
        "prioritization": prioritization,
        "success_metrics": success_metrics,
        "requirements_analysis": {
            "completeness": completeness,
            "story_quality": story_quality,
            "dependencies": dependencies,
        },
    }
