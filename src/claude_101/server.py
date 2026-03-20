"""MCP Server for Claude 101 — 27 tools (3 meta + 24 use case)."""

from __future__ import annotations

import json

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise ImportError("Install mcp extra: pip install 'claude-101[mcp]'")

from ._guides import (
    list_guides as _list_guides,
    get_guide as _get_guide,
    search_guides as _search_guides,
)

# Writing tools
from .writing.email import draft_email as _draft_email
from .writing.blog import draft_blog_post as _draft_blog_post
from .writing.meeting import parse_meeting_notes as _parse_meeting_notes
from .writing.social import format_social_content as _format_social_content
from .writing.techdoc import scaffold_tech_doc as _scaffold_tech_doc
from .writing.creative import structure_story as _structure_story

# Analysis tools
from .analysis.data import analyze_data as _analyze_data
from .analysis.summarize import summarize_document as _summarize_document
from .analysis.competitive import build_comparison_matrix as _build_comparison_matrix
from .analysis.survey import analyze_survey as _analyze_survey
from .analysis.financial import analyze_financials as _analyze_financials
from .analysis.legal import review_legal_document as _review_legal_document

# Coding tools
from .coding.codegen import scaffold_code as _scaffold_code
from .coding.review import analyze_code as _analyze_code
from .coding.sql import process_sql as _process_sql
from .coding.apidoc import scaffold_api_doc as _scaffold_api_doc
from .coding.testgen import generate_test_cases as _generate_test_cases
from .coding.architecture import create_adr as _create_adr

# Business tools
from .business.planning import plan_project as _plan_project
from .business.interview import prepare_interview as _prepare_interview
from .business.proposal import scaffold_proposal as _scaffold_proposal
from .business.support import build_support_response as _build_support_response
from .business.prd import scaffold_prd as _scaffold_prd
from .business.decision import evaluate_decision as _evaluate_decision


mcp = FastMCP("claude-101")


def _json(data: dict | list) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── Meta Tools ──────────────────────────────────────────────────────────────


@mcp.tool()
async def list_guides(category: str = "") -> str:
    """List all 24 Claude AI use-case guides.

    Args:
        category: Filter by category (writing, analysis, coding, business). Empty = all.

    Returns:
        JSON catalog of guides with id, title, category, difficulty, and tool name.
    """
    return _json(_list_guides(category or None))


@mcp.tool()
async def get_guide(guide_id: int) -> str:
    """Get full details of a specific guide.

    Args:
        guide_id: Guide number (1-24).

    Returns:
        JSON with title, description, tips, steps, and tool name.
    """
    guide = _get_guide(guide_id)
    if not guide:
        return _json({"error": f"Guide {guide_id} not found. Valid range: 1-24."})
    return _json(guide)


@mcp.tool()
async def search_guides(query: str, category: str = "") -> str:
    """Search guides by keyword.

    Args:
        query: Search keyword to match against guide titles, descriptions, and tags.
        category: Optional category filter.

    Returns:
        JSON list of matching guides.
    """
    results = _search_guides(query, category or None)
    return _json(results)


# ── Writing & Communication ─────────────────────────────────────────────────


@mcp.tool()
async def draft_email(
    context: str,
    tone: str = "professional",
    output_format: str = "standard",
) -> str:
    """Draft a professional email scaffold with sections and tone guidance.

    Args:
        context: Email context — who, what, why (e.g. "follow-up to client meeting about Q3 proposal").
        tone: Tone style: professional, friendly, assertive, apologetic, congratulatory.
        output_format: Length format: standard, brief, detailed.

    Returns:
        JSON with subject suggestions, sectioned draft, tone guide, and pre-send checklist.
    """
    return _json(_draft_email(context, tone, output_format))


@mcp.tool()
async def draft_blog_post(
    topic: str,
    target_words: int = 1500,
    style: str = "educational",
) -> str:
    """Create a structured blog post outline with word allocations and SEO fields.

    Args:
        topic: Blog post topic or title.
        target_words: Target word count (default: 1500).
        style: Writing style: educational, opinion, tutorial, listicle, case-study.

    Returns:
        JSON with outline, heading hierarchy, SEO fields, and style guide.
    """
    return _json(_draft_blog_post(topic, target_words, style))


