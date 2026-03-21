---
name: claude-101-mastery
description: Provides optimal workflows for 24 use cases (writing, analysis, coding, business) powered by the claude-101 MCP server. Calls the matching MCP tool to obtain structured methodology and computed metrics, then produces output grounded in real data.
allowed-tools:
  - mcp__claude-101__draft_email
  - mcp__claude-101__draft_blog_post
  - mcp__claude-101__parse_meeting_notes
  - mcp__claude-101__format_social_content
  - mcp__claude-101__scaffold_tech_doc
  - mcp__claude-101__structure_story
  - mcp__claude-101__analyze_data
  - mcp__claude-101__summarize_document
  - mcp__claude-101__build_comparison_matrix
  - mcp__claude-101__analyze_survey
  - mcp__claude-101__analyze_financials
  - mcp__claude-101__review_legal_document
  - mcp__claude-101__scaffold_code
  - mcp__claude-101__analyze_code
  - mcp__claude-101__process_sql
  - mcp__claude-101__scaffold_api_doc
  - mcp__claude-101__generate_test_cases
  - mcp__claude-101__create_adr
  - mcp__claude-101__plan_project
  - mcp__claude-101__prepare_interview
  - mcp__claude-101__scaffold_proposal
  - mcp__claude-101__build_support_response
  - mcp__claude-101__scaffold_prd
  - mcp__claude-101__evaluate_decision
  - Read
---

# Claude 101 Mastery

This skill provides the optimal workflow for 24 use cases powered by the `claude-101` MCP server. Each use case follows the same pattern: call the MCP tool first to get structured data and computation, then use that data to produce a superior final output.

The `claude-101` MCP server provides 27 tools (3 meta + 24 use-case tools) that perform real local computation — statistics, code analysis, SQL parsing, financial math, text analysis, and scoring — and return structured JSON.

## Core Principle

Always call the MCP tool FIRST before writing the final output. The tool provides two things that enhance the quality of the response:

1. **Methodology** — structured frameworks, best practices, section templates, and checklists that guide the approach to each use case. Following these frameworks ensures a professional-grade result that covers all standard elements.

2. **Computation** — precise metrics (scores, rankings, statistics, parsed data) that the user cannot get from natural language generation alone. These numbers ground the response in verifiable data.

Never skip the tool call. Never attempt to compute statistics, parse structured data, or calculate financial metrics manually. The tool handles computation; the final writing and reasoning come from Claude.

## Workflow Pattern

For every use case, follow these five steps:

1. **Identify** the matching MCP tool from the mapping table below
2. **Call** the tool with the user's input as parameters
3. **Read** every field in the result — each exists for a reason
4. **Produce** the final output informed by both the methodology and the computed data
5. **Present** key metrics (scores, rankings, statistics) explicitly to the user

When the tool returns both a template/scaffold AND computed analysis, use the template as a structural guide (do not copy it verbatim) and weave the computed metrics into the final output. The combination of professional structure and precise data is what makes the output superior.

## Use Case to Tool Mapping

### Writing and Communication

| User Intent | MCP Tool | Key Output Fields |
|------------|----------|------------------|
| Write or draft email | `draft_email` | `text_analysis` (formality, readability, tone), `tone_guide`, `pre_send_checklist` |
| Plan blog post or article | `draft_blog_post` | `outline` (section word targets), `seo_fields`, `topic_analysis`, `readability_target`, `heading_validation`, `content_gaps` |
| Organize meeting notes | `parse_meeting_notes` | `attendees`, `action_items` (owner + deadline), `decisions`, `topics_discussed`, `metrics` |
| Create social media post | `format_social_content` | `within_limit`, `chunks` (if over limit), `hashtags`, `engagement_signals` (question, CTA, hook strength) |
| Write technical documentation | `scaffold_tech_doc` | `template`, `sections` (required vs optional), `best_practices`, `effort_estimate`, optional `analysis` (code structure, completeness) |
| Structure a story | `structure_story` | `beats` (word targets + tension levels), `tension_curve`, `character_arc_template`, `genre_conventions`, optional `text_analysis` (pacing, dialogue ratio, scene transitions) |

### Analysis and Research

| User Intent | MCP Tool | Key Output Fields |
|------------|----------|------------------|
| Analyze CSV or JSON data | `analyze_data` | `columns` (per-column stats), `correlations` (Pearson r + strength), `outliers` |
| Summarize a document | `summarize_document` | `key_sentences` (scored), `flesch_score`, `flesch_grade`, `keywords`, `reading_time_minutes` |
| Compare options or competitors | `build_comparison_matrix` | `rankings` (weighted scores), `winner` (option + margin), `sensitivity_framework` |
| Analyze survey results | `analyze_survey` | `questions` (per-question mean, median, distribution), `nps` (promoter/passive/detractor), `overall_satisfaction` |
| Review financial data | `analyze_financials` | `margins` (gross, operating, net), `growth_rates`, `burn_rate`, `cash_runway`, `summary` |
| Review legal document | `review_legal_document` | `clauses_found` (type + risk level + snippet), `missing_clauses`, `complexity_score` |

