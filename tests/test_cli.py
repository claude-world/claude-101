"""Tests for the CLI interface."""

import json
from io import StringIO
from unittest.mock import patch

import pytest

from claude_101.cli import main, _build_registry, _parse_docstring_args


class TestRegistry:
    def test_all_27_tools_registered(self):
        registry = _build_registry()
        # Each tool is registered twice (hyphen + underscore), so 27 * 2 = 54
        unique_names = {e.name for e in registry.values()}
        assert len(unique_names) == 27

    def test_categories(self):
        registry = _build_registry()
        categories = {e.category for e in registry.values()}
        assert categories == {"meta", "writing", "analysis", "coding", "business"}

    def test_hyphen_and_underscore_both_work(self):
        registry = _build_registry()
        assert "draft-email" in registry
        assert "draft_email" in registry
        assert registry["draft-email"].func is registry["draft_email"].func

    def test_entries_have_description(self):
        registry = _build_registry()
        for entry in registry.values():
            assert entry.description, f"{entry.name} has no description"


class TestDocstringParser:
    def test_parses_args(self):
        docstring = """Do something.

        Args:
            name: The name of the thing.
            value: The value to set.
                   Can span multiple lines.

        Returns:
            Something.
        """
        result = _parse_docstring_args(docstring)
        assert "name" in result
        assert result["name"] == "The name of the thing."
        assert "value" in result
        assert "multiple lines" in result["value"]

    def test_empty_docstring(self):
        assert _parse_docstring_args(None) == {}
        assert _parse_docstring_args("") == {}

    def test_no_args_section(self):
        assert _parse_docstring_args("Just a simple function.") == {}


class TestMainHelp:
    def test_no_args_shows_help(self, capsys):
        ret = main([])
        assert ret == 0
        captured = capsys.readouterr()
        assert "claude-101" in captured.out

    def test_version(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0


class TestListCommand:
    def test_list_all(self, capsys):
        ret = main(["list"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "27 tools available" in captured.out
        assert "draft-email" in captured.out

    def test_list_category_filter(self, capsys):
        ret = main(["list", "--category", "writing"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "draft-email" in captured.out
        assert "analyze-data" not in captured.out

    def test_list_pretty_json(self, capsys):
        ret = main(["--pretty", "list"])
        assert ret == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) == 27


class TestToolDispatch:
    def test_draft_email(self, capsys):
        ret = main(["draft-email", "follow-up about Q3 proposal"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "subject_suggestions" in result
        assert "text_analysis" in result

    def test_draft_email_pretty(self, capsys):
        ret = main(["--pretty", "draft-email", "quick note"])
        assert ret == 0
        captured = capsys.readouterr()
        # Pretty output has indentation
        assert "\n  " in captured.out
        result = json.loads(captured.out)
        assert "sections" in result

    def test_draft_email_with_options(self, capsys):
        ret = main(["draft-email", "thanks for help", "--tone", "friendly", "--format", "brief"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["tone_guide"]["formality"] in ("low", "medium")

    def test_analyze_code(self, capsys):
        ret = main(["analyze-code", "def foo():\n    return 42", "--language", "python"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["language"] == "python"

    def test_scaffold_prd(self, capsys):
        ret = main(["scaffold-prd", "TaskFlow", "Teams need better task tracking"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["product_name"] == "TaskFlow"

    def test_underscore_name_in_registry(self):
        """Underscore names resolve in the registry (CLI uses hyphen subcommands)."""
        registry = _build_registry()
        assert "draft_email" in registry
        assert registry["draft_email"].func is registry["draft-email"].func

    def test_int_parameter(self, capsys):
        ret = main(["draft-blog-post", "AI Tips", "--target-words", "800"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["target_words"] == 800

    def test_float_parameter(self, capsys):
        ret = main([
            "scaffold-proposal", "business", "Cloud Migration",
            "--investment", "100000", "--annual-return", "50000",
        ])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "roi_analysis" in result

    def test_bool_parameter(self, capsys):
        ret = main(["format-social-content", "Test post", "--no-include-hashtags"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        # Hashtags feature should be off
        assert "hashtags" not in result or result.get("hashtags") == []


class TestStdinSupport:
    def test_stdin_reading(self, capsys):
        stdin_text = "SELECT * FROM users WHERE id = 1"
        with patch("sys.stdin", StringIO(stdin_text)):
            ret = main(["process-sql", "-"])
        assert ret == 0
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert "users" in result["tables"]


class TestToolHelp:
    def test_tool_help(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["draft-email", "--help"])
        assert exc_info.value.code == 0


class TestErrorHandling:
    def test_unknown_tool(self):
        """Unknown subcommand causes argparse to exit with code 2."""
        with pytest.raises(SystemExit) as exc_info:
            main(["nonexistent-tool"])
        assert exc_info.value.code == 2