@mcp.tool()
async def parse_meeting_notes(
    raw_notes: str,
    output_format: str = "structured",
) -> str:
    """Extract action items, decisions, and attendees from meeting notes.

    Args:
        raw_notes: Raw meeting notes or transcript text.
        output_format: Output format: structured (full), brief (summary), action-only (just action items).

    Returns:
        JSON with attendees, action items, decisions, topics, and metrics.
    """
    return _json(_parse_meeting_notes(raw_notes, output_format))


@mcp.tool()
async def format_social_content(
    text: str,
    platform: str = "twitter",
    include_hashtags: bool = True,
) -> str:
    """Format text for a social media platform with character limits and engagement analysis.

    Args:
        text: Content text to format.
        platform: Target platform: twitter, linkedin, threads, instagram, facebook.
        include_hashtags: Whether to extract/suggest hashtags (default: true).

    Returns:
        JSON with formatted text, character analysis, chunks (if over limit), and engagement signals.
    """
    return _json(_format_social_content(text, platform, include_hashtags))


@mcp.tool()
async def scaffold_tech_doc(
    doc_type: str,
    title: str,
    sections: str = "",
    content: str = "",
) -> str:
    """Generate a technical document template with standard sections.

    Args:
        doc_type: Document type: readme, api, rfc, adr, runbook, changelog, contributing, architecture.
        title: Document title.
        sections: Optional comma-separated custom sections (overrides defaults).
        content: Optional code or existing document to analyze for structure and completeness.

    Returns:
        JSON with markdown template, section list, best practices, and optional analysis.
    """
    return _json(_scaffold_tech_doc(doc_type, title, sections, content))


@mcp.tool()
async def structure_story(
    genre: str = "general",
    elements: str = "",
    structure: str = "three-act",
    text: str = "",
) -> str:
    """Create a story structure with beats, tension curve, and character arcs.

    Args:
        genre: Story genre: general, fantasy, sci-fi, mystery, romance, thriller, horror, literary, comedy.
        elements: Story elements (e.g. "protagonist: detective, setting: 1920s Chicago, conflict: murder mystery").
        structure: Narrative structure: three-act, heros-journey, five-act.
        text: Optional existing story text to analyze for pacing, dialogue, and transitions.

    Returns:
        JSON with story beats, tension curve, word targets, character arc, and optional text analysis.
    """
    return _json(_structure_story(genre, elements, structure, text))


# ── Analysis & Research ──────────────────────────────────────────────────────


@mcp.tool()
async def analyze_data(
    data: str,
    output_format: str = "csv",
    operations: str = "summary",
) -> str:
    """Analyze CSV or JSON data with statistics, outlier detection, and correlations.

    Args:
        data: Raw data as CSV or JSON string.
        output_format: Data format: csv, json.
        operations: What to compute: summary, correlations, outliers, all.

    Returns:
        JSON with column stats, types, outliers, and correlations.
    """
    return _json(_analyze_data(data, output_format, operations))


@mcp.tool()
async def summarize_document(
    text: str,
    max_sentences: int = 5,
) -> str:
    """Analyze and extract key sentences from a document.

    Args:
        text: Document text to summarize.
        max_sentences: Maximum number of key sentences to extract (default: 5).

    Returns:
        JSON with readability scores, key sentences, keywords, and word count.
    """
    return _json(_summarize_document(text, max_sentences))


@mcp.tool()
async def build_comparison_matrix(
    items: str,
    criteria: str,
    weights: str = "",
) -> str:
    """Build a weighted comparison matrix for competitive analysis.

    Args:
        items: Comma-separated items to compare (e.g. "React, Vue, Angular").
        criteria: Comma-separated evaluation criteria (e.g. "Performance, DX, Ecosystem").
        weights: Optional comma-separated weights (e.g. "0.4, 0.3, 0.3"). Equal if omitted.

    Returns:
        JSON with matrix structure, weight normalization, and sensitivity framework.
    """
    return _json(_build_comparison_matrix(items, criteria, weights))


