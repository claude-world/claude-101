"""Interview preparation tool — role-based question generation with STAR templates."""

from __future__ import annotations

import re

from .._utils import text_structure_check, count_pattern_matches


# ---------------------------------------------------------------------------
# Level configuration
# ---------------------------------------------------------------------------

_LEVELS = {
    "junior": {
        "difficulty_range": ["easy", "easy", "medium"],
        "years": "0-2",
        "focus_areas": ["fundamentals", "learning ability", "teamwork"],
        "question_count": 8,
    },
    "mid": {
        "difficulty_range": ["easy", "medium", "medium"],
        "years": "2-5",
        "focus_areas": ["problem solving", "ownership", "collaboration"],
        "question_count": 10,
    },
    "senior": {
        "difficulty_range": ["medium", "medium", "hard"],
        "years": "5-8",
        "focus_areas": ["system design", "mentorship", "technical leadership"],
        "question_count": 10,
    },
    "lead": {
        "difficulty_range": ["medium", "hard", "hard"],
        "years": "8+",
        "focus_areas": ["architecture", "team building", "strategic planning"],
        "question_count": 12,
    },
    "executive": {
        "difficulty_range": ["hard", "hard", "hard"],
        "years": "10+",
        "focus_areas": ["vision", "organizational leadership", "business strategy"],
        "question_count": 12,
    },
}

# ---------------------------------------------------------------------------
# Role detection and question banks
# ---------------------------------------------------------------------------

_ROLE_TYPES = {
    "technical": [
        "engineer",
        "developer",
        "programmer",
        "devops",
        "sre",
        "backend",
        "frontend",
        "fullstack",
        "full-stack",
        "architect",
        "infrastructure",
        "platform",
        "security",
    ],
    "manager": [
        "manager",
        "director",
        "vp",
        "head of",
        "lead",
        "chief",
        "cto",
        "cio",
        "coo",
        "scrum master",
        "product owner",
    ],
    "designer": [
        "designer",
        "ux",
        "ui",
        "product design",
        "graphic",
        "visual",
        "interaction",
        "design lead",
    ],
    "data": [
        "data",
        "analyst",
        "scientist",
        "machine learning",
        "ml",
        "ai",
        "analytics",
        "business intelligence",
        "statistician",
    ],
    "product": ["product manager", "product", "pm", "growth", "strategy"],
}

