"""Customer support response builder — issue classification and response scaffolding."""

from __future__ import annotations

import re

from .._utils import flesch_score, count_pattern_matches


# ---------------------------------------------------------------------------
# Classification keywords
# ---------------------------------------------------------------------------

_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "billing": [
        "charge", "bill", "refund", "invoice", "payment", "subscription",
        "cancel", "overcharge", "double charge", "credit card", "pricing",
        "discount", "coupon", "receipt", "transaction", "renewal", "fee",
    ],
    "technical": [
        "error", "bug", "crash", "not working", "broken", "slow", "timeout",
        "502", "503", "404", "login", "password", "reset", "install",
        "update", "upgrade", "compatibility", "display", "loading", "freeze",
    ],
    "complaint": [
        "angry", "frustrated", "terrible", "worst", "unacceptable",
        "disappointed", "disgusted", "horrible", "awful", "pathetic",
        "outraged", "furious", "ridiculous", "incompetent", "lawsuit",
    ],
    "feature_request": [
        "feature", "suggestion", "would be nice", "wish", "could you add",
        "request", "enhancement", "improve", "idea", "option to",
        "ability to", "please add", "missing feature", "need support for",
    ],
    "account": [
        "account", "profile", "settings", "delete account", "deactivate",
        "merge", "transfer", "permissions", "role", "access", "locked out",
        "verification", "two-factor", "2fa", "username", "email change",
    ],
    "shipping": [
        "shipping", "delivery", "tracking", "package", "order", "lost",
        "damaged", "late", "estimated", "courier", "return", "exchange",
        "warehouse", "dispatch", "customs", "address change",
    ],
}

_SEVERITY_ESCALATORS: list[tuple[str, str]] = [
    # (keyword, severity_if_found)
    ("lawsuit", "critical"),
    ("legal", "critical"),
    ("data breach", "critical"),
    ("security", "critical"),
    ("all data lost", "critical"),
    ("cannot access", "high"),
    ("completely broken", "high"),
    ("production down", "critical"),
    ("outage", "critical"),
    ("urgent", "high"),
    ("immediately", "high"),
    ("asap", "high"),
    ("refund", "high"),
    ("angry", "high"),
    ("furious", "critical"),
    ("unacceptable", "high"),
    ("frustrated", "medium"),
    ("disappointed", "medium"),
    ("confused", "low"),
    ("question", "low"),
    ("wondering", "low"),
    ("curious", "low"),
]

_SENTIMENT_KEYWORDS: dict[str, list[str]] = {
    "positive": [
        "love", "great", "amazing", "excellent", "thank", "appreciate",
        "wonderful", "fantastic", "happy", "pleased", "impressed",
    ],
    "negative": [
        "bad", "poor", "disappointed", "unhappy", "not satisfied",
        "problem", "issue", "trouble", "difficult", "confusing",
    ],
    "angry": [
        "angry", "furious", "outraged", "disgusted", "terrible",
        "worst", "unacceptable", "pathetic", "incompetent", "ridiculous",
        "lawsuit", "never again", "scam",
    ],
}


# ---------------------------------------------------------------------------
# Tone profiles
# ---------------------------------------------------------------------------

_TONE_PROFILES: dict[str, dict] = {
    "empathetic": {
        "greeting_style": "warm",
        "vocabulary": ["understand", "appreciate", "hear you", "important to us", "right away"],
        "avoid": ["policy states", "unfortunately", "as per", "not possible"],
    },
    "professional": {
        "greeting_style": "formal",
        "vocabulary": ["regarding", "pleased to assist", "at your convenience", "resolution"],
        "avoid": ["hey", "no worries", "gonna", "stuff"],
    },
    "technical": {
        "greeting_style": "direct",
        "vocabulary": ["diagnose", "root cause", "workaround", "reproduce", "resolution steps"],
        "avoid": ["feelings", "sorry to hear", "must be frustrating"],
    },
    "casual": {
        "greeting_style": "friendly",
        "vocabulary": ["got it", "totally", "for sure", "happy to help", "no worries"],
        "avoid": ["pursuant to", "herewith", "kindly be advised"],
    },
}


# ---------------------------------------------------------------------------
# Channel configuration
# ---------------------------------------------------------------------------

