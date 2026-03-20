# claude-101

> 27 practical AI tools — MCP server + CLI. Real computation, zero API cost.

[![PyPI](https://img.shields.io/pypi/v/claude-101.svg)](https://pypi.org/project/claude-101/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/claude-world/claude-101/actions/workflows/ci.yml/badge.svg)](https://github.com/claude-world/claude-101/actions/workflows/ci.yml)

**[English](README.md) | [繁體中文](README.zh-TW.md)**

## What is this?

Claude 101 gives Claude (or any LLM) **27 structured tools** that do real local computation — statistics, parsing, scoring, validation, text analysis — and return structured JSON.

**Why?** LLMs are great at generating text but unreliable at math, counting, and structured analysis. These tools handle the computation so the LLM can focus on reasoning.

**Two interfaces:**
- **MCP Server** — Claude Code connects via MCP protocol
- **CLI** — Run any tool from your terminal: `claude-101 analyze-code "def foo(): pass"`

**Zero cost.** No paid APIs. All processing is local Python.

## Quick Start

```bash
# Install
pip install "claude-101[mcp]"

# Install the Skill (teaches Claude how to use all 24 tools)
mkdir -p ~/.claude/skills
curl -sL https://raw.githubusercontent.com/claude-world/claude-101/main/skills/claude-101-mastery.md \
  -o ~/.claude/skills/claude-101-mastery.md

# CLI — try a tool
claude-101 list
claude-101 draft-email "follow-up about Q3 budget" --tone friendly
claude-101 analyze-code "def fib(n): return n if n<2 else fib(n-1)+fib(n-2)"
claude-101 --pretty process-sql "SELECT * FROM users WHERE active = true"

# MCP Server — for Claude Code
claude-101 serve
```

### Connect to Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "claude-101": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "claude-101[mcp]", "claude-101-server"]
    }
  }
}
```

Or for local development:

```json
{
  "mcpServers": {
    "claude-101": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "claude_101.server"],
      "cwd": "/path/to/claude-101"
    }
  }
}
```

## All 27 Tools

### Writing & Communication (6)

| Tool | What it computes |
|------|-----------------|
| `draft-email` | Formality score, Flesch readability, tone analysis, email structure validation, pre-send checklist |
| `draft-blog-post` | Topic keyword extraction, heading hierarchy validation, readability targets, content gap analysis, SEO fields |
| `parse-meeting-notes` | Regex extraction of attendees, action items (owner + deadline), decisions, topics, timestamps |
| `format-social-content` | Platform-aware chunking, hashtag extraction, engagement signal detection (question/CTA/hook strength) |
| `scaffold-tech-doc` | 8 doc types with effort estimation; optional code structure parsing and README completeness scoring |
| `structure-story` | Tension curve interpolation, word targets; optional pacing analysis, dialogue ratio, scene transition detection |

### Analysis & Research (6)

| Tool | What it computes |
|------|-----------------|
| `analyze-data` | Per-column statistics (mean/median/stdev), Pearson correlation, IQR outlier detection |
| `summarize-document` | Extractive summarization via sentence scoring, Flesch readability, keyword frequency |
| `build-comparison-matrix` | Weight normalization, critical weight identification, sensitivity framework |
| `analyze-survey` | Per-question distributions, NPS calculation (promoter/passive/detractor), satisfaction scores |
| `analyze-financials` | Gross/operating/net margins, period-over-period growth, burn rate, cash runway |
| `review-legal-document` | 18+ clause pattern matching, risk levels, missing clause alerts, complexity score |

### Coding & Technical (6)

| Tool | What it computes |
|------|-----------------|
| `scaffold-code` | Code templates for 6 languages x 8 design patterns |
| `analyze-code` | Language detection, cyclomatic complexity, nesting depth, issue detection, quality grade A-F |
| `process-sql` | SQL parsing/formatting via sqlparse, dialect detection, structure extraction |
| `scaffold-api-doc` | Endpoint parsing, OpenAPI/Markdown generation, API consistency check, auth pattern detection |
| `generate-test-cases` | Function signature parsing, happy/edge/boundary test generation, coverage analysis |
| `create-adr` | Architecture Decision Records with trade-off matrix |

### Business & Productivity (6)

| Tool | What it computes |
|------|-----------------|
| `plan-project` | WBS decomposition, milestones, critical path, risk identification, effort estimation |
| `prepare-interview` | Role/level-based question curation, difficulty balancing, time allocation; optional JD skill extraction, STAR validation |
| `scaffold-proposal` | AIDA coverage scoring; optional argument strength analysis (claims vs evidence), ROI/NPV calculation |
| `build-support-response` | Issue classification, escalation risk 0-100, resolution time estimate, customer effort score; optional response quality scoring |
| `scaffold-prd` | MoSCoW auto-prioritization, requirements completeness scoring, user story quality validation, dependency detection |
| `evaluate-decision` | Weighted scoring, ranking, sensitivity analysis (+-10% weight simulation) |

### Meta (3)

| Tool | What it does |
|------|-------------|
| `list-guides` | Browse 24 use-case guides by category |
| `get-guide` | Get full guide with tips and steps |
| `search-guides` | Full-text search across guides |

## CLI Usage

```bash
# List all tools
claude-101 list
claude-101 list --category analysis

