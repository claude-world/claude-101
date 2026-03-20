---
name: claude-101-mastery
description: Master skill for all 24 Claude 101 use cases. Guides Claude through the optimal workflow for each use case — when to call which MCP tool, how to interpret the results, and how to produce the final output.
---

# Claude 101 — 24 Use Case Mastery Skill

You have access to the `claude-101` MCP server with 27 tools. This skill teaches you the **optimal workflow** for each of the 24 use cases.

**Core Principle:** Call the MCP tool FIRST to get structured data and methodology, then use that data to produce a superior final output. The tool provides the framework and computation; you provide the writing and reasoning.

---

## Writing & Communication

### 1. Professional Email Drafting

**When:** User asks to write, draft, or review an email.

**Workflow:**
1. Call `draft_email` with the user's context, desired tone, and format
2. From the result, use:
   - `text_analysis.formality_score` — adjust your writing to match the target formality
   - `text_analysis.tone_words` — ensure your draft's tone matches the analysis
   - `text_analysis.structure` — check if greeting/CTA/closing are present
   - `tone_guide.vocabulary` — weave these phrases naturally into the draft
   - `tone_guide.avoid` — ensure none of these appear in your output
   - `pre_send_checklist` — present this to the user at the end
3. Write the actual email yourself (don't use the template sections verbatim — they're structural guides)
4. Include the subject line suggestions and pre-send checklist

**Quality check:** Re-read and verify formality matches the computed score range.

### 2. Blog Post & Article Writing

**When:** User wants to plan, outline, or write a blog post.

**Workflow:**
1. Call `draft_blog_post` with topic, target word count, and style
2. From the result, use:
   - `outline` — follow this section structure with exact word targets per section
   - `style_guide` — match voice, sentence length, and examples-per-section guidance
   - `seo_fields` — include the focus keyword, use the slug, optimize title tag
   - `topic_analysis.primary_keywords` — ensure these appear in headings and body
   - `readability_target` — write within this Flesch score range
   - `heading_validation` — verify your heading structure is valid
   - `content_gaps` — address each identified gap
3. Write each section following the word targets
4. Present the SEO fields for the user to configure in their CMS

### 3. Meeting Notes & Summaries

**When:** User pastes raw meeting notes or transcript.

**Workflow:**
1. Call `parse_meeting_notes` with the raw text
2. From the result, use:
   - `attendees` — list all participants
   - `action_items` — present each with owner, task, and deadline
   - `decisions` — highlight all decisions made
   - `topics` — organize notes by topic
   - `metrics` — summarize (duration, action count, decision count)
3. Format into a clean structured summary the user can share with the team
4. Flag any action items with "unassigned" owner — ask the user who should own them

### 4. Social Media Content Creation

**When:** User wants to create social media posts.

**Workflow:**
1. Call `format_social_content` with the user's draft text and target platform
2. From the result, use:
   - `within_limit` — if false, you MUST shorten the content
   - `chunks` — if the text needs splitting, use these pre-numbered chunks
   - `hashtags` — append relevant ones (or weave them in)
   - `engagement_signals` — if `has_question` is false, consider adding one; if `hook_strength` is weak, rewrite the first line
3. Rewrite the content optimizing for the platform while keeping the user's message
4. If over the character limit, present the chunked version as a thread

### 5. Technical Documentation

**When:** User needs a README, API doc, RFC, ADR, runbook, or other technical doc.

**Workflow:**
1. Call `scaffold_tech_doc` with doc type, title, and optionally pass existing code via `content`
2. From the result, use:
   - `sections` — follow this exact section structure (required vs optional)
   - `best_practices` — incorporate each practice into your writing
   - `template` — use as starting skeleton, replace all `[placeholders]`
   - `effort_estimate` — share with user for planning
   - `analysis.code_structure` (if code provided) — reference extracted functions/classes
   - `analysis.completeness` (if README) — address every item in `missing` list
3. Write each section with appropriate detail for the audience
4. For README type, ensure every item in the completeness checklist is covered

### 6. Creative Writing & Storytelling

**When:** User wants to write fiction, plan a story, or analyze existing text.

**Workflow:**
1. Call `structure_story` with genre, elements, structure, and optionally existing text
2. From the result, use:
   - `beats` — follow these story beats with their word targets
   - `tension_curve` — ensure your writing follows this emotional arc
   - `character_arc_template` — use as guide for character development
   - `genre_conventions` — incorporate at least 3 of these conventions
   - If `text_analysis` is present:
     - `pacing` — fix any beats marked "slow" or "fast"
     - `dialogue.ratio` — adjust if too heavy or too light for genre
     - `scene_transitions` — add more if `avg_scene_words` is very high
     - `character_mentions.distribution` — balance screen time
3. Write or revise the story following the computed structure

---

## Analysis & Research

### 7. Data Analysis & Interpretation

**When:** User provides CSV/JSON data or asks for data analysis.

**Workflow:**
1. Call `analyze_data` with the data, format, and `operations="all"`
2. From the result, use:
   - `columns` — describe each column's type and key stats
   - `correlations` — explain what the Pearson r values mean in context
   - `outliers` — flag specific outlier values and hypothesize why
