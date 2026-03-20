# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-03-20

### Added

- **Skill system**: `skills/claude-101-mastery.md` — teaches Claude the optimal workflow for all 24 use cases (when to call which tool, how to use every result field, how to produce the final output)
- `create_adr`: technology knowledge base with 28 real profiles (databases, message queues, frameworks, cloud providers) for differentiated trade-off values
- `scaffold_code`: description-aware code generation — recognizes CRUD, API, auth, cache, queue patterns and generates relevant methods
- `build_comparison_matrix`: `scores` parameter for weighted ranking computation
- `process_sql`: 6 performance hints (SELECT *, cartesian join, subquery in WHERE, leading wildcard, ORDER BY without LIMIT, HAVING without aggregation)

### Fixed

- `parse_meeting_notes`: extract owner names from "Bob to update" patterns (was always "unassigned")
- `summarize_document`: improved sentence scoring with median threshold (was selecting 86% of sentences)
- `analyze_survey`: NPS calculated from single recommend column instead of summing across all questions
- `process_sql`: suppress "Missing semicolon" warning for single-statement queries

## [0.1.0] - 2026-03-20

### Added

- 27 tools across 4 categories: writing (6), analysis (6), coding (6), business (6), meta (3)
- MCP server via FastMCP (`claude-101 serve`)
- CLI interface with auto-generated subparsers (`claude-101 <tool> [args]`)
- 14 shared utility functions in `_utils.py` (statistics, text analysis, scoring)
- 24 embedded use-case guides
- Real computation in all tools: formality scoring, Flesch readability, Pearson correlation, IQR outlier detection, NPS calculation, cyclomatic complexity, SQL parsing, and more
- 160 tests across 6 test files
- CI/CD: GitHub Actions for testing (Python 3.10-3.13) and PyPI publishing via trusted publishing
- Documentation: README (EN + zh-TW), CONTRIBUTING (EN + zh-TW), SECURITY (EN + zh-TW)

[0.2.0]: https://github.com/claude-world/claude-101/releases/tag/v0.2.0
[0.1.0]: https://github.com/claude-world/claude-101/releases/tag/v0.1.0
