# Claude 101 — Project Instructions

This is the claude-101 MCP server project. When working on this codebase:

- Run tests with `pytest` before committing
- Run `ruff check src/ tests/` and `ruff format src/ tests/` for lint/format
- All tool functions must return `dict`, have type annotations, and Google-style docstrings
- MCP tools are registered in `server.py`, CLI in `cli.py` — keep both in sync
- Every tool must provide both **methodology** (framework/best practices) and **computation** (numbers/scores/metrics)
