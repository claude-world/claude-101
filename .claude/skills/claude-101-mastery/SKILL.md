---
name: claude-101-mastery
description: This skill should be used when the user asks to "write an email", "draft a blog post", "analyze data", "review code", "optimize SQL", "compare options", "plan a project", "prepare for interview", "write a proposal", "create a PRD", "handle customer support", "make a decision", "summarize a document", "analyze survey results", "review a contract", "generate API docs", "write tests", "structure a story", "format social media post", "organize meeting notes", "scaffold code", "choose between technologies", or "analyze financials". Covers all 24 Claude 101 use cases via MCP tools.
version: 0.2.1
---

# Claude 101 Mastery

This skill provides the optimal workflow for 24 use cases powered by the `claude-101` MCP server. Each use case follows the same pattern: call the MCP tool first to get structured data and computation, then use that data to produce a superior final output.

## Core Principle

Always call the MCP tool FIRST. The tool provides framework + computation; the final writing and reasoning come from Claude. Never skip the tool call — the computed metrics (scores, rankings, statistics) are what the user cannot get from Claude alone.

## Workflow Pattern

For every use case:
1. Identify the matching MCP tool from the table below
2. Call the tool with appropriate parameters
3. Read every field in the result — each exists for a reason
4. Produce the final output informed by the tool's data
5. Present key metrics (scores, rankings, statistics) to the user

## Use Case → Tool Mapping

| User Intent | MCP Tool | Key Output Fields |
|------------|----------|------------------|
| Write/draft email | `draft_email` | `text_analysis`, `tone_guide`, `pre_send_checklist` |
| Plan blog post | `draft_blog_post` | `outline`, `seo_fields`, `topic_analysis`, `readability_target` |
| Organize meeting notes | `parse_meeting_notes` | `attendees`, `action_items`, `decisions`, `metrics` |
| Create social media post | `format_social_content` | `within_limit`, `chunks`, `hashtags`, `engagement_signals` |
| Write technical docs | `scaffold_tech_doc` | `template`, `sections`, `best_practices`, `analysis` |
| Structure a story | `structure_story` | `beats`, `tension_curve`, `text_analysis` |
| Analyze data (CSV/JSON) | `analyze_data` | `columns`, `correlations`, `outliers` |
| Summarize document | `summarize_document` | `key_sentences`, `flesch_score`, `keywords` |
| Compare options | `build_comparison_matrix` | `rankings`, `winner`, `sensitivity_framework` |
| Analyze survey | `analyze_survey` | `questions`, `nps`, `overall_satisfaction` |
| Review financials | `analyze_financials` | `margins`, `growth_rates`, `burn_rate` |
| Review legal document | `review_legal_document` | `clauses_found`, `missing_clauses`, `complexity_score` |
| Generate code scaffold | `scaffold_code` | `code`, `description_matched`, `naming_convention` |
| Review code quality | `analyze_code` | `complexity`, `issues`, `metrics` |
| Process SQL | `process_sql` | `result`, `tables`, `warnings`, `performance_hints` |
| Generate API docs | `scaffold_api_doc` | `document`, `consistency`, `code_analysis` |
| Generate test cases | `generate_test_cases` | `test_cases`, `coverage_analysis` |
| Architecture decision | `create_adr` | `trade_off_matrix`, `adr`, `markdown` |
| Plan project | `plan_project` | `phases`, `milestones`, `critical_path`, `risks` |
| Prepare interview | `prepare_interview` | `questions`, `difficulty_distribution`, `star_validation` |
| Write proposal | `scaffold_proposal` | `sections`, `aida_coverage`, `roi_analysis`, `argument_analysis` |
| Handle support issue | `build_support_response` | `issue_classification`, `escalation_risk`, `resolution_estimate` |
| Create PRD | `scaffold_prd` | `user_stories`, `prioritization`, `requirements_analysis` |
| Decision analysis | `evaluate_decision` | `rankings`, `winner`, `sensitivity_analysis` |

## Per-Tool Guidance

Detailed workflow instructions for each of the 24 tools are in the `references/` directory:

- To see writing tool workflows: read `references/writing-workflows.md`
- To see analysis tool workflows: read `references/analysis-workflows.md`
- To see coding tool workflows: read `references/coding-workflows.md`
- To see business tool workflows: read `references/business-workflows.md`

## Critical Rules

1. **Always call the tool first** — do not attempt computation manually
2. **Use every returned field** — each field guides a specific aspect of the output
3. **Never copy templates verbatim** — use them as structural guides, write original content
4. **Present computed metrics** — share scores, rankings, and statistics with the user
5. **Flag issues found** — if the tool detects problems (missing clauses, low scores, weak arguments), tell the user
6. **Add reasoning** — the tool provides data, add interpretation and recommendations