3. Write a narrative interpretation: "The data shows... The strongest relationship is... Notable outliers include..."
4. Suggest follow-up analyses based on what the data reveals

### 8. Document Summarization

**When:** User wants a document summarized.

**Workflow:**
1. Call `summarize_document` with the text and desired sentence count
2. From the result, use:
   - `key_sentences` — these are the most important sentences (algorithmically selected)
   - `flesch_score` / `flesch_grade` — report readability level
   - `keywords` — these are the document's core themes
3. Write a coherent summary that connects the key sentences into a narrative
4. Add your own interpretation and key takeaways beyond what the algorithm found

### 9. Competitive Research

**When:** User wants to compare products, tools, or options.

**Workflow:**
1. Call `build_comparison_matrix` with items, criteria, weights, and scores (if available)
2. From the result, use:
   - `weights` — explain why each criterion has its weight
   - `rankings` — present the ranked results with weighted scores
   - `winner` — highlight the winner and margin
   - `sensitivity_framework` — discuss which weights would flip the result
3. Write an analysis narrative: "Based on weighted scoring, X leads with... However, this is sensitive to..."
4. Recommend based on the user's specific context, not just the numbers

### 10. Survey & Feedback Analysis

**When:** User provides survey data.

**Workflow:**
1. Call `analyze_survey` with CSV data and scale max
2. From the result, use:
   - `questions` — report per-question mean, median, and distribution
   - `nps` — explain the NPS score and what promoter/passive/detractor split means
   - `overall_satisfaction` — contextualize (industry benchmarks: 70%+ is good)
3. Identify the weakest questions (lowest mean) and strongest
4. Recommend specific actions based on the distribution patterns

### 11. Financial Report Analysis

**When:** User provides financial data.

**Workflow:**
1. Call `analyze_financials` with CSV data and period
2. From the result, use:
   - `margins` — report gross, operating, and net margins with trends
   - `metrics.revenue.growth_rates` — highlight growth trends
   - `burn_rate` / `cash_runway` — flag if concerning
   - `summary` — reference best/worst periods and overall trend
3. Write an executive summary with actionable recommendations
4. Flag any concerning trends (declining margins, increasing burn rate)

### 12. Legal Document Review

**When:** User provides a contract or legal document.

**Workflow:**
1. Call `review_legal_document` with text and document type
2. From the result, use:
   - `clauses_found` — list each detected clause with its risk level
   - `missing_clauses` — **critically important** — flag every missing standard clause
   - `complexity_score` — explain what this means for readability
3. Write a review organized by risk level (high → medium → low)
4. For each missing clause, explain WHY it matters and what risk it creates
5. **Always remind the user to have a lawyer review the final analysis**

---

## Coding & Technical

### 13. Code Generation & Explanation

**When:** User wants code scaffolding.

**Workflow:**
1. Call `scaffold_code` with language, pattern, name, and description
2. From the result, use:
   - `code` — use as starting point, then customize
   - `description_matched` — if a pattern was matched, the methods are domain-relevant
   - `naming_convention` — follow this convention consistently
   - `notes` — incorporate these best practices
3. Enhance the scaffold with proper error handling, type hints, and docstrings
4. If `description_matched` is null, generate more contextual methods yourself

### 14. Code Review & Debugging

**When:** User wants code reviewed.

**Workflow:**
1. Call `analyze_code` with the code
2. From the result, use:
   - `complexity.complexity_grade` — report the overall grade
   - `complexity.cyclomatic_estimate` — explain what this means
   - `complexity.max_nesting_depth` — flag if > 3
   - `issues` — address each issue with specific fix suggestions
   - `metrics.comment_ratio` — suggest if too low
3. Write a review covering: quality grade, specific issues, and improvement suggestions
4. Prioritize issues by severity

### 15. SQL Query Writing

**When:** User wants SQL help.

**Workflow:**
1. Call `process_sql` with the query and operation (format/validate/explain/extract)
2. From the result, use:
   - `result` — the formatted/explained query
   - `tables` / `columns` — confirm correct table references
   - `warnings` — address every warning
   - `performance_hints` (if explain) — discuss each performance concern
3. If formatting: present the clean version
4. If explaining: walk through the execution step by step, then address performance hints
5. If validating: fix any issues found

### 16. API Documentation

**When:** User needs API docs generated.

**Workflow:**
1. Call `scaffold_api_doc` with endpoints, title, format, and optionally source code
2. From the result, use:
   - `document` — present the generated OpenAPI YAML or Markdown
   - `consistency` — address any API design issues flagged
   - `example_bodies` — include these in the documentation
   - `code_analysis.auth` (if code provided) — document the auth method
3. Enhance the generated doc with better descriptions, more examples, and error scenarios

### 17. Test Case Generation

**When:** User wants test cases for a function.

**Workflow:**
1. Call `generate_test_cases` with the function signature and strategy
2. From the result, use:
   - `test_cases` — cover every category (happy, edge, boundary, error)
   - `coverage_analysis` — ensure all categories have test cases
   - `code` — use as starting scaffold for the test file