_CHANNEL_CONFIG: dict[str, dict] = {
    "email": {
        "max_length": "500-800 words",
        "response_time_target": "Within 4 business hours",
        "format_tips": [
            "Use clear subject line that references the issue",
            "Open with empathy, close with next steps",
            "Use bullet points for action items",
            "Include case/ticket number for reference",
            "Attach relevant screenshots or documentation",
        ],
    },
    "chat": {
        "max_length": "100-200 words per message",
        "response_time_target": "Within 2 minutes",
        "format_tips": [
            "Keep messages short and scannable",
            "Use one message per topic — avoid walls of text",
            "Confirm understanding before providing solutions",
            "Use canned responses for common issues",
            "Provide links rather than lengthy explanations",
        ],
    },
    "phone": {
        "max_length": "5-10 minute call script",
        "response_time_target": "Answer within 30 seconds",
        "format_tips": [
            "Greet with your name and department",
            "Listen actively before offering solutions",
            "Summarize the issue back to the customer",
            "Speak clearly and at a moderate pace",
            "Confirm resolution before ending the call",
        ],
    },
    "social": {
        "max_length": "140-280 characters (public), DM for details",
        "response_time_target": "Within 1 hour during business hours",
        "format_tips": [
            "Acknowledge publicly, resolve privately",
            "Never share account details in public replies",
            "Use the brand voice consistently",
            "Move complex issues to DM or email quickly",
            "Thank them for reaching out publicly",
        ],
    },
}


# ---------------------------------------------------------------------------
# Empathy phrase banks by severity
# ---------------------------------------------------------------------------

_EMPATHY_PHRASES: dict[str, list[str]] = {
    "low": [
        "Thank you for reaching out — happy to help with this.",
        "Great question! Let me look into that for you.",
        "I appreciate you bringing this to our attention.",
    ],
    "medium": [
        "I understand this can be frustrating, and I want to help resolve it quickly.",
        "Thank you for your patience while we work on this.",
        "I can see why this would be concerning — let me take care of it.",
        "I appreciate you taking the time to let us know about this issue.",
    ],
    "high": [
        "I completely understand your frustration, and I take this very seriously.",
        "I sincerely apologize for the inconvenience this has caused you.",
        "This is not the experience we want you to have, and I am committed to making it right.",
        "I hear you, and I want you to know that resolving this is my top priority right now.",
    ],
    "critical": [
        "I am deeply sorry for this experience. This is being treated as our highest priority.",
        "I understand how serious this situation is, and I am escalating this immediately.",
        "You have every right to be upset. I am personally ensuring this gets resolved as fast as possible.",
        "I take full responsibility for this issue and am involving our senior team right now.",
        "This is completely unacceptable and I want you to know we are treating this with the urgency it deserves.",
    ],
}


# ---------------------------------------------------------------------------
# Classification functions
# ---------------------------------------------------------------------------

def _classify_category(issue: str) -> str:
    """Classify issue into a category based on keyword matching."""
    lower = issue.lower()
    scores: dict[str, int] = {}

    for category, keywords in _CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in lower)
        scores[category] = score

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    if scores[best] == 0:
        return "general"
    return best


def _classify_severity(issue: str) -> str:
    """Classify issue severity from language intensity."""
    lower = issue.lower()

    for keyword, severity in _SEVERITY_ESCALATORS:
        if keyword in lower:
            return severity

    # Word count heuristic: longer issues tend to be more serious
    word_count = len(issue.split())
    if word_count > 100:
        return "medium"

    return "low"


def _classify_sentiment(issue: str) -> str:
    """Classify sentiment from keyword analysis."""
    lower = issue.lower()

    scores: dict[str, int] = {}
    for sentiment, keywords in _SENTIMENT_KEYWORDS.items():
        scores[sentiment] = sum(1 for kw in keywords if kw in lower)

    # Check angry first (highest intensity)
    if scores.get("angry", 0) > 0:
        return "angry"
    if scores.get("negative", 0) > scores.get("positive", 0):
        return "negative"
    if scores.get("positive", 0) > 0:
        return "positive"
    return "neutral"


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def _build_greeting(tone: str, channel: str, severity: str) -> str:
    """Build an appropriate greeting."""
    greetings: dict[str, dict[str, str]] = {
        "empathetic": {
            "email": "Hello,\n\nThank you for reaching out to us.",
            "chat": "Hi there! Thanks for contacting us.",
            "phone": "Thank you for calling. My name is [Agent Name], and I am here to help.",
            "social": "Hi! Thank you for reaching out.",
        },
        "professional": {
            "email": "Dear Customer,\n\nThank you for contacting our support team.",
            "chat": "Hello. Thank you for contacting support.",
            "phone": "Good [morning/afternoon]. This is [Agent Name] from [Company] support.",
            "social": "Hello, thank you for contacting us.",
        },
        "technical": {
            "email": "Hello,\n\nThank you for reporting this issue.",
            "chat": "Hi. I see you have a technical issue — let me help.",
            "phone": "Hello, this is [Agent Name] from technical support.",
            "social": "Hi — we see your report and are looking into it.",
        },
        "casual": {
            "email": "Hey there!\n\nThanks for getting in touch.",
            "chat": "Hey! How can I help?",
            "phone": "Hi there! This is [Agent Name]. How can I help you today?",
            "social": "Hey! Thanks for reaching out to us.",
        },
    }

    tone_greetings = greetings.get(tone, greetings["empathetic"])
    return tone_greetings.get(channel, tone_greetings["email"])


