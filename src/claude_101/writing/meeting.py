"""Meeting notes parser — extracts structure from raw text via regex."""

from __future__ import annotations

import re


def parse_meeting_notes(
    raw_notes: str,
    output_format: str = "structured",
) -> dict:
    """Extract attendees, action items, decisions, and topics from raw notes.

    Args:
        raw_notes: Free-form meeting notes text.
        output_format: One of structured (full), brief (summary only),
                action-only (just action items).
    """
    output_format = output_format.lower().strip()
    if output_format not in ("structured", "brief", "action-only"):
        output_format = "structured"

    attendees = _extract_attendees(raw_notes)
    action_items = _extract_action_items(raw_notes)
    decisions = _extract_decisions(raw_notes)
    topics = _extract_topics(raw_notes)
    timestamps = _extract_timestamps(raw_notes)
    duration = _extract_duration(raw_notes)

    metrics = {
        "duration_mentioned": duration,
        "action_item_count": len(action_items),
        "decision_count": len(decisions),
        "attendee_count": len(attendees),
    }

    if output_format == "action-only":
        return {
            "attendees": attendees,
            "action_items": action_items,
            "decisions": [],
            "topics_discussed": [],
            "timestamps": [],
            "metrics": metrics,
            "format": output_format,
        }

    if output_format == "brief":
        return {
            "attendees": attendees,
            "action_items": action_items[:3],
            "decisions": decisions[:3],
            "topics_discussed": topics[:5],
            "timestamps": [],
            "metrics": metrics,
            "format": output_format,
        }

    # structured — full output
    return {
        "attendees": attendees,
        "action_items": action_items,
        "decisions": decisions,
        "topics_discussed": topics,
        "timestamps": timestamps,
        "metrics": metrics,
        "format": output_format,
    }


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def _extract_attendees(text: str) -> list[str]:
    """Extract attendee names from @mentions or 'Attendees:' line."""
    attendees: list[str] = []
    seen: set[str] = set()

    # Pattern 1: "Attendees:" / "Participants:" / "Present:" line
    # First try a single-line match (most common: "Attendees: A, B, C")
    header_match = re.search(
        r"(?:attendees|participants|present|people)\s*[:]\s*(.+)",
        text,
        re.IGNORECASE,
    )
    if not header_match:
        # Try multi-line list (one name per line under the header)
        header_match = re.search(
            r"(?:attendees|participants|present|people)\s*[:]\s*\n((?:\s*[\-\*]?\s*.+\n?)+)",
            text,
            re.IGNORECASE,
        )
    if header_match:
        line = header_match.group(1)
        # Split by comma, semicolon, newline, or " and "
        names = re.split(r"[,;\n]|\band\b", line)
        for name in names:
            name = name.strip().strip("-").strip("*").strip()
            # Remove common prefixes
            name = re.sub(r"^[@\-\*\d\.\)]+\s*", "", name).strip()
            if name and len(name) > 1 and name.lower() not in seen:
                seen.add(name.lower())
                attendees.append(name)

    # Pattern 2: @mentions throughout the text
    mentions = re.findall(r"@(\w[\w.]*)", text)
    for m in mentions:
        if m.lower() not in seen:
            seen.add(m.lower())
            attendees.append(f"@{m}")

    return attendees


