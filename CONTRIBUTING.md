# Contributing to claude-101

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/claude-world/claude-101.git
cd claude-101
pip install -e ".[all]"
pip install pytest ruff
```

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_writing.py -v

# Single test
pytest tests/test_cli.py::TestToolDispatch::test_draft_email -v
```

## Code Style

- **Linter:** `ruff check src/`
- **Type hints:** All public functions must have type annotations
- **Docstrings:** Google-style with `Args:` and `Returns:` sections
- **No new dependencies** unless absolutely necessary — prefer stdlib

## Adding a New Tool

1. Create the function in the appropriate module (`writing/`, `analysis/`, `coding/`, `business/`)
2. Function must:
   - Accept typed parameters and return `dict`
   - Perform **real computation** (not just return templates)
   - Have a Google-style docstring with `Args:` and `Returns:`
3. Register in `server.py` with `@mcp.tool()` wrapper
4. Add to `cli.py` registry in `_build_registry()`
5. Add tests in the corresponding test file
6. Update the tool count in `README.md` and `__init__.py`

## Pull Request Process

1. Fork the repo and create a feature branch from `main`
2. Make your changes with tests
3. Ensure all tests pass: `pytest`
4. Ensure lint passes: `ruff check src/`
5. Open a PR against `main` with a clear description

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add sentiment analysis tool
fix: correct Flesch score calculation for short texts
docs: update CLI usage examples
test: add edge case tests for formality_score
```

## Reporting Issues

- Use GitHub Issues
- Include: Python version, OS, steps to reproduce, expected vs actual behavior
- For tool bugs: include the exact input and output JSON

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
