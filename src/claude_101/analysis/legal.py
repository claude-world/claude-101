"""Legal document review tool — regex-based clause detection and risk analysis."""

from __future__ import annotations

import re

from .._utils import sentence_tokenize, word_count


# ── Clause patterns ────────────────────────────────────────────
# Each entry: (clause_type, regex_pattern, risk_level)
_CLAUSE_PATTERNS: list[tuple[str, str, str]] = [
    (
        "indemnification",
        r"\b(indemnif|hold\s+harmless|defend\s+and\s+indemnify)\b",
        "high",
    ),
    (
        "limitation_of_liability",
        r"\b(limit(ation)?\s+(of|on)\s+liability|maximum\s+liability|aggregate\s+liability)\b",
        "high",
    ),
    (
        "termination",
        r"\b(terminat(e|ion)|right\s+to\s+terminate|cancel(lation)?)\b",
        "medium",
    ),
    (
        "ip_assignment",
        r"\b(intellectual\s+property|ip\s+assign|work\s+(for|made\s+for)\s+hire|patent\s+assign|copyright\s+assign)\b",
        "high",
    ),
    (
        "confidentiality",
        r"\b(confidential(ity)?|non[\-\s]?disclosure|nda|proprietary\s+information)\b",
        "medium",
    ),
    (
        "non_compete",
        r"\b(non[\-\s]?compet(e|ition)|restrictive\s+covenant|compete\s+with)\b",
        "high",
    ),
    (
        "force_majeure",
        r"\b(force\s+majeure|act\s+of\s+god|unforeseeable\s+(event|circumstance)|beyond\s+.{0,20}control)\b",
        "low",
    ),
    (
        "governing_law",
        r"\b(governing\s+law|governed\s+by|choice\s+of\s+law|applicable\s+law|laws\s+of\s+the\s+state)\b",
        "low",
    ),
    (
        "arbitration",
        r"\b(arbitrat(ion|e|or)|binding\s+arbitration|dispute\s+resolution)\b",
        "medium",
    ),
    (
        "warranty",
        r"\b(warrant(y|ies)|as[\-\s]is|without\s+warranty|disclaim(s|ed)?\s+.{0,20}warrant)\b",
        "medium",
    ),
    (
        "data_protection",
        r"\b(data\s+protect(ion)?|gdpr|personal\s+data|privacy|data\s+processing|data\s+breach)\b",
        "high",
    ),
    (
        "payment_terms",
        r"\b(payment\s+terms?|net\s+\d+|due\s+(upon|within)|invoice|late\s+(fee|payment|charge))\b",
        "medium",
    ),
    (
        "auto_renewal",
        r"\b(auto[\-\s]?renew(al)?|automatic(ally)?\s+renew|evergreen)\b",
        "medium",
    ),
    (
        "assignment",
        r"\b(assign(ment|able)?|transfer\s+(of\s+)?(this|the)\s+(agreement|contract)|successor)\b",
        "low",
    ),
    (
        "amendment",
        r"\b(amend(ment|ed)?|modif(y|ication)|written\s+consent|mutual\s+agreement\s+.{0,15}modif)\b",
        "low",
    ),
    (
        "severability",
        r"\b(severab(ility|le)|invalid\s+.{0,30}remain|unenforceable\s+.{0,30}provision)\b",
        "low",
    ),
    (
        "entire_agreement",
        r"\b(entire\s+agreement|whole\s+agreement|supersede|merge(r|s)?\s+clause)\b",
        "low",
    ),
    (
        "notice",
        r"\b(notice(s)?\s+(shall|must|should|will)\s+be|written\s+notice|deliver(y|ed)?\s+of\s+notice)\b",
        "low",
    ),
    (
        "survival",
        r"\b(surviv(e|al)|shall\s+survive|obligations\s+.{0,20}surviv)\b",
        "low",
    ),
    (
        "representations",
        r"\b(represent(s|ation)?(\s+and\s+warrant(y|ies)?)?|hereby\s+represents)\b",
        "medium",
    ),
]

# Compiled patterns for performance
_COMPILED_PATTERNS = [
    (clause_type, re.compile(pattern, re.IGNORECASE), risk)
    for clause_type, pattern, risk in _CLAUSE_PATTERNS
]

# Standard clauses expected per document type
_EXPECTED_CLAUSES: dict[str, set[str]] = {
    "contract": {
        "termination",
        "governing_law",
        "confidentiality",
        "limitation_of_liability",
        "indemnification",
        "warranty",
        "payment_terms",
        "amendment",
        "severability",
        "entire_agreement",
        "notice",
        "assignment",
    },
    "nda": {
        "confidentiality",
        "termination",
        "governing_law",
        "severability",
        "entire_agreement",
        "notice",
        "representations",
        "survival",
    },
    "employment": {
        "termination",
        "confidentiality",
        "ip_assignment",
        "non_compete",
        "governing_law",
        "severability",
        "representations",
        "payment_terms",
        "entire_agreement",
    },
    "saas": {
        "termination",
        "governing_law",
        "limitation_of_liability",
        "warranty",
        "data_protection",
        "payment_terms",
        "auto_renewal",
        "confidentiality",
        "indemnification",
        "severability",
    },
    "partnership": {
        "termination",
        "governing_law",
        "confidentiality",
        "ip_assignment",
        "indemnification",
        "amendment",
        "severability",
        "entire_agreement",
        "arbitration",
        "assignment",
    },
}

