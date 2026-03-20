"""SQL processing tool — format, validate, explain, and extract using sqlparse."""

from __future__ import annotations

import re
from typing import Any

import sqlparse
from sqlparse.sql import (
    Identifier,
    IdentifierList,
    Where,
)
from sqlparse.tokens import Keyword, DML, DDL


# ── Dialect detection ────────────────────────────────────────────────────────

_DIALECT_HINTS: dict[str, list[str]] = {
    "postgresql": [
        "RETURNING",
        "ILIKE",
        "::int",
        "::text",
        "SERIAL",
        "BIGSERIAL",
        "JSONB",
        "ARRAY[",
    ],
    "mysql": ["LIMIT", "AUTO_INCREMENT", "ENGINE=", "UNSIGNED", "ENUM(", "`"],
    "sqlite": ["AUTOINCREMENT", "GLOB", "PRAGMA", "INTEGER PRIMARY KEY"],
    "mssql": ["TOP ", "NVARCHAR", "GETDATE()", "IDENTITY(", "NOLOCK"],
    "oracle": ["ROWNUM", "NVL(", "SYSDATE", "DUAL", "CONNECT BY"],
}


def _detect_dialect(query: str) -> str:
    """Best-effort SQL dialect detection."""
    upper = query.upper()
    scores: dict[str, int] = {}
    for dialect, hints in _DIALECT_HINTS.items():
        score = sum(1 for h in hints if h.upper() in upper)
        if score:
            scores[dialect] = score
    if not scores:
        return "ansi"
    return max(scores, key=scores.get)  # type: ignore[arg-type]


# ── Table / column extraction ────────────────────────────────────────────────


def _extract_tables(parsed: list[sqlparse.sql.Statement]) -> list[str]:
    """Extract table names from parsed statements."""
    tables: list[str] = []
    table_keywords = {
        "FROM",
        "JOIN",
        "INNER JOIN",
        "LEFT JOIN",
        "RIGHT JOIN",
        "FULL JOIN",
        "CROSS JOIN",
        "LEFT OUTER JOIN",
        "RIGHT OUTER JOIN",
        "FULL OUTER JOIN",
        "INTO",
        "UPDATE",
        "TABLE",
    }

    for stmt in parsed:
        tokens = list(stmt.flatten())
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            # Check for DML/Keyword tokens that precede table names
            if tok.ttype in (Keyword, DML, DDL):
                word = tok.value.upper().strip()
                # Handle multi-word keywords like "LEFT JOIN", "INNER JOIN"
                combined = word
                if i + 1 < len(tokens) and tokens[i + 1].ttype in (Keyword,):
                    combined = word + " " + tokens[i + 1].value.upper().strip()

                if combined in table_keywords or word in table_keywords:
                    # Advance past whitespace to find the table name
                    j = i + 1
                    if combined in table_keywords and combined != word:
                        j = i + 2
                    while j < len(tokens) and tokens[j].ttype in (
                        sqlparse.tokens.Whitespace,
                        sqlparse.tokens.Newline,
                    ):
                        j += 1
                    if j < len(tokens) and tokens[j].ttype in (
                        sqlparse.tokens.Name,
                        None,
                    ):
                        name = tokens[j].value.strip('`"[] ')
                        if (
                            name
                            and name.upper() not in table_keywords
                            and not name.startswith("(")
                        ):
                            tables.append(name)
                    i = j
                    continue
            i += 1

    # Deduplicate preserving order
    seen: set[str] = set()
    result: list[str] = []
    for t in tables:
        low = t.lower()
        if low not in seen:
            seen.add(low)
            result.append(t)
    return result


def _extract_columns(parsed: list[sqlparse.sql.Statement]) -> list[str]:
    """Extract column references from parsed statements."""
    columns: list[str] = []

    for stmt in parsed:
        # Walk the token tree
        _walk_for_columns(stmt, columns)

    # Deduplicate preserving order
    seen: set[str] = set()
    result: list[str] = []
    for c in columns:
        low = c.lower()
        if low not in seen and low != "*":
            seen.add(low)
            result.append(c)
    return result


