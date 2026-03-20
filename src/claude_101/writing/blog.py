"""Blog post drafting tool — outlines, SEO fields, and style guides."""

from __future__ import annotations

import re


def draft_blog_post(
    topic: str,
    target_words: int = 1500,
    style: str = "educational",
) -> dict:
    """Generate a structured blog post outline with SEO metadata.

    Args:
        topic: The blog post topic or working title.
        target_words: Target word count for the full post.
        style: One of educational, opinion, tutorial, listicle, case-study.
    """
    style = style.lower().strip()
    if style not in _STYLE_PROFILES:
        style = "educational"

    profile = _STYLE_PROFILES[style]
    target_words = max(300, target_words)

    # --- Build outline sections ---
    sections = _build_sections(topic, target_words, style, profile)

    # --- Heading hierarchy ---
    heading_hierarchy = _build_heading_hierarchy(topic, sections)

    # --- SEO fields ---
    seo_fields = _build_seo_fields(topic, style)

    # --- Reading time ---
    reading_time_minutes = round(target_words / 238, 1)

    # --- Content analysis ---
    topic_analysis = _extract_topic_keywords(topic)
    readability_target = _compute_readability_target(style)
    heading_validation = _validate_heading_hierarchy(heading_hierarchy)
    content_gaps = _analyze_content_gaps(topic, style)

    return {
        "topic": topic,
        "style": style,
        "target_words": target_words,
        "outline": sections,
        "heading_hierarchy": heading_hierarchy,
        "seo_fields": seo_fields,
        "reading_time_minutes": reading_time_minutes,
        "style_guide": {
            "voice": profile["voice"],
            "sentence_length": profile["sentence_length"],
            "examples_per_section": profile["examples_per_section"],
        },
        "topic_analysis": topic_analysis,
        "readability_target": readability_target,
        "heading_validation": heading_validation,
        "content_gaps": content_gaps,
    }


# ---------------------------------------------------------------------------
# Style profiles
# ---------------------------------------------------------------------------

