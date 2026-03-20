"""Tests for server.py — MCP tool registration and basic execution."""

import json
import asyncio

from claude_101.cli import _build_registry


class TestServerTools:
    """Test that all 27 tools are registered and accessible."""

    def test_total_tool_count(self):
        registry = _build_registry()
        unique = {e.name for e in registry.values()}
        assert len(unique) == 27

    def test_all_categories_present(self):
        registry = _build_registry()
        categories = {e.category for e in registry.values()}
        assert categories == {"meta", "writing", "analysis", "coding", "business"}

    def test_server_imports_without_error(self):
        """Verify server module loads and mcp object exists."""
        from claude_101.server import mcp

        assert mcp is not None


class TestMetaToolExecution:
    """Test meta tool execution returns valid JSON."""

    def _run(self, coro):
        return asyncio.run(coro)

    def test_list_guides_all(self):
        from claude_101.server import list_guides

        result = self._run(list_guides())
        data = json.loads(result)
        assert len(data) == 24

    def test_list_guides_by_category(self):
        from claude_101.server import list_guides

        result = self._run(list_guides("writing"))
        data = json.loads(result)
        assert len(data) == 6
        assert all(g["category"] == "writing" for g in data)

    def test_get_guide(self):
        from claude_101.server import get_guide

        result = self._run(get_guide(1))
        data = json.loads(result)
        assert data["id"] == 1
        assert data["title"] == "Professional Email Drafting"
        assert data["tool"] == "draft_email"

    def test_get_guide_not_found(self):
        from claude_101.server import get_guide

        result = self._run(get_guide(99))
        data = json.loads(result)
        assert "error" in data

    def test_search_guides(self):
        from claude_101.server import search_guides

        result = self._run(search_guides("email"))
        data = json.loads(result)
        assert len(data) >= 1
        assert any("email" in g["title"].lower() for g in data)


class TestVersion:
    def test_version(self):
        from claude_101 import __version__

        assert __version__ == "0.2.0"