def _walk_for_columns(token_list: Any, columns: list[str]) -> None:
    """Recursively walk tokens to find column identifiers."""
    in_select = False

    for token in token_list.tokens:
        if token.ttype is DML and token.value.upper() == "SELECT":
            in_select = True
            continue
        if token.ttype is Keyword and token.value.upper() in (
            "FROM",
            "INTO",
            "SET",
            "VALUES",
        ):
            in_select = False
            continue

        if isinstance(token, Where):
            # Extract columns from WHERE clause
            for sub in token.tokens:
                if isinstance(sub, Identifier):
                    name = sub.get_real_name()
                    if name:
                        columns.append(name)
                elif isinstance(sub, IdentifierList):
                    for ident in sub.get_identifiers():
                        if isinstance(ident, Identifier):
                            name = ident.get_real_name()
                            if name:
                                columns.append(name)
            continue

        if in_select:
            if isinstance(token, IdentifierList):
                for ident in token.get_identifiers():
                    if isinstance(ident, Identifier):
                        name = ident.get_real_name()
                        if name and name != "*":
                            columns.append(name)
                    elif hasattr(ident, "value"):
                        val = ident.value.strip()
                        if val and val != "*" and val != ",":
                            columns.append(val)
            elif isinstance(token, Identifier):
                name = token.get_real_name()
                if name and name != "*":
                    columns.append(name)


# ── Query type detection ─────────────────────────────────────────────────────


def _query_type(parsed: list[sqlparse.sql.Statement]) -> str:
    """Determine the primary query type."""
    for stmt in parsed:
        first_token = stmt.token_first(skip_ws=True, skip_cm=True)
        if first_token:
            val = first_token.value.upper()
            if val in (
                "SELECT",
                "INSERT",
                "UPDATE",
                "DELETE",
                "CREATE",
                "ALTER",
                "DROP",
                "TRUNCATE",
                "MERGE",
                "WITH",
                "EXPLAIN",
                "GRANT",
                "REVOKE",
            ):
                return val
    return "UNKNOWN"


# ── Operations ───────────────────────────────────────────────────────────────


def _format_sql(query: str) -> str:
    """Pretty-print SQL using sqlparse."""
    return sqlparse.format(
        query,
        reindent=True,
        keyword_case="upper",
        strip_comments=False,
        indent_width=2,
    ).strip()


def _validate_sql(query: str) -> list[str]:
    """Check for common SQL syntax issues."""
    warnings: list[str] = []
    stripped = query.strip()

    # Unmatched parentheses
    open_parens = stripped.count("(")
    close_parens = stripped.count(")")
    if open_parens != close_parens:
        diff = open_parens - close_parens
        if diff > 0:
            warnings.append(f"{diff} unmatched opening parenthesis(es)")
        else:
            warnings.append(f"{-diff} unmatched closing parenthesis(es)")

    # Unmatched quotes
    single_quotes = stripped.count("'") - stripped.count("\\'")
    if single_quotes % 2 != 0:
        warnings.append("Unmatched single quote")

    # Missing semicolon at end — only warn for multi-statement queries
    if stripped and not stripped.endswith(";"):
        # Count non-empty statements
        stmts = [s for s in sqlparse.parse(stripped) if str(s).strip()]
        if len(stmts) > 1:
            warnings.append("Missing semicolon at end of statement")

    # SELECT without FROM (not SELECT 1, SELECT CURRENT_DATE, etc.)
    upper = stripped.upper()
    if "SELECT" in upper and "FROM" not in upper:
        # Check if it's a simple expression (SELECT 1, SELECT NOW(), etc.)
        select_match = re.search(r"SELECT\s+(.+)", upper)
        if select_match:
            expr = select_match.group(1).strip().rstrip(";")
            # Only warn if it looks like column references
            if re.search(r"[a-zA-Z_]\w*\s*,", expr) or "." in expr:
                warnings.append("SELECT without FROM clause")

    # DELETE without WHERE
    if "DELETE" in upper and "WHERE" not in upper:
        warnings.append("DELETE without WHERE clause — this will delete all rows")

    # UPDATE without WHERE
    if "UPDATE" in upper and "SET" in upper and "WHERE" not in upper:
        warnings.append("UPDATE without WHERE clause — this will update all rows")

    # SELECT *
    if re.search(r"SELECT\s+\*", upper):
        warnings.append("SELECT * used — consider specifying columns explicitly")

    return warnings