def _extract_action_items(text: str) -> list[dict]:
    """Extract action items from TODO:, ACTION:, [ ], and similar patterns."""
    items: list[dict] = []

    # Patterns that signal action items
    patterns = [
        # TODO: ... @owner ... by date
        r"(?:TODO|ACTION|TASK|AI)\s*[:]\s*(.+)",
        # - [ ] checkbox items
        r"\[\s*\]\s*(.+)",
        # "needs to", "should", "will" + verb phrases
        r"(\S+)\s+(?:needs?\s+to|should|will|must)\s+(.+?)(?:\.|$)",
        # "assigned to @person: task"
        r"(?:assigned?\s+to)\s+@?(\w+)\s*[:]\s*(.+)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            groups = match.groups()
            raw = " ".join(g for g in groups if g).strip()
            if not raw or len(raw) < 5:
                continue
            item = _parse_action_item(raw)
            # Deduplicate by task text
            if not any(i["task"] == item["task"] for i in items):
                items.append(item)

    return items


def _parse_action_item(raw: str) -> dict:
    """Parse a raw action item string into task / owner / deadline."""
    task = raw.strip().rstrip(".")
    owner = "unassigned"
    deadline = "not specified"

    # Extract owner from @mention
    owner_match = re.search(r"@(\w+)", task)
    if owner_match:
        owner = f"@{owner_match.group(1)}"

    # Extract owner from "Name to <verb>" pattern (e.g. "Bob to update timeline")
    # Only match if no @mention owner was found and the text starts with a
    # capitalized name followed by " to <verb>".
    if owner == "unassigned":
        name_to_match = re.match(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+to\s+\w+", task)
        if name_to_match:
            owner = name_to_match.group(1).strip()

    # Extract deadline patterns
    deadline_patterns = [
        r"(?:by|before|due|deadline)\s*[:\-]?\s*(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)",
        r"(?:by|before|due|deadline)\s*[:\-]?\s*(\w+\s+\d{1,2}(?:,?\s+\d{4})?)",
        r"(?:by|before|due)\s+(EOD|end of day|end of week|EOW|tomorrow|next\s+\w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    ]
    for dp in deadline_patterns:
        dm = re.search(dp, task, re.IGNORECASE)
        if dm:
            deadline = dm.group(1).strip()
            break

    # Clean the task text (remove owner/deadline markers)
    task = re.sub(r"@\w+", "", task).strip()
    # Remove leading "Name to " when we extracted an owner from that pattern
    if owner != "unassigned" and not owner.startswith("@"):
        task = re.sub(
            r"^" + re.escape(owner) + r"\s+to\s+",
            "",
            task,
        ).strip()
    task = re.sub(
        r"(?:by|before|due|deadline)\s*[:\-]?\s*\S+(?:\s+\S+)?",
        "",
        task,
        flags=re.IGNORECASE,
    ).strip()
    task = re.sub(r"\s{2,}", " ", task).strip().rstrip(",;:")

    return {"task": task, "owner": owner, "deadline": deadline}


def _extract_decisions(text: str) -> list[str]:
    """Extract decisions — lines containing decision-related keywords."""
    decisions: list[str] = []
    keywords = r"\b(?:decided|agreed|approved|confirmed|resolved|concluded|will\s+go\s+with|chose|selected|finalized)\b"

    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        if re.search(keywords, line, re.IGNORECASE):
            # Also check for explicit markers
            clean = re.sub(r"^[\-\*\d\.\)]+\s*", "", line).strip()
            clean = re.sub(
                r"^(?:DECISION|AGREED|RESOLVED)\s*[:]\s*",
                "",
                clean,
                flags=re.IGNORECASE,
            ).strip()
            if clean and clean not in decisions:
                decisions.append(clean)

    # Also look for DECISION: prefix lines
    explicit = re.findall(
        r"(?:DECISION|AGREED|RESOLVED)\s*[:]\s*(.+)", text, re.IGNORECASE
    )
    for d in explicit:
        d = d.strip().rstrip(".")
        if d and d not in decisions:
            decisions.append(d)

    return decisions


def _extract_topics(text: str) -> list[str]:
    """Extract discussed topics from headers, bold items, and section markers."""
    topics: list[str] = []
    seen: set[str] = set()

    # Markdown headers
    for m in re.finditer(r"^#{1,3}\s+(.+)", text, re.MULTILINE):
        topic = m.group(1).strip()
        if topic.lower() not in seen:
            seen.add(topic.lower())
            topics.append(topic)

    # Bold markers **topic** or __topic__
    for m in re.finditer(r"\*\*(.+?)\*\*|__(.+?)__", text):
        topic = (m.group(1) or m.group(2)).strip()
        if len(topic) > 3 and topic.lower() not in seen:
            seen.add(topic.lower())
            topics.append(topic)

    # Lines starting with "Topic:", "Discussion:", "Agenda:"
    for m in re.finditer(
        r"(?:topic|discussion|agenda\s*item)\s*[:]\s*(.+)", text, re.IGNORECASE
    ):
        topic = m.group(1).strip()
        if topic.lower() not in seen:
            seen.add(topic.lower())
            topics.append(topic)

    # If no explicit topics found, extract from first words of substantial paragraphs
    if not topics:
        for line in text.split("\n"):
            line = line.strip()
            if len(line.split()) >= 5 and not line.startswith(("-", "*", "#", "[")):
                summary = " ".join(line.split()[:6])
                if summary.lower() not in seen:
                    seen.add(summary.lower())
                    topics.append(summary + "...")
                    if len(topics) >= 5:
                        break

    return topics


def _extract_timestamps(text: str) -> list[str]:
    """Extract HH:MM or HH:MM:SS patterns from text."""
    raw = re.findall(r"\b(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?)\b", text)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for ts in raw:
        normalized = ts.strip()
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def _extract_duration(text: str) -> str | None:
    """Extract meeting duration from text."""
    patterns = [
        r"(?:duration|length|lasted)\s*[:\-]?\s*(\d+\s*(?:min(?:ute)?s?|hours?|hrs?))",
        r"(\d+\s*(?:min(?:ute)?s?|hours?|hrs?))\s+(?:meeting|call|session)",
        r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            if m.lastindex and m.lastindex >= 2:
                return f"{m.group(1)} - {m.group(2)}"
            return m.group(1).strip()
    return None
