# Claude 101 Skills

Copy the skill file to your Claude Code skills directory to unlock all 24 use cases.

## Quick Setup

```bash
# One-liner: copy skill to your Claude Code config
mkdir -p ~/.claude/skills && cp claude-101-mastery.md ~/.claude/skills/
```

Or manually: copy `claude-101-mastery.md` to `~/.claude/skills/` or `<your-project>/.claude/skills/`.

## What This Does

The skill teaches Claude the optimal workflow for each of the 24 use cases:

1. **When to call which MCP tool** — pattern matching on user intent
2. **How to interpret the results** — which fields matter and why
3. **How to produce the final output** — combining tool data with Claude's writing

## Example

Without the skill, you say: "Write me an email" → Claude writes an email (decent but generic).

With the skill, you say: "Write me an email" → Claude calls `draft_email` MCP tool → gets formality analysis, tone guidance, structure validation → writes a better email informed by real metrics.