def _performance_hints(query: str, parsed: list[sqlparse.sql.Statement]) -> list[str]:
    """Detect common SQL performance anti-patterns."""
    hints: list[str] = []
    upper = query.upper()

    # SELECT * — consider selecting only needed columns
    if re.search(r"SELECT\s+\*", upper):
        hints.append(
            "SELECT * — Consider selecting only needed columns for better performance"
        )

    # JOIN without ON or with always-true condition (cartesian join)
    # Look for JOIN ... JOIN or JOIN ... WHERE without an ON in between
    join_positions = [m.start() for m in re.finditer(r"\bJOIN\b", upper)]
    on_positions = [m.start() for m in re.finditer(r"\bON\b", upper)]
    for jpos in join_positions:
        # Check for CROSS JOIN — those are intentionally without ON
        pre = upper[:jpos].rstrip()
        if pre.endswith("CROSS"):
            continue
        # Find the next relevant keyword after JOIN (another JOIN, WHERE, GROUP, ORDER, LIMIT, HAVING, or end)
        next_kw = re.search(
            r"\b(?:JOIN|WHERE|GROUP|ORDER|LIMIT|HAVING|UNION)\b", upper[jpos + 4 :]
        )
        boundary = jpos + 4 + next_kw.start() if next_kw else len(upper)
        # Check if there's an ON between this JOIN and the next boundary
        has_on = any(jpos < op < boundary for op in on_positions)
        if not has_on:
            hints.append("Potential cartesian join — JOIN without ON condition")
            break  # one warning is enough

    # Subquery in WHERE → may cause N+1 performance
    where_match = re.search(r"\bWHERE\b", upper)
    if where_match:
        where_clause = upper[where_match.start() :]
        if re.search(r"\(\s*SELECT\b", where_clause):
            hints.append(
                "Subquery in WHERE may cause N+1 performance; consider using a JOIN"
            )

    # LIKE with leading wildcard
    if re.search(r"LIKE\s+'%", upper):
        hints.append("Leading wildcard in LIKE prevents index usage")

    # ORDER BY without LIMIT
    if re.search(r"\bORDER\s+BY\b", upper) and not re.search(r"\bLIMIT\b", upper):
        hints.append(
            "ORDER BY without LIMIT — consider adding LIMIT for large result sets"
        )

    # HAVING without aggregation function
    having_match = re.search(
        r"\bHAVING\s+(.+?)(?:\bORDER\b|\bLIMIT\b|\bUNION\b|;|$)", upper, re.DOTALL
    )
    if having_match:
        having_clause = having_match.group(1)
        agg_funcs = r"\b(?:COUNT|SUM|AVG|MIN|MAX|GROUP_CONCAT|STRING_AGG)\s*\("
        if not re.search(agg_funcs, having_clause):
            hints.append(
                "HAVING without aggregation function — may indicate a logic error; "
                "use WHERE for non-aggregate filters"
            )

    return hints