@mcp.tool()
async def analyze_survey(
    data: str,
    scale_max: int = 5,
) -> str:
    """Analyze survey data with per-question stats and NPS calculation.

    Args:
        data: Survey data as CSV (rows=respondents, columns=questions).
        scale_max: Maximum value on the rating scale (default: 5).

    Returns:
        JSON with per-question stats, distributions, NPS, and satisfaction scores.
    """
    return _json(_analyze_survey(data, scale_max))


@mcp.tool()
async def analyze_financials(
    data: str,
    period: str = "quarterly",
) -> str:
    """Analyze financial data for margins, growth rates, and trends.

    Args:
        data: Financial data as CSV (rows=metrics like Revenue/COGS/Profit, columns=periods).
        period: Reporting period: quarterly, monthly, annual.

    Returns:
        JSON with metrics, ratios, growth rates, burn rate, and trend analysis.
    """
    return _json(_analyze_financials(data, period))


@mcp.tool()
async def review_legal_document(
    text: str,
    doc_type: str = "contract",
) -> str:
    """Review a legal document for clause patterns and missing protections.

    Args:
        text: Legal document text.
        doc_type: Document type: contract, nda, employment, saas, partnership, lease.

    Returns:
        JSON with found clauses, missing clauses, complexity score, and recommendations.
    """
    return _json(_review_legal_document(text, doc_type))


# ── Coding & Technical ───────────────────────────────────────────────────────


@mcp.tool()
async def scaffold_code(
    language: str,
    pattern: str,
    name: str,
    description: str = "",
) -> str:
    """Generate a code scaffold for a given language and design pattern.

    Args:
        language: Programming language: python, javascript, typescript, go, rust, java.
        pattern: Design pattern: class, function, api-endpoint, cli, model, singleton, factory, observer.
        name: Name for the generated code (class/function name).
        description: Optional description of what the code should do.

    Returns:
        JSON with generated code, imports, naming convention, and notes.
    """
    return _json(_scaffold_code(language, pattern, name, description))


@mcp.tool()
async def analyze_code(
    code: str,
    language: str = "auto",
) -> str:
    """Analyze code for complexity, quality metrics, and potential issues.

    Args:
        code: Source code to analyze.
        language: Programming language (auto-detected if not specified).

    Returns:
        JSON with line counts, complexity metrics, detected issues, and quality grade.
    """
    return _json(_analyze_code(code, language))


@mcp.tool()
async def process_sql(
    query: str,
    operation: str = "format",
    dialect: str = "auto",
) -> str:
    """Format, validate, or explain a SQL query.

    Args:
        query: SQL query string.
        operation: What to do: format (pretty-print), validate (check syntax), explain (step-by-step), extract (tables/columns).
        dialect: SQL dialect: auto, postgresql, mysql, sqlite, mssql.

    Returns:
        JSON with processed query, extracted tables/columns, and any warnings.
    """
    return _json(_process_sql(query, operation, dialect))


@mcp.tool()
async def scaffold_api_doc(
    endpoints: str,
    title: str = "API Reference",
    output_format: str = "openapi",
    code: str = "",
) -> str:
    """Generate API documentation from endpoint definitions.

    Args:
        endpoints: Endpoint definitions (e.g. "GET /users - List users, POST /users - Create user").
        title: API documentation title.
        output_format: Output format: openapi (YAML), markdown.
        code: Optional source code to extract routes and detect auth patterns.

    Returns:
        JSON with parsed endpoints, parameters, full document, consistency check, and optional code analysis.
    """
    return _json(_scaffold_api_doc(endpoints, title, output_format, code))


@mcp.tool()
async def generate_test_cases(
    function_signature: str,
    language: str = "python",
    strategy: str = "comprehensive",
) -> str:
    """Generate test cases from a function signature.

    Args:
        function_signature: Function signature (e.g. "def add(a: int, b: int) -> int").
        language: Programming language for test code.
        strategy: Test strategy: happy (basic), edge (+ edge cases), comprehensive (all categories).

    Returns:
        JSON with test cases, code, and coverage analysis.
    """
    return _json(_generate_test_cases(function_signature, language, strategy))


