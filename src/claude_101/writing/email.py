"""Email drafting tool — scaffolds professional emails from context."""

from __future__ import annotations

import re

from .._utils import (
    formality_score as _formality_score,
    flesch_score,
    flesch_grade,
    sentence_tokenize,
    basic_stats,
    text_structure_check,
    count_pattern_matches,
)


def draft_email(
    context: str,
    tone: str = "professional",
    format: str = "standard",
) -> dict:
    """Parse context and scaffold a structured email draft.

    Args:
        context: Natural-language description of the email purpose,
                 recipient, and key points.
        tone: One of professional, friendly, assertive, apologetic,
              congratulatory.
        format: One of standard, brief, detailed.
    """
    tone = tone.lower().strip()
    format = format.lower().strip()

    if tone not in _TONE_PROFILES:
        tone = "professional"
    if format not in ("standard", "brief", "detailed"):
        format = "standard"

    profile = _TONE_PROFILES[tone]

    # --- Parse context for structured cues ---
    recipient = _extract_field(context, r"(?:to|recipient|for)\s*[:\-]?\s*(.+?)(?:\.|,|$)")
    purpose = _extract_field(context, r"(?:purpose|about|regarding|re)\s*[:\-]?\s*(.+?)(?:\.|,|$)")
    key_points = _extract_key_points(context)

    recipient_label = recipient or "the recipient"
    purpose_label = purpose or _summarize(context, max_words=10)

    # --- Subject suggestions ---
    subjects = _generate_subjects(purpose_label, tone)

    # --- Section content ---
    opening = _build_opening(tone, recipient_label, purpose_label)
    body = _build_body(tone, purpose_label, key_points, format)
    closing = _build_closing(tone)
    cta = _build_cta(tone, purpose_label)

    # --- Assemble sections dict ---
    sections = {
        "opening": opening,
        "body": body,
        "closing": closing,
        "cta": cta,
    }

    full_text = f"{opening}\n\n{body}\n\n{cta}\n\n{closing}"
    wc = len(full_text.split())

    # --- Pre-send checklist ---
    checklist = _pre_send_checklist(context)

    # --- Text analysis (computed from context) ---
    computed_formality = _compute_formality(context)
    fs = flesch_score(context)

    text_analysis = {
        "formality_score": computed_formality,
        "readability": {
            "flesch_score": fs,
            "flesch_grade": flesch_grade(fs),
        },
        "tone_words": _analyze_tone_words(context),
        "sentence_stats": _sentence_length_stats(context),
        "structure": _analyze_email_structure(context),
    }

    return {
        "subject_suggestions": subjects,
        "sections": sections,
        "tone_guide": {
            "formality": profile["formality"],
            "vocabulary": profile["vocabulary"],
            "avoid": profile["avoid"],
        },
        "formality_score": computed_formality,
        "text_analysis": text_analysis,
        "pre_send_checklist": checklist,
        "word_count": wc,
        "estimated_read_time": f"{max(1, round(wc / 238))} min",
    }


# ---------------------------------------------------------------------------
# Tone profiles
# ---------------------------------------------------------------------------

