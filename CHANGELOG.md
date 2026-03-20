# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

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

[0.1.0]: https://github.com/claude-world/claude-101/releases/tag/v0.1.0