# Run a tool (positional args + optional flags)
claude-101 draft-email "meeting follow-up" --tone assertive --format brief
claude-101 scaffold-prd "TaskFlow" "Teams need better task tracking" --target-users "PM, Engineer"
claude-101 scaffold-proposal business "Cloud Migration" --investment 100000 --annual-return 50000

# Pretty JSON output
claude-101 --pretty analyze-data "name,score\nAlice,95\nBob,87" --format csv

# Read from stdin
echo "SELECT * FROM users" | claude-101 process-sql -
cat mycode.py | claude-101 analyze-code -

# Tool help
claude-101 draft-email --help
```

## Python Library

```python
from claude_101.writing.email import draft_email
from claude_101.analysis.data import analyze_data
from claude_101.coding.review import analyze_code
from claude_101.business.decision import evaluate_decision

# Every function returns a dict
result = draft_email("proposal to investor", tone="professional")
result["text_analysis"]["formality_score"]  # 73.5
result["text_analysis"]["readability"]["flesch_grade"]  # "Standard (8th-9th grade)"
```

## Development

```bash
git clone https://github.com/claude-world/claude-101.git
cd claude-101
pip install -e ".[all]"
pip install pytest ruff

# Run tests (160 tests)
pytest

# Lint
ruff check src/

# Start MCP server locally
python -m claude_101.server
```

## Architecture

```
src/claude_101/
    __init__.py         # Package version
    _utils.py           # 14 shared utilities (stats, text analysis, scoring)
    _guides.py          # 24 embedded use-case guides
    server.py           # MCP server (FastMCP wrapper)
    cli.py              # CLI interface (argparse, auto-generated from signatures)
    writing/            # 6 writing tools
    analysis/           # 6 analysis tools
    coding/             # 6 coding tools
    business/           # 6 business tools
tests/
    test_writing.py     # 48 tests
    test_business.py    # 40 tests
    test_coding.py      # 25 tests
    test_analysis.py    # 11 tests
    test_cli.py         # 24 tests
    test_server.py      # 12 tests
```

**Dependencies:** Only `sqlparse` (stdlib for everything else). MCP is optional.

## Skill System

The `skills/claude-101-mastery.md` file teaches Claude the optimal workflow for all 24 use cases. Install it once:

```bash
mkdir -p ~/.claude/skills
cp skills/claude-101-mastery.md ~/.claude/skills/
```

**What the Skill does:**
- Maps user intents to the right MCP tool
- Tells Claude which result fields to use and how
- Ensures Claude produces high-quality output informed by real computation
- Without the skill: Claude uses the tools. With the skill: Claude **masters** the tools.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT — see [LICENSE](LICENSE).
