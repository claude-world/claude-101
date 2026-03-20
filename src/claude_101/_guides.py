"""Embedded guide catalog for Claude 101 (24 use cases)."""

from __future__ import annotations

GUIDES: list[dict] = [
    # === Writing & Communication ===
    {
        "id": 1,
        "title": "Professional Email Drafting",
        "description": "Draft clear, professional emails for any business context — from follow-ups to proposals.",
        "category": "writing",
        "difficulty": "beginner",
        "tags": ["email", "communication", "professional"],
        "tool": "draft_email",
        "tips": [
            "Specify the recipient's role and your relationship",
            "Include the desired tone (formal, friendly, assertive)",
            "Mention any constraints (word limit, must include specific info)",
        ],
        "steps": [
            "Load Claude with context: who, what, why",
            "Set the tone and formality level",
            "Review and iterate on the draft",
            "Add a clear call-to-action",
        ],
    },
    {
        "id": 2,
        "title": "Blog Post & Article Writing",
        "description": "Plan, outline, draft, and polish blog posts and articles that engage your audience.",
        "category": "writing",
        "difficulty": "beginner",
        "tags": ["blog", "content", "seo"],
        "tool": "draft_blog_post",
        "tips": [
            "Define your target audience before writing",
            "Use the outline-first approach for longer posts",
            "Include data or examples to support key points",
        ],
        "steps": [
            "Define topic, audience, and key message",
            "Generate an outline with section headings",
            "Draft each section with target word counts",
            "Polish with SEO keywords and formatting",
        ],
    },
    {
        "id": 3,
        "title": "Meeting Notes & Summaries",
        "description": "Transform messy meeting transcripts into structured notes, action items, and summaries.",
        "category": "writing",
        "difficulty": "beginner",
        "tags": ["meetings", "productivity", "notes"],
        "tool": "parse_meeting_notes",
        "tips": [
            "Paste raw notes or transcript directly",
            "Use @mentions to tag action item owners",
            "Include TODO: prefix for action items",
        ],
        "steps": [
            "Paste your raw meeting notes",
            "Let Claude extract attendees, decisions, and actions",
            "Review and assign owners to action items",
            "Distribute the structured summary",
        ],
    },
    {
        "id": 4,
        "title": "Social Media Content Creation",
        "description": "Create engaging social media posts for multiple platforms.",
        "category": "writing",
        "difficulty": "beginner",
        "tags": ["social media", "marketing", "content"],
        "tool": "format_social_content",
        "tips": [
            "Write for one platform at a time",
            "Front-load the hook in the first line",
            "Use platform-specific features (threads, carousels)",
        ],
        "steps": [
            "Define your message and target platform",
            "Draft the core content",
            "Optimize for platform character limits",
            "Add hashtags and engagement elements",
        ],
    },
    {
        "id": 5,
        "title": "Technical Documentation",
        "description": "Write clear technical documentation — API docs, user guides, READMEs.",
        "category": "writing",
        "difficulty": "intermediate",
        "tags": ["documentation", "technical", "api"],
        "tool": "scaffold_tech_doc",
        "tips": [
            "Choose the right doc type (README, API, RFC, ADR)",
            "Follow the standard section ordering for that doc type",
            "Include code examples for technical docs",
        ],
        "steps": [
            "Select doc type and define the audience",
            "Generate the section structure",
            "Fill in each section with appropriate detail",
            "Add code examples and cross-references",
        ],
    },
    {
        "id": 6,
        "title": "Creative Writing & Storytelling",
        "description": "Explore creative writing — stories, characters, world-building, and narrative techniques.",
        "category": "writing",
        "difficulty": "beginner",
        "tags": ["creative", "storytelling", "fiction"],
        "tool": "structure_story",
        "tips": [
            "Start with character and conflict, not plot",
            "Use a story structure framework (three-act, hero's journey)",
            "Build tension through escalating stakes",
        ],
        "steps": [
            "Define genre, characters, and central conflict",
            "Choose a narrative structure",
            "Map out story beats with word targets",
            "Draft scenes following the tension curve",
        ],
    },
    # === Analysis & Research ===
    {
        "id": 7,
        "title": "Data Analysis & Interpretation",
        "description": "Analyze datasets, identify patterns, and create data-driven narratives.",
        "category": "analysis",
        "difficulty": "intermediate",
        "tags": ["data", "statistics", "insights"],
        "tool": "analyze_data",
        "tips": [
            "Format data as CSV or JSON for best results",
            "Specify what questions you want answered",
            "Ask for both statistics and narrative interpretation",
        ],
        "steps": [
            "Prepare and format your data",
            "Run statistical analysis",
            "Identify patterns and outliers",
            "Generate narrative insights",
        ],
    },
    {
        "id": 8,
        "title": "Document Summarization",
        "description": "Summarize long documents, research papers, and reports at any level of detail.",
        "category": "analysis",
        "difficulty": "beginner",
        "tags": ["summarization", "research", "documents"],
        "tool": "summarize_document",
        "tips": [
            "Specify the target audience for the summary",
            "Set a maximum sentence count for conciseness",
            "Ask for key takeaways, not just compression",
        ],
        "steps": [
            "Paste the full document text",
            "Specify summary length and audience",
            "Review extracted key sentences",
            "Refine for your specific use case",
        ],
    },
    {
        "id": 9,
        "title": "Competitive Research",
        "description": "Conduct thorough competitive analysis — feature comparisons to market positioning.",
        "category": "analysis",
        "difficulty": "intermediate",
        "tags": ["competitive", "research", "business"],
        "tool": "build_comparison_matrix",
        "tips": [
            "Define clear comparison criteria first",
            "Weight criteria by importance to your decision",
            "Include at least 3 competitors for meaningful comparison",
        ],
        "steps": [
            "List competitors and comparison criteria",
            "Assign weights to each criterion",
            "Score each competitor on each criterion",
            "Analyze rankings and sensitivity",
        ],
    },
    {
        "id": 10,
        "title": "Survey & Feedback Analysis",
        "description": "Analyze customer surveys and feedback to extract actionable insights.",
        "category": "analysis",
        "difficulty": "intermediate",
        "tags": ["survey", "feedback", "customer"],
        "tool": "analyze_survey",
        "tips": [
            "Include the scale range (1-5, 1-10) in your request",
            "Group questions by theme for clearer analysis",
            "Look for NPS patterns across segments",
        ],
        "steps": [
            "Format survey data as CSV or JSON",
            "Run per-question statistical analysis",
            "Calculate NPS and satisfaction scores",
            "Identify trends and actionable insights",
        ],
    },
    {
        "id": 11,
        "title": "Financial Report Analysis",
        "description": "Analyze financial statements and data for key metrics and trends.",
        "category": "analysis",
        "difficulty": "advanced",
        "tags": ["finance", "reports", "metrics"],
        "tool": "analyze_financials",
        "tips": [
            "Include multiple periods for trend analysis",
            "Specify the reporting period (quarterly, annual)",
            "Ask for both ratios and narrative interpretation",
        ],
        "steps": [
            "Input financial data with period labels",
            "Calculate margins and growth rates",
            "Compute key financial ratios",
            "Assess trends and generate recommendations",
        ],
    },
    {
        "id": 12,
        "title": "Legal Document Review",
        "description": "Review contracts and legal documents — identify key clauses and potential issues.",
        "category": "analysis",
        "difficulty": "advanced",
        "tags": ["legal", "contracts", "compliance"],
        "tool": "review_legal_document",
        "tips": [
            "Specify the document type (NDA, employment, SaaS)",
            "Focus on high-risk clauses first",
            "Always have a lawyer review the final analysis",
        ],
        "steps": [
            "Paste the legal document text",
            "Identify document type and context",
            "Scan for standard clause patterns",
            "Flag missing clauses and potential risks",
        ],
    },
    # === Coding & Technical ===
    {
        "id": 13,
        "title": "Code Generation & Explanation",
        "description": "Generate clean, well-documented code and get explanations of complex code.",
        "category": "coding",
        "difficulty": "intermediate",
        "tags": ["code generation", "development", "programming"],
        "tool": "scaffold_code",
        "tips": [
            "Specify language, framework, and coding style",
            "Include input/output examples",
            "Ask for error handling and edge cases",
        ],
        "steps": [
            "Define requirements with precision",
            "Specify language and design pattern",
            "Generate the code scaffold",
            "Review and customize the output",
        ],
    },
    {
        "id": 14,
        "title": "Code Review & Debugging",
        "description": "Find bugs, security issues, and get improvement suggestions.",
        "category": "coding",
        "difficulty": "intermediate",
        "tags": ["code review", "debugging", "quality"],
        "tool": "analyze_code",
        "tips": [
            "Include the full function/class, not just snippets",
            "Specify what you're most concerned about (bugs, perf, security)",
            "Ask for severity ratings on issues found",
        ],
        "steps": [
            "Paste the code to review",
            "Run static analysis metrics",
            "Review complexity and quality indicators",
            "Address flagged issues by priority",
        ],
    },
    {
        "id": 15,
        "title": "SQL Query Writing",
        "description": "Write efficient SQL queries — from SELECTs to complex JOINs, CTEs, and optimization.",
        "category": "coding",
        "difficulty": "intermediate",
        "tags": ["sql", "database", "queries"],
        "tool": "process_sql",
        "tips": [
            "Describe your data schema before writing queries",
            "Start simple and add complexity incrementally",
            "Ask Claude to explain query execution order",
        ],
        "steps": [
            "Write or paste your SQL query",
            "Format for readability",
            "Validate syntax",
            "Review execution plan and optimize",
        ],
    },
    {
        "id": 16,
        "title": "API Documentation",
        "description": "Generate comprehensive API documentation — endpoints, parameters, examples.",
        "category": "coding",
        "difficulty": "intermediate",
        "tags": ["api", "documentation", "openapi"],
        "tool": "scaffold_api_doc",
        "tips": [
            "List all endpoints with HTTP methods",
            "Include request/response examples",
            "Document error codes and edge cases",
        ],
        "steps": [
            "List your API endpoints",
            "Define parameters and response schemas",
            "Generate OpenAPI or markdown docs",
            "Add examples and error documentation",
        ],
    },
    {
        "id": 17,
        "title": "Test Case Generation",
        "description": "Generate comprehensive test suites — unit tests, edge cases, and test data.",
        "category": "coding",
        "difficulty": "intermediate",
        "tags": ["testing", "quality", "test cases"],
        "tool": "generate_test_cases",
        "tips": [
            "Include the function signature and docstring",
            "Specify the testing framework (pytest, jest, etc.)",
            "Ask for edge cases and boundary values",
        ],
        "steps": [
            "Provide the function signature",
            "Generate happy path test cases",
            "Add edge cases and boundary values",
            "Review coverage and add missing scenarios",
        ],
    },
    {
        "id": 18,
        "title": "Architecture & Design Decisions",
        "description": "Evaluate architectural options, create ADRs, and make technical design decisions.",
        "category": "coding",
        "difficulty": "advanced",
        "tags": ["architecture", "design", "adr"],
        "tool": "create_adr",
        "tips": [
            "List at least 2-3 options to compare",
            "Include constraints and non-functional requirements",
            "Document the decision rationale, not just the choice",
        ],
        "steps": [
            "Define the architectural context and problem",
            "List options with trade-offs",
            "Evaluate against criteria",
            "Document the decision as an ADR",
        ],
    },
    # === Business & Productivity ===
    {
        "id": 19,
        "title": "Project Planning & Task Breakdown",
        "description": "Break down complex projects into manageable tasks, timelines, and dependencies.",
        "category": "business",
        "difficulty": "beginner",
        "tags": ["planning", "project management", "tasks"],
        "tool": "plan_project",
        "tips": [
            "Start with the end goal and work backwards",
            "Include team size and timeline constraints",
            "Ask Claude to surface hidden dependencies",
        ],
        "steps": [
            "Define the project goal and constraints",
            "Generate work breakdown structure",
            "Estimate durations and map dependencies",
            "Identify milestones and critical path",
        ],
    },
    {
        "id": 20,
        "title": "Interview Preparation",
        "description": "Prepare for any interview — practice questions, STAR responses, and negotiation strategies.",
        "category": "business",
        "difficulty": "beginner",
        "tags": ["interview", "career", "preparation"],
        "tool": "prepare_interview",
        "tips": [
            "Specify the role, company, and interview stage",
            "Practice behavioral questions with STAR format",
            "Prepare 3-5 questions to ask the interviewer",
        ],
        "steps": [
            "Define the role and interview context",
            "Generate relevant practice questions",
            "Prepare STAR-format responses",
            "Build your question list and study plan",
        ],
    },
    {
        "id": 21,
        "title": "Proposal & Pitch Writing",
        "description": "Craft compelling business proposals and pitch decks.",
        "category": "business",
        "difficulty": "intermediate",
        "tags": ["proposals", "sales", "pitch"],
        "tool": "scaffold_proposal",
        "tips": [
            "Lead with the problem, not your solution",
            "Include ROI projections or social proof",
            "Tailor the structure to your audience",
        ],
        "steps": [
            "Define proposal type and audience",
            "Structure sections by persuasion framework",
            "Draft each section with word targets",
            "Add supporting evidence and projections",
        ],
    },
    {
        "id": 22,
        "title": "Customer Support Responses",
        "description": "Draft empathetic customer support responses — complaints, technical issues, escalations.",
        "category": "business",
        "difficulty": "beginner",
        "tags": ["support", "customer service", "communication"],
        "tool": "build_support_response",
        "tips": [
            "Always acknowledge the customer's frustration first",
            "Provide concrete next steps, not vague promises",
            "Match the tone to the severity of the issue",
        ],
        "steps": [
            "Classify the issue type and severity",
            "Draft an empathetic opening",
            "Provide the solution or next steps",
            "Close with a clear follow-up plan",
        ],
    },
    {
        "id": 23,
        "title": "Product Requirements Documents",
        "description": "Create structured PRDs — user stories, acceptance criteria, technical requirements.",
        "category": "business",
        "difficulty": "intermediate",
        "tags": ["product", "requirements", "prd"],
        "tool": "scaffold_prd",
        "tips": [
            "Start with the problem, not the feature",
            "Write user stories from the user's perspective",
            "Include measurable success metrics",
        ],
        "steps": [
            "Define the problem and target users",
            "Write user stories with acceptance criteria",
            "Prioritize features using MoSCoW",
            "Add technical requirements and metrics",
        ],
    },
    {
        "id": 24,
        "title": "Decision Frameworks & Evaluation",
        "description": "Build decision matrices, evaluate options, and make data-informed decisions.",
        "category": "business",
        "difficulty": "intermediate",
        "tags": ["decision making", "strategy", "evaluation"],
        "tool": "evaluate_decision",
        "tips": [
            "Weight criteria before scoring options",
            "Include at least 3 criteria for meaningful analysis",
            "Run sensitivity analysis on close decisions",
        ],
        "steps": [
            "Define options and evaluation criteria",
            "Assign weights and score each option",
            "Calculate weighted rankings",
            "Run sensitivity analysis on the top choices",
        ],
    },
]

