"""Code scaffold generator — produce real template code for common patterns."""

from __future__ import annotations


# ── Language metadata ────────────────────────────────────────────────────────

_NAMING = {
    "python": "snake_case",
    "javascript": "camelCase",
    "typescript": "camelCase",
    "go": "PascalCase",
    "rust": "snake_case",
    "java": "PascalCase",
}

_EXTENSIONS = {
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "go": ".go",
    "rust": ".rs",
    "java": ".java",
}


# ── Name conversion helpers ──────────────────────────────────────────────────


def _to_snake(name: str) -> str:
    """Convert any name to snake_case."""
    import re

    s = re.sub(r"[-\s]+", "_", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def _to_camel(name: str) -> str:
    """Convert any name to camelCase."""
    parts = _to_snake(name).split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def _to_pascal(name: str) -> str:
    """Convert any name to PascalCase."""
    return "".join(p.capitalize() for p in _to_snake(name).split("_"))


def _convert_name(name: str, convention: str) -> str:
    if convention == "snake_case":
        return _to_snake(name)
    if convention == "camelCase":
        return _to_camel(name)
    return _to_pascal(name)


# ── Template generators (per language × pattern) ────────────────────────────


def _python_class(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''"""Module for {cn}."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class {cn}:
    """{desc or f"{cn} class."}"""

    name: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def process(self) -> dict[str, Any]:
        """Process and return results."""
        return {{"name": self.name, "status": "processed", **self._data}}

    def validate(self) -> bool:
        """Validate internal state."""
        return bool(self.name)

    def __str__(self) -> str:
        return f"{cn}(name={{self.name!r}})"
'''
    return code, ["dataclasses", "typing"]


def _python_function(name: str, desc: str) -> tuple[str, list[str]]:
    fn = _to_snake(name)
    code = f'''"""Utility functions for {fn}."""

from __future__ import annotations

from typing import Any


def {fn}(data: Any, *, verbose: bool = False) -> dict[str, Any]:
    """{desc or f"Process data via {fn}."}

    Args:
        data: Input data to process.
        verbose: If True, include debug information.

    Returns:
        Dictionary with processing results.
    """
    result: dict[str, Any] = {{"input_type": type(data).__name__}}

    if isinstance(data, str):
        result["length"] = len(data)
        result["word_count"] = len(data.split())
    elif isinstance(data, (list, tuple)):
        result["length"] = len(data)
        result["element_types"] = list({{type(x).__name__ for x in data}})
    elif isinstance(data, dict):
        result["keys"] = list(data.keys())

    result["status"] = "success"
    if verbose:
        result["raw_input"] = repr(data)

    return result
'''
    return code, ["typing"]


def _python_api(name: str, desc: str) -> tuple[str, list[str]]:
    fn = _to_snake(name)
    code = f'''"""API endpoint handler for {fn}."""

from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any


def handle_{fn}(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    """{desc or f"Handle API requests for {fn}."}

    Args:
        method: HTTP method (GET, POST, PUT, DELETE).
        path: Request path.
        body: Request body (for POST/PUT).

    Returns:
        Response dictionary with status, headers, and body.
    """
    handlers = {{
        "GET": _handle_get,
        "POST": _handle_post,
        "PUT": _handle_put,
        "DELETE": _handle_delete,
    }}

    handler = handlers.get(method.upper())
    if handler is None:
        return _response(HTTPStatus.METHOD_NOT_ALLOWED, {{"error": f"Method {{method}} not allowed"}})

    return handler(path, body)


def _handle_get(path: str, body: dict | None) -> dict[str, Any]:
    return _response(HTTPStatus.OK, {{"items": [], "total": 0}})


def _handle_post(path: str, body: dict | None) -> dict[str, Any]:
    if not body:
        return _response(HTTPStatus.BAD_REQUEST, {{"error": "Request body required"}})
    return _response(HTTPStatus.CREATED, {{"id": 1, **body}})


def _handle_put(path: str, body: dict | None) -> dict[str, Any]:
    if not body:
        return _response(HTTPStatus.BAD_REQUEST, {{"error": "Request body required"}})
    return _response(HTTPStatus.OK, {{"updated": True, **body}})


def _handle_delete(path: str, body: dict | None) -> dict[str, Any]:
    return _response(HTTPStatus.NO_CONTENT, {{}})


def _response(status: HTTPStatus, body: dict[str, Any]) -> dict[str, Any]:
    return {{
        "status_code": status.value,
        "status_text": status.phrase,
        "headers": {{"Content-Type": "application/json"}},
        "body": body,
    }}
'''
    return code, ["json", "http"]


def _python_cli(name: str, desc: str) -> tuple[str, list[str]]:
    fn = _to_snake(name)
    code = f'''"""CLI tool for {fn}."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """{desc or f"Run the {fn} CLI."}"""
    parser = argparse.ArgumentParser(
        prog="{fn}",
        description="{desc or fn}",
    )
    parser.add_argument("input", nargs="?", default="-", help="Input file (default: stdin)")
    parser.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            data = sys.stdin.read()
        else:
            with open(args.input) as f:
                data = f.read()

        result = process(data, verbose=args.verbose)

        if args.output == "-":
            print(result)
        else:
            with open(args.output, "w") as f:
                f.write(result)

        return 0
    except Exception as exc:
        print(f"Error: {{exc}}", file=sys.stderr)
        return 1


def process(data: str, *, verbose: bool = False) -> str:
    """Process input data and return result."""
    lines = data.strip().splitlines()
    if verbose:
        print(f"Processing {{len(lines)}} lines...", file=sys.stderr)
    return f"Processed {{len(lines)}} lines"


if __name__ == "__main__":
    sys.exit(main())
'''
    return code, ["argparse", "sys"]


def _python_model(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''"""Data model for {cn}."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class {cn}:
    """{desc or f"{cn} data model."}"""

    id: str = field(default_factory=lambda: uuid4().hex[:12])
    name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def update(self, **kwargs: Any) -> None:
        """Update fields and set updated_at timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> {cn}:
        """Deserialize from dictionary."""
        known_fields = {{f.name for f in cls.__dataclass_fields__.values()}}
        filtered = {{k: v for k, v in data.items() if k in known_fields}}
        return cls(**filtered)

    def validate(self) -> list[str]:
        """Return list of validation errors (empty if valid)."""
        errors: list[str] = []
        if not self.name:
            errors.append("name is required")
        return errors
'''
    return code, ["dataclasses", "datetime", "uuid", "typing"]


def _python_singleton(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''"""Singleton pattern for {cn}."""

from __future__ import annotations

import threading
from typing import Any


class {cn}:
    """{desc or f"{cn} singleton."}

    Thread-safe singleton implementation using double-checked locking.
    """

    _instance: {cn} | None = None
    _lock = threading.Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> {cn}:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        if self._initialized:
            return
        self._config = config or {{}}
        self._data: dict[str, Any] = {{}}
        self._initialized = True

    @property
    def config(self) -> dict[str, Any]:
        return self._config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (mainly for testing)."""
        with cls._lock:
            cls._instance = None
'''
    return code, ["threading", "typing"]


def _python_factory(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''"""Factory pattern for {cn}."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Base{cn}(ABC):
    """{desc or f"Abstract base for {cn} products."}"""

    @abstractmethod
    def execute(self, data: Any) -> Any:
        """Execute the product's operation."""
        ...

    @abstractmethod
    def describe(self) -> str:
        """Return a description of the product."""
        ...


class Default{cn}(Base{cn}):
    """Default implementation."""

    def execute(self, data: Any) -> Any:
        return {{"type": "default", "input": data}}

    def describe(self) -> str:
        return "Default {cn} implementation"


class Custom{cn}(Base{cn}):
    """Custom implementation."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {{}}

    def execute(self, data: Any) -> Any:
        return {{"type": "custom", "input": data, "config": self._config}}

    def describe(self) -> str:
        return f"Custom {cn} with config: {{self._config}}"


class {cn}Factory:
    """Factory for creating {cn} instances."""

    _registry: dict[str, type[Base{cn}]] = {{
        "default": Default{cn},
        "custom": Custom{cn},
    }}

    @classmethod
    def create(cls, product_type: str = "default", **kwargs: Any) -> Base{cn}:
        """Create a product by type name."""
        product_cls = cls._registry.get(product_type)
        if product_cls is None:
            available = ", ".join(sorted(cls._registry))
            raise ValueError(f"Unknown type '{{product_type}}'. Available: {{available}}")
        return product_cls(**kwargs)

    @classmethod
    def register(cls, name: str, product_cls: type[Base{cn}]) -> None:
        """Register a new product type."""
        cls._registry[name] = product_cls

    @classmethod
    def available_types(cls) -> list[str]:
        """List registered product types."""
        return sorted(cls._registry)
'''
    return code, ["abc", "typing"]


def _python_observer(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''"""Observer pattern for {cn}."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from collections import defaultdict


class {cn}Event:
    """Event emitted by {cn}."""

    def __init__(self, event_type: str, data: Any = None, source: str = "") -> None:
        self.event_type = event_type
        self.data = data
        self.source = source

    def __repr__(self) -> str:
        return f"{cn}Event(type={{self.event_type!r}}, source={{self.source!r}})"


class {cn}Observer(ABC):
    """Abstract observer for {cn} events."""

    @abstractmethod
    def on_event(self, event: {cn}Event) -> None:
        """Handle an event."""
        ...


class {cn}Subject:
    """{desc or f"Observable subject that notifies {cn}Observer instances."}"""

    def __init__(self) -> None:
        self._observers: dict[str, list[{cn}Observer]] = defaultdict(list)

    def subscribe(self, event_type: str, observer: {cn}Observer) -> None:
        """Subscribe an observer to an event type."""
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)

    def unsubscribe(self, event_type: str, observer: {cn}Observer) -> None:
        """Unsubscribe an observer from an event type."""
        observers = self._observers.get(event_type, [])
        if observer in observers:
            observers.remove(observer)

    def notify(self, event: {cn}Event) -> int:
        """Notify all observers subscribed to the event type.

        Returns the number of observers notified.
        """
        observers = self._observers.get(event.event_type, [])
        all_observers = self._observers.get("*", [])
        notified = 0
        for obs in observers + all_observers:
            obs.on_event(event)
            notified += 1
        return notified

    def emit(self, event_type: str, data: Any = None, source: str = "") -> int:
        """Convenience method: create and emit an event."""
        return self.notify({cn}Event(event_type, data, source))

    @property
    def subscriber_count(self) -> int:
        """Total number of subscriptions."""
        return sum(len(obs) for obs in self._observers.values())
'''
    return code, ["abc", "typing", "collections"]


# ── JS / TS generators ──────────────────────────────────────────────────────


def _js_class(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    ts_types = ": string" if is_ts else ""
    ts_data = ": Record<string, unknown>" if is_ts else ""
    ts_bool = ": boolean" if is_ts else ""
    ts_obj = ": Record<string, unknown>" if is_ts else ""
    code = f"""/**
 * {desc or f"{cn} class."}
 */
export class {cn} {{
  constructor(name{ts_types} = "") {{
    this.name = name;
    this._data{ts_data} = {{}};
  }}

  process(){ts_obj} {{
    return {{ name: this.name, status: "processed", ...this._data }};
  }}

  validate(){ts_bool} {{
    return Boolean(this.name);
  }}

  toString(){ts_types} {{
    return `{cn}(name=${{this.name}})`;
  }}
}}
"""
    return code, []


def _js_function(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    fn = _to_camel(name)
    ts_param = (
        "data: unknown, options: {{ verbose?: boolean }} = {{}}"
        if is_ts
        else "data, options = {}"
    )
    ts_ret = ": Record<string, unknown>" if is_ts else ""
    code = f"""/**
 * {desc or f"Process data via {fn}."}
 * @param data - Input data to process.
 * @param options - Processing options.
 * @returns Processing results.
 */
export function {fn}({ts_param}){ts_ret} {{
  const result{": Record<string, unknown>" if is_ts else ""} = {{
    inputType: typeof data,
  }};

  if (typeof data === "string") {{
    result.length = data.length;
    result.wordCount = data.split(/\\s+/).filter(Boolean).length;
  }} else if (Array.isArray(data)) {{
    result.length = data.length;
    result.elementTypes = [...new Set(data.map((x) => typeof x))];
  }} else if (data && typeof data === "object") {{
    result.keys = Object.keys(data);
  }}

  result.status = "success";
  if (options.verbose) {{
    result.rawInput = JSON.stringify(data);
  }}

  return result;
}}
"""
    return code, []


def _js_api(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    fn = _to_camel(name)
    code_lines = ["/**", f" * {desc or f'API endpoint handler for {fn}.'}", " */"]
    if is_ts:
        code_lines += [
            "",
            "interface ApiResponse {",
            "  statusCode: number;",
            "  body: Record<string, unknown>;",
            "}",
            "",
            f"export function handle{_to_pascal(name)}(",
            "  method: string,",
            "  path: string,",
            "  body?: Record<string, unknown>,",
            "): ApiResponse {",
        ]
    else:
        code_lines += [
            "",
            f"export function handle{_to_pascal(name)}(method, path, body) {{",
        ]
    code_lines += [
        "  const handlers = {",
        "    GET: () => ({ statusCode: 200, body: { items: [], total: 0 } }),",
        "    POST: () => {",
        '      if (!body) return { statusCode: 400, body: { error: "Body required" } };',
        "      return { statusCode: 201, body: { id: 1, ...body } };",
        "    },",
        "    PUT: () => {",
        '      if (!body) return { statusCode: 400, body: { error: "Body required" } };',
        "      return { statusCode: 200, body: { updated: true, ...body } };",
        "    },",
        "    DELETE: () => ({ statusCode: 204, body: {} }),",
        "  };",
        "",
        "  const handler = handlers[method.toUpperCase()];",
        "  if (!handler) {",
        "    return { statusCode: 405, body: { error: `Method ${method} not allowed` } };",
        "  }",
        "  return handler();",
        "}",
    ]
    return "\n".join(code_lines) + "\n", []


def _js_cli(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    fn = _to_camel(name)
    code = f"""#!/usr/bin/env node
/**
 * {desc or f"CLI tool for {fn}."}
 */

import {{ readFileSync }} from "fs";

function main() {{
  const args = process.argv.slice(2);
  const verbose = args.includes("--verbose") || args.includes("-v");
  const inputFile = args.find((a) => !a.startsWith("-")) || "-";

  try {{
    const data =
      inputFile === "-"
        ? readFileSync(0, "utf-8")
        : readFileSync(inputFile, "utf-8");

    const lines = data.trim().split("\\n");
    if (verbose) {{
      console.error(`Processing ${{lines.length}} lines...`);
    }}
    console.log(`Processed ${{lines.length}} lines`);
  }} catch (err) {{
    console.error(`Error: ${{err.message}}`);
    process.exit(1);
  }}
}}

main();
"""
    return code, ["fs"]


def _js_singleton(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    ts_any = ": unknown" if is_ts else ""
    ts_inst = f": {cn} | null" if is_ts else ""
    ts_map = ": Map<string, unknown>" if is_ts else ""
    code = f"""/**
 * {desc or f"{cn} singleton."}
 */
export class {cn} {{
  static _instance{ts_inst} = null;

  constructor() {{
    if ({cn}._instance) {{
      return {cn}._instance;
    }}
    this._data{ts_map} = new Map();
    {cn}._instance = this;
  }}

  get(key{": string" if is_ts else ""}){ts_any} {{
    return this._data.get(key);
  }}

  set(key{": string" if is_ts else ""}, value{ts_any}) {{
    this._data.set(key, value);
  }}

  static getInstance(){f": {cn}" if is_ts else ""} {{
    if (!{cn}._instance) {{
      new {cn}();
    }}
    return {cn}._instance;
  }}

  static reset() {{
    {cn}._instance = null;
  }}
}}
"""
    return code, []


def _js_factory(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    if is_ts:
        code = f"""/**
 * {desc or f"Factory pattern for {cn}."}
 */

export interface I{cn} {{
  execute(data: unknown): unknown;
  describe(): string;
}}

class Default{cn} implements I{cn} {{
  execute(data: unknown): unknown {{
    return {{ type: "default", input: data }};
  }}
  describe(): string {{
    return "Default {cn} implementation";
  }}
}}

class Custom{cn} implements I{cn} {{
  constructor(private config: Record<string, unknown> = {{}}) {{}}
  execute(data: unknown): unknown {{
    return {{ type: "custom", input: data, config: this.config }};
  }}
  describe(): string {{
    return `Custom {cn} with config: ${{JSON.stringify(this.config)}}`;
  }}
}}

type {cn}Constructor = new (...args: unknown[]) => I{cn};

export class {cn}Factory {{
  private static registry: Map<string, {cn}Constructor> = new Map([
    ["default", Default{cn} as {cn}Constructor],
    ["custom", Custom{cn} as {cn}Constructor],
  ]);

  static create(type: string = "default", ...args: unknown[]): I{cn} {{
    const Ctor = this.registry.get(type);
    if (!Ctor) throw new Error(`Unknown type '${{type}}'`);
    return new Ctor(...args);
  }}

  static register(name: string, ctor: {cn}Constructor): void {{
    this.registry.set(name, ctor);
  }}
}}
"""
    else:
        code = f"""/**
 * {desc or f"Factory pattern for {cn}."}
 */

class Default{cn} {{
  execute(data) {{
    return {{ type: "default", input: data }};
  }}
  describe() {{
    return "Default {cn} implementation";
  }}
}}

class Custom{cn} {{
  constructor(config = {{}}) {{
    this.config = config;
  }}
  execute(data) {{
    return {{ type: "custom", input: data, config: this.config }};
  }}
  describe() {{
    return `Custom {cn} with config: ${{JSON.stringify(this.config)}}`;
  }}
}}

export class {cn}Factory {{
  static _registry = new Map([
    ["default", Default{cn}],
    ["custom", Custom{cn}],
  ]);

  static create(type = "default", ...args) {{
    const Ctor = this._registry.get(type);
    if (!Ctor) throw new Error(`Unknown type '${{type}}'`);
    return new Ctor(...args);
  }}

  static register(name, ctor) {{
    this._registry.set(name, ctor);
  }}
}}
"""
    return code, []


def _js_observer(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    if is_ts:
        code = f"""/**
 * {desc or f"Observer pattern for {cn}."}
 */

export interface {cn}Event {{
  type: string;
  data?: unknown;
  source?: string;
}}

export interface {cn}Observer {{
  onEvent(event: {cn}Event): void;
}}

export class {cn}Subject {{
  private observers: Map<string, {cn}Observer[]> = new Map();

  subscribe(eventType: string, observer: {cn}Observer): void {{
    const list = this.observers.get(eventType) || [];
    if (!list.includes(observer)) {{
      list.push(observer);
      this.observers.set(eventType, list);
    }}
  }}

  unsubscribe(eventType: string, observer: {cn}Observer): void {{
    const list = this.observers.get(eventType);
    if (list) {{
      const idx = list.indexOf(observer);
      if (idx !== -1) list.splice(idx, 1);
    }}
  }}

  notify(event: {cn}Event): number {{
    const specific = this.observers.get(event.type) || [];
    const wildcard = this.observers.get("*") || [];
    const all = [...specific, ...wildcard];
    all.forEach((obs) => obs.onEvent(event));
    return all.length;
  }}

  emit(type: string, data?: unknown, source?: string): number {{
    return this.notify({{ type, data, source }});
  }}
}}
"""
    else:
        code = f"""/**
 * {desc or f"Observer pattern for {cn}."}
 */

export class {cn}Subject {{
  constructor() {{
    this._observers = new Map();
  }}

  subscribe(eventType, observer) {{
    const list = this._observers.get(eventType) || [];
    if (!list.includes(observer)) {{
      list.push(observer);
      this._observers.set(eventType, list);
    }}
  }}

  unsubscribe(eventType, observer) {{
    const list = this._observers.get(eventType);
    if (list) {{
      const idx = list.indexOf(observer);
      if (idx !== -1) list.splice(idx, 1);
    }}
  }}

  notify(event) {{
    const specific = this._observers.get(event.type) || [];
    const wildcard = this._observers.get("*") || [];
    const all = [...specific, ...wildcard];
    all.forEach((obs) => obs.onEvent(event));
    return all.length;
  }}

  emit(type, data = null, source = "") {{
    return this.notify({{ type, data, source }});
  }}
}}
"""
    return code, []


def _js_model(name: str, desc: str, is_ts: bool) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    if is_ts:
        code = f"""/**
 * {desc or f"{cn} data model."}
 */

export interface {cn}Data {{
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  metadata: Record<string, unknown>;
}}

export class {cn} implements {cn}Data {{
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  metadata: Record<string, unknown>;

  constructor(data: Partial<{cn}Data> = {{}}) {{
    this.id = data.id || crypto.randomUUID().slice(0, 12);
    this.name = data.name || "";
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || "";
    this.metadata = data.metadata || {{}};
  }}

  update(fields: Partial<{cn}Data>): void {{
    Object.assign(this, fields);
    this.updatedAt = new Date().toISOString();
  }}

  toJSON(): {cn}Data {{
    return {{ id: this.id, name: this.name, createdAt: this.createdAt, updatedAt: this.updatedAt, metadata: this.metadata }};
  }}

  validate(): string[] {{
    const errors: string[] = [];
    if (!this.name) errors.push("name is required");
    return errors;
  }}
}}
"""
    else:
        code = f"""/**
 * {desc or f"{cn} data model."}
 */

export class {cn} {{
  constructor(data = {{}}) {{
    this.id = data.id || crypto.randomUUID().slice(0, 12);
    this.name = data.name || "";
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || "";
    this.metadata = data.metadata || {{}};
  }}

  update(fields) {{
    Object.assign(this, fields);
    this.updatedAt = new Date().toISOString();
  }}

  toJSON() {{
    return {{ id: this.id, name: this.name, createdAt: this.createdAt, updatedAt: this.updatedAt, metadata: this.metadata }};
  }}

  validate() {{
    const errors = [];
    if (!this.name) errors.push("name is required");
    return errors;
  }}
}}
"""
    return code, []


# ── Go generators ────────────────────────────────────────────────────────────


def _go_class(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f"""// Package {_to_snake(name)} provides {cn}.
package {_to_snake(name)}

// {cn} represents {desc or f"a {cn} entity"}.
type {cn} struct {{
\tName string
\tdata map[string]interface{{}}
}}

// New{cn} creates a new {cn} instance.
func New{cn}(name string) *{cn} {{
\treturn &{cn}{{
\t\tName: name,
\t\tdata: make(map[string]interface{{}}),
\t}}
}}

// Process processes the entity and returns results.
func (e *{cn}) Process() map[string]interface{{}} {{
\tresult := map[string]interface{{}}{{
\t\t"name":   e.Name,
\t\t"status": "processed",
\t}}
\tfor k, v := range e.data {{
\t\tresult[k] = v
\t}}
\treturn result
}}

// Validate checks if the entity is valid.
func (e *{cn}) Validate() bool {{
\treturn e.Name != ""
}}
"""
    return code, []


def _go_function(name: str, desc: str) -> tuple[str, list[str]]:
    fn = _to_pascal(name)
    code = f"""// Package {_to_snake(name)} provides {desc or fn}.
package {_to_snake(name)}

import "fmt"

// {fn} processes the input data and returns results.
func {fn}(data interface{{}}, verbose bool) map[string]interface{{}} {{
\tresult := map[string]interface{{}}{{
\t\t"status": "success",
\t}}

\tswitch v := data.(type) {{
\tcase string:
\t\tresult["input_type"] = "string"
\t\tresult["length"] = len(v)
\tcase []interface{{}}:
\t\tresult["input_type"] = "slice"
\t\tresult["length"] = len(v)
\tcase map[string]interface{{}}:
\t\tresult["input_type"] = "map"
\t\tkeys := make([]string, 0, len(v))
\t\tfor k := range v {{
\t\t\tkeys = append(keys, k)
\t\t}}
\t\tresult["keys"] = keys
\tdefault:
\t\tresult["input_type"] = fmt.Sprintf("%T", data)
\t}}

\tif verbose {{
\t\tresult["raw_input"] = fmt.Sprintf("%v", data)
\t}}

\treturn result
}}
"""
    return code, ["fmt"]


def _go_generic(name: str, desc: str, pattern: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''// Package {_to_snake(name)} provides {desc or f"{cn} ({pattern})"}.
package {_to_snake(name)}

// {cn} implements the {pattern} pattern.
type {cn} struct {{
\tName string
}}

// New{cn} creates a new {cn}.
func New{cn}(name string) *{cn} {{
\treturn &{cn}{{Name: name}}
}}

// Execute runs the {pattern} logic.
func (s *{cn}) Execute(input interface{{}}) (interface{{}}, error) {{
\t// TODO: implement {pattern} logic
\treturn map[string]interface{{}}{{"name": s.Name, "pattern": "{pattern}", "input": input}}, nil
}}
'''
    return code, []


# ── Rust generators ──────────────────────────────────────────────────────────


def _rust_class(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    sn = _to_snake(name)
    code = f'''//! {desc or f"{cn} implementation."}

use std::collections::HashMap;
use std::fmt;

/// {cn} entity.
#[derive(Debug, Clone)]
pub struct {cn} {{
    pub name: String,
    data: HashMap<String, String>,
}}

impl {cn} {{
    /// Create a new `{cn}`.
    pub fn new(name: impl Into<String>) -> Self {{
        Self {{
            name: name.into(),
            data: HashMap::new(),
        }}
    }}

    /// Process and return results.
    pub fn process(&self) -> HashMap<String, String> {{
        let mut result = self.data.clone();
        result.insert("name".into(), self.name.clone());
        result.insert("status".into(), "processed".into());
        result
    }}

    /// Validate the entity.
    pub fn validate(&self) -> bool {{
        !self.name.is_empty()
    }}

    /// Set a data field.
    pub fn set(&mut self, key: impl Into<String>, value: impl Into<String>) {{
        self.data.insert(key.into(), value.into());
    }}
}}

impl fmt::Display for {cn} {{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {{
        write!(f, "{cn}(name={{}})", self.name)
    }}
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_new_{sn}() {{
        let item = {cn}::new("test");
        assert!(item.validate());
    }}
}}
'''
    return code, ["std::collections::HashMap", "std::fmt"]


def _rust_function(name: str, desc: str) -> tuple[str, list[str]]:
    fn = _to_snake(name)
    code = f"""//! {desc or f"Utility for {fn}."}

use std::collections::HashMap;

/// Process the input string and return results.
///
/// # Arguments
/// * `data` - Input data to process.
/// * `verbose` - If true, include debug information.
pub fn {fn}(data: &str, verbose: bool) -> HashMap<String, String> {{
    let mut result = HashMap::new();
    result.insert("input_type".into(), "string".into());
    result.insert("length".into(), data.len().to_string());
    result.insert(
        "word_count".into(),
        data.split_whitespace().count().to_string(),
    );
    result.insert("status".into(), "success".into());

    if verbose {{
        result.insert("raw_input".into(), data.to_string());
    }}

    result
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_{fn}() {{
        let result = {fn}("hello world", false);
        assert_eq!(result["word_count"], "2");
    }}
}}
"""
    return code, ["std::collections::HashMap"]


def _rust_generic(name: str, desc: str, pattern: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    sn = _to_snake(name)
    code = f'''//! {desc or f"{cn} ({pattern} pattern)."}

/// {cn} implements the {pattern} pattern.
pub struct {cn} {{
    name: String,
}}

impl {cn} {{
    /// Create a new `{cn}`.
    pub fn new(name: impl Into<String>) -> Self {{
        Self {{ name: name.into() }}
    }}

    /// Execute the {pattern} logic.
    pub fn execute(&self, input: &str) -> String {{
        format!("{cn}({{}}): {pattern} on {{}}", self.name, input)
    }}
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_{sn}() {{
        let s = {cn}::new("test");
        assert!(!s.execute("data").is_empty());
    }}
}}
'''
    return code, []


# ── Java generators ──────────────────────────────────────────────────────────


def _java_class(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''import java.util.HashMap;
import java.util.Map;

/**
 * {desc or f"{cn} class."}
 */
public class {cn} {{
    private String name;
    private final Map<String, Object> data;

    public {cn}(String name) {{
        this.name = name;
        this.data = new HashMap<>();
    }}

    public Map<String, Object> process() {{
        Map<String, Object> result = new HashMap<>(data);
        result.put("name", name);
        result.put("status", "processed");
        return result;
    }}

    public boolean validate() {{
        return name != null && !name.isEmpty();
    }}

    public String getName() {{
        return name;
    }}

    public void setName(String name) {{
        this.name = name;
    }}

    public void setData(String key, Object value) {{
        data.put(key, value);
    }}

    @Override
    public String toString() {{
        return String.format("{cn}(name=%s)", name);
    }}
}}
'''
    return code, ["java.util.HashMap", "java.util.Map"]


def _java_function(name: str, desc: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f"""import java.util.HashMap;
import java.util.Map;

/**
 * {desc or f"Utility class for {cn}."}
 */
public class {cn}Util {{

    /**
     * Process the input data and return results.
     *
     * @param data    Input data to process.
     * @param verbose Whether to include debug info.
     * @return Map with processing results.
     */
    public static Map<String, Object> process(Object data, boolean verbose) {{
        Map<String, Object> result = new HashMap<>();
        result.put("inputType", data.getClass().getSimpleName());

        if (data instanceof String s) {{
            result.put("length", s.length());
            result.put("wordCount", s.split("\\\\s+").length);
        }} else if (data instanceof java.util.List<?> list) {{
            result.put("length", list.size());
        }} else if (data instanceof Map<?, ?> map) {{
            result.put("keyCount", map.size());
        }}

        result.put("status", "success");
        if (verbose) {{
            result.put("rawInput", data.toString());
        }}

        return result;
    }}
}}
"""
    return code, ["java.util.HashMap", "java.util.Map"]


def _java_generic(name: str, desc: str, pattern: str) -> tuple[str, list[str]]:
    cn = _to_pascal(name)
    code = f'''/**
 * {desc or f"{cn} — {pattern} pattern."}
 */
public class {cn} {{
    private final String name;

    public {cn}(String name) {{
        this.name = name;
    }}

    /**
     * Execute the {pattern} logic.
     */
    public Object execute(Object input) {{
        // TODO: implement {pattern} logic
        return java.util.Map.of("name", name, "pattern", "{pattern}", "input", input);
    }}
}}
'''
    return code, []


# ── Dispatcher ───────────────────────────────────────────────────────────────

_PYTHON_GENERATORS = {
    "class": _python_class,
    "function": _python_function,
    "api-endpoint": _python_api,
    "cli": _python_cli,
    "model": _python_model,
    "singleton": _python_singleton,
    "factory": _python_factory,
    "observer": _python_observer,
}


def _generate_code(
    language: str, pattern: str, name: str, desc: str
) -> tuple[str, list[str]]:
    """Dispatch to the correct generator and return (code, imports)."""
    lang = language.lower()

    if lang == "python":
        gen = _PYTHON_GENERATORS.get(pattern)
        if gen:
            return gen(name, desc)
        return _python_function(name, desc)

    if lang in ("javascript", "typescript"):
        is_ts = lang == "typescript"
        generators = {
            "class": _js_class,
            "model": _js_model,
            "singleton": _js_singleton,
            "factory": _js_factory,
            "observer": _js_observer,
            "function": _js_function,
            "api-endpoint": _js_api,
            "cli": _js_cli,
        }
        gen = generators.get(pattern)
        if gen:
            return gen(name, desc, is_ts)
        return _js_function(name, desc, is_ts)

    if lang == "go":
        if pattern == "class":
            return _go_class(name, desc)
        if pattern == "function":
            return _go_function(name, desc)
        return _go_generic(name, desc, pattern)

    if lang == "rust":
        if pattern == "class":
            return _rust_class(name, desc)
        if pattern == "function":
            return _rust_function(name, desc)
        return _rust_generic(name, desc, pattern)

    if lang == "java":
        if pattern == "class":
            return _java_class(name, desc)
        if pattern == "function":
            return _java_function(name, desc)
        return _java_generic(name, desc, pattern)

    # Fallback: Python
    return _python_function(name, desc)


# ── Public API ───────────────────────────────────────────────────────────────


def scaffold_code(
    language: str,
    pattern: str,
    name: str,
    description: str = "",
) -> dict:
    """Generate a code scaffold for the given language, pattern, and name.

    Args:
        language: Programming language (python, javascript, typescript, go, rust, java).
        pattern: Design pattern (class, function, api-endpoint, cli, model, singleton, factory, observer).
        name: Name for the generated entity.
        description: Optional description to include in docstrings.

    Returns:
        Dictionary with generated code, metadata, and notes.
    """
    lang = language.lower()
    pat = pattern.lower()

    supported_languages = {"python", "javascript", "typescript", "go", "rust", "java"}
    supported_patterns = {
        "class",
        "function",
        "api-endpoint",
        "cli",
        "model",
        "singleton",
        "factory",
        "observer",
    }

    notes: list[str] = []
    if lang not in supported_languages:
        notes.append(f"Unsupported language '{language}', falling back to python")
        lang = "python"
    if pat not in supported_patterns:
        notes.append(f"Unsupported pattern '{pattern}', falling back to function")
        pat = "function"

    convention = _NAMING.get(lang, "snake_case")
    extension = _EXTENSIONS.get(lang, ".py")

    code, imports = _generate_code(lang, pat, name, description)
    converted_name = _convert_name(name, convention)
    notes.append(f"Generated {pat} scaffold for '{converted_name}' in {lang}")

    return {
        "language": lang,
        "pattern": pat,
        "name": converted_name,
        "code": code,
        "naming_convention": convention,
        "imports": imports,
        "file_extension": extension,
        "notes": notes,
    }
