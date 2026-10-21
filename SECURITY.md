# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT open a public GitHub issue**
2. Email: **hello@claude-world.com** with subject "Security: claude-101"
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge your report within 48 hours and provide a timeline for a fix.

## Scope

This project processes user-provided text locally. Key areas of concern:

- **Input validation:** All tool inputs are strings/numbers — no file system access, no network calls
- **Regex DoS:** Complex regex patterns could cause slowdowns with crafted input
- **Dependency chain:** Only `sqlparse` (>= 0.6, which fixes several parser DoS advisories) as a runtime dependency; the optional `mcp` extra adds the MCP Python SDK 2.x for the server

## Security Design

- No network calls from any tool
- No file system reads/writes
- No code execution (tools analyze code as text, never execute it)
- All computation is deterministic and local