_TECHNICAL_QUESTIONS = {
    "technical": [
        {
            "question": "Describe a system you designed from scratch. What trade-offs did you make?",
            "difficulty": "hard",
            "star": {
                "situation": "Describe the business need and constraints you faced",
                "task": "Explain what you were responsible for designing",
                "action": "Detail the architecture decisions and trade-offs you made",
                "result": "Share the outcome — performance, scalability, team adoption",
            },
        },
        {
            "question": "How do you approach debugging a production issue you've never seen before?",
            "difficulty": "medium",
            "star": {
                "situation": "A critical production issue appeared with no prior precedent",
                "task": "You needed to diagnose and resolve it under time pressure",
                "action": "Describe your systematic debugging approach step by step",
                "result": "Explain the resolution and what you put in place to prevent recurrence",
            },
        },
        {
            "question": "Tell me about a time you had to learn a new technology quickly for a project.",
            "difficulty": "easy",
            "star": {
                "situation": "A project required technology outside your current expertise",
                "task": "You needed to become productive with it in a short timeframe",
                "action": "Describe your learning strategy and resources used",
                "result": "Share how quickly you became productive and the project outcome",
            },
        },
        {
            "question": "How would you improve the performance of a slow database query?",
            "difficulty": "medium",
            "star": {
                "situation": "A critical query was causing page load times over 10 seconds",
                "task": "You were asked to optimize it without changing the feature behavior",
                "action": "Explain the profiling, indexing, and query rewriting steps you took",
                "result": "Share the performance improvement metrics",
            },
        },
        {
            "question": "Describe your approach to code review. What do you look for?",
            "difficulty": "easy",
            "star": {
                "situation": "Your team established a code review process",
                "task": "You needed to review code effectively and provide constructive feedback",
                "action": "Describe what you check for and how you communicate feedback",
                "result": "Explain how code quality improved and team knowledge grew",
            },
        },
        {
            "question": "How do you decide between building vs. buying a solution?",
            "difficulty": "hard",
            "star": {
                "situation": "The team needed functionality that could be built or purchased",
                "task": "You were responsible for the technical recommendation",
                "action": "Describe the evaluation criteria: cost, fit, maintenance, risk",
                "result": "Share the decision made and its long-term outcome",
            },
        },
        {
            "question": "Walk me through how you would design a rate limiter.",
            "difficulty": "medium",
            "star": {
                "situation": "An API needed protection from abuse and traffic spikes",
                "task": "Design a rate limiting solution with specific requirements",
                "action": "Describe algorithm choice (token bucket, sliding window), storage, and failure modes",
                "result": "Explain expected behavior under load and monitoring approach",
            },
        },
        {
            "question": "Tell me about a time you refactored a significant piece of legacy code.",
            "difficulty": "medium",
            "star": {
                "situation": "A legacy codebase was hindering feature development",
                "task": "You needed to refactor it without breaking existing functionality",
                "action": "Describe your strategy: test coverage first, incremental changes, rollback plan",
                "result": "Share the improvement in development velocity and code health metrics",
            },
        },
    ],
    "behavioral": [
        {
            "question": "Tell me about a time you disagreed with a teammate on a technical decision.",
            "difficulty": "medium",
            "star": {
                "situation": "You and a teammate had conflicting views on a technical approach",
                "task": "You needed to resolve the disagreement and move forward",
                "action": "Describe how you presented your case and listened to theirs",
                "result": "Explain the resolution and what you learned from the experience",
            },
        },
        {
            "question": "Describe a project where you had to manage competing priorities.",
            "difficulty": "medium",
            "star": {
                "situation": "Multiple stakeholders needed different things simultaneously",
                "task": "You had to prioritize and deliver within constraints",
                "action": "Explain your prioritization framework and stakeholder communication",
                "result": "Share what was delivered and stakeholder satisfaction",
            },
        },
        {
            "question": "Tell me about a failure and what you learned from it.",
            "difficulty": "easy",
            "star": {
                "situation": "A project or decision did not go as planned",
                "task": "You needed to address the failure and learn from it",
                "action": "Describe what went wrong and the corrective steps you took",
                "result": "Share the lessons learned and how you applied them later",
            },
        },
        {
            "question": "How do you handle receiving critical feedback?",
            "difficulty": "easy",
            "star": {
                "situation": "You received tough feedback from a manager or peer",
                "task": "You needed to process the feedback and act on it",
                "action": "Describe your reaction and the steps you took to improve",
                "result": "Explain how the feedback changed your approach going forward",
            },
        },
    ],
    "situational": [
        {
            "question": "Your team is behind schedule on a critical deadline. What do you do?",
            "difficulty": "medium",
            "star": {
                "situation": "The project is at risk of missing its deadline",
                "task": "You need to get the project back on track",
                "action": "Describe scope negotiation, resource reallocation, or timeline adjustment",
                "result": "Explain the outcome and how you communicated the situation",
            },
        },
        {
            "question": "A junior developer keeps making the same mistakes in code reviews. How do you handle it?",
            "difficulty": "medium",
            "star": {
                "situation": "A team member is repeatedly making similar errors",
                "task": "You need to help them improve without demoralizing them",
                "action": "Describe your mentoring approach: pairing, documentation, check-ins",
                "result": "Share the improvement in their code quality over time",
            },
        },
    ],
    "culture_fit": [
        {
            "question": "What kind of engineering culture do you thrive in?",
            "difficulty": "easy",
            "star": {
                "situation": "Reflect on past work environments",
                "task": "Identify what made you most productive and engaged",
                "action": "Describe specific cultural elements: autonomy, collaboration, innovation",
                "result": "Connect it to why this company's culture appeals to you",
            },
        },
        {
            "question": "How do you stay current with technology trends?",
            "difficulty": "easy",
            "star": {
                "situation": "Technology evolves rapidly in your field",
                "task": "You need to keep your skills relevant",
                "action": "Describe your learning habits: reading, side projects, conferences, communities",
                "result": "Share a specific technology you adopted early and its impact",
            },
        },
    ],
}

