"""Tests for server.py — MCP tool registration and basic execution."""

import json
import asyncio

from claude_101.server import mcp


class TestServerTools:
    """Test that all 27 MCP tools are registered."""

    def test_total_tool_count(self):
        tools = mcp._tool_manager._tools
        assert len(tools) == 27

    def test_meta_tools_present(self):
        tools = mcp._tool_manager._tools
        for name in ("list_guides", "get_guide", "search_guides"):
            assert name in tools, f"Missing meta tool: {name}"

    def test_writing_tools_present(self):
        tools = mcp._tool_manager._tools
        for name in ("draft_email", "draft_blog_post", "parse_meeting_notes",
                      "format_social_content", "scaffold_tech_doc", "structure_story"):
            assert name in tools, f"Missing writing tool: {name}"

    def test_analysis_tools_present(self):
        tools = mcp._tool_manager._tools
        for name in ("analyze_data", "summarize_document", "build_comparison_matrix",
                      "analyze_survey", "analyze_financials", "review_legal_document"):
            assert name in tools, f"Missing analysis tool: {name}"

    def test_coding_tools_present(self):
        tools = mcp._tool_manager._tools
        for name in ("scaffold_code", "analyze_code", "process_sql",
                      "scaffold_api_doc", "generate_test_cases", "create_adr"):
            assert name in tools, f"Missing coding tool: {name}"

    def test_business_tools_present(self):
        tools = mcp._tool_manager._tools
        for name in ("plan_project", "prepare_interview", "scaffold_proposal",
                      "build_support_response", "scaffold_prd", "evaluate_decision"):
            assert name in tools, f"Missing business tool: {name}"


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
        assert __version__ == "0.1.0"
