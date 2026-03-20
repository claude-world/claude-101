"""Test case generator — produce real test scaffolds from function signatures."""

from __future__ import annotations

import re
from typing import Any


# ── Signature parsing ────────────────────────────────────────────────────────


def _parse_signature(sig: str) -> dict[str, Any]:
    """Parse a function signature to extract name, parameters, and types.

    Handles signatures like:
        def add(a: int, b: int) -> int
        function multiply(x, y)
        func Divide(a float64, b float64) (float64, error)
        fn process(data: &str, count: usize) -> Result<String, Error>
        public int calculate(int x, int y)
    """
    result: dict[str, Any] = {"name": "", "params": [], "return_type": ""}

    sig = sig.strip()

    # Python: def name(params) -> return
    m = re.match(r"def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(.+))?", sig)
    if m:
        result["name"] = m.group(1)
        result["return_type"] = m.group(3).strip() if m.group(3) else ""
        result["params"] = _parse_python_params(m.group(2))
        return result

    # JS/TS: function name(params) or (params) => or name(params): return
    m = re.match(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*(.+))?",
        sig,
    )
    if m:
        result["name"] = m.group(1)
        result["return_type"] = m.group(3).strip() if m.group(3) else ""
        result["params"] = _parse_ts_params(m.group(2))
        return result

    # Go: func Name(params) (returns)
    m = re.match(r"func\s+(\w+)\s*\(([^)]*)\)\s*(.*)", sig)
    if m:
        result["name"] = m.group(1)
        result["return_type"] = m.group(3).strip().strip("()") if m.group(3) else ""
        result["params"] = _parse_go_params(m.group(2))
        return result

    # Rust: fn name(params) -> return
    m = re.match(r"(?:pub\s+)?fn\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(.+))?", sig)
    if m:
        result["name"] = m.group(1)
        result["return_type"] = m.group(3).strip() if m.group(3) else ""
        result["params"] = _parse_rust_params(m.group(2))
        return result

    # Java: ReturnType name(params)
    m = re.match(
        r"(?:public\s+|private\s+|protected\s+|static\s+)*(\w+)\s+(\w+)\s*\(([^)]*)\)",
        sig,
    )
    if m:
        result["return_type"] = m.group(1)
        result["name"] = m.group(2)
        result["params"] = _parse_java_params(m.group(3))
        return result

    # Fallback: just a name
    m = re.match(r"(\w+)", sig)
    if m:
        result["name"] = m.group(1)

    return result


