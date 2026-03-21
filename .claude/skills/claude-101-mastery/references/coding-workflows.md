# Coding & Technical Tool Workflows

## 13. Code Generation (`scaffold_code`)

**Trigger:** User wants code scaffolding.

**Call:** `scaffold_code(language, pattern, name, description)`

**Workflow:**
1. Use `code` as starting point, then customize
2. Check `description_matched` — if a pattern was matched, methods are domain-relevant
3. Follow `naming_convention` consistently
4. Incorporate `notes` best practices
5. Enhance the scaffold with proper error handling, type hints, and docstrings
6. If `description_matched` is null, generate more contextual methods

## 14. Code Review (`analyze_code`)

**Trigger:** User wants code reviewed.

**Call:** `analyze_code(code, language)`

**Workflow:**
1. Report `complexity.complexity_grade` as the overall quality grade
2. Explain `complexity.cyclomatic_estimate` meaning
3. Flag `complexity.max_nesting_depth` if > 3
4. Address each item in `issues` with specific fix suggestions
5. Check `metrics.comment_ratio` — suggest improvement if too low
6. Write review: quality grade, specific issues, and improvement suggestions prioritized by severity

## 15. SQL Processing (`process_sql`)

**Trigger:** User wants SQL help.

**Call:** `process_sql(query, operation, dialect)`

**Workflow:**
1. Present `result` (formatted/explained query)
2. Confirm correct `tables` / `columns` references
3. Address every `warnings` item
4. Discuss each `performance_hints` concern (if explain operation)
5. For format: present the clean version
6. For explain: walk through execution step by step, then address performance hints
7. For validate: fix any issues found

## 16. API Documentation (`scaffold_api_doc`)

**Trigger:** User needs API docs generated.

**Call:** `scaffold_api_doc(endpoints, title, output_format, code)`

**Workflow:**
1. Present `document` (OpenAPI YAML or Markdown)
2. Address any `consistency` issues flagged
3. Include `example_bodies` in the documentation
4. Document `code_analysis.auth` method (if code provided)
5. Enhance with better descriptions, more examples, and error scenarios

## 17. Test Generation (`generate_test_cases`)

**Trigger:** User wants test cases for a function.

**Call:** `generate_test_cases(function_signature, language, strategy)`

**Workflow:**
1. Cover every category in `test_cases` (happy, edge, boundary, error)
2. Ensure `coverage_analysis` shows all categories have test cases
3. Use `code` as starting scaffold for the test file
4. Enhance generated tests with more meaningful assertions
5. Add domain-specific test cases the tool may have missed

## 18. Architecture Decisions (`create_adr`)

**Trigger:** User needs to evaluate architecture options.

**Call:** `create_adr(title, context, options, decision)`

**Workflow:**
1. Present `trade_off_matrix` differentiated comparison
2. Discuss each option's `pros` and `cons`
3. Use `markdown` as the ADR document template
4. Enhance trade-off analysis with the user's specific constraints
5. If any options show default values, provide deeper assessment based on context