def _explain_sql(query: str, parsed: list[sqlparse.sql.Statement]) -> str:
    """Generate a step-by-step explanation of the query."""
    parts: list[str] = []
    qtype = _query_type(parsed)

    tables = _extract_tables(parsed)
    columns = _extract_columns(parsed)

    upper = query.upper()

    parts.append(f"Query type: {qtype}")

    if tables:
        parts.append(f"Data source: table(s) {', '.join(tables)}")

    # Explain logical execution order for SELECT
    if qtype == "SELECT":
        # FROM
        if tables:
            parts.append(f"1. FROM: Read from {', '.join(tables)}")
        # JOIN
        join_match = re.findall(
            r"(?:LEFT|RIGHT|INNER|FULL|CROSS)?\s*JOIN\s+(\w+)", upper
        )
        if join_match:
            parts.append(
                f"2. JOIN: Join with {', '.join(j.lower() for j in join_match)}"
            )
        # WHERE
        where_match = re.search(
            r"WHERE\s+(.+?)(?:GROUP|ORDER|HAVING|LIMIT|UNION|$)", upper, re.DOTALL
        )
        if where_match:
            parts.append(
                f"3. WHERE: Filter rows where {where_match.group(1).strip()[:80]}"
            )
        # GROUP BY
        group_match = re.search(
            r"GROUP\s+BY\s+(.+?)(?:HAVING|ORDER|LIMIT|$)", upper, re.DOTALL
        )
        if group_match:
            parts.append(f"4. GROUP BY: Group by {group_match.group(1).strip()[:60]}")
        # HAVING
        having_match = re.search(r"HAVING\s+(.+?)(?:ORDER|LIMIT|$)", upper, re.DOTALL)
        if having_match:
            parts.append(
                f"5. HAVING: Filter groups where {having_match.group(1).strip()[:60]}"
            )
        # SELECT
        if columns:
            parts.append(f"6. SELECT: Return columns {', '.join(columns[:10])}")
        else:
            parts.append("6. SELECT: Return all columns (*)")
        # ORDER BY
        order_match = re.search(
            r"ORDER\s+BY\s+(.+?)(?:LIMIT|OFFSET|$)", upper, re.DOTALL
        )
        if order_match:
            parts.append(f"7. ORDER BY: Sort by {order_match.group(1).strip()[:60]}")
        # LIMIT
        limit_match = re.search(r"LIMIT\s+(\d+)", upper)
        if limit_match:
            parts.append(f"8. LIMIT: Return at most {limit_match.group(1)} rows")
    elif qtype == "INSERT":
        parts.append(f"Inserts data into {tables[0] if tables else '?'}")
        if columns:
            parts.append(f"Target columns: {', '.join(columns)}")
    elif qtype == "UPDATE":
        parts.append(f"Updates rows in {tables[0] if tables else '?'}")
        set_match = re.search(r"SET\s+(.+?)(?:WHERE|$)", upper, re.DOTALL)
        if set_match:
            parts.append(f"Sets: {set_match.group(1).strip()[:80]}")
    elif qtype == "DELETE":
        parts.append(f"Deletes rows from {tables[0] if tables else '?'}")

    return "\n".join(parts)


# ── Public API ───────────────────────────────────────────────────────────────


def process_sql(
    query: str,
    operation: str = "format",
    dialect: str = "auto",
) -> dict:
    """Process a SQL query — format, validate, explain, or extract.

    Args:
        query: SQL query string.
        operation: One of "format", "validate", "explain", "extract".
        dialect: SQL dialect (auto-detected if "auto").

    Returns:
        Dictionary with processed result, extracted tables/columns, etc.
    """
    if dialect == "auto" or not dialect:
        dialect = _detect_dialect(query)

    parsed = sqlparse.parse(query)
    stmt_count = len([s for s in parsed if s.tokens and str(s).strip()])
    qtype = _query_type(parsed)
    tables = _extract_tables(parsed)
    columns = _extract_columns(parsed)
    warnings: list[str] = []

    op = operation.lower()

    if op == "format":
        result = _format_sql(query)
    elif op == "validate":
        warnings = _validate_sql(query)
        result = "Valid" if not warnings else f"Found {len(warnings)} issue(s)"
    elif op == "explain":
        result = _explain_sql(query, parsed)
    elif op == "extract":
        result = f"Tables: {', '.join(tables) or 'none'}; Columns: {', '.join(columns) or 'none'}"
    else:
        result = _format_sql(query)
        warnings.append(f"Unknown operation '{operation}', defaulting to format")

    # Always run validation for non-validate operations to populate warnings
    if op != "validate":
        warnings.extend(_validate_sql(query))

    output: dict[str, Any] = {
        "operation": op,
        "dialect": dialect,
        "result": result,
        "tables": tables,
        "columns": columns,
        "query_type": qtype,
        "statement_count": stmt_count,
        "warnings": warnings,
    }

    # Add performance hints for explain operations
    if op == "explain":
        output["performance_hints"] = _performance_hints(query, parsed)

    return output