def _parse_python_params(raw: str) -> list[dict[str, str]]:
    params: list[dict[str, str]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part or part == "self" or part == "cls":
            continue
        # name: type = default
        m = re.match(r"(\*{0,2}\w+)\s*(?::\s*([^=]+))?\s*(?:=\s*(.+))?", part)
        if m:
            params.append(
                {
                    "name": m.group(1).lstrip("*"),
                    "type": m.group(2).strip() if m.group(2) else "Any",
                    "default": m.group(3).strip() if m.group(3) else "",
                }
            )
    return params


def _parse_ts_params(raw: str) -> list[dict[str, str]]:
    params: list[dict[str, str]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"(\w+)\??\s*(?::\s*([^=]+))?\s*(?:=\s*(.+))?", part)
        if m:
            params.append(
                {
                    "name": m.group(1),
                    "type": m.group(2).strip() if m.group(2) else "any",
                    "default": m.group(3).strip() if m.group(3) else "",
                }
            )
    return params


def _parse_go_params(raw: str) -> list[dict[str, str]]:
    params: list[dict[str, str]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        tokens = part.split()
        if len(tokens) >= 2:
            params.append({"name": tokens[0], "type": tokens[1], "default": ""})
        elif tokens:
            params.append({"name": tokens[0], "type": "", "default": ""})
    return params


def _parse_rust_params(raw: str) -> list[dict[str, str]]:
    params: list[dict[str, str]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part or part in ("&self", "&mut self", "self"):
            continue
        m = re.match(r"(\w+)\s*:\s*(.+)", part)
        if m:
            params.append(
                {"name": m.group(1), "type": m.group(2).strip(), "default": ""}
            )
    return params


def _parse_java_params(raw: str) -> list[dict[str, str]]:
    params: list[dict[str, str]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        tokens = part.split()
        if len(tokens) >= 2:
            params.append({"name": tokens[-1], "type": tokens[0], "default": ""})
    return params


# ── Test value generation ────────────────────────────────────────────────────


def _edge_values(param_type: str) -> list[tuple[str, str, str]]:
    """Return (category, test_name_suffix, value_repr) tuples for edge cases."""
    t = param_type.lower().strip()
    values: list[tuple[str, str, str]] = []

    if t in (
        "int",
        "integer",
        "i32",
        "i64",
        "int32",
        "int64",
        "number",
        "float",
        "f64",
        "float64",
        "double",
    ):
        values.extend(
            [
                ("edge_case", "zero", "0"),
                ("edge_case", "negative", "-1"),
                ("boundary", "large_positive", "2**31 - 1"),
                ("boundary", "large_negative", "-(2**31)"),
            ]
        )
    elif t in ("str", "string", "&str", "String"):
        values.extend(
            [
                ("edge_case", "empty_string", '""'),
                ("edge_case", "whitespace", '" "'),
                ("edge_case", "unicode", '"\\u00e9\\u00e8\\u00ea"'),
                ("boundary", "very_long_string", '"x" * 10000'),
                ("boundary", "single_char", '"a"'),
            ]
        )
    elif t.startswith(("list", "vec", "array", "[]", "List")):
        values.extend(
            [
                ("edge_case", "empty_list", "[]"),
                ("boundary", "single_element", "[1]"),
                ("boundary", "large_list", "list(range(10000))"),
            ]
        )
    elif t in ("bool", "boolean"):
        values.extend(
            [
                ("happy_path", "true_value", "True"),
                ("happy_path", "false_value", "False"),
            ]
        )
    elif t in ("none", "null", "nil", "optional", "Any"):
        values.extend(
            [
                ("edge_case", "none_value", "None"),
            ]
        )
    else:
        values.extend(
            [
                ("edge_case", "none_value", "None"),
            ]
        )

    return values


# ── Test framework templates ─────────────────────────────────────────────────

_FRAMEWORKS = {
    "python": "pytest",
    "javascript": "jest",
    "typescript": "jest",
    "go": "testing",
    "rust": "#[test]",
    "java": "JUnit5",
}


def _python_test(
    func_name: str, test_name: str, category: str, desc: str, args: str, expected: str
) -> str:
    return f'''def test_{func_name}_{test_name}():
    """{desc}"""
    result = {func_name}({args})
    assert result is not None  # {category}: {desc}
'''


def _jest_test(
    func_name: str, test_name: str, category: str, desc: str, args: str, expected: str
) -> str:
    camel = func_name[0].lower() + func_name[1:] if func_name else func_name
    return f'''test("{camel} - {desc}", () => {{
  const result = {camel}({args});
  expect(result).toBeDefined(); // {category}: {desc}
}});
'''


def _go_test(
    func_name: str, test_name: str, category: str, desc: str, args: str, expected: str
) -> str:
    pascal = func_name[0].upper() + func_name[1:] if func_name else func_name
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", test_name)
    return f'''func Test{pascal}_{safe_name.title()}(t *testing.T) {{
\t// {desc}
\tresult := {pascal}({args})
\tif result == nil {{
\t\tt.Errorf("{pascal}({args}) returned nil")
\t}}
}}
'''


def _rust_test(
    func_name: str, test_name: str, category: str, desc: str, args: str, expected: str
) -> str:
    return f"""#[test]
fn test_{func_name}_{test_name}() {{
    // {desc}
    let result = {func_name}({args});
    assert!(result.is_ok()); // {category}
}}
"""


def _java_test(
    func_name: str, test_name: str, category: str, desc: str, args: str, expected: str
) -> str:
    pascal = test_name[0].upper() + test_name[1:] if test_name else test_name
    pascal = re.sub(r"_(\w)", lambda m: m.group(1).upper(), pascal)
    return f"""@Test
void {func_name}{pascal}() {{
    // {desc}
    var result = {func_name}({args});
    assertNotNull(result); // {category}: {desc}
}}
"""


_TEST_GENERATORS = {
    "python": _python_test,
    "javascript": _jest_test,
    "typescript": _jest_test,
    "go": _go_test,
    "rust": _rust_test,
    "java": _java_test,
}


# ── Test case generation ─────────────────────────────────────────────────────


def _build_test_cases(
    func_name: str,
    params: list[dict[str, str]],
    language: str,
    strategy: str,
) -> list[dict[str, Any]]:
    """Generate test cases based on parameters and strategy."""
    cases: list[dict[str, Any]] = []
    gen = _TEST_GENERATORS.get(language, _python_test)

    categories_to_include: set[str] = set()
    if strategy == "happy":
        categories_to_include = {"happy_path"}
    elif strategy == "edge":
        categories_to_include = {"happy_path", "edge_case"}
    else:  # comprehensive
        categories_to_include = {"happy_path", "edge_case", "boundary", "error"}

    # ── Happy path ──────────────────────────────────────────────────
    if "happy_path" in categories_to_include:
        # Generate a basic happy path test with typical values
        happy_args: list[str] = []
        for p in params:
            t = p["type"].lower()
            if t in ("int", "integer", "i32", "i64", "number", "float", "f64"):
                happy_args.append("42")
            elif t in ("str", "string", "&str"):
                happy_args.append('"hello"')
            elif t.startswith(("list", "vec", "array", "[]")):
                happy_args.append("[1, 2, 3]")
            elif t in ("bool", "boolean"):
                happy_args.append("True" if language == "python" else "true")
            elif t.startswith(("dict", "map", "HashMap")):
                happy_args.append(
                    '{"key": "value"}'
                    if language in ("python",)
                    else '{ key: "value" }'
                )
            else:
                if p.get("default"):
                    happy_args.append(p["default"])
                else:
                    happy_args.append('"test"')

        args_str = ", ".join(happy_args)
        code = gen(
            func_name,
            "basic_usage",
            "happy_path",
            "Should handle typical input correctly",
            args_str,
            "expected",
        )
        cases.append(
            {
                "name": f"test_{func_name}_basic_usage",
                "category": "happy_path",
                "description": "Should handle typical input correctly",
                "code": code,
            }
        )

        # If there are multiple params, add a test with different valid values
        if len(params) > 1:
            alt_args: list[str] = []
            for p in params:
                t = p["type"].lower()
                if t in ("int", "integer", "i32", "i64", "number", "float", "f64"):
                    alt_args.append("100")
                elif t in ("str", "string", "&str"):
                    alt_args.append('"world"')
                elif t.startswith(("list", "vec", "array", "[]")):
                    alt_args.append("[10, 20, 30, 40, 50]")
                else:
                    alt_args.append('"test2"')
            alt_args_str = ", ".join(alt_args)
            code = gen(
                func_name,
                "alternate_values",
                "happy_path",
                "Should handle alternative valid input",
                alt_args_str,
                "expected",
            )
            cases.append(
                {
                    "name": f"test_{func_name}_alternate_values",
                    "category": "happy_path",
                    "description": "Should handle alternative valid input",
                    "code": code,
                }
            )

    # ── Edge cases and boundary ──────────────────────────────────────
    if "edge_case" in categories_to_include or "boundary" in categories_to_include:
        for param in params:
            edge_vals = _edge_values(param["type"])
            for category, suffix, value in edge_vals:
                if category not in categories_to_include:
                    continue
                test_name = f"{param['name']}_{suffix}"
                desc = f"Should handle {param['name']}={value} ({category.replace('_', ' ')})"

                # Build args with this specific edge value for the target param, typical for others
                test_args: list[str] = []
                for p in params:
                    if p["name"] == param["name"]:
                        test_args.append(value)
                    else:
                        t = p["type"].lower()
                        if t in (
                            "int",
                            "integer",
                            "i32",
                            "i64",
                            "number",
                            "float",
                            "f64",
                        ):
                            test_args.append("1")
                        elif t in ("str", "string", "&str"):
                            test_args.append('"test"')
                        else:
                            test_args.append('"test"')

                args_str = ", ".join(test_args)
                code = gen(func_name, test_name, category, desc, args_str, "expected")
                cases.append(
                    {
                        "name": f"test_{func_name}_{test_name}",
                        "category": category,
                        "description": desc,
                        "code": code,
                    }
                )

    # ── Error cases ─────────────────────────────────────────────────
    if "error" in categories_to_include:
        # Test with None/null for each parameter
        for param in params:
            test_name = f"{param['name']}_invalid_type"
            null_val = "None" if language in ("python",) else "null"
            desc = f"Should handle invalid type for {param['name']}"

            test_args: list[str] = []
            for p in params:
                if p["name"] == param["name"]:
                    test_args.append(null_val)
                else:
                    t = p["type"].lower()
                    if t in ("int", "integer", "i32", "i64", "number", "float", "f64"):
                        test_args.append("1")
                    else:
                        test_args.append('"test"')

            args_str = ", ".join(test_args)

            if language == "python":
                error_code = f'''def test_{func_name}_{test_name}():
    """{desc}"""
    import pytest
    with pytest.raises((TypeError, ValueError)):
        {func_name}({args_str})
'''
            elif language in ("javascript", "typescript"):
                error_code = f'''test("{func_name} - {desc}", () => {{
  expect(() => {{
    {func_name}({args_str});
  }}).toThrow();
}});
'''
            elif language == "go":
                pascal_fn = func_name[0].upper() + func_name[1:]
                error_code = f"""func Test{pascal_fn}_{test_name.title().replace("_", "")}(t *testing.T) {{
\t// {desc}
\t_, err := {pascal_fn}({args_str})
\tif err == nil {{
\t\tt.Error("expected error for invalid input")
\t}}
}}
"""
            elif language == "rust":
                error_code = f"""#[test]
#[should_panic]
fn test_{func_name}_{test_name}() {{
    // {desc}
    {func_name}({args_str});
}}
"""
            elif language == "java":
                camel_tn = re.sub(r"_(\w)", lambda m: m.group(1).upper(), test_name)
                camel_tn = camel_tn[0].upper() + camel_tn[1:]
                error_code = f"""@Test
void {func_name}{camel_tn}() {{
    // {desc}
    assertThrows(IllegalArgumentException.class, () -> {{
        {func_name}({args_str});
    }});
}}
"""
            else:
                error_code = gen(func_name, test_name, "error", desc, args_str, "error")

            cases.append(
                {
                    "name": f"test_{func_name}_{test_name}",
                    "category": "error",
                    "description": desc,
                    "code": error_code,
                }
            )

        # Missing required params (call with fewer args)
        if len(params) > 1:
            # Only the first param
            first_arg = (
                "1"
                if params[0]["type"].lower() in ("int", "integer", "number")
                else '"test"'
            )
            desc = "Should fail when required parameters are missing"

            if language == "python":
                missing_code = f'''def test_{func_name}_missing_params():
    """{desc}"""
    import pytest
    with pytest.raises(TypeError):
        {func_name}({first_arg})
'''
            elif language in ("javascript", "typescript"):
                missing_code = f'''test("{func_name} - {desc}", () => {{
  expect(() => {{
    {func_name}({first_arg});
  }}).toThrow();
}});
'''
            else:
                missing_code = gen(
                    func_name, "missing_params", "error", desc, first_arg, "error"
                )

            cases.append(
                {
                    "name": f"test_{func_name}_missing_params",
                    "category": "error",
                    "description": desc,
                    "code": missing_code,
                }
            )

    return cases


# ── Public API ───────────────────────────────────────────────────────────────


def generate_test_cases(
    function_signature: str,
    language: str = "python",
    strategy: str = "comprehensive",
) -> dict:
    """Generate test case scaffolds from a function signature.

    Args:
        function_signature: Function signature string.
        language: Target language (python, javascript, typescript, go, rust, java).
        strategy: Test strategy — "happy", "edge", or "comprehensive".

    Returns:
        Dictionary with test cases, coverage analysis, and test framework info.
    """
    lang = language.lower()
    strat = strategy.lower()
    if strat not in ("happy", "edge", "comprehensive"):
        strat = "comprehensive"

    parsed = _parse_signature(function_signature)
    func_name = parsed["name"] or "unnamed"
    params = parsed["params"]

    test_cases = _build_test_cases(func_name, params, lang, strat)

    # Coverage analysis
    category_counts: dict[str, int] = {
        "happy_path": 0,
        "edge_case": 0,
        "boundary": 0,
        "error": 0,
    }
    for tc in test_cases:
        cat = tc["category"]
        if cat in category_counts:
            category_counts[cat] += 1

    framework = _FRAMEWORKS.get(lang, "pytest")

    return {
        "function_name": func_name,
        "language": lang,
        "strategy": strat,
        "test_cases": test_cases,
        "coverage_analysis": {
            "categories": category_counts,
            "total": len(test_cases),
        },
        "test_framework": framework,
    }