_TONE_PROFILES: dict[str, dict] = {
    "professional": {
        "formality": "high",
        "formality_score": 85,
        "vocabulary": ["please", "regarding", "as discussed", "at your convenience", "I would appreciate"],
        "avoid": ["hey", "gonna", "wanna", "ASAP", "FYI"],
        "greeting": "Dear",
        "sign_off": "Best regards,",
    },
    "friendly": {
        "formality": "medium",
        "formality_score": 50,
        "vocabulary": ["thanks", "looking forward", "great to hear", "sounds good", "happy to"],
        "avoid": ["pursuant to", "herewith", "kindly be advised", "per our last email"],
        "greeting": "Hi",
        "sign_off": "Cheers,",
    },
    "assertive": {
        "formality": "high",
        "formality_score": 80,
        "vocabulary": ["require", "expect", "by [date]", "non-negotiable", "must"],
        "avoid": ["maybe", "if possible", "no rush", "whenever you can", "sorry to bother"],
        "greeting": "Dear",
        "sign_off": "Regards,",
    },
    "apologetic": {
        "formality": "high",
        "formality_score": 75,
        "vocabulary": ["sincerely apologize", "understand your frustration", "take full responsibility", "corrective steps", "will ensure"],
        "avoid": ["but", "however", "in our defense", "it was not our fault", "you should have"],
        "greeting": "Dear",
        "sign_off": "With sincere apologies,",
    },
    "congratulatory": {
        "formality": "medium",
        "formality_score": 55,
        "vocabulary": ["congratulations", "well-deserved", "thrilled", "proud", "outstanding achievement"],
        "avoid": ["about time", "finally", "took long enough", "not bad"],
        "greeting": "Dear",
        "sign_off": "Warm regards,",
    },
}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_field(text: str, pattern: str) -> str | None:
    """Extract the first capture group matching *pattern* in *text*."""
    m = re.search(pattern, text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def _extract_key_points(text: str) -> list[str]:
    """Pull bullet-style key points or sentences from the context."""
    # Try numbered or bulleted items first
    bullets = re.findall(r'(?:^|\n)\s*[\-\*\d\.]+\s*(.+)', text)
    if bullets:
        return [b.strip() for b in bullets[:6]]
    # Fall back to sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    # Filter out very short fragments
    points = [s.strip() for s in sentences if len(s.split()) >= 3]
    return points[:6]


def _summarize(text: str, max_words: int = 10) -> str:
    """Return the first *max_words* words of text as a summary."""
    words = text.split()[:max_words]
    summary = " ".join(words)
    if len(text.split()) > max_words:
        summary += "..."
    return summary


def _generate_subjects(purpose: str, tone: str) -> list[str]:
    """Generate 3 subject line options based on purpose and tone."""
    purpose_clean = purpose.rstrip(".")
    if tone == "assertive":
        return [
            f"Action Required: {purpose_clean}",
            f"Urgent: {purpose_clean}",
            f"Follow-Up Needed — {purpose_clean}",
        ]
    if tone == "apologetic":
        return [
            f"Our Apologies Regarding {purpose_clean}",
            f"Following Up — {purpose_clean}",
            f"We Want to Make This Right — {purpose_clean}",
        ]
    if tone == "congratulatory":
        return [
            f"Congratulations — {purpose_clean}",
            f"Well Deserved! {purpose_clean}",
            f"Celebrating {purpose_clean}",
        ]
    if tone == "friendly":
        return [
            f"Quick Note: {purpose_clean}",
            f"Hey! Re: {purpose_clean}",
            f"Touching Base — {purpose_clean}",
        ]
    # professional (default)
    return [
        f"Regarding {purpose_clean}",
        f"Re: {purpose_clean}",
        f"Follow-Up: {purpose_clean}",
    ]


def _build_opening(tone: str, recipient: str, purpose: str) -> str:
    profile = _TONE_PROFILES[tone]
    greeting = profile["greeting"]
    openers = {
        "professional": f"{greeting} {recipient},\n\nI am writing to you regarding {purpose}.",
        "friendly": f"{greeting} {recipient},\n\nHope you're doing well! I wanted to reach out about {purpose}.",
        "assertive": f"{greeting} {recipient},\n\nI am writing to address {purpose} and request your immediate attention.",
        "apologetic": f"{greeting} {recipient},\n\nThank you for bringing this to our attention. I sincerely apologize regarding {purpose}.",
        "congratulatory": f"{greeting} {recipient},\n\nI wanted to take a moment to congratulate you on {purpose}!",
    }
    return openers.get(tone, openers["professional"])


def _build_body(tone: str, purpose: str, key_points: list[str], fmt: str) -> str:
    if fmt == "brief":
        if key_points:
            return f"Key point: {key_points[0]}"
        return f"[Provide the main message about {purpose} here.]"

    lines: list[str] = []
    if key_points:
        lines.append("Here are the key points I would like to address:\n")
        for i, point in enumerate(key_points, 1):
            lines.append(f"  {i}. {point}")
    else:
        lines.append(f"[Paragraph 1: Provide context about {purpose}.]")
        lines.append("\n[Paragraph 2: Detail the key information or request.]")

    if fmt == "detailed":
        lines.append(f"\n[Additional context: Provide background information about {purpose}.]")
        lines.append("[Supporting details: Include data, references, or examples.]")
        lines.append("[Timeline: Mention any relevant dates or deadlines.]")

    return "\n".join(lines)


def _build_closing(tone: str) -> str:
    profile = _TONE_PROFILES[tone]
    sign_off = profile["sign_off"]
    closings = {
        "professional": f"Thank you for your time and consideration.\n\n{sign_off}\n[Your Name]",
        "friendly": f"Thanks so much — looking forward to hearing from you!\n\n{sign_off}\n[Your Name]",
        "assertive": f"I expect a response by [deadline]. Thank you for your prompt attention.\n\n{sign_off}\n[Your Name]",
        "apologetic": f"We are committed to making this right and will keep you updated on our progress.\n\n{sign_off}\n[Your Name]",
        "congratulatory": f"Once again, congratulations — this is truly well-deserved!\n\n{sign_off}\n[Your Name]",
    }
    return closings.get(tone, closings["professional"])


def _build_cta(tone: str, purpose: str) -> str:
    ctas = {
        "professional": "Could you please review and share your thoughts at your earliest convenience?",
        "friendly": "Would love to hear your thoughts — let me know when you have a moment!",
        "assertive": "Please confirm receipt and provide your response by [deadline].",
        "apologetic": "Please let us know how we can further assist you to resolve this matter.",
        "congratulatory": "I would love to hear about your plans — let's catch up soon!",
    }
    return ctas.get(tone, ctas["professional"])


def _compute_formality(text: str) -> float:
    """Compute real formality score from context text."""
    return _formality_score(text)


def _analyze_tone_words(text: str) -> dict:
    """Count positive/negative/neutral word ratios."""
    _POSITIVE = [
        "great", "excellent", "happy", "pleased", "thank", "appreciate",
        "wonderful", "fantastic", "good", "amazing", "love", "enjoy",
        "thrilled", "delighted", "perfect", "outstanding", "brilliant",
    ]
    _NEGATIVE = [
        "unfortunately", "sorry", "problem", "issue", "concerned",
        "disappointed", "frustrated", "difficult", "fail", "wrong",
        "bad", "poor", "terrible", "awful", "regret", "mistake",
    ]
    words = text.lower().split()
    total = len(words) if words else 1
    pos = count_pattern_matches(text, _POSITIVE)
    neg = count_pattern_matches(text, _NEGATIVE)
    pos_ratio = round(pos / total, 4)
    neg_ratio = round(neg / total, 4)
    if pos_ratio > neg_ratio:
        dominant = "positive"
    elif neg_ratio > pos_ratio:
        dominant = "negative"
    else:
        dominant = "neutral"
    return {
        "positive_ratio": pos_ratio,
        "negative_ratio": neg_ratio,
        "dominant": dominant,
    }


def _analyze_email_structure(text: str) -> dict:
    """Detect structural email components via pattern matching."""
    markers = {
        "has_greeting": ["dear", "hi ", "hello", "hey ", "good morning", "good afternoon"],
        "has_cta": [
            "please review", "let me know", "could you", "would you",
            "looking forward", "your thoughts", "please confirm", "please advise",
        ],
        "has_closing": [
            "regards", "sincerely", "cheers", "thanks", "best",
            "warm regards", "kind regards", "thank you",
        ],
        "has_signature": ["[your name]", "sent from", "---"],
    }
    found = text_structure_check(text, markers)
    present = sum(1 for v in found.values() if v)
    found["completeness"] = round(present / len(markers), 2)
    return found


def _sentence_length_stats(text: str) -> dict:
    """Compute sentence-level word count statistics."""
    sentences = sentence_tokenize(text)
    if not sentences:
        return {"mean": 0, "max": 0, "stdev": 0.0, "count": 0}
    lengths = [len(s.split()) for s in sentences]
    stats = basic_stats([float(x) for x in lengths])
    return {
        "mean": stats.get("mean", 0),
        "max": stats.get("max", 0),
        "stdev": stats.get("stdev", 0.0),
        "count": stats.get("count", 0),
    }


def _pre_send_checklist(context: str) -> list[str]:
    """Generate a context-aware pre-send checklist."""
    checklist = [
        "Verify recipient name and email address",
        "Review subject line for clarity",
        "Check greeting matches the relationship",
        "Ensure all key points are addressed",
        "Proofread for spelling and grammar",
    ]
    lower = context.lower()
    if any(w in lower for w in ("attach", "file", "document", "pdf", "report")):
        checklist.append("Verify all mentioned attachments are included")
    if any(w in lower for w in ("date", "deadline", "by", "due", "schedule")):
        checklist.append("Double-check all dates and deadlines")
    if any(w in lower for w in ("price", "cost", "amount", "budget", "fee", "payment")):
        checklist.append("Verify all monetary amounts and figures")
    if any(w in lower for w in ("link", "url", "website")):
        checklist.append("Test all links before sending")
    if any(w in lower for w in ("cc", "copy", "team", "group")):
        checklist.append("Confirm CC/BCC recipients are correct")
    checklist.append("Read the email aloud for tone and flow")
    return checklist
