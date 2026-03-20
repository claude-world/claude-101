"""API documentation scaffold generator — OpenAPI YAML and markdown."""

from __future__ import annotations

import re
from typing import Any


# ── Endpoint parsing ─────────────────────────────────────────────────────────

_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

_STANDARD_RESPONSES: dict[str, dict[str, str]] = {
    "GET": {
        "200": "Success",
        "400": "Bad Request",
        "404": "Not Found",
        "500": "Internal Server Error",
    },
    "POST": {
        "201": "Created",
        "400": "Bad Request",
        "409": "Conflict",
        "500": "Internal Server Error",
    },
    "PUT": {
        "200": "Updated",
        "400": "Bad Request",
        "404": "Not Found",
        "500": "Internal Server Error",
    },
    "PATCH": {
        "200": "Updated",
        "400": "Bad Request",
        "404": "Not Found",
        "500": "Internal Server Error",
    },
    "DELETE": {
        "204": "No Content",
        "404": "Not Found",
        "500": "Internal Server Error",
    },
}


def _parse_endpoints(raw: str) -> list[dict[str, Any]]:
    """Parse endpoint definitions from a string.

    Accepts formats like:
        GET /users - List users
        POST /users - Create user
        GET /users/{id} - Get user by ID
        DELETE /users/{id}/posts/{post_id}
    """
    endpoints: list[dict[str, Any]] = []

    # Split by comma or newline
    parts = re.split(r"[,\n]+", raw.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Match: METHOD /path - description  OR  METHOD /path
        m = re.match(
            r"(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/\S*)\s*(?:-\s*(.+))?",
            part,
            re.IGNORECASE,
        )
        if not m:
            continue

        method = m.group(1).upper()
        path = m.group(2).strip()
        description = m.group(3).strip() if m.group(3) else f"{method} {path}"

        # Extract path parameters from {curly_braces}
        path_params = re.findall(r"\{(\w+)\}", path)
        parameters: list[dict[str, Any]] = []
        for param in path_params:
            # Infer type from common naming patterns
            if param.endswith("_id") or param == "id":
                ptype = "integer"
            else:
                ptype = "string"
            parameters.append(
                {
                    "name": param,
                    "in": "path",
                    "type": ptype,
                    "required": True,
                }
            )

        # Add common query parameters for GET list endpoints
        if method == "GET" and not path_params:
            parameters.extend(
                [
                    {
                        "name": "page",
                        "in": "query",
                        "type": "integer",
                        "required": False,
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "type": "integer",
                        "required": False,
                    },
                ]
            )

        # Determine responses
        responses: dict[str, dict[str, str]] = {}
        standard = _STANDARD_RESPONSES.get(
            method, {"200": "Success", "500": "Internal Server Error"}
        )
        for code, desc in standard.items():
            responses[code] = {"description": desc}

        endpoints.append(
            {
                "method": method,
                "path": path,
                "description": description,
                "parameters": parameters,
                "responses": responses,
            }
        )

    return endpoints


# ── OpenAPI YAML generation ──────────────────────────────────────────────────


def _indent(text: str, level: int) -> str:
    """Indent each line by the given number of spaces."""
    prefix = "  " * level
    return "\n".join(
        prefix + line if line.strip() else line for line in text.splitlines()
    )


def _generate_openapi(title: str, endpoints: list[dict[str, Any]]) -> str:
    """Generate an OpenAPI 3.0 YAML skeleton."""
    lines: list[str] = [
        "openapi: '3.0.3'",
        "info:",
        f"  title: {title}",
        "  version: '1.0.0'",
        f"  description: {title} - auto-generated API specification",
        "",
        "servers:",
        "  - url: http://localhost:8000",
        "    description: Local development",
        "",
        "paths:",
    ]

    # Group endpoints by path
    paths: dict[str, list[dict[str, Any]]] = {}
    for ep in endpoints:
        paths.setdefault(ep["path"], []).append(ep)

    for path, methods in paths.items():
        lines.append(f"  {path}:")
        for ep in methods:
            method = ep["method"].lower()
            lines.append(f"    {method}:")
            # Generate operation ID
            op_parts = path.strip("/").replace("{", "").replace("}", "").split("/")
            op_id = method + "".join(p.capitalize() for p in op_parts if p)
            lines.append(f"      operationId: {op_id}")
            lines.append(f"      summary: {ep['description']}")

            # Tags from first path segment
            if op_parts and op_parts[0]:
                lines.append("      tags:")
                lines.append(f"        - {op_parts[0]}")

            # Parameters
            if ep["parameters"]:
                lines.append("      parameters:")
                for param in ep["parameters"]:
                    lines.append(f"        - name: {param['name']}")
                    lines.append(f"          in: {param['in']}")
                    lines.append(
                        f"          required: {'true' if param['required'] else 'false'}"
                    )
                    lines.append("          schema:")
                    lines.append(f"            type: {param['type']}")

            # Request body for POST/PUT/PATCH
            if method in ("post", "put", "patch"):
                lines.append("      requestBody:")
                lines.append("        required: true")
                lines.append("        content:")
                lines.append("          application/json:")
                lines.append("            schema:")
                lines.append("              type: object")
                lines.append("              properties:")
                lines.append("                name:")
                lines.append("                  type: string")
                lines.append("                  description: Resource name")

            # Responses
            lines.append("      responses:")
            for code, resp in sorted(ep["responses"].items()):
                lines.append(f"        '{code}':")
                lines.append(f"          description: {resp['description']}")
                if code.startswith("2") and code != "204":
                    lines.append("          content:")
                    lines.append("            application/json:")
                    lines.append("              schema:")
                    lines.append("                type: object")
            lines.append("")

    return "\n".join(lines)


# ── Markdown generation ──────────────────────────────────────────────────────


def _generate_markdown(title: str, endpoints: list[dict[str, Any]]) -> str:
    """Generate a markdown API reference."""
    lines: list[str] = [
        f"# {title}",
        "",
        f"> Auto-generated API reference with {len(endpoints)} endpoint(s).",
        "",
        "## Table of Contents",
        "",
    ]

    # Table of contents
    for i, ep in enumerate(endpoints, 1):
        anchor = f"{ep['method'].lower()}-{ep['path'].strip('/').replace('/', '-').replace('{', '').replace('}', '')}"
        lines.append(
            f"{i}. [{ep['method']} {ep['path']}](#{anchor}) — {ep['description']}"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Endpoint details
    for ep in endpoints:
        lines.append(f"## {ep['method']} `{ep['path']}`")
        lines.append("")
        lines.append(f"**{ep['description']}**")
        lines.append("")

        # Parameters
        if ep["parameters"]:
            lines.append("### Parameters")
            lines.append("")
            lines.append("| Name | In | Type | Required |")
            lines.append("|------|-----|------|----------|")
            for param in ep["parameters"]:
                req = "Yes" if param["required"] else "No"
                lines.append(
                    f"| `{param['name']}` | {param['in']} | {param['type']} | {req} |"
                )
            lines.append("")

        # Request body
        if ep["method"] in ("POST", "PUT", "PATCH"):
            lines.append("### Request Body")
            lines.append("")
            lines.append("```json")
            lines.append("{")
            lines.append('  "name": "string"')
            lines.append("}")
            lines.append("```")
            lines.append("")

        # Responses
        lines.append("### Responses")
        lines.append("")
        lines.append("| Status | Description |")
        lines.append("|--------|-------------|")
        for code, resp in sorted(ep["responses"].items()):
            lines.append(f"| {code} | {resp['description']} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def _parse_code_routes(code: str) -> list[dict[str, Any]]:
    """Extract route definitions from Flask/FastAPI/Express code."""
    if not code.strip():
        return []

    routes: list[dict[str, Any]] = []

    # Flask: @app.route("/path", methods=["GET"])
    flask_pat = re.findall(
        r'@\w+\.(?:route|get|post|put|patch|delete)\s*\(\s*["\'](/[^"\']*)["\']'
        r"(?:.*?methods\s*=\s*\[([^\]]*)\])?",
        code,
        re.IGNORECASE | re.DOTALL,
    )
    for path, methods_str in flask_pat:
        if methods_str:
            methods = [m.strip().strip("'\"").upper() for m in methods_str.split(",")]
        else:
            methods = ["GET"]
        for m in methods:
            routes.append({"method": m, "path": path, "source": "flask"})

    # FastAPI: @app.get("/path")
    fastapi_pat = re.findall(
        r'@\w+\.(get|post|put|patch|delete)\s*\(\s*["\'](/[^"\']*)["\']',
        code,
        re.IGNORECASE,
    )
    for method, path in fastapi_pat:
        routes.append({"method": method.upper(), "path": path, "source": "fastapi"})

    # Express: app.get("/path", ...)  or router.get("/path", ...)
    express_pat = re.findall(
        r'(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*["\'](/[^"\']*)["\']',
        code,
        re.IGNORECASE,
    )
    for method, path in express_pat:
        routes.append({"method": method.upper(), "path": path, "source": "express"})

    return routes


def _detect_auth_patterns(
    endpoints: list[dict[str, Any]],
    code: str,
) -> dict[str, Any]:
    """Detect authentication patterns from endpoints and code."""
    if not code.strip():
        return {"type": "none", "details": []}

    auth_types: list[str] = []
    details: list[str] = []

    # Bearer / JWT
    if re.search(
        r"bearer|jwt|jsonwebtoken|access_token|authorization.*header",
        code,
        re.IGNORECASE,
    ):
        auth_types.append("bearer_token")
        details.append("JWT/Bearer token authentication detected")

    # API Key
    if re.search(r"api[_-]?key|x-api-key|apikey", code, re.IGNORECASE):
        auth_types.append("api_key")
        details.append("API key authentication detected")

    # OAuth
    if re.search(
        r"oauth|client_id|client_secret|authorization_code|refresh_token",
        code,
        re.IGNORECASE,
    ):
        auth_types.append("oauth2")
        details.append("OAuth 2.0 flow detected")

    # Basic Auth
    if re.search(r"basic\s+auth|base64|username.*password", code, re.IGNORECASE):
        auth_types.append("basic")
        details.append("Basic authentication detected")

    primary = auth_types[0] if auth_types else "none"
    return {"type": primary, "all_types": auth_types, "details": details}


def _check_api_consistency(endpoints: list[dict[str, Any]]) -> dict:
    """Check API endpoints for naming and method consistency."""
    issues: list[str] = []
    score = 100

    if not endpoints:
        return {"score": score, "issues": issues}

    paths = [ep["path"] for ep in endpoints]

    # Check plural/singular consistency
    segments: list[str] = []
    for path in paths:
        parts = path.strip("/").split("/")
        segments.extend(p for p in parts if p and not p.startswith("{"))

    plural_count = sum(1 for s in segments if s.endswith("s"))
    singular_count = len(segments) - plural_count
    if (
        plural_count > 0
        and singular_count > 0
        and min(plural_count, singular_count) / max(plural_count, singular_count) > 0.3
    ):
        issues.append("Inconsistent plural/singular naming in path segments")
        score -= 15

    # Check HTTP method correctness
    for ep in endpoints:
        method = ep["method"]
        path = ep["path"]
        has_id = bool(re.search(r"\{[^}]+\}", path))

        if method == "GET" and has_id:
            pass  # GET /resource/{id} is fine
        elif method == "POST" and has_id:
            issues.append(
                f"POST {path} — POST usually targets collection paths, not individual resources"
            )
            score -= 10
        elif method == "DELETE" and not has_id:
            issues.append(
                f"DELETE {path} — DELETE usually targets specific resources with an ID"
            )
            score -= 10

    # Check for consistent param naming
    param_names: list[str] = []
    for ep in endpoints:
        for p in ep.get("parameters", []):
            param_names.append(p["name"])

    if param_names:
        has_snake = any("_" in n for n in param_names)
        has_camel = any(re.search(r"[a-z][A-Z]", n) for n in param_names)
        if has_snake and has_camel:
            issues.append(
                "Mixed naming conventions in parameters (snake_case and camelCase)"
            )
            score -= 10

    return {"score": max(0, score), "issues": issues}


def _generate_example_bodies(endpoints: list[dict[str, Any]]) -> dict[str, dict]:
    """Generate example request bodies based on resource path segments."""
    examples: dict[str, dict] = {}

    # Common fields by resource name
    resource_fields: dict[str, dict[str, str]] = {
        "users": {"name": "string", "email": "string", "role": "string"},
        "posts": {"title": "string", "content": "string", "author_id": "integer"},
        "products": {"name": "string", "price": "number", "description": "string"},
        "orders": {"product_id": "integer", "quantity": "integer", "status": "string"},
        "comments": {"text": "string", "author_id": "integer"},
        "tasks": {"title": "string", "description": "string", "status": "string"},
    }

    for ep in endpoints:
        if ep["method"] not in ("POST", "PUT", "PATCH"):
            continue

        key = f"{ep['method']} {ep['path']}"
        # Infer resource from first path segment
        segments = ep["path"].strip("/").split("/")
        resource = segments[0] if segments else ""

        fields = resource_fields.get(resource, {"name": "string"})
        examples[key] = fields

    return examples


# ── Public API ───────────────────────────────────────────────────────────────


def scaffold_api_doc(
    endpoints: str,
    title: str = "API Reference",
    output_format: str = "openapi",
    code: str = "",
) -> dict:
    """Generate an API documentation skeleton from endpoint definitions.

    Args:
        endpoints: Endpoint definitions as a string, e.g.
            "GET /users - List users, POST /users - Create user".
        title: Document title.
        output_format: Output format — "openapi" (YAML) or "markdown".
        code: Optional source code to extract routes and detect auth patterns.

    Returns:
        Dictionary with parsed endpoints and the generated document.
    """
    parsed_endpoints = _parse_endpoints(endpoints)
    fmt = output_format.lower()

    if fmt == "markdown" or fmt == "md":
        document = _generate_markdown(title, parsed_endpoints)
        fmt = "markdown"
    else:
        document = _generate_openapi(title, parsed_endpoints)
        fmt = "openapi"

    result = {
        "title": title,
        "format": fmt,
        "endpoint_count": len(parsed_endpoints),
        "endpoints": parsed_endpoints,
        "document": document,
        "consistency": _check_api_consistency(parsed_endpoints),
        "example_bodies": _generate_example_bodies(parsed_endpoints),
    }

    if code.strip():
        code_routes = _parse_code_routes(code)
        auth_info = _detect_auth_patterns(parsed_endpoints, code)
        result["code_analysis"] = {
            "routes_found": code_routes,
            "route_count": len(code_routes),
            "auth": auth_info,
        }

    return result