_MANAGER_QUESTIONS = {
    "technical": [
        {
            "question": "How do you balance technical debt with feature delivery?",
            "difficulty": "hard",
            "star": {
                "situation": "The team faced growing technical debt while stakeholders demanded new features",
                "task": "You needed a sustainable strategy for both",
                "action": "Describe how you quantified tech debt and negotiated time allocation",
                "result": "Share the long-term impact on velocity and team morale",
            },
        },
        {
            "question": "Describe how you've built and scaled an engineering team.",
            "difficulty": "hard",
            "star": {
                "situation": "The organization needed to grow the engineering team significantly",
                "task": "You were responsible for hiring and onboarding strategy",
                "action": "Describe your hiring process, onboarding, and culture-building efforts",
                "result": "Share team growth metrics and retention rates",
            },
        },
    ],
    "behavioral": [
        {
            "question": "Tell me about a time you had to deliver difficult feedback to a direct report.",
            "difficulty": "medium",
            "star": {
                "situation": "A direct report's performance or behavior needed correction",
                "task": "You needed to address it constructively",
                "action": "Describe your preparation and the conversation approach",
                "result": "Share the outcome and how the relationship evolved",
            },
        },
        {
            "question": "How do you handle a situation where two teams have conflicting priorities?",
            "difficulty": "hard",
            "star": {
                "situation": "Two teams under your purview had conflicting resource needs",
                "task": "You needed to resolve the conflict and keep both productive",
                "action": "Describe negotiation, escalation, or creative reallocation",
                "result": "Explain the resolution and lessons for future resource planning",
            },
        },
        {
            "question": "Describe a time you championed an unpopular decision that turned out well.",
            "difficulty": "medium",
            "star": {
                "situation": "You believed in a direction that others resisted",
                "task": "You needed to build support and execute on the decision",
                "action": "Describe how you communicated your reasoning and built consensus",
                "result": "Share the outcome and how it affected trust in your judgment",
            },
        },
    ],
    "situational": [
        {
            "question": "One of your top performers wants to leave. What do you do?",
            "difficulty": "medium",
            "star": {
                "situation": "A high-value team member expressed intent to leave",
                "task": "You need to understand their motivation and respond appropriately",
                "action": "Describe the conversation, what you offered, and decision framework",
                "result": "Whether they stayed or left, explain how you handled the transition",
            },
        },
    ],
    "culture_fit": [
        {
            "question": "What is your management philosophy?",
            "difficulty": "easy",
            "star": {
                "situation": "Reflect on your leadership experiences",
                "task": "Articulate your core management principles",
                "action": "Describe specific practices: 1-on-1s, autonomy, accountability",
                "result": "Share evidence of these principles working in practice",
            },
        },
    ],
}

_DESIGNER_QUESTIONS = {
    "technical": [
        {
            "question": "Walk me through your design process for a recent project.",
            "difficulty": "medium",
            "star": {
                "situation": "A new feature or product needed design work",
                "task": "You were responsible for the end-to-end design",
                "action": "Describe research, ideation, prototyping, testing, and iteration",
                "result": "Share user feedback and business impact of the final design",
            },
        },
        {
            "question": "How do you handle design critiques and iterate based on feedback?",
            "difficulty": "easy",
            "star": {
                "situation": "Your design received critical feedback from stakeholders or users",
                "task": "You needed to incorporate feedback while maintaining design integrity",
                "action": "Describe how you evaluated which feedback to act on",
                "result": "Share how the design improved through iteration",
            },
        },
    ],
    "behavioral": _TECHNICAL_QUESTIONS["behavioral"],
    "situational": [
        {
            "question": "Engineering says your design is too complex to build in the timeline. What do you do?",
            "difficulty": "medium",
            "star": {
                "situation": "There was a gap between design vision and engineering feasibility",
                "task": "You needed to find a compromise without sacrificing user experience",
                "action": "Describe collaboration with engineers on phased delivery or simplification",
                "result": "Explain the shipped solution and user reception",
            },
        },
    ],
    "culture_fit": _TECHNICAL_QUESTIONS["culture_fit"],
}