3. Enhance the generated tests with more meaningful assertions
4. Add any domain-specific test cases the tool may have missed

### 18. Architecture & Design Decisions

**When:** User needs to evaluate architecture options.

**Workflow:**
1. Call `create_adr` with title, context, options, and decision (if made)
2. From the result, use:
   - `trade_off_matrix` — present the differentiated comparison (now with real tech profiles)
   - `adr.options` — discuss each option's pros and cons
   - `markdown` — use as the ADR document template
3. Enhance the trade-off analysis with the user's specific constraints
4. If any options show "unknown technology — using default values", provide your own assessment

---

## Business & Productivity

### 19. Project Planning & Task Breakdown

**When:** User describes a project to plan.

**Workflow:**
1. Call `plan_project` with description, team size, and duration
2. From the result, use:
   - `phases` — present the phased breakdown with hours
   - `milestones` — highlight key checkpoints
   - `critical_path` — explain which tasks are blocking
   - `risks` — discuss each risk and mitigation
   - `total_hours` / `resource_allocation` — validate feasibility
3. Create a timeline visualization (text-based Gantt chart)
4. Ask the user if the scope/timeline/team fit their constraints

### 20. Interview Preparation

**When:** User is preparing for an interview.

**Workflow:**
1. Call `prepare_interview` with role, level, focus, and optionally JD and practice response
2. From the result, use:
   - `preparation.questions` — practice each with the STAR template
   - `difficulty_distribution` — ensure balanced preparation
   - `per_question_time` — allocate practice time accordingly
   - `job_analysis` (if JD provided) — map skills to preparation topics
   - `star_validation` (if response provided) — give feedback on missing STAR components
   - `preparation_checklist` — present as a to-do list
3. For each practice question, help the user craft a strong STAR response
4. If STAR validation score < 100, coach them on the missing components

### 21. Proposal & Pitch Writing

**When:** User wants to write a business proposal.

**Workflow:**
1. Call `scaffold_proposal` with type, title, audience, and optionally content/investment/return
2. From the result, use:
   - `sections` — follow the section structure with word targets
   - `persuasion_framework` — map each section to AIDA (Attention/Interest/Desire/Action)
   - `aida_coverage.balance_score` — aim for > 80
   - `objection_templates` — prepare responses for each potential objection
   - `argument_analysis` (if content provided) — strengthen weak arguments
   - `roi_analysis` (if investment provided) — include exact ROI%, payback period, NPV
3. Write each section following the AIDA framework
4. Include the ROI calculations as supporting evidence

### 22. Customer Support Responses

**When:** User needs to handle a support issue.

**Workflow:**
1. Call `build_support_response` with issue, channel, tone, and optionally a draft
2. From the result, use:
   - `issue_classification` — understand category, severity, sentiment
   - `escalation_risk` — if high/critical, escalate immediately
   - `resolution_estimate` — set expectations with the customer
   - `customer_effort` — if repeat contact, acknowledge the frustration explicitly
   - `response_quality` (if draft provided) — improve based on scores
   - `response_scaffold` — use as structural guide (not verbatim)
   - `empathy_phrases` — weave these naturally into your response
3. Write a response that matches the channel guidelines
4. If escalation risk is high, suggest the user involve a manager

### 23. Product Requirements Documents

**When:** User needs to create a PRD.

**Workflow:**
1. Call `scaffold_prd` with product name, problem, and target users
2. From the result, use:
   - `sections` — follow the PRD structure
   - `user_stories` — include each with its STAR format
   - `prioritization.categories` — present the MoSCoW breakdown
   - `requirements_analysis.completeness` — address every issue flagged
   - `requirements_analysis.story_quality` — improve low-scoring stories
   - `requirements_analysis.dependencies` — visualize the dependency graph
   - `success_metrics` — include all metrics with targets
3. Write each PRD section with the user's domain knowledge
4. Challenge any completeness issues: "The analysis shows [gap] — let's address this"

### 24. Decision Frameworks & Evaluation

**When:** User needs to make a decision between options.

**Workflow:**
1. Ask the user for: options, criteria, weights, and scores
2. Call `evaluate_decision` with all parameters
3. From the result, use:
   - `rankings` — present the weighted ranking
   - `winner` — highlight with margin of victory
   - `sensitivity_analysis` — explain which criteria could flip the result
4. Write a decision recommendation: "Based on weighted analysis, [winner] leads by [margin]. This result is robust/fragile because [sensitivity insight]."
5. If the margin is small, recommend the user reconsider their weights

---

## General Rules

1. **Always call the MCP tool first** — don't try to do computation yourself
2. **Use every field the tool returns** — each field exists for a reason
3. **Don't copy templates verbatim** — use them as structural guides, write original content
4. **Present computation results** — share scores, metrics, and analysis with the user
5. **Add your own reasoning** — the tool provides data, you provide insight
6. **Flag issues** — if the tool finds problems (missing clauses, low scores, weak arguments), tell the user