def _build_acknowledgment(category: str, severity: str, tone: str) -> str:
    """Build an acknowledgment that reflects the category and severity."""
    ack_templates: dict[str, str] = {
        "billing": "I can see this is about a billing concern, and I want to make sure we get this sorted out for you.",
        "technical": "I understand you are experiencing a technical issue, and I want to help resolve it as quickly as possible.",
        "complaint": "I hear your concern and I take it very seriously. You deserve better, and I am here to make this right.",
        "feature_request": "Thank you for sharing this suggestion! We value feedback like this because it helps us improve.",
        "account": "I understand you need help with your account. Let me look into this for you right away.",
        "shipping": "I can see this is about your order, and I understand how important timely delivery is to you.",
        "general": "I understand your concern and I am here to help.",
    }

    ack = ack_templates.get(category, ack_templates["general"])

    if severity == "critical":
        ack += " I am treating this as a top priority."
    elif severity == "high":
        ack += " I am prioritizing this for a fast resolution."

    return ack


def _build_solution(category: str, severity: str) -> str:
    """Build solution scaffolding based on category."""
    solutions: dict[str, str] = {
        "billing": (
            "Here is what I can do to resolve this:\n\n"
            "1. [Review the specific charges/transaction in question]\n"
            "2. [Explain what happened or initiate the adjustment]\n"
            "3. [Confirm the resolution: refund amount, timeline, or corrected invoice]\n\n"
            "The [refund/credit/adjustment] should be reflected in your account within [X] business days."
        ),
        "technical": (
            "Let me help you troubleshoot this:\n\n"
            "1. [Step 1: Verify the current state of the issue]\n"
            "2. [Step 2: Attempt the most likely fix]\n"
            "3. [Step 3: Confirm the issue is resolved]\n\n"
            "If these steps do not resolve the issue, I will escalate to our engineering team for a deeper investigation."
        ),
        "complaint": (
            "I want to address your concerns directly:\n\n"
            "1. [Acknowledge the specific problem they experienced]\n"
            "2. [Explain what went wrong and take responsibility]\n"
            "3. [Detail the specific actions being taken to resolve it]\n"
            "4. [Offer appropriate compensation if applicable]\n\n"
            "I want to ensure this does not happen again, and I am [taking specific preventive action]."
        ),
        "feature_request": (
            "Thank you for this thoughtful suggestion. Here is what happens next:\n\n"
            "1. I have logged your request in our product feedback system\n"
            "2. Our product team reviews all feedback during sprint planning\n"
            "3. If this gains traction, you will be notified when it enters our roadmap\n\n"
            "In the meantime, [suggest any existing workaround or related feature]."
        ),
        "account": (
            "Let me help you with your account:\n\n"
            "1. [Verify identity: ask for verification details]\n"
            "2. [Perform the requested account action]\n"
            "3. [Confirm the change and provide any updated credentials]\n\n"
            "For security, [mention any additional verification steps or follow-up]."
        ),
        "shipping": (
            "Let me look into your order:\n\n"
            "1. [Check current order/tracking status]\n"
            "2. [Explain the situation: delay reason, current location, etc.]\n"
            "3. [Provide resolution: reship, refund, updated delivery estimate]\n\n"
            "You can track the updated status at [tracking link]."
        ),
        "general": (
            "Here is how I can help:\n\n"
            "1. [Identify the specific issue or question]\n"
            "2. [Provide the relevant information or solution]\n"
            "3. [Confirm that the issue is resolved]\n\n"
            "Please let me know if you need any additional assistance."
        ),
    }

    return solutions.get(category, solutions["general"])