_DATA_QUESTIONS = {
    "technical": [
        {
            "question": "Describe a data analysis that changed a business decision.",
            "difficulty": "medium",
            "star": {
                "situation": "The business needed data to inform a strategic decision",
                "task": "You were responsible for the analysis and recommendation",
                "action": "Describe data collection, methodology, and how you presented findings",
                "result": "Share the business decision made and its measurable impact",
            },
        },
        {
            "question": "How do you ensure data quality in your pipelines?",
            "difficulty": "medium",
            "star": {
                "situation": "Data quality issues were affecting downstream consumers",
                "task": "You needed to implement a data quality framework",
                "action": "Describe validation rules, monitoring, and alerting you set up",
                "result": "Share the reduction in data quality incidents",
            },
        },
        {
            "question": "Explain a complex technical concept to a non-technical stakeholder.",
            "difficulty": "easy",
            "star": {
                "situation": "A non-technical audience needed to understand a data concept",
                "task": "You had to explain it clearly without jargon",
                "action": "Describe analogies, visualizations, or frameworks you used",
                "result": "Share how the stakeholder's understanding improved their decision-making",
            },
        },
    ],
    "behavioral": _TECHNICAL_QUESTIONS["behavioral"],
    "situational": _TECHNICAL_QUESTIONS["situational"],
    "culture_fit": _TECHNICAL_QUESTIONS["culture_fit"],
}

_PRODUCT_QUESTIONS = {
    "technical": [
        {
            "question": "How do you prioritize features when everything seems important?",
            "difficulty": "medium",
            "star": {
                "situation": "Multiple high-priority features competing for limited resources",
                "task": "You needed a systematic way to prioritize",
                "action": "Describe frameworks used (RICE, impact/effort, user research data)",
                "result": "Share the prioritized roadmap and business outcomes",
            },
        },
        {
            "question": "Describe a product you shipped that didn't meet expectations. What happened?",
            "difficulty": "hard",
            "star": {
                "situation": "A shipped product underperformed against targets",
                "task": "You needed to diagnose the problem and course-correct",
                "action": "Describe your analysis of what went wrong and recovery plan",
                "result": "Share what you changed and the eventual outcome",
            },
        },
    ],
    "behavioral": _MANAGER_QUESTIONS["behavioral"][:2]
    + _TECHNICAL_QUESTIONS["behavioral"][:2],
    "situational": _TECHNICAL_QUESTIONS["situational"],
    "culture_fit": _TECHNICAL_QUESTIONS["culture_fit"],
}

