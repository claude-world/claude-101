# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] - 2026-10-21

### Fixed

- **MCP server starts with the MCP Python SDK 2.x.** 0.2.x imported `mcp.server.fastmcp`, which mcp 2.0 removed, so every fresh `uvx --from "claude-101[mcp]" claude-101-server` install failed at startup with `ImportError: Install mcp extra`. The server now uses `MCPServer`, and the `mcp` extra is capped below 3 so a future major cannot break installs the same way
- Skill: `analyze_financials` workflows referred to a non-existent `cash_runway` field (the tool returns `burn_rate.runway_months`), and `build_support_response` workflows referred to `customer_effort.repeat_contact` (the field is `repeat_contact_signals`)
- README: `~/.claude/.mcp.json` is not a file Claude Code reads; setup now uses `claude mcp add --scope user` or a project `.mcp.json`. The `analyze-data` CLI example passed a literal `\n` and parsed zero rows; it now pipes the CSV through `printf`. The `analyze_data` library example now produces the correlation its comment shows
- CLI: the `--help` example `analyze-code --language python < myfile.py` failed with a missing `CODE` argument; it now passes `-` to read stdin
- SECURITY: the dependency list no longer claims `jinja2`, and supported versions are current

### Changed

- `mcp` extra requires `mcp>=2.3,<3` (was `mcp>=1.0`)
- Tools are advertised as read-only (`readOnlyHint: true`, `openWorldHint: false`) since they are local computations, and return plain JSON text without the redundant `{"result": "<json>"}` structured copy and output schema the SDK adds for `str` return types. The text output is unchanged
- The server reports its own version in `serverInfo` instead of the SDK's
- `sqlparse>=0.6` (was `>=0.5`), which fixes DoS advisories reachable through `process_sql` input: GHSA-prg7-hcfm-mfcr, GHSA-pwgv-4x5q-6m9f, GHSA-f2ff-p2ww-7p4p, GHSA-cfqr-cjx5-5jcm
- Skill description now names the requests that should trigger it, per current Claude Code and Agent Skills guidance
- Dev tooling: `pytest>=9.1`, `ruff>=0.17`; the ruff rule set is pinned in `pyproject.toml` because ruff 0.17 widened its defaults
- CI: `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8`; tests run on Python 3.10–3.15; a new job builds the package and runs `twine check --strict`. Dependabot now proposes monthly, grouped updates for pip and GitHub Actions
- Python 3.14 and 3.15 classifiers
- Docs: requirements section and 0.2.x upgrade note in all three READMEs; CONTRIBUTING (EN/zh-TW) uses the `dev` extra and the full lint/format commands

### Added

- Protocol-level server tests through the in-memory MCP client (162 tests, up from 157)

### Removed

- The unused `nlp` extra (`textblob` was never imported). Installing `claude-101[nlp]` now only prints an unknown-extra warning

## [0.2.2] - 2026-03-21

### Changed

- Skill restructured to the Claude Code skill format: `skills/claude-101-mastery/SKILL.md` with four per-domain `references/` workflow files
- Skill frontmatter: concise third-person description and `allowed-tools` pre-approving all 24 use-case MCP tools plus `Read`
- README install instructions updated for the directory-based skill

## [0.2.1] - 2026-03-20

### Added

- Complete trilingual documentation: English, Traditional Chinese (繁體中文), Japanese (日本語)
- Full 24 use-case table in all READMEs showing "You say → Claude calls → You get"
- Improved setup guide (2-step: MCP + Skill)

### Changed

- README rewritten with user-centric focus (what users say, not tool internals)
- Clearer architecture section

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

[0.3.0]: https://github.com/claude-world/claude-101/releases/tag/v0.3.0
[0.2.2]: https://github.com/claude-world/claude-101/releases/tag/v0.2.2
[0.2.1]: https://github.com/claude-world/claude-101/releases/tag/v0.2.1
[0.2.0]: https://github.com/claude-world/claude-101/releases/tag/v0.2.0
[0.1.0]: https://github.com/claude-world/claude-101/releases/tag/v0.1.0