def _build_next_steps(category: str, severity: str) -> str:
    """Build next steps based on category and severity."""
    steps: dict[str, str] = {
        "billing": "I will send you a confirmation email with the details of this adjustment. You should see the change reflected within 3-5 business days.",
        "technical": "If the issue persists after trying these steps, please reply with [screenshot/error log/steps to reproduce] and I will escalate to our engineering team.",
        "complaint": "I will personally follow up with you within 24 hours to confirm everything is resolved to your satisfaction.",
        "feature_request": "We will keep you updated on the status of this request. In the meantime, feel free to share any additional details or use cases.",
        "account": "Your account changes will take effect within [timeframe]. You will receive a confirmation email shortly.",
        "shipping": "You will receive an updated tracking notification by email. If the package does not arrive by [date], please contact us again.",
        "general": "If you have any other questions, do not hesitate to reach out. We are here to help.",
    }

    base = steps.get(category, steps["general"])

    if severity in ("critical", "high"):
        base += " I have also flagged this internally for additional review."

    return base


def _build_closing(tone: str, channel: str) -> str:
    """Build an appropriate closing."""
    closings: dict[str, dict[str, str]] = {
        "empathetic": {
            "email": "Thank you for your patience and understanding. We truly value your business.\n\nWarm regards,\n[Agent Name]",
            "chat": "Thank you for chatting with us! Is there anything else I can help with?",
            "phone": "Thank you for calling, and I appreciate your patience. Have a great day!",
            "social": "Thank you for reaching out! We are here if you need anything else.",
        },
        "professional": {
            "email": "Thank you for contacting us. Please do not hesitate to reach out if you need further assistance.\n\nBest regards,\n[Agent Name]",
            "chat": "Thank you for contacting support. Is there anything else I can assist with?",
            "phone": "Thank you for calling [Company] support. Have a good day.",
            "social": "Thank you for reaching out. We are always here to help.",
        },
        "technical": {
            "email": "If the issue recurs, please include the error logs and steps to reproduce. We are here to help.\n\nRegards,\n[Agent Name]",
            "chat": "Let me know if the issue persists after trying these steps.",
            "phone": "If the issue returns, call us back with the ticket number and we can continue from where we left off.",
            "social": "Please DM us the details and we will follow up.",
        },
        "casual": {
            "email": "Hope that helps! Hit me up if you need anything else.\n\nCheers,\n[Agent Name]",
            "chat": "Hope that helps! Anything else?",
            "phone": "Glad I could help! Have an awesome day!",
            "social": "Hope that helps! Let us know if you need anything else.",
        },
    }

    tone_closings = closings.get(tone, closings["empathetic"])
    return tone_closings.get(channel, tone_closings["email"])


def _build_escalation_criteria(category: str, severity: str) -> list[str]:
    """Generate escalation criteria based on category and severity."""
    base = [
        "Customer explicitly requests to speak with a manager",
        "Issue cannot be resolved with available tools or permissions",
        "Customer threatens legal action",
        "Same issue reported 3+ times by the same customer",
    ]

    category_specific: dict[str, list[str]] = {
        "billing": [
            "Disputed amount exceeds $500",
            "Suspected fraudulent transaction",
            "Customer requests account closure due to billing issue",
        ],
        "technical": [
            "Issue affects multiple customers (potential outage)",
            "Data loss or corruption reported",
            "Security vulnerability identified",
            "Issue persists after all documented troubleshooting steps",
        ],
        "complaint": [
            "Customer mentions social media or public review",
            "Pattern of complaints about the same issue from multiple customers",
            "Customer is a high-value or enterprise account",
        ],
        "shipping": [
            "Package is confirmed lost",
            "Damage exceeds $200 in value",
            "International shipment stuck in customs",
        ],
        "account": [
            "Suspected unauthorized access to the account",
            "Account involves sensitive or regulated data",
        ],
    }

    return base + category_specific.get(category, [])