_STYLE_PROFILES: dict[str, dict] = {
    "educational": {
        "voice": "Authoritative yet approachable; explain concepts clearly with concrete examples.",
        "sentence_length": "Mix short (8-12 words) and medium (15-20 words) sentences. Avoid long compound sentences.",
        "examples_per_section": 2,
        "section_templates": [
            (
                "Introduction",
                10,
                [
                    "Hook the reader with a relatable problem",
                    "State what they will learn",
                    "Preview the key takeaways",
                ],
            ),
            (
                "Background & Context",
                15,
                [
                    "Define key terms",
                    "Explain why this topic matters",
                    "Provide necessary background",
                ],
            ),
            (
                "Core Concept 1",
                20,
                [
                    "Explain the first major idea",
                    "Provide a concrete example",
                    "Connect to the reader's experience",
                ],
            ),
            (
                "Core Concept 2",
                20,
                [
                    "Build on the previous section",
                    "Introduce the next key idea",
                    "Include a real-world application",
                ],
            ),
            (
                "Practical Application",
                15,
                [
                    "Show how to apply the concepts",
                    "Step-by-step walkthrough",
                    "Common mistakes to avoid",
                ],
            ),
            (
                "Conclusion",
                20,
                [
                    "Summarize the key takeaways",
                    "Provide next steps for the reader",
                    "End with a thought-provoking question or CTA",
                ],
            ),
        ],
    },
    "opinion": {
        "voice": "Confident and personal; use first person and take a clear stance.",
        "sentence_length": "Vary between punchy short sentences and longer persuasive ones. Use rhetorical questions.",
        "examples_per_section": 1,
        "section_templates": [
            (
                "Introduction",
                10,
                [
                    "Open with a bold statement or controversial take",
                    "State your thesis clearly",
                    "Preview your argument",
                ],
            ),
            (
                "The Current State",
                15,
                [
                    "Describe the status quo",
                    "Identify what most people believe",
                    "Set up the contrast with your view",
                ],
            ),
            (
                "My Argument",
                25,
                [
                    "Present your main argument with evidence",
                    "Address the strongest counter-argument",
                    "Provide supporting data or examples",
                ],
            ),
            (
                "Why This Matters",
                20,
                [
                    "Explain the stakes",
                    "Show real-world consequences",
                    "Connect to the reader's interests",
                ],
            ),
            (
                "What Should Change",
                10,
                [
                    "Propose concrete actions",
                    "Call readers to reconsider their stance",
                    "End with a memorable closing thought",
                ],
            ),
            (
                "Conclusion",
                20,
                [
                    "Restate thesis in a new way",
                    "Final call to action",
                    "Leave the reader thinking",
                ],
            ),
        ],
    },
    "tutorial": {
        "voice": "Clear and instructional; use second person (you). Be precise and step-oriented.",
        "sentence_length": "Short and direct (8-15 words). Use imperative mood for instructions.",
        "examples_per_section": 3,
        "section_templates": [
            (
                "Introduction",
                8,
                [
                    "State what the reader will build or achieve",
                    "List prerequisites",
                    "Estimate time to complete",
                ],
            ),
            (
                "Setup & Prerequisites",
                12,
                [
                    "List required tools and versions",
                    "Installation commands",
                    "Verify setup is working",
                ],
            ),
            (
                "Step 1: Foundation",
                20,
                [
                    "Walk through the first major step",
                    "Include code/commands",
                    "Show expected output",
                ],
            ),
            (
                "Step 2: Core Implementation",
                25,
                [
                    "Build the main functionality",
                    "Explain each decision",
                    "Include code/commands",
                ],
            ),
            (
                "Step 3: Polish & Edge Cases",
                15,
                [
                    "Handle errors and edge cases",
                    "Add finishing touches",
                    "Test the result",
                ],
            ),
            (
                "Conclusion & Next Steps",
                20,
                [
                    "Summarize what was built",
                    "Suggest extensions and improvements",
                    "Link to further resources",
                ],
            ),
        ],
    },
    "listicle": {
        "voice": "Energetic and scannable; use numbered items with clear headers.",
        "sentence_length": "Short and punchy (8-12 words). Each item should stand alone.",
        "examples_per_section": 1,
        "section_templates": [
            (
                "Introduction",
                8,
                [
                    "Hook with a compelling statistic or question",
                    "Explain why this list matters",
                    "Preview the number of items",
                ],
            ),
            (
                "Items 1-3",
                20,
                [
                    "Present items with clear subheadings",
                    "One key insight per item",
                    "Include a quick tip or example",
                ],
            ),
            (
                "Items 4-6",
                20,
                [
                    "Continue the list with variety",
                    "Mix formats: tip, tool, technique",
                    "Keep each item self-contained",
                ],
            ),
            (
                "Items 7-10",
                25,
                [
                    "Present the remaining items",
                    "Save a strong one for the end",
                    "Vary the depth per item",
                ],
            ),
            (
                "Bonus Tips",
                7,
                [
                    "Add 1-2 unexpected extras",
                    "Make the reader feel they got more than expected",
                ],
            ),
            (
                "Conclusion",
                20,
                [
                    "Summarize the top 3 picks",
                    "Invite the reader to share their own",
                    "End with a CTA",
                ],
            ),
        ],
    },
    "case-study": {
        "voice": "Analytical and evidence-based; use third person. Focus on data and outcomes.",
        "sentence_length": "Medium (12-18 words). Use precise language and avoid hedging.",
        "examples_per_section": 2,
        "section_templates": [
            (
                "Introduction",
                8,
                [
                    "Introduce the company or scenario",
                    "State the challenge",
                    "Preview the result",
                ],
            ),
            (
                "Background & Challenge",
                15,
                [
                    "Detail the context and constraints",
                    "Quantify the problem",
                    "Explain previous attempts",
                ],
            ),
            (
                "Approach & Solution",
                25,
                [
                    "Describe the strategy chosen",
                    "Explain why this approach was selected",
                    "Detail the implementation steps",
                ],
            ),
            (
                "Results & Metrics",
                25,
                [
                    "Present quantified outcomes",
                    "Before vs. after comparison",
                    "Include supporting data",
                ],
            ),
            (
                "Lessons Learned",
                10,
                ["What worked well", "What could be improved", "Unexpected findings"],
            ),
            (
                "Conclusion & Takeaways",
                17,
                [
                    "Summarize the key results",
                    "Generalize lessons for the reader",
                    "CTA or next steps",
                ],
            ),
        ],
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_sections(
    topic: str,
    target_words: int,
    style: str,
    profile: dict,
) -> list[dict]:
    """Build the outline sections with word counts and key points."""
    templates = profile["section_templates"]
    total_pct = sum(t[1] for t in templates)

    sections: list[dict] = []
    for name_template, pct, key_points in templates:
        # Personalize section names with topic keywords
        name = _personalize_section_name(name_template, topic, style)
        section_words = round(target_words * pct / total_pct)
        actual_pct = round(pct / total_pct * 100)
        sections.append(
            {
                "section": name,
                "target_words": section_words,
                "percentage": actual_pct,
                "key_points": key_points,
            }
        )
    return sections


def _personalize_section_name(template: str, topic: str, style: str) -> str:
    """Replace generic section names with topic-aware names."""
    # Extract a short topic phrase (first 5 words)
    topic_short = " ".join(topic.split()[:5])
    replacements = {
        "Core Concept 1": f"Understanding {topic_short}",
        "Core Concept 2": f"Advanced {topic_short} Techniques",
        "Practical Application": f"Applying {topic_short} in Practice",
        "My Argument": f"Why {topic_short} Matters",
        "The Current State": f"The State of {topic_short} Today",
        "What Should Change": f"A Better Path for {topic_short}",
        "Step 1: Foundation": f"Step 1: Setting Up {topic_short}",
        "Step 2: Core Implementation": f"Step 2: Building {topic_short}",
        "Step 3: Polish & Edge Cases": f"Step 3: Polishing {topic_short}",
        "Items 1-3": "Top Picks (1-3)",
        "Items 4-6": "Strong Contenders (4-6)",
        "Items 7-10": "Hidden Gems (7-10)",
        "Approach & Solution": f"The {topic_short} Solution",
        "Results & Metrics": f"Results: Measuring {topic_short} Impact",
    }
    return replacements.get(template, template)


def _build_heading_hierarchy(topic: str, sections: list[dict]) -> list[str]:
    """Build a heading hierarchy from the outline."""
    hierarchy = [f"h1: {topic}"]
    for sec in sections:
        hierarchy.append(f"  h2: {sec['section']}")
        for kp in sec.get("key_points", [])[:2]:
            hierarchy.append(f"    h3: {kp}")
    return hierarchy


def _extract_topic_keywords(topic: str) -> dict:
    """Extract keywords and bigrams from the topic."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", topic.lower())
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "into",
        "about",
        "that",
        "this",
        "how",
    }
    filtered = [w for w in words if w not in stopwords]

    # Unigrams
    unigrams = list(dict.fromkeys(filtered))  # deduplicate, preserve order

    # Bigrams from the topic
    bigrams: list[str] = []
    for i in range(len(filtered) - 1):
        bigrams.append(f"{filtered[i]} {filtered[i + 1]}")

    return {
        "primary_keywords": unigrams[:5],
        "bigrams": bigrams[:5],
        "keyword_count": len(unigrams),
    }


def _compute_readability_target(style: str) -> dict:
    """Return target Flesch readability range for the writing style."""
    targets = {
        "educational": {"min": 50, "max": 70, "label": "Standard to Fairly Easy"},
        "opinion": {"min": 40, "max": 65, "label": "Fairly Difficult to Standard"},
        "tutorial": {"min": 60, "max": 80, "label": "Standard to Easy"},
        "listicle": {"min": 60, "max": 80, "label": "Standard to Easy"},
        "case-study": {"min": 40, "max": 60, "label": "Fairly Difficult to Standard"},
    }
    return targets.get(style, targets["educational"])


def _validate_heading_hierarchy(hierarchy: list[str]) -> dict:
    """Validate heading structure for SEO and accessibility."""
    issues: list[str] = []
    h1_count = 0
    prev_level = 0

    for h in hierarchy:
        stripped = h.strip()
        # Detect heading level
        level = 0
        if stripped.startswith("h1:"):
            level = 1
            h1_count += 1
        elif stripped.startswith("h2:"):
            level = 2
        elif stripped.startswith("h3:"):
            level = 3
        elif stripped.startswith("h4:"):
            level = 4

        if level == 0:
            continue

        # Check for skipped levels
        if prev_level > 0 and level > prev_level + 1:
            issues.append(f"Skipped heading level: h{prev_level} -> h{level}")
        prev_level = level

    if h1_count == 0:
        issues.append("Missing h1 heading")
    elif h1_count > 1:
        issues.append(f"Multiple h1 headings ({h1_count}) — should have exactly one")

    return {
        "valid": len(issues) == 0,
        "h1_count": h1_count,
        "issues": issues,
    }


def _analyze_content_gaps(topic: str, style: str) -> list[str]:
    """Identify potential content gaps based on topic and style."""
    topic_lower = topic.lower()
    gaps: list[str] = []

    # Style-specific expected subtopics
    style_expectations = {
        "educational": [
            "definition",
            "example",
            "comparison",
            "best practice",
            "common mistake",
        ],
        "opinion": ["counter-argument", "evidence", "data", "personal experience"],
        "tutorial": [
            "prerequisites",
            "step-by-step",
            "expected output",
            "troubleshooting",
        ],
        "listicle": ["ranking criteria", "pro/con for each item", "recommendation"],
        "case-study": ["baseline metrics", "methodology", "results", "lessons learned"],
    }

    expected = style_expectations.get(style, style_expectations["educational"])
    for subtopic in expected:
        if subtopic.lower() not in topic_lower:
            gaps.append(f"Consider adding: {subtopic}")

    return gaps[:5]


def _build_seo_fields(topic: str, style: str) -> dict:
    """Generate SEO metadata from topic."""
    # Focus keyword: longest meaningful phrase (2-4 words)
    words = topic.lower().split()
    if len(words) >= 4:
        focus_keyword = " ".join(words[:4])
    elif len(words) >= 2:
        focus_keyword = " ".join(words[:3])
    else:
        focus_keyword = topic.lower()

    # Slug
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    if len(slug) > 60:
        slug = slug[:60].rsplit("-", 1)[0]

    # Title tag (50-60 chars)
    title_tag = topic
    if len(title_tag) > 60:
        title_tag = title_tag[:57] + "..."

    # Meta description (120-160 chars)
    style_intros = {
        "educational": f"Learn everything about {topic.lower()}.",
        "opinion": f"A fresh perspective on {topic.lower()}.",
        "tutorial": f"Step-by-step guide to {topic.lower()}.",
        "listicle": f"The best {topic.lower()} you need to know.",
        "case-study": f"How {topic.lower()} drove real results.",
    }
    meta_base = style_intros.get(style, f"Explore {topic.lower()}.")
    meta_description = (
        f"{meta_base} Practical insights, examples, and actionable takeaways."
    )
    if len(meta_description) > 160:
        meta_description = meta_description[:157] + "..."

    return {
        "title_tag": title_tag,
        "meta_description": meta_description,
        "focus_keyword": focus_keyword,
        "slug": slug,
    }