# Legal jargon terms for complexity scoring
_LEGAL_JARGON = {
    "herein",
    "hereto",
    "hereof",
    "hereby",
    "hereinafter",
    "whereas",
    "thereof",
    "therein",
    "thereto",
    "forthwith",
    "notwithstanding",
    "aforementioned",
    "heretofore",
    "aforesaid",
    "pursuant",
    "provision",
    "stipulate",
    "covenant",
    "indemnify",
    "arbitration",
    "jurisdiction",
    "enforceable",
    "severability",
    "waiver",
    "breach",
    "tort",
    "liable",
    "liability",
    "damages",
    "remedy",
    "remedies",
    "clause",
    "subsection",
    "subparagraph",
    "representations",
    "warranties",
    "obligations",
    "successor",
    "assigns",
    "successors",
    "counterparts",
    "execution",
    "governing",
    "venue",
    "injunctive",
    "equitable",
    "irrevocable",
    "perpetual",
    "exclusive",
    "non-exclusive",
    "royalty-free",
    "sublicense",
}


def _find_line_number(text: str, match_start: int) -> int:
    """Approximate line number for a match position."""
    return text[:match_start].count("\n") + 1


def review_legal_document(text: str, doc_type: str = "contract") -> dict:
    """Review a legal document for clause detection, risk, and completeness.

    Args:
        text: Full text of the legal document.
        doc_type: Document type — "contract", "nda", "employment", "saas", "partnership".

    Returns:
        Dictionary with clause analysis, missing clauses, complexity, and recommendations.
    """
    wc = word_count(text)
    sentences = sentence_tokenize(text)

    # ── Clause detection ────────────────────────────────────────
    found_types: set[str] = set()
    clauses_found: list[dict] = []

    for clause_type, pattern, risk_level in _COMPILED_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            found_types.add(clause_type)
            # Take the first match for the snippet
            m = matches[0]
            start = max(0, m.start() - 50)
            end = min(len(text), m.end() + 100)
            snippet = text[start:end].replace("\n", " ").strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."

            clauses_found.append(
                {
                    "type": clause_type,
                    "text_snippet": snippet,
                    "line_approx": _find_line_number(text, m.start()),
                    "risk_level": risk_level,
                    "occurrences": len(matches),
                }
            )

    # Sort by risk level (high first) then by position
    risk_order = {"high": 0, "medium": 1, "low": 2}
    clauses_found.sort(
        key=lambda c: (risk_order.get(c["risk_level"], 3), c["line_approx"])
    )

    # ── Missing clauses ─────────────────────────────────────────
    doc_key = doc_type.lower()
    expected = _EXPECTED_CLAUSES.get(doc_key, _EXPECTED_CLAUSES["contract"])
    missing_clauses = sorted(expected - found_types)

    # ── Complexity score ────────────────────────────────────────
    # Based on: average sentence length and legal jargon density
    avg_sentence_length = len(text.split()) / len(sentences) if sentences else 0

    words_lower = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    jargon_count = sum(1 for w in words_lower if w in _LEGAL_JARGON)
    jargon_density = (
        round(jargon_count / len(words_lower) * 100, 2) if words_lower else 0.0
    )

    # Complexity: 0-10 scale
    # Sentence length component: 0-5 (30+ words = max)
    sent_complexity = min(5.0, avg_sentence_length / 6.0)
    # Jargon component: 0-5 (5%+ jargon = max)
    jargon_complexity = min(5.0, jargon_density)
    complexity_score = round(sent_complexity + jargon_complexity, 1)

    # ── Recommendations ─────────────────────────────────────────
    recommendations: list[str] = []

    if missing_clauses:
        recommendations.append(f"Add missing clauses: {', '.join(missing_clauses)}")

    high_risk = [c for c in clauses_found if c["risk_level"] == "high"]
    if high_risk:
        types = ", ".join(c["type"] for c in high_risk)
        recommendations.append(f"Review high-risk clauses carefully: {types}")

    if (
        "indemnification" in found_types
        and "limitation_of_liability" not in found_types
    ):
        recommendations.append(
            "Indemnification clause found without liability cap — consider adding limitation of liability"
        )

    if "auto_renewal" in found_types and "termination" not in found_types:
        recommendations.append(
            "Auto-renewal present without clear termination clause — risk of unwanted renewal"
        )

    if "ip_assignment" in found_types and "confidentiality" not in found_types:
        recommendations.append(
            "IP assignment without confidentiality clause — consider adding NDA provisions"
        )

    if complexity_score > 7:
        recommendations.append(
            "Document complexity is very high — consider simplifying language for clarity"
        )

    if "data_protection" not in found_types and doc_key in ("saas", "contract"):
        recommendations.append(
            "No data protection clause detected — consider adding GDPR/privacy provisions"
        )

    if not recommendations:
        recommendations.append(
            "Document appears well-structured with standard clauses present"
        )

    return {
        "doc_type": doc_type,
        "word_count": wc,
        "complexity_score": complexity_score,
        "clauses_found": clauses_found,
        "missing_clauses": missing_clauses,
        "jargon_density": jargon_density,
        "recommendations": recommendations,
    }