CATEGORIES = {
    "writing": {
        "name": "Writing & Communication",
        "description": "Tools for drafting, formatting, and structuring written content.",
        "guide_ids": [1, 2, 3, 4, 5, 6],
    },
    "analysis": {
        "name": "Analysis & Research",
        "description": "Tools for analyzing data, documents, and competitive landscapes.",
        "guide_ids": [7, 8, 9, 10, 11, 12],
    },
    "coding": {
        "name": "Coding & Technical",
        "description": "Tools for code generation, review, SQL, API docs, testing, and architecture.",
        "guide_ids": [13, 14, 15, 16, 17, 18],
    },
    "business": {
        "name": "Business & Productivity",
        "description": "Tools for planning, interviews, proposals, support, PRDs, and decisions.",
        "guide_ids": [19, 20, 21, 22, 23, 24],
    },
}


def get_guide(guide_id: int) -> dict | None:
    """Get a guide by ID."""
    for g in GUIDES:
        if g["id"] == guide_id:
            return g
    return None


def list_guides(category: str | None = None) -> list[dict]:
    """List guides, optionally filtered by category."""
    result = GUIDES
    if category:
        result = [g for g in result if g["category"] == category]
    return [
        {"id": g["id"], "title": g["title"], "category": g["category"],
         "difficulty": g["difficulty"], "tool": g["tool"]}
        for g in result
    ]


def search_guides(query: str, category: str | None = None) -> list[dict]:
    """Search guides by keyword in title, description, and tags."""
    query_lower = query.lower()
    results = []
    for g in GUIDES:
        if category and g["category"] != category:
            continue
        searchable = f"{g['title']} {g['description']} {' '.join(g['tags'])}".lower()
        if query_lower in searchable:
            results.append({
                "id": g["id"], "title": g["title"], "category": g["category"],
                "difficulty": g["difficulty"], "tool": g["tool"],
                "description": g["description"],
            })
    return results