def _build_follow_up_template(category: str, channel: str) -> str:
    """Generate a follow-up template."""
    templates: dict[str, str] = {
        "billing": (
            "Subject: Follow-up on your billing inquiry [Ticket #]\n\n"
            "Hi [Customer Name],\n\n"
            "I wanted to follow up on the billing matter we discussed on [date]. "
            "[Confirm resolution status: refund processed, invoice corrected, etc.]\n\n"
            "If you have any further questions about your account, please do not "
            "hesitate to reach out.\n\n"
            "Best regards,\n[Agent Name]"
        ),
        "technical": (
            "Subject: Follow-up on your technical issue [Ticket #]\n\n"
            "Hi [Customer Name],\n\n"
            "I am following up on the technical issue you reported on [date]. "
            "[Confirm fix status: resolved, patch deployed, workaround provided]\n\n"
            "If you experience any further issues, please reply to this email "
            "with your ticket number and we will prioritize it.\n\n"
            "Best regards,\n[Agent Name]"
        ),
        "complaint": (
            "Subject: Following up on your recent experience [Ticket #]\n\n"
            "Hi [Customer Name],\n\n"
            "I wanted to personally follow up regarding your experience on [date]. "
            "[Describe actions taken and improvements made]\n\n"
            "Your feedback has directly contributed to [specific change]. We truly "
            "value your business and hope to earn back your trust.\n\n"
            "Sincerely,\n[Agent Name]"
        ),
    }

    default = (
        "Subject: Follow-up on your support request [Ticket #]\n\n"
        "Hi [Customer Name],\n\n"
        "I wanted to check in regarding your inquiry on [date]. "
        "[Confirm status and resolution]\n\n"
        "Please let us know if there is anything else we can help with.\n\n"
        "Best regards,\n[Agent Name]"
    )

    return templates.get(category, default)


def _compute_escalation_risk(
    category: str, severity: str, sentiment: str, issue: str,
) -> dict:
    """Compute escalation risk score (0-100) from multiple signals."""
    severity_weights = {"low": 10, "medium": 30, "high": 60, "critical": 90}
    sentiment_weights = {"positive": 0, "neutral": 10, "negative": 40, "angry": 70}
    category_weights = {
        "billing": 30, "complaint": 40, "technical": 20,
        "account": 25, "shipping": 20, "feature_request": 5, "general": 10,
    }

    sev_score = severity_weights.get(severity, 20) * 0.4
    sent_score = sentiment_weights.get(sentiment, 10) * 0.3
    cat_score = category_weights.get(category, 10) * 0.2

    # Text signals (10%)
    escalation_phrases = [
        "lawyer", "lawsuit", "legal", "attorney", "bbb", "social media",
        "review", "never again", "cancel", "refund", "manager", "supervisor",
    ]
    text_hits = count_pattern_matches(issue, escalation_phrases)
    text_score = min(10.0, text_hits * 3.0)

    total = round(sev_score + sent_score + cat_score + text_score, 1)
    total = max(0.0, min(100.0, total))

    if total >= 70:
        level = "critical"
    elif total >= 50:
        level = "high"
    elif total >= 30:
        level = "medium"
    else:
        level = "low"

    return {"score": total, "level": level}


def _score_response_quality(response: str) -> dict:
    """Score a draft response for empathy, clarity, and actionability."""
    if not response.strip():
        return {"overall": 0, "empathy": 0, "readability": 0, "actionability": 0}

    # Empathy markers (0-30)
    empathy_words = [
        "understand", "sorry", "apologize", "appreciate", "hear you",
        "frustrating", "inconvenience", "right away", "priority",
    ]
    empathy_hits = count_pattern_matches(response, empathy_words)
    empathy = min(30, empathy_hits * 10)

    # Readability (0-30) — Flesch score mapped
    fs = flesch_score(response)
    readability = round(fs * 0.3, 1)

    # Actionability (0-30) — action verbs and concrete steps
    action_words = [
        "will", "can", "here is", "step", "follow", "click",
        "navigate", "contact", "send", "check", "update", "resolve",
    ]
    action_hits = count_pattern_matches(response, action_words)
    actionability = min(30, action_hits * 5)

    # No placeholder penalty (0-10)
    placeholder_patterns = ["[", "___", "xxx", "TODO"]
    placeholder_hits = count_pattern_matches(response, placeholder_patterns)
    no_placeholder = 10 if placeholder_hits == 0 else max(0, 10 - placeholder_hits * 3)

    overall = round(empathy + readability + actionability + no_placeholder, 1)
    return {
        "overall": min(100.0, overall),
        "empathy": empathy,
        "readability": round(readability, 1),
        "actionability": actionability,
    }