_ROLE_QUESTION_BANKS: dict[str, dict] = {
    "technical": _TECHNICAL_QUESTIONS,
    "manager": _MANAGER_QUESTIONS,
    "designer": _DESIGNER_QUESTIONS,
    "data": _DATA_QUESTIONS,
    "product": _PRODUCT_QUESTIONS,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _detect_role_type(role: str) -> str:
    """Detect role type from role title keywords."""
    lower = role.lower()
    for role_type, keywords in _ROLE_TYPES.items():
        if any(kw in lower for kw in keywords):
            return role_type
    return "technical"  # default


def _pick_difficulty(level_config: dict, index: int) -> str:
    """Cycle through difficulty range for question selection."""
    dr = level_config["difficulty_range"]
    return dr[index % len(dr)]


def _select_questions(
    bank: dict[str, list[dict]],
    level: str,
    focus: str,
    count: int,
) -> list[dict]:
    """Select and tag questions from the bank, respecting level and focus."""
    level_config = _LEVELS.get(level, _LEVELS["mid"])
    selected: list[dict] = []

    # Determine category weights based on focus
    categories = list(bank.keys())
    weights: dict[str, float] = {cat: 1.0 for cat in categories}

    if focus:
        focus_lower = focus.lower()
        for cat in categories:
            if focus_lower in cat.lower() or cat.lower() in focus_lower:
                weights[cat] = 3.0

    # Sort categories by weight (highest first)
    sorted_cats = sorted(categories, key=lambda c: weights[c], reverse=True)

    # Distribute count across categories proportionally
    total_weight = sum(weights[c] for c in sorted_cats)
    cat_counts: dict[str, int] = {}
    remaining = count
    for i, cat in enumerate(sorted_cats):
        if i == len(sorted_cats) - 1:
            cat_counts[cat] = remaining
        else:
            n = max(1, round(count * weights[cat] / total_weight))
            cat_counts[cat] = min(n, remaining)
            remaining -= cat_counts[cat]

    # Select questions from each category
    for cat in sorted_cats:
        questions = bank.get(cat, [])
        n_to_pick = min(cat_counts.get(cat, 0), len(questions))

        # Filter by difficulty preference
        target_difficulties = set(level_config["difficulty_range"])
        preferred = [q for q in questions if q.get("difficulty") in target_difficulties]
        if len(preferred) < n_to_pick:
            preferred = questions  # fall back to all

        for q in preferred[:n_to_pick]:
            entry: dict = {
                "category": cat,
                "question": q["question"],
                "difficulty": q.get("difficulty", "medium"),
            }
            if "star" in q:
                entry["star_template"] = q["star"]
            selected.append(entry)

    return selected[:count]


def _technical_topics(role_type: str, level: str) -> list[str]:
    """Generate technical topics to study based on role and level."""
    base_topics: dict[str, list[str]] = {
        "technical": [
            "Data structures and algorithms",
            "System design and architecture",
            "Design patterns",
            "Testing strategies",
            "Version control best practices",
            "CI/CD and deployment",
            "Security fundamentals",
            "Performance optimization",
        ],
        "manager": [
            "Agile and Scrum methodologies",
            "Engineering metrics (DORA, velocity)",
            "Technical architecture review",
            "Incident management processes",
            "Capacity planning",
            "Technical roadmap creation",
        ],
        "designer": [
            "Design systems and component libraries",
            "User research methodologies",
            "Accessibility standards (WCAG)",
            "Prototyping tools proficiency",
            "Information architecture",
            "Interaction design patterns",
        ],
        "data": [
            "SQL and query optimization",
            "Statistical methods and hypothesis testing",
            "Data modeling and warehousing",
            "ETL pipeline design",
            "Data visualization best practices",
            "Machine learning fundamentals",
        ],
        "product": [
            "Product analytics and metrics",
            "A/B testing methodology",
            "User research and personas",
            "Roadmap prioritization frameworks",
            "Go-to-market strategy",
            "Competitive analysis",
        ],
    }

    topics = list(base_topics.get(role_type, base_topics["technical"]))

    # Add level-specific topics
    if level in ("senior", "lead", "executive"):
        topics.extend(
            [
                "Cross-team collaboration",
                "Mentoring and knowledge sharing",
                "Strategic planning",
            ]
        )
    if level in ("lead", "executive"):
        topics.extend(
            [
                "Organizational design",
                "Budget and resource management",
            ]
        )

    return topics


def _behavioral_topics(level: str) -> list[str]:
    """Generate behavioral topics based on seniority level."""
    base = [
        "Conflict resolution",
        "Communication skills",
        "Time management",
        "Adaptability to change",
    ]

    level_additions: dict[str, list[str]] = {
        "junior": ["Willingness to learn", "Following processes", "Asking for help"],
        "mid": [
            "Taking ownership",
            "Proactive problem solving",
            "Cross-team collaboration",
        ],
        "senior": ["Mentorship", "Technical decision making", "Stakeholder management"],
        "lead": ["Team building", "Strategic vision", "Driving organizational change"],
        "executive": [
            "Company-wide impact",
            "Board communication",
            "Industry thought leadership",
        ],
    }

    return base + level_additions.get(level, level_additions["mid"])


def _questions_to_ask(role_type: str, level: str) -> list[str]:
    """Generate questions the candidate should ask the interviewer."""
    base = [
        "What does success look like in this role in the first 90 days?",
        "How does the team handle technical disagreements?",
        "What is the biggest challenge the team is facing right now?",
    ]

    role_specific: dict[str, list[str]] = {
        "technical": [
            "What does the tech stack look like, and are there plans to change it?",
            "How do you balance feature work with technical debt?",
            "What does the code review process look like?",
            "How are on-call rotations handled?",
        ],
        "manager": [
            "What is the current team size and any planned growth?",
            "How is engineering success measured here?",
            "What is the relationship between engineering and product?",
            "How much autonomy do engineering managers have in team decisions?",
        ],
        "designer": [
            "How involved are designers in product discovery?",
            "What design tools does the team use?",
            "How is design quality measured?",
            "What is the designer-to-engineer ratio?",
        ],
        "data": [
            "What data infrastructure is currently in place?",
            "How data-driven is the decision-making culture?",
            "What is the data team's relationship with engineering?",
            "What data governance practices are in place?",
        ],
        "product": [
            "How are product decisions made? Who has final say?",
            "What is the product development lifecycle here?",
            "How does the team gather and prioritize user feedback?",
            "What metrics does the team track most closely?",
        ],
    }

    questions = base + role_specific.get(role_type, role_specific["technical"])

    if level in ("lead", "executive"):
        questions.extend(
            [
                "What is the company's 3-year vision?",
                "How does this role influence company strategy?",
            ]
        )

    return questions


def _common_pitfalls(level: str) -> list[str]:
    """Generate common interview pitfalls based on level."""
    base = [
        "Giving vague answers without specific examples",
        "Speaking negatively about previous employers or colleagues",
        "Not asking any questions when given the opportunity",
        "Failing to quantify the impact of your work",
        "Rambling without a clear structure (use STAR format)",
    ]

    level_specific: dict[str, list[str]] = {
        "junior": [
            "Pretending to know something you do not — it is better to be honest",
            "Not showing enthusiasm for learning",
        ],
        "mid": [
            "Not demonstrating ownership of past projects",
            "Focusing only on individual contributions without mentioning team impact",
        ],
        "senior": [
            "Only discussing technical details without business context",
            "Not showing evidence of mentoring or leadership",
        ],
        "lead": [
            "Focusing too much on individual coding rather than team outcomes",
            "Not articulating a clear management philosophy",
        ],
        "executive": [
            "Getting lost in technical details instead of strategic thinking",
            "Not demonstrating cross-functional influence",
        ],
    }

    return base + level_specific.get(level, level_specific["mid"])


def _preparation_checklist(role_type: str, level: str) -> list[str]:
    """Generate a preparation checklist."""
    checklist = [
        "Research the company's recent news, products, and culture",
        "Review the job description and map your experience to each requirement",
        "Prepare 3-5 STAR stories covering different competencies",
        "Practice explaining your resume chronologically in 2 minutes",
        "Prepare a list of thoughtful questions for the interviewer",
        "Test your video/audio setup if the interview is remote",
        "Plan your outfit appropriate to the company culture",
        "Arrive (or log in) 5-10 minutes early",
    ]

    if role_type == "technical":
        checklist.extend(
            [
                "Review fundamental data structures and algorithms",
                "Practice coding on a whiteboard or shared editor",
                "Prepare to discuss system design for your level",
            ]
        )
    elif role_type == "designer":
        checklist.extend(
            [
                "Update your portfolio with recent work and case studies",
                "Prepare to walk through your design process end-to-end",
                "Practice presenting your work clearly in under 5 minutes per case study",
            ]
        )
    elif role_type == "data":
        checklist.extend(
            [
                "Review SQL queries — expect a live exercise",
                "Prepare to explain statistical concepts in plain language",
                "Have examples of data-driven decisions you influenced",
            ]
        )

    if level in ("senior", "lead", "executive"):
        checklist.append("Prepare examples of cross-team or organizational impact")

    return checklist


def _parse_job_description(text: str) -> dict:
    """Extract skills, years of experience, and qualifications from a job description."""
    if not text.strip():
        return {"skills": [], "years_experience": None, "qualifications": []}

    # Extract skills from common JD patterns
    skill_patterns = [
        r"(?:experience (?:with|in|using))\s+([A-Za-z\s,/+#]+?)(?:\.|,\s*(?:and|or)|\n)",
        r"(?:proficiency in|proficient in|knowledge of|familiar with)\s+([A-Za-z\s,/+#]+?)(?:\.|,\s*(?:and|or)|\n)",
        r"(?:skills?(?:\s+required)?:?\s*)([A-Za-z\s,/+#]+?)(?:\n|$)",
    ]
    skills: list[str] = []
    for pat in skill_patterns:
        for match in re.findall(pat, text, re.IGNORECASE):
            parts = re.split(r"[,;]|\band\b|\bor\b", match)
            skills.extend(p.strip() for p in parts if p.strip() and len(p.strip()) > 1)

    # Extract years of experience
    years_match = re.search(
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        text,
        re.IGNORECASE,
    )
    years = int(years_match.group(1)) if years_match else None

    # Extract qualifications
    qual_patterns = [
        r"(?:bachelor'?s?|master'?s?|ph\.?d\.?|mba|degree)\s+(?:in\s+)?([A-Za-z\s]+?)(?:\.|,|\n|$)",
        r"(?:certified|certification)\s+(?:in\s+)?([A-Za-z\s]+?)(?:\.|,|\n|$)",
    ]
    qualifications: list[str] = []
    for pat in qual_patterns:
        for match in re.findall(pat, text, re.IGNORECASE):
            qualifications.append(match.strip())

    # Deduplicate
    skills = list(dict.fromkeys(s for s in skills if len(s) > 2))[:15]
    qualifications = list(dict.fromkeys(qualifications))[:5]

    return {
        "skills": skills,
        "years_experience": years,
        "qualifications": qualifications,
    }


def _compute_difficulty_distribution(questions: list[dict]) -> dict:
    """Analyze difficulty balance across selected questions."""
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for q in questions:
        d = q.get("difficulty", "medium")
        if d in counts:
            counts[d] += 1

    total = sum(counts.values()) or 1
    ratios = {k: round(v / total, 2) for k, v in counts.items()}

    # Balance score: ideal is roughly 25% easy, 50% medium, 25% hard
    ideal = {"easy": 0.25, "medium": 0.50, "hard": 0.25}
    deviation = sum(abs(ratios.get(k, 0) - v) for k, v in ideal.items())
    balance_score = round(max(0, 100 - deviation * 100), 1)

    return {"counts": counts, "ratios": ratios, "balance_score": balance_score}


def _validate_star_response(response: str) -> dict:
    """Validate a STAR response for completeness."""
    if not response.strip():
        return {"score": 0, "components": {}, "feedback": ["No response provided"]}

    markers = {
        "situation": [
            "situation",
            "context",
            "background",
            "when i was",
            "at my previous",
            "in my role",
        ],
        "task": [
            "task",
            "responsibility",
            "my role was",
            "i was asked",
            "i needed to",
            "goal was",
        ],
        "action": [
            "action",
            "i did",
            "i decided",
            "i implemented",
            "steps i took",
            "i created",
            "i led",
        ],
        "result": [
            "result",
            "outcome",
            "achieved",
            "led to",
            "increased",
            "decreased",
            "improved",
            "saved",
        ],
    }
    components = text_structure_check(response, markers)
    present = sum(1 for v in components.values() if v)
    score = round(present / 4 * 100, 1)

    feedback: list[str] = []
    for comp, found in components.items():
        if not found:
            feedback.append(
                f"Missing '{comp.upper()}' component — add context about your {comp}"
            )

    if (
        count_pattern_matches(
            response, ["percent", "%", "increased", "decreased", "saved", "$"]
        )
        == 0
    ):
        feedback.append(
            "Consider adding quantified results (numbers, percentages, dollar amounts)"
        )

    return {"score": score, "components": components, "feedback": feedback}


def _compute_time_allocation(
    questions: list[dict], total_minutes: int = 60
) -> list[dict]:
    """Allocate time per question based on difficulty."""
    if not questions:
        return []

    time_per_difficulty = {"easy": 2, "medium": 3, "hard": 5}
    raw_times = [
        time_per_difficulty.get(q.get("difficulty", "medium"), 3) for q in questions
    ]
    raw_total = sum(raw_times) or 1
    scale = total_minutes / raw_total

    return [
        {
            "question": q.get("question", "")[:60],
            "difficulty": q.get("difficulty", "medium"),
            "minutes": round(t * scale, 1),
        }
        for q, t in zip(questions, raw_times)
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def prepare_interview(
    role: str,
    level: str = "mid",
    focus: str = "",
    job_description: str = "",
    response: str = "",
) -> dict:
    """Generate interview preparation materials for a given role and level.

    Args:
        role: Job title or role description (e.g. "Senior Software Engineer").
        level: Seniority level — junior, mid, senior, lead, or executive.
        focus: Optional focus area to weight questions toward
               (e.g. "system design", "leadership").
        job_description: Optional job description text to extract required skills.
        response: Optional STAR response text to validate.

    Returns:
        Dictionary with practice questions, topics, time allocation,
        pitfalls, and preparation checklist.
    """
    level = level.lower().strip()
    if level not in _LEVELS:
        level = "mid"

    role_type = _detect_role_type(role)
    level_config = _LEVELS[level]
    question_count = level_config["question_count"]

    bank = _ROLE_QUESTION_BANKS.get(role_type, _TECHNICAL_QUESTIONS)
    questions = _select_questions(bank, level, focus, question_count)

    # Time allocation varies by level
    time_allocations: dict[str, dict[str, str]] = {
        "junior": {
            "intro": "5 min",
            "technical": "15-20 min",
            "behavioral": "15-20 min",
            "questions": "5-10 min",
        },
        "mid": {
            "intro": "5 min",
            "technical": "20-30 min",
            "behavioral": "15-20 min",
            "questions": "5-10 min",
        },
        "senior": {
            "intro": "5 min",
            "technical": "25-35 min",
            "behavioral": "15-20 min",
            "questions": "5-10 min",
        },
        "lead": {
            "intro": "5 min",
            "technical": "20-25 min",
            "behavioral": "20-25 min",
            "questions": "10-15 min",
        },
        "executive": {
            "intro": "5 min",
            "technical": "15-20 min",
            "behavioral": "25-30 min",
            "questions": "10-15 min",
        },
    }

    # --- Computed analysis ---
    difficulty_distribution = _compute_difficulty_distribution(questions)
    per_question_time = _compute_time_allocation(questions)

    result = {
        "role": role,
        "level": level,
        "preparation": {
            "questions": questions,
            "technical_topics": _technical_topics(role_type, level),
            "behavioral_topics": _behavioral_topics(level),
            "questions_to_ask": _questions_to_ask(role_type, level),
        },
        "difficulty_distribution": difficulty_distribution,
        "time_allocation": time_allocations.get(level, time_allocations["mid"]),
        "per_question_time": per_question_time,
        "common_pitfalls": _common_pitfalls(level),
        "preparation_checklist": _preparation_checklist(role_type, level),
    }

    if job_description.strip():
        result["job_analysis"] = _parse_job_description(job_description)

    if response.strip():
        result["star_validation"] = _validate_star_response(response)

    return result