@mcp.tool()
async def create_adr(
    title: str,
    context: str,
    options: str,
    decision: str = "",
) -> str:
    """Create an Architecture Decision Record (ADR).

    Args:
        title: Decision title (e.g. "Choose database for user service").
        context: Background and constraints driving the decision.
        options: Comma-separated options (e.g. "PostgreSQL, MongoDB, DynamoDB").
        decision: The chosen option (leave empty for 'proposed' status).

    Returns:
        JSON with structured ADR, trade-off matrix, and markdown document.
    """
    return _json(_create_adr(title, context, options, decision))


# ── Business & Productivity ──────────────────────────────────────────────────


@mcp.tool()
async def plan_project(
    description: str,
    team_size: int = 1,
    duration_weeks: int = 4,
) -> str:
    """Generate a project plan with WBS, milestones, and risk analysis.

    Args:
        description: Project description and goals.
        team_size: Number of team members (default: 1).
        duration_weeks: Project duration in weeks (default: 4).

    Returns:
        JSON with phases, tasks, milestones, critical path, and risks.
    """
    return _json(_plan_project(description, team_size, duration_weeks))


@mcp.tool()
async def prepare_interview(
    role: str,
    level: str = "mid",
    focus: str = "",
    job_description: str = "",
    response: str = "",
) -> str:
    """Generate interview preparation materials with practice questions.

    Args:
        role: Job role (e.g. "software engineer", "product manager", "data scientist").
        level: Experience level: junior, mid, senior, lead, executive.
        focus: Optional focus area (e.g. "system design", "leadership", "algorithms").
        job_description: Optional job description text to extract required skills.
        response: Optional STAR response text to validate for completeness.

    Returns:
        JSON with practice questions, STAR templates, time allocation, preparation checklist, and optional analysis.
    """
    return _json(_prepare_interview(role, level, focus, job_description, response))


@mcp.tool()
async def scaffold_proposal(
    type: str,
    title: str,
    audience: str = "executive",
    content: str = "",
    investment: float = 0,
    annual_return: float = 0,
) -> str:
    """Generate a proposal structure with persuasion framework.

    Args:
        type: Proposal type: business, sales, grant, partnership, internal, technical.
        title: Proposal title.
        audience: Target audience: executive, technical, general.
        content: Optional proposal text to analyze for argument strength.
        investment: Optional investment amount for ROI calculation.
        annual_return: Optional expected annual return for ROI calculation.

    Returns:
        JSON with sections, word targets, AIDA framework, objection templates, and optional analysis.
    """
    return _json(
        _scaffold_proposal(type, title, audience, content, investment, annual_return)
    )


@mcp.tool()
async def build_support_response(
    issue: str,
    channel: str = "email",
    tone: str = "empathetic",
    draft_response: str = "",
) -> str:
    """Build a customer support response scaffold.

    Args:
        issue: Customer issue description.
        channel: Support channel: email, chat, phone, social.
        tone: Response tone: empathetic, professional, technical, casual.
        draft_response: Optional draft response text to score for quality.

    Returns:
        JSON with issue classification, response scaffold, escalation risk, and optional response quality score.
    """
    return _json(_build_support_response(issue, channel, tone, draft_response))


@mcp.tool()
async def scaffold_prd(
    product_name: str,
    problem: str,
    target_users: str = "",
) -> str:
    """Generate a Product Requirements Document (PRD) scaffold.

    Args:
        product_name: Product or feature name.
        problem: Problem statement the product solves.
        target_users: Optional comma-separated target user personas.

    Returns:
        JSON with PRD sections, user stories, acceptance criteria, and MoSCoW framework.
    """
    return _json(_scaffold_prd(product_name, problem, target_users))


@mcp.tool()
async def evaluate_decision(
    options: str,
    criteria: str,
    weights: str = "",
    scores: str = "",
) -> str:
    """Evaluate options using weighted decision matrix with sensitivity analysis.

    Args:
        options: Comma-separated options to evaluate.
        criteria: Comma-separated evaluation criteria.
        weights: Optional comma-separated weights (normalized automatically). Equal if omitted.
        scores: Optional scores (format: "opt1:c1=8,c2=7;opt2:c1=6,c2=9").

    Returns:
        JSON with weighted scores, rankings, winner, and sensitivity analysis.
    """
    return _json(_evaluate_decision(options, criteria, weights, scores))


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
