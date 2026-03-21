# claude-101

> 27 AI tools as MCP server + CLI + Skill. Just talk to Claude — it handles the rest.

[![PyPI](https://img.shields.io/pypi/v/claude-101.svg)](https://pypi.org/project/claude-101/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/claude-world/claude-101/actions/workflows/ci.yml/badge.svg)](https://github.com/claude-world/claude-101/actions/workflows/ci.yml)

**[English](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)**

## What is this?

Install once, get 24 superpowers. Claude 101 is an MCP server that gives Claude **real computation abilities** — statistics, code analysis, SQL parsing, financial math, and more — things LLMs cannot do reliably on their own.

**How it works:**

```
You: "Compare React, Vue, and Svelte for our project"
  ↓
Skill tells Claude to call build_comparison_matrix
  ↓
MCP tool computes: Vue 8.1 > React 7.9 > Svelte 7.5 (weighted scoring)
  ↓
Claude writes: "Vue leads by 0.2 points. The result is sensitive to
               the DX weight — if you value Ecosystem more, React wins."
```

**Without claude-101:** Claude guesses at numbers and rankings.
**With claude-101:** Claude uses precise computation, then reasons about the results.

## Setup (2 minutes)

### Step 1: Add MCP Server

Add to your `.mcp.json` (project root or `~/.claude/.mcp.json`):

```json
{
  "mcpServers": {
    "claude-101": {
      "command": "uvx",
      "args": ["--from", "claude-101[mcp]", "claude-101-server"]
    }
  }
}
```

### Step 2: Install Skill

The Skill teaches Claude *when* to call each tool and *how* to use every field in the result:

```bash
mkdir -p ~/.claude/skills/claude-101-mastery/references
cd ~/.claude/skills/claude-101-mastery
BASE=https://raw.githubusercontent.com/claude-world/claude-101/main/skills/claude-101-mastery
curl -sLO $BASE/SKILL.md
curl -sLO $BASE/references/writing-workflows.md   --output-dir references
curl -sLO $BASE/references/analysis-workflows.md   --output-dir references
curl -sLO $BASE/references/coding-workflows.md     --output-dir references
curl -sLO $BASE/references/business-workflows.md   --output-dir references
```

**Done.** Start a new Claude Code session and just talk naturally.

## 24 Use Cases

After setup, you can simply ask Claude to do any of these — the Skill handles the rest:

### Writing & Communication

| # | You say... | Claude calls | What you get |
|---|-----------|-------------|-------------|
| 1 | "Write a follow-up email to the client" | `draft_email` | Email with computed formality score, Flesch readability, tone analysis, pre-send checklist |
| 2 | "Plan a blog post about FastAPI" | `draft_blog_post` | Outline with word targets per section, SEO fields, keyword analysis, heading validation |
| 3 | "Organize these meeting notes" | `parse_meeting_notes` | Extracted attendees, action items with owners + deadlines, decisions, topics |
| 4 | "Create a Threads post for this launch" | `format_social_content` | Platform-formatted text, character count check, hashtags, engagement signals |
| 5 | "Write a README for this project" | `scaffold_tech_doc` | Template + code structure analysis, completeness scoring, effort estimate |
| 6 | "Help me structure this novel" | `structure_story` | Story beats with word targets, tension curve, pacing/dialogue/transition analysis |

### Analysis & Research

| # | You say... | Claude calls | What you get |
|---|-----------|-------------|-------------|
| 7 | "Analyze this CSV data" | `analyze_data` | Per-column statistics, Pearson correlations, IQR outlier detection |
| 8 | "Summarize this 10-page report" | `summarize_document` | Key sentences (algorithmically scored), Flesch readability, keyword frequency |
| 9 | "Compare these 3 frameworks" | `build_comparison_matrix` | Weighted ranking with scores, winner + margin, sensitivity analysis |
| 10 | "Analyze our survey results" | `analyze_survey` | Per-question stats, NPS score (promoter/passive/detractor), satisfaction % |
| 11 | "Review this quarter's financials" | `analyze_financials` | Gross/operating/net margins, growth rates, burn rate, cash runway |
| 12 | "Check this contract for issues" | `review_legal_document` | 18+ clause detection, missing clause alerts, complexity score, risk levels |

### Coding & Technical

| # | You say... | Claude calls | What you get |
|---|-----------|-------------|-------------|
| 13 | "Scaffold a UserService class" | `scaffold_code` | Description-aware code (CRUD/API/auth patterns), 6 languages x 8 patterns |
| 14 | "Review this code for issues" | `analyze_code` | Cyclomatic complexity, nesting depth, magic numbers, quality grade A-F |
| 15 | "Explain and optimize this SQL" | `process_sql` | Formatted query, execution plan, performance hints (SELECT *, index usage) |
| 16 | "Generate API docs for these endpoints" | `scaffold_api_doc` | OpenAPI YAML/Markdown, consistency check, auth detection from code |
| 17 | "Write tests for this function" | `generate_test_cases` | Signature parsing, happy/edge/boundary cases, coverage analysis |
| 18 | "Should we use Kafka or SQS?" | `create_adr` | ADR with tech knowledge base (28 technologies), differentiated trade-offs |

### Business & Productivity

| # | You say... | Claude calls | What you get |
|---|-----------|-------------|-------------|
| 19 | "Plan this 8-week project" | `plan_project` | WBS with hours, milestones, critical path, risks, resource allocation |
| 20 | "Prepare me for this interview" | `prepare_interview` | Role-specific questions, STAR validation, JD skill extraction, time allocation |
| 21 | "Write a business proposal" | `scaffold_proposal` | AIDA framework, ROI/NPV calculation, argument strength analysis |
| 22 | "Handle this angry customer" | `build_support_response` | Issue classification, escalation risk 0-100, resolution estimate, quality scoring |
| 23 | "Create a PRD for this feature" | `scaffold_prd` | User stories, MoSCoW prioritization, completeness scoring, dependency detection |
| 24 | "Help me decide between these options" | `evaluate_decision` | Weighted scoring matrix, rankings, sensitivity analysis |

## CLI Usage

Also works as a standalone command-line tool:

```bash
# Install
pip install "claude-101[mcp]"

# List all tools
claude-101 list
claude-101 list --category analysis

# Run any tool directly
claude-101 draft-email "meeting follow-up" --tone assertive
claude-101 --pretty analyze-data "name,score\nAlice,95\nBob,87"
claude-101 scaffold-proposal business "Cloud Migration" --investment 100000 --annual-return 50000

# Pipe from stdin
echo "SELECT * FROM users" | claude-101 process-sql -
cat mycode.py | claude-101 analyze-code -

# Tool help
claude-101 draft-email --help
```

## Python Library

```python
from claude_101.analysis.data import analyze_data
from claude_101.business.decision import evaluate_decision

result = analyze_data("name,score\nAlice,95\nBob,87", output_format="csv", operations="all")
result["correlations"]  # [{"column_a": "score", "column_b": "hours", "pearson_r": 0.94}]

result = evaluate_decision("A,B", "Speed,Cost", "0.6,0.4", "A:Speed=9,Cost=5;B:Speed=6,Cost=9")
result["winner"]  # {"option": "A", "score": 7.4, "margin": 0.2}
```

## Architecture

```
claude-101/
  src/claude_101/
    server.py           # MCP server (27 tools via FastMCP)
    cli.py              # CLI (auto-generated from function signatures)
    _utils.py           # 14 shared computation functions
    _guides.py          # 24 embedded use-case guides
    writing/            # 6 tools: email, blog, meeting, social, techdoc, story
    analysis/           # 6 tools: data, summary, comparison, survey, financial, legal
    coding/             # 6 tools: codegen, review, sql, apidoc, testgen, adr
    business/           # 6 tools: planning, interview, proposal, support, prd, decision
  skills/
    claude-101-mastery.md  # Skill file (teaches Claude how to use all 24 tools)
  tests/                   # 157 tests across 6 files
```

**Dependencies:** Only `sqlparse` (everything else is stdlib). MCP is optional.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

MIT — see [LICENSE](LICENSE).
