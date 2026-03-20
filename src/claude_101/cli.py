"""CLI interface for Claude 101 — run any tool from the command line."""

from __future__ import annotations

import argparse
import inspect
import json
import re
import sys
import textwrap
from dataclasses import dataclass
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

@dataclass
class ToolEntry:
    name: str          # CLI name (hyphen-case)
    func: Callable
    category: str
    description: str   # first line of docstring


def _build_registry() -> dict[str, ToolEntry]:
    """Build the tool registry by importing all 27 functions."""
    # Meta tools
    from ._guides import list_guides, get_guide, search_guides

    # Writing tools
    from .writing.email import draft_email
    from .writing.blog import draft_blog_post
    from .writing.meeting import parse_meeting_notes
    from .writing.social import format_social_content
    from .writing.techdoc import scaffold_tech_doc
    from .writing.creative import structure_story

    # Analysis tools
    from .analysis.data import analyze_data
    from .analysis.summarize import summarize_document
    from .analysis.competitive import build_comparison_matrix
    from .analysis.survey import analyze_survey
    from .analysis.financial import analyze_financials
    from .analysis.legal import review_legal_document

    # Coding tools
    from .coding.codegen import scaffold_code
    from .coding.review import analyze_code
    from .coding.sql import process_sql
    from .coding.apidoc import scaffold_api_doc
    from .coding.testgen import generate_test_cases
    from .coding.architecture import create_adr

    # Business tools
    from .business.planning import plan_project
    from .business.interview import prepare_interview
    from .business.proposal import scaffold_proposal
    from .business.support import build_support_response
    from .business.prd import scaffold_prd
    from .business.decision import evaluate_decision

    tools: list[tuple[str, Callable, str]] = [
        # (func_name, func, category)
        ("list_guides", list_guides, "meta"),
        ("get_guide", get_guide, "meta"),
        ("search_guides", search_guides, "meta"),

        ("draft_email", draft_email, "writing"),
        ("draft_blog_post", draft_blog_post, "writing"),
        ("parse_meeting_notes", parse_meeting_notes, "writing"),
        ("format_social_content", format_social_content, "writing"),
        ("scaffold_tech_doc", scaffold_tech_doc, "writing"),
        ("structure_story", structure_story, "writing"),

        ("analyze_data", analyze_data, "analysis"),
        ("summarize_document", summarize_document, "analysis"),
        ("build_comparison_matrix", build_comparison_matrix, "analysis"),
        ("analyze_survey", analyze_survey, "analysis"),
        ("analyze_financials", analyze_financials, "analysis"),
        ("review_legal_document", review_legal_document, "analysis"),

        ("scaffold_code", scaffold_code, "coding"),
        ("analyze_code", analyze_code, "coding"),
        ("process_sql", process_sql, "coding"),
        ("scaffold_api_doc", scaffold_api_doc, "coding"),
        ("generate_test_cases", generate_test_cases, "coding"),
        ("create_adr", create_adr, "coding"),

        ("plan_project", plan_project, "business"),
        ("prepare_interview", prepare_interview, "business"),
        ("scaffold_proposal", scaffold_proposal, "business"),
        ("build_support_response", build_support_response, "business"),
        ("scaffold_prd", scaffold_prd, "business"),
        ("evaluate_decision", evaluate_decision, "business"),
    ]

    registry: dict[str, ToolEntry] = {}
    for func_name, func, category in tools:
        cli_name = func_name.replace("_", "-")
        doc = inspect.getdoc(func) or ""
        first_line = doc.split("\n")[0] if doc else func_name
        entry = ToolEntry(name=cli_name, func=func, category=category, description=first_line)
        registry[cli_name] = entry
        # Also register underscore variant for convenience
        registry[func_name] = entry

    return registry


# ---------------------------------------------------------------------------
# Docstring parsing
# ---------------------------------------------------------------------------

def _parse_docstring_args(docstring: str | None) -> dict[str, str]:
    """Extract parameter descriptions from Google-style docstring Args section."""
    if not docstring:
        return {}

    result: dict[str, str] = {}
    in_args = False
    current_param = ""
    current_desc = ""

    for line in docstring.splitlines():
        stripped = line.strip()

        if stripped == "Args:":
            in_args = True
            continue

        if in_args:
            # End of Args section
            if stripped and not stripped[0].isspace() and ":" not in stripped:
                if stripped.startswith("Returns") or stripped.startswith("Raises"):
                    break

            # New parameter line: "param_name: description"
            m = re.match(r'^(\w+)\s*[:]\s*(.+)', stripped)
            if m:
                if current_param:
                    result[current_param] = current_desc.strip()
                current_param = m.group(1)
                current_desc = m.group(2)
            elif current_param and stripped:
                # Continuation line
                current_desc += " " + stripped
            elif not stripped and current_param:
                # Blank line ends the param
                result[current_param] = current_desc.strip()
                current_param = ""
                current_desc = ""

    if current_param:
        result[current_param] = current_desc.strip()

    return result


# ---------------------------------------------------------------------------
# Argparse subparser generation
# ---------------------------------------------------------------------------

_TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