### Coding and Technical

| User Intent | MCP Tool | Key Output Fields |
|------------|----------|------------------|
| Generate code scaffold | `scaffold_code` | `code`, `description_matched` (CRUD/API/auth pattern), `naming_convention`, `notes` |
| Review code quality | `analyze_code` | `complexity` (grade, cyclomatic, nesting), `issues` (type + severity + line), `metrics` (lines, comments) |
| Process or optimize SQL | `process_sql` | `result` (formatted/explained), `tables`, `columns`, `warnings`, `performance_hints` |
| Generate API documentation | `scaffold_api_doc` | `document` (OpenAPI/Markdown), `consistency` (score + issues), `example_bodies`, optional `code_analysis` (routes, auth) |
| Generate test cases | `generate_test_cases` | `test_cases` (happy/edge/boundary), `coverage_analysis`, `code` (test file scaffold) |
| Make architecture decision | `create_adr` | `trade_off_matrix` (per-option ratings from tech knowledge base), `adr` (status, pros/cons), `markdown` |

### Business and Productivity

| User Intent | MCP Tool | Key Output Fields |
|------------|----------|------------------|
| Plan a project | `plan_project` | `phases` (hours + tasks), `milestones`, `critical_path`, `risks`, `total_hours`, `resource_allocation` |
| Prepare for interview | `prepare_interview` | `preparation.questions` (with STAR templates), `difficulty_distribution`, `per_question_time`, optional `job_analysis`, optional `star_validation` |
| Write a proposal | `scaffold_proposal` | `sections` (with word targets), `persuasion_framework` (AIDA), `objection_templates`, `aida_coverage`, optional `argument_analysis`, optional `roi_analysis` |
| Handle customer support | `build_support_response` | `issue_classification` (category, severity, sentiment), `escalation_risk` (score + level), `resolution_estimate`, `customer_effort`, optional `response_quality` |
| Create a PRD | `scaffold_prd` | `user_stories`, `prioritization` (MoSCoW), `success_metrics`, `requirements_analysis` (completeness, story quality, dependencies) |
| Make a decision | `evaluate_decision` | `rankings` (weighted scores), `winner` (option + margin), `sensitivity_analysis` (weight change needed to flip) |

## Per-Tool Workflow Details

Before executing any use case, load the relevant reference file for that domain. Each file contains the exact tool call parameters, field-by-field workflow, and output instructions:

- For writing and communication tools (email, blog, meeting notes, social, tech doc, story): read `references/writing-workflows.md`
- For analysis and research tools (data, summary, comparison, survey, financial, legal): read `references/analysis-workflows.md`
- For coding and technical tools (codegen, review, SQL, API doc, test gen, ADR): read `references/coding-workflows.md`
- For business and productivity tools (planning, interview, proposal, support, PRD, decision): read `references/business-workflows.md`

Each reference file provides the exact workflow for each tool: what to call, which parameters to pass, which result fields to use, and how to produce the final output.

## Critical Rules

1. **Always call the tool first** — do not attempt computation (statistics, scoring, parsing) manually. The tool provides precise results.

2. **Use every returned field** — each field in the tool result guides a specific aspect of the output. Ignoring fields means missing part of the methodology or computation.

3. **Never copy templates verbatim** — use scaffold sections and templates as structural guides. Write original, contextual content that fits the user's specific situation.

4. **Present computed metrics explicitly** — share scores, rankings, percentages, and statistics with the user. These are the unique value the tool provides. For example, state "Formality score: 73.5" or "Vue leads with 8.1 points (margin: 0.2)".

5. **Flag issues the tool detects** — if the tool finds problems (missing legal clauses, low completeness scores, weak argument strength, high escalation risk), proactively tell the user and explain the implications.

6. **Add reasoning and recommendations** — the tool provides data; add interpretation, context, and actionable recommendations. Explain what the numbers mean and what the user should do about them.

7. **Use optional parameters when available** — many tools accept optional input (existing text, code, job description, draft response, investment amounts) that unlocks additional analysis. Ask the user for this input when relevant.

8. **Always remind about limitations** — for legal review, always note "have a lawyer review the final analysis." For financial analysis, note these are computed from the provided data only.
