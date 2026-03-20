"""Static code analysis — metrics, complexity, and issue detection."""

from __future__ import annotations

import re
from typing import Any


# ── Language detection ───────────────────────────────────────────────────────

_LANG_SIGNALS: list[tuple[str, list[str]]] = [
    ("python", [r'\bdef\s+\w+\s*\(', r'\bimport\s+\w+', r'\bclass\s+\w+.*:', r'\bself\b', r':\s*$']),
    ("rust", [r'\bfn\s+\w+', r'\blet\s+mut\b', r'\bimpl\b', r'\bpub\s+fn\b', r'->.*\{']),
    ("go", [r'\bfunc\s+\w+', r'\bpackage\s+\w+', r'\bgo\s+\w+', r':=', r'\bdefer\b']),
    ("java", [r'\bpublic\s+class\b', r'\bprivate\s+\w+', r'\bSystem\.out\b', r'\bvoid\s+\w+', r'@Override']),
    ("typescript", [r'\binterface\s+\w+', r':\s*\w+\s*[=;,\)]', r'\bconst\s+\w+:\s*\w+', r'\btype\s+\w+\s*=']),
    ("javascript", [r'\bfunction\s+\w+', r'\bconst\s+\w+\s*=', r'\blet\s+\w+\s*=', r'=>', r'\brequire\(']),
    ("c", [r'#include\s*<', r'\bint\s+main\s*\(', r'\bprintf\s*\(', r'\bmalloc\s*\(', r'\bvoid\s*\*']),
    ("cpp", [r'#include\s*<', r'\bstd::', r'\bcout\b', r'\btemplate\s*<', r'\bnamespace\b']),
]


def _detect_language(code: str) -> str:
    """Detect programming language from code content."""
    scores: dict[str, int] = {}
    for lang, patterns in _LANG_SIGNALS:
        score = sum(1 for p in patterns if re.search(p, code, re.MULTILINE))
        if score:
            scores[lang] = score
    if not scores:
        return "unknown"
    return max(scores, key=scores.get)  # type: ignore[arg-type]


# ── Comment detection ────────────────────────────────────────────────────────

def _count_comments(lines: list[str], language: str) -> int:
    """Count comment lines (single-line and multi-line block comments)."""
    count = 0
    in_block = False
    block_end = "*/"

    for line in lines:
        stripped = line.strip()

        if in_block:
            count += 1
            if block_end in stripped:
                in_block = False
            continue

        # Python docstrings / multi-line strings
        if language == "python":
            if stripped.startswith('"""') or stripped.startswith("'''"):
                delimiter = stripped[:3]
                # Check if it closes on the same line
                rest = stripped[3:]
                if delimiter in rest:
                    count += 1
                    continue
                in_block = True
                block_end = delimiter
                count += 1
                continue

        # C-style block comments: /* ... */
        if stripped.startswith("/*"):
            count += 1
            if "*/" not in stripped[2:]:
                in_block = True
                block_end = "*/"
            continue

        # Single-line comments
        if language == "python" and stripped.startswith("#"):
            count += 1
        elif language in ("javascript", "typescript", "java", "go", "rust", "c", "cpp") and stripped.startswith("//"):
            count += 1
        elif language == "rust" and stripped.startswith("///"):
            count += 1

    return count


# ── Complexity analysis ──────────────────────────────────────────────────────

_BRANCH_KEYWORDS = re.compile(
    r'\b(if|elif|else|for|while|and|or|except|catch|case|switch|&&|\|\|)\b'
)

_FUNC_PATTERNS: dict[str, re.Pattern[str]] = {
    "python": re.compile(r'^\s*def\s+\w+', re.MULTILINE),
    "javascript": re.compile(r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>)', re.MULTILINE),
    "typescript": re.compile(r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*(?::\s*[^=]+)?\s*=\s*(?:async\s+)?(?:\([^)]*\)|[a-zA-Z_]\w*)\s*=>)', re.MULTILINE),
    "go": re.compile(r'^\s*func\s+', re.MULTILINE),
    "rust": re.compile(r'^\s*(?:pub\s+)?fn\s+\w+', re.MULTILINE),
    "java": re.compile(r'^\s*(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\(', re.MULTILINE),
}