def _add_tool_subparser(
    subparsers: Any,
    entry: ToolEntry,
) -> None:
    """Create an argparse subparser for a tool from its function signature."""
    sig = inspect.signature(entry.func)
    doc = inspect.getdoc(entry.func) or ""
    param_help = _parse_docstring_args(doc)

    # Build epilog from full docstring (skip first line)
    doc_lines = doc.split("\n")
    epilog = "\n".join(doc_lines[1:]).strip() if len(doc_lines) > 1 else ""

    parser = subparsers.add_parser(
        entry.name,
        help=entry.description,
        description=entry.description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    for param_name, param in sig.parameters.items():
        annotation = param.annotation
        has_default = param.default is not inspect.Parameter.empty
        default = param.default if has_default else None
        help_text = param_help.get(param_name, "")

        # Resolve annotation to a Python type
        py_type = str  # default
        if annotation is not inspect.Parameter.empty:
            if annotation in (int, float, str, bool):
                py_type = annotation
            elif isinstance(annotation, str):
                py_type = _TYPE_MAP.get(annotation, str)

        cli_flag = f"--{param_name.replace('_', '-')}"

        if py_type is bool:
            # Use BooleanOptionalAction for --flag / --no-flag
            parser.add_argument(
                cli_flag,
                default=default,
                action=argparse.BooleanOptionalAction,
                help=help_text or None,
            )
        elif has_default:
            # Optional argument
            suffix = f" (default: {default!r})" if default != "" else ""
            parser.add_argument(
                cli_flag,
                type=py_type,
                default=default,
                metavar=param_name.upper(),
                help=(help_text + suffix) if help_text else suffix.strip() or None,
            )
        else:
            # Positional (required) argument
            parser.add_argument(
                param_name,
                type=py_type,
                metavar=param_name.upper(),
                help=help_text or None,
            )


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _run_tool(entry: ToolEntry, args: argparse.Namespace, pretty: bool) -> int:
    """Execute a tool function and print JSON output."""
    sig = inspect.signature(entry.func)
    kwargs: dict[str, Any] = {}

    for param_name in sig.parameters:
        # argparse stores hyphenated names with underscores
        attr_name = param_name.replace("-", "_")
        if hasattr(args, attr_name):
            value = getattr(args, attr_name)
            # Support stdin reading: if string value is "-", read from stdin
            if isinstance(value, str) and value == "-":
                value = sys.stdin.read()
            kwargs[param_name] = value

    try:
        result = entry.func(**kwargs)
    except Exception as exc:
        err = {"error": str(exc), "tool": entry.name}
        print(json.dumps(err, indent=2 if pretty else None, ensure_ascii=False), file=sys.stderr)
        return 1

    indent = 2 if pretty else None
    print(json.dumps(result, indent=indent, ensure_ascii=False))
    return 0


def _run_list(registry: dict[str, ToolEntry], category: str, pretty: bool) -> int:
    """List all available tools."""
    # Deduplicate (each tool is registered twice: hyphen + underscore)
    seen: set[str] = set()
    entries: list[ToolEntry] = []
    for entry in registry.values():
        if entry.name not in seen:
            seen.add(entry.name)
            if not category or entry.category == category:
                entries.append(entry)

    entries.sort(key=lambda e: (e.category, e.name))

    if pretty:
        data = [
            {"name": e.name, "category": e.category, "description": e.description}
            for e in entries
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        # Human-friendly table
        if not entries:
            print("No tools found.")
            return 0

        max_name = max(len(e.name) for e in entries)
        max_cat = max(len(e.category) for e in entries)

        header = f"{'TOOL':<{max_name}}  {'CATEGORY':<{max_cat}}  DESCRIPTION"
        print(header)
        print("-" * len(header))
        for e in entries:
            print(f"{e.name:<{max_name}}  {e.category:<{max_cat}}  {e.description}")
        print(f"\n{len(entries)} tools available. Use 'claude-101 <tool> --help' for details.")

    return 0


def _run_serve() -> int:
    """Start the MCP server."""
    try:
        from .server import main as server_main
    except ImportError:
        print(
            "Error: MCP dependency not installed.\n"
            "Install it with: pip install 'claude-101[mcp]'",
            file=sys.stderr,
        )
        return 1

    server_main()
    return 0


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    registry = _build_registry()

    parser = argparse.ArgumentParser(
        prog="claude-101",
        description="Claude 101 — 27 practical AI tools for writing, analysis, coding, and business.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            modes:
              claude-101 serve                Start the MCP server
              claude-101 list                 List all available tools
              claude-101 <tool> [args]        Run a tool and get JSON output

            examples:
              claude-101 draft-email "follow-up to client meeting about Q3"
              claude-101 analyze-code --language python < myfile.py
              claude-101 scaffold-prd "TaskFlow" "Teams need better task tracking"
              echo "SELECT * FROM users" | claude-101 process-sql -
        """),
    )
    parser.add_argument("--version", action="version", version=f"claude-101 {_get_version()}")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output (indent=2)")

    subparsers = parser.add_subparsers(dest="command")

    # serve command
    subparsers.add_parser("serve", help="Start the MCP server (requires mcp extra)")

    # list command
    list_parser = subparsers.add_parser("list", help="List all available tools")
    list_parser.add_argument(
        "--category", "-c",
        choices=["writing", "analysis", "coding", "business", "meta"],
        default="",
        help="Filter by category",
    )

    # Tool subparsers
    seen: set[str] = set()
    for entry in registry.values():
        if entry.name not in seen:
            seen.add(entry.name)
            _add_tool_subparser(subparsers, entry)

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    pretty = args.pretty

    if args.command == "serve":
        return _run_serve()

    if args.command == "list":
        return _run_list(registry, args.category, pretty)

    # Normalize command name for lookup
    key = args.command
    if key not in registry:
        key = key.replace("-", "_")
    if key not in registry:
        print(f"Unknown tool: {args.command}", file=sys.stderr)
        return 1

    return _run_tool(registry[key], args, pretty)


def _get_version() -> str:
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "0.0.0"


if __name__ == "__main__":
    sys.exit(main())
