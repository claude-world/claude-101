# Business & Productivity Tool Workflows

## 19. Project Planning (`plan_project`)

**Trigger:** User describes a project to plan.

**Call:** `plan_project(description, team_size, duration_weeks)`

**Workflow:**
1. Present `phases` breakdown with hours
2. Highlight `milestones` key checkpoints
3. Explain `critical_path` blocking tasks
4. Discuss each `risks` item and mitigation
5. Validate `total_hours` / `resource_allocation` feasibility
6. Create a timeline visualization (text-based Gantt chart)
7. Ask the user if scope/timeline/team fit their constraints

## 20. Interview Preparation (`prepare_interview`)

**Trigger:** User is preparing for an interview.

**Call:** `prepare_interview(role, level, focus, job_description, response)`

**Workflow:**
1. Practice each `preparation.questions` with the STAR template
2. Use `difficulty_distribution` to ensure balanced preparation
3. Allocate practice time using `per_question_time`
4. Map `job_analysis` skills to preparation topics (if JD provided)
5. Give feedback on `star_validation` missing components (if response provided)
6. Present `preparation_checklist` as a to-do list
7. For each practice question, help craft a strong STAR response
8. If STAR validation score < 100, coach on the missing components

## 21. Proposal Writing (`scaffold_proposal`)

**Trigger:** User wants to write a business proposal.

**Call:** `scaffold_proposal(type, title, audience, content, investment, annual_return)`

**Workflow:**
1. Follow `sections` structure with `target_words` per section
2. Map each section to AIDA using `persuasion_framework`
3. Aim for `aida_coverage.balance_score` > 80
4. Prepare `objection_templates` responses
5. Strengthen weak arguments per `argument_analysis` (if content provided)
6. Include exact ROI%, payback period, NPV from `roi_analysis` (if investment provided)
7. Write each section following the AIDA framework
8. Include ROI calculations as supporting evidence

## 22. Customer Support (`build_support_response`)

**Trigger:** User needs to handle a support issue.

**Call:** `build_support_response(issue, channel, tone, draft_response)`

**Workflow:**
1. Understand `issue_classification` category, severity, sentiment
2. If `escalation_risk` is high/critical, recommend escalation immediately
3. Set expectations using `resolution_estimate`
4. If `customer_effort.repeat_contact` is true, acknowledge frustration explicitly
5. Improve draft based on `response_quality` scores (if draft provided)
6. Use `response_scaffold` as structural guide (not verbatim)
7. Weave `empathy_phrases` naturally into the response
8. Follow `channel_guidelines` format tips

## 23. Product Requirements (`scaffold_prd`)

**Trigger:** User needs to create a PRD.

**Call:** `scaffold_prd(product_name, problem, target_users)`

**Workflow:**
1. Follow `sections` PRD structure
2. Include each `user_stories` with STAR format
3. Present `prioritization.categories` MoSCoW breakdown
4. Address every `requirements_analysis.completeness` issue
5. Improve low-scoring stories per `requirements_analysis.story_quality`
6. Visualize `requirements_analysis.dependencies` graph
7. Include all `success_metrics` with targets
8. Challenge completeness issues: "The analysis shows [gap] — address this"

## 24. Decision Analysis (`evaluate_decision`)

**Trigger:** User needs to make a decision between options.

**Call:** `evaluate_decision(options, criteria, weights, scores)`

**Workflow:**
1. If options, criteria, weights, or scores are missing, infer reasonable defaults from context or use equal weights
2. Present `rankings` weighted ranking
3. Highlight `winner` with margin of victory
4. Explain `sensitivity_analysis` — which criteria could flip the result
5. Write recommendation: "Based on weighted analysis, [winner] leads by [margin]. This result is robust/fragile because [sensitivity insight]."
6. If the margin is small, recommend the user reconsider their weights