_CLASS_PATTERNS: dict[str, re.Pattern[str]] = {
    "python": re.compile(r'^\s*class\s+\w+', re.MULTILINE),
    "javascript": re.compile(r'^\s*(?:export\s+)?class\s+\w+', re.MULTILINE),
    "typescript": re.compile(r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+\w+', re.MULTILINE),
    "java": re.compile(r'^\s*(?:public|private|abstract)?\s*class\s+\w+', re.MULTILINE),
    "rust": re.compile(r'^\s*(?:pub\s+)?struct\s+\w+', re.MULTILINE),
    "go": re.compile(r'^\s*type\s+\w+\s+struct\b', re.MULTILINE),
}


def _nesting_depth(lines: list[str], language: str) -> int:
    """Calculate maximum nesting depth."""
    max_depth = 0

    if language == "python":
        # Use indentation to determine depth
        for line in lines:
            stripped = line.rstrip()
            if not stripped or stripped.lstrip().startswith("#"):
                continue
            indent = len(stripped) - len(stripped.lstrip())
            # Assume 4-space indentation
            depth = indent // 4
            max_depth = max(max_depth, depth)
    else:
        # Use brace counting
        depth = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            for ch in stripped:
                if ch == '{':
                    depth += 1
                    max_depth = max(max_depth, depth)
                elif ch == '}':
                    depth = max(0, depth - 1)

    return max_depth


def _complexity_grade(cyclomatic: int) -> str:
    """Grade based on cyclomatic complexity estimate."""
    if cyclomatic < 10:
        return "A"
    if cyclomatic <= 20:
        return "B"
    if cyclomatic <= 30:
        return "C"
    if cyclomatic <= 50:
        return "D"
    return "F"


# ── Issue detection ──────────────────────────────────────────────────────────

def _detect_issues(lines: list[str], code: str, language: str) -> list[dict[str, Any]]:
    """Detect common code issues."""
    issues: list[dict[str, Any]] = []

    # Magic numbers — numeric literals > 2 used in expressions (not assignments of constants)
    magic_re = re.compile(r'(?<!["\'])\b(\d+\.?\d*)\b(?!["\'])')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip comments, blank, pure assignments, constant definitions
        if not stripped or stripped.startswith(('#', '//', '/*', '*', '"""', "'''")):
            continue
        # Look for numbers in conditional / arithmetic contexts
        if any(kw in stripped for kw in ('if ', 'elif ', 'while ', 'for ', 'return ', '==', '!=', '>', '<', '+', '-', '*', '/')):
            for m in magic_re.finditer(stripped):
                try:
                    val = float(m.group(1))
                except ValueError:
                    continue
                if val not in (0, 1, 2, -1, 0.0, 1.0):
                    issues.append({
                        "type": "magic_number",
                        "description": f"Magic number {m.group(1)} — consider using a named constant",
                        "line": i,
                        "severity": "info",
                    })
                    break  # One per line is enough

    # Long functions (>50 lines between def/func/fn)
    func_starts: list[int] = []
    func_pat = _FUNC_PATTERNS.get(language)
    if func_pat:
        for i, line in enumerate(lines, 1):
            if func_pat.match(line):
                func_starts.append(i)
    for idx in range(len(func_starts)):
        start = func_starts[idx]
        end = func_starts[idx + 1] - 1 if idx + 1 < len(func_starts) else len(lines)
        length = end - start + 1
        if length > 50:
            issues.append({
                "type": "long_function",
                "description": f"Function starting here is {length} lines (>50). Consider breaking it up.",
                "line": start,
                "severity": "warning",
            })

    # Deep nesting (>4)
    if language == "python":
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            if not stripped or stripped.lstrip().startswith('#'):
                continue
            indent = len(stripped) - len(stripped.lstrip())
            depth = indent // 4
            if depth > 4:
                issues.append({
                    "type": "deep_nesting",
                    "description": f"Nesting depth of {depth} (>4). Consider extracting to a function.",
                    "line": i,
                    "severity": "warning",
                })
                break  # Report once
    else:
        depth = 0
        for i, line in enumerate(lines, 1):
            for ch in line:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth = max(0, depth - 1)
            if depth > 4:
                issues.append({
                    "type": "deep_nesting",
                    "description": f"Nesting depth of {depth} (>4). Consider extracting to a function.",
                    "line": i,
                    "severity": "warning",
                })
                break

    # TODO / FIXME / HACK comments
    todo_re = re.compile(r'\b(TODO|FIXME|HACK|XXX)\b', re.IGNORECASE)
    for i, line in enumerate(lines, 1):
        m = todo_re.search(line)
        if m:
            tag = m.group(1).upper()
            issues.append({
                "type": "todo_comment",
                "description": f"{tag} comment found",
                "line": i,
                "severity": "info",
            })

    # Unused imports (simple heuristic: import name not referenced elsewhere)
    if language == "python":
        import_re = re.compile(r'^\s*(?:from\s+\S+\s+)?import\s+(.+)', re.MULTILINE)
        for i, line in enumerate(lines, 1):
            m = import_re.match(line)
            if m:
                imported_names = m.group(1)
                # Handle "import X as Y", "from X import a, b"
                for part in imported_names.split(','):
                    part = part.strip()
                    if ' as ' in part:
                        name = part.split(' as ')[-1].strip()
                    else:
                        name = part.split('.')[-1].strip()
                    if name.startswith('(') or not name or name == '*':
                        continue
                    # Check if name appears anywhere else in the code (not on import lines)
                    rest_lines = lines[:i - 1] + lines[i:]
                    rest = '\n'.join(rest_lines)
                    if not re.search(r'\b' + re.escape(name) + r'\b', rest):
                        issues.append({
                            "type": "unused_import",
                            "description": f"Import '{name}' appears unused",
                            "line": i,
                            "severity": "warning",
                        })

    return issues


# ── Public API ───────────────────────────────────────────────────────────────

def analyze_code(code: str, language: str = "auto") -> dict:
    """Perform static analysis on a code snippet.

    Args:
        code: Source code to analyze.
        language: Programming language (or "auto" to detect).

    Returns:
        Dictionary with metrics, complexity, issues, and summary.
    """
    if language == "auto" or not language:
        language = _detect_language(code)

    lines = code.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = _count_comments(lines, language)
    code_lines = total_lines - blank_lines - comment_lines

    comment_ratio = round(comment_lines / max(code_lines, 1), 3)

    # Complexity
    func_pat = _FUNC_PATTERNS.get(language)
    func_count = len(func_pat.findall(code)) if func_pat else 0

    class_pat = _CLASS_PATTERNS.get(language)
    class_count = len(class_pat.findall(code)) if class_pat else 0

    max_nesting = _nesting_depth(lines, language)
    branch_count = len(_BRANCH_KEYWORDS.findall(code))
    # Cyclomatic estimate: branches + 1 per function (or 1 if no functions)
    cyclomatic = branch_count + max(func_count, 1)
    grade = _complexity_grade(cyclomatic)

    issues = _detect_issues(lines, code, language)

    # Summary
    issue_counts: dict[str, int] = {}
    for issue in issues:
        sev = issue["severity"]
        issue_counts[sev] = issue_counts.get(sev, 0) + 1

    parts = [f"{total_lines} lines of {language} code"]
    parts.append(f"complexity grade {grade} (cyclomatic estimate {cyclomatic})")
    if issues:
        issue_summary = ", ".join(f"{c} {s}" for s, c in sorted(issue_counts.items()))
        parts.append(f"{len(issues)} issues ({issue_summary})")
    else:
        parts.append("no issues detected")

    return {
        "language": language,
        "metrics": {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "comment_ratio": comment_ratio,
        },
        "complexity": {
            "functions": func_count,
            "classes": class_count,
            "max_nesting_depth": max_nesting,
            "cyclomatic_estimate": cyclomatic,
            "complexity_grade": grade,
        },
        "issues": issues,
        "summary": "; ".join(parts),
    }