def _estimate_resolution_time(category: str, severity: str) -> dict:
    """Estimate resolution time based on category and severity."""
    base_hours = {
        "billing": 4, "technical": 8, "complaint": 2, "feature_request": 0,
        "account": 3, "shipping": 6, "general": 4,
    }
    severity_multiplier = {
        "low": 0.5, "medium": 1.0, "high": 1.5, "critical": 2.0,
    }
    base = base_hours.get(category, 4)
    mult = severity_multiplier.get(severity, 1.0)
    min_h = round(base * mult * 0.5, 1)
    max_h = round(base * mult * 1.5, 1)
    return {"min_hours": min_h, "max_hours": max_h}


def _compute_customer_effort(issue: str) -> dict:
    """Estimate customer effort based on issue signals."""
    words = issue.split()
    length_score = min(30, len(words))  # longer = more effort already spent

    repeat_indicators = [
        "again", "still", "already contacted", "second time", "third time",
        "keep getting", "keeps happening", "multiple times", "follow up",
        "following up", "last time", "previous",
    ]
    repeat_hits = count_pattern_matches(issue, repeat_indicators)
    repeat_score = min(40, repeat_hits * 15)

    frustration_words = [
        "frustrated", "exhausted", "tired", "wasted", "hours",
        "days", "weeks", "nobody", "no one", "impossible",
    ]
    frust_hits = count_pattern_matches(issue, frustration_words)
    frust_score = min(30, frust_hits * 10)

    total = min(100, length_score + repeat_score + frust_score)
    return {"score": total, "repeat_contact_signals": repeat_hits > 0}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_support_response(
    issue: str,
    channel: str = "email",
    tone: str = "empathetic",
    draft_response: str = "",
) -> dict:
    """Classify a support issue and scaffold a structured response.

    Args:
        issue: Customer's issue description or message.
        channel: Support channel — email, chat, phone, or social.
        tone: Response tone — empathetic, professional, technical, or casual.
        draft_response: Optional draft response text to score for quality.

    Returns:
        Dictionary with issue classification, response scaffold,
        empathy phrases, escalation criteria, channel guidelines,
        and follow-up template.
    """
    channel = channel.lower().strip()
    if channel not in _CHANNEL_CONFIG:
        channel = "email"

    tone = tone.lower().strip()
    if tone not in _TONE_PROFILES:
        tone = "empathetic"

    # ── Classify ─────────────────────────────────────────────────
    category = _classify_category(issue)
    severity = _classify_severity(issue)
    sentiment = _classify_sentiment(issue)

    # ── Build response scaffold ──────────────────────────────────
    greeting = _build_greeting(tone, channel, severity)
    acknowledgment = _build_acknowledgment(category, severity, tone)
    solution = _build_solution(category, severity)
    next_steps = _build_next_steps(category, severity)
    closing = _build_closing(tone, channel)

    # ── Select empathy phrases ───────────────────────────────────
    empathy_phrases = list(_EMPATHY_PHRASES.get(severity, _EMPATHY_PHRASES["low"]))

    # ── Escalation criteria ──────────────────────────────────────
    escalation_criteria = _build_escalation_criteria(category, severity)

    # ── Channel guidelines ───────────────────────────────────────
    channel_config = _CHANNEL_CONFIG[channel]

    # ── Follow-up template ───────────────────────────────────────
    follow_up = _build_follow_up_template(category, channel)

    # ── Computed risk & effort ────────────────────────────────────
    escalation_risk = _compute_escalation_risk(category, severity, sentiment, issue)
    resolution_estimate = _estimate_resolution_time(category, severity)
    customer_effort = _compute_customer_effort(issue)

    result: dict = {
        "issue_classification": {
            "category": category,
            "severity": severity,
            "sentiment": sentiment,
        },
        "response_scaffold": {
            "greeting": greeting,
            "acknowledgment": acknowledgment,
            "solution": solution,
            "next_steps": next_steps,
            "closing": closing,
        },
        "empathy_phrases": empathy_phrases,
        "escalation_risk": escalation_risk,
        "resolution_estimate": resolution_estimate,
        "customer_effort": customer_effort,
        "escalation_criteria": escalation_criteria,
        "channel_guidelines": {
            "max_length": channel_config["max_length"],
            "response_time_target": channel_config["response_time_target"],
            "format_tips": channel_config["format_tips"],
        },
        "follow_up_template": follow_up,
    }

    if draft_response.strip():
        result["response_quality"] = _score_response_quality(draft_response)

    return result
