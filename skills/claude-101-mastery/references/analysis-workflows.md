# Analysis & Research Tool Workflows

## 7. Data Analysis (`analyze_data`)

**Trigger:** User provides CSV/JSON data or asks for data analysis.

**Call:** `analyze_data(data, output_format, operations="all")`

**Workflow:**
1. Describe each column using `columns` type and key stats
2. Explain `correlations` Pearson r values in context (strong/moderate/weak)
3. Flag specific `outliers` values and hypothesize why
4. Write a narrative: "The data shows... The strongest relationship is... Notable outliers include..."
5. Suggest follow-up analyses based on what the data reveals

## 8. Document Summarization (`summarize_document`)

**Trigger:** User wants a document summarized.

**Call:** `summarize_document(text, max_sentences)`

**Workflow:**
1. Use `key_sentences` as the most important sentences (algorithmically selected)
2. Report `flesch_score` / `flesch_grade` readability level
3. Use `keywords` to identify core themes
4. Write a coherent summary connecting key sentences into a narrative
5. Add interpretation and key takeaways beyond what the algorithm found

## 9. Competitive Research (`build_comparison_matrix`)

**Trigger:** User wants to compare products, tools, or options.

**Call:** `build_comparison_matrix(items, criteria, weights, scores)`

**Workflow:**
1. Explain `weights` — why each criterion has its weight
2. Present `rankings` with weighted scores
3. Highlight `winner` and margin
4. Discuss `sensitivity_framework` — which weights would flip the result
5. Write analysis: "Based on weighted scoring, X leads with... However, this is sensitive to..."
6. Recommend based on the user's specific context

## 10. Survey Analysis (`analyze_survey`)

**Trigger:** User provides survey data.

**Call:** `analyze_survey(data, scale_max)`

**Workflow:**
1. Report per-question mean, median, and distribution from `questions`
2. Explain `nps` score and promoter/passive/detractor split
3. Contextualize `overall_satisfaction` (industry benchmark: 70%+ is good)
4. Identify weakest questions (lowest mean) and strongest
5. Recommend specific actions based on distribution patterns

## 11. Financial Analysis (`analyze_financials`)

**Trigger:** User provides financial data.

**Call:** `analyze_financials(data, period)`

**Workflow:**
1. Report `margins` (gross, operating, net) with trends
2. Highlight `growth_rates` for revenue
3. Flag `burn_rate` / `cash_runway` if concerning
4. Reference `summary` best/worst periods and overall trend
5. Write executive summary with actionable recommendations

## 12. Legal Review (`review_legal_document`)

**Trigger:** User provides a contract or legal document.

**Call:** `review_legal_document(text, doc_type)`

**Workflow:**
1. List each `clauses_found` with its risk level
2. **Critical:** Flag every `missing_clauses` standard clause
3. Explain `complexity_score` for readability
4. Organize review by risk level (high → medium → low)
5. For each missing clause, explain WHY it matters and what risk it creates
6. **Always remind the user to have a lawyer review the final analysis**
