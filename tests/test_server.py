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


class TestMCPServer:
    """Test the MCP surface the server exposes to clients."""

    def test_server_identity(self):
        from claude_101 import __version__
        from claude_101.server import mcp

        assert mcp.name == "claude-101"
        assert mcp.version == __version__

    def test_tools_match_cli_registry(self):
        from claude_101.server import mcp

        tools = asyncio.run(mcp.list_tools())
        registry = _build_registry()
        assert {t.name for t in tools} == {e.func.__name__ for e in registry.values()}

    def test_tools_are_read_only_with_text_output(self):
        from claude_101.server import mcp

        for tool in asyncio.run(mcp.list_tools()):
            assert tool.annotations.read_only_hint is True, tool.name
            assert tool.annotations.open_world_hint is False, tool.name
            assert tool.output_schema is None, tool.name
            assert tool.description, tool.name

    def test_call_tool_over_protocol(self):
        """List and call tools through an in-memory MCP client session."""
        from mcp.client import Client

        from claude_101 import __version__
        from claude_101.server import mcp

        async def session():
            async with Client(mcp) as client:
                tools = await client.list_tools()
                result = await client.call_tool("get_guide", {"guide_id": 1})
                return client.server_info, tools, result

        server_info, tools, result = asyncio.run(session())
        assert server_info.name == "claude-101"
        assert server_info.version == __version__
        assert len(tools.tools) == 27
        assert not result.is_error
        assert result.structured_content is None
        data = json.loads(result.content[0].text)
        assert data["id"] == 1
        assert data["tool"] == "draft_email"

    def test_call_tool_rejects_invalid_arguments(self):
        from mcp.client import Client

        from claude_101.server import mcp

        async def session():
            async with Client(mcp) as client:
                return await client.call_tool("get_guide", {"guide_id": "not-a-number"})

        result = asyncio.run(session())
        assert result.is_error


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

        assert __version__ == "0.3.0"
