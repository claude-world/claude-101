"""Social media content formatter — platform-aware splitting and analysis."""

from __future__ import annotations

import re
import unicodedata


def format_social_content(
    text: str,
    platform: str = "twitter",
    include_hashtags: bool = True,
) -> dict:
    """Format text for a specific social media platform.

    Args:
        text: The raw content to format.
        platform: One of twitter, linkedin, threads, instagram, facebook.
        include_hashtags: Whether to extract/suggest hashtags.
    """
    platform = platform.lower().strip()
    if platform not in _PLATFORM_LIMITS:
        platform = "twitter"

    char_limit = _PLATFORM_LIMITS[platform]

    # --- Extract existing hashtags ---
    existing_hashtags = re.findall(r'#(\w+)', text)

    # --- Build formatted text ---
    formatted_text = _format_for_platform(text, platform, char_limit)

    # --- Chunk if needed ---
    chunks = _chunk_text(formatted_text, char_limit)
    within_limit = len(chunks) <= 1

    # --- Hashtags ---
    if include_hashtags:
        hashtags = _build_hashtags(text, existing_hashtags, platform)
    else:
        hashtags = existing_hashtags

    # --- Engagement signals ---
    engagement = _analyze_engagement(formatted_text)

    # --- Platform tips ---
    tips = _platform_tips(platform, formatted_text, engagement)

    char_count = len(formatted_text)

    return {
        "platform": platform,
        "formatted_text": formatted_text,
        "char_count": char_count,
        "char_limit": char_limit,
        "within_limit": within_limit,
        "chunks": chunks,
        "hashtags": hashtags,
        "engagement_signals": engagement,
        "platform_tips": tips,
    }


# ---------------------------------------------------------------------------
# Platform limits
# ---------------------------------------------------------------------------

_PLATFORM_LIMITS: dict[str, int] = {
    "twitter": 280,
    "linkedin": 3000,
    "threads": 500,
    "instagram": 2200,
    "facebook": 63206,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _format_for_platform(text: str, platform: str, limit: int) -> str:
    """Clean and format text for the target platform."""
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text.strip())
    text = re.sub(r'[ \t]+', ' ', text)

    if platform == "twitter":
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'#{1,6}\s+', '', text)
        # Do NOT truncate — let chunking handle overflow for thread-style posts

    elif platform == "linkedin":
        # LinkedIn supports basic formatting; keep line breaks
        # Add hook spacing (blank line after first line)
        lines = text.split('\n', 1)
        if len(lines) == 2 and not lines[1].startswith('\n'):
            text = lines[0] + '\n\n' + lines[1]

    elif platform == "threads":
        # Similar to Twitter but slightly more room
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        # Do NOT truncate — let chunking handle overflow for thread-style posts

    elif platform == "instagram":
        # Instagram captions can be longer; keep hashtags at end
        # Move hashtags to the bottom with spacing
        hashtags_in_text = re.findall(r'#\w+', text)
        if hashtags_in_text:
            text_clean = re.sub(r'\s*#\w+', '', text).strip()
            hashtag_block = ' '.join(hashtags_in_text)
            text = f"{text_clean}\n\n.\n.\n.\n{hashtag_block}"

    # facebook: generous limit, minimal formatting needed
    return text.strip()


def _truncate_at_word(text: str, max_len: int) -> str:
    """Truncate text at a word boundary, not exceeding max_len."""
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    # Find the last space to avoid cutting mid-word
    last_space = truncated.rfind(' ')
    if last_space > max_len * 0.5:
        return truncated[:last_space]
    return truncated


def _chunk_text(text: str, limit: int) -> list[str]:
    """Split text into chunks that fit within the character limit.

    Splits at sentence boundaries first, then at word boundaries.
    """
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    current_chunk = ""
    for sentence in sentences:
        candidate = f"{current_chunk} {sentence}".strip() if current_chunk else sentence
        if len(candidate) <= limit:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If a single sentence exceeds the limit, split at word boundary
            if len(sentence) > limit:
                words = sentence.split()
                current_chunk = ""
                for word in words:
                    candidate = f"{current_chunk} {word}".strip() if current_chunk else word
                    if len(candidate) <= limit:
                        current_chunk = candidate
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = word
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    # Add thread numbering for multi-chunk posts
    if len(chunks) > 1:
        total = len(chunks)
        chunks = [f"({i+1}/{total}) {chunk}" for i, chunk in enumerate(chunks)]

    return chunks


def _build_hashtags(
    text: str,
    existing: list[str],
    platform: str,
) -> list[str]:
    """Build a hashtag list: keep existing + suggest new from content."""
    hashtags = list(existing)
    seen = {h.lower() for h in hashtags}

    # Extract meaningful words (3+ chars, not stopwords)
    stopwords = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can",
        "had", "her", "was", "one", "our", "out", "has", "his", "how",
        "its", "may", "new", "now", "old", "see", "way", "who", "did",
        "get", "let", "say", "she", "too", "use", "with", "this", "that",
        "from", "have", "been", "will", "more", "when", "very", "just",
        "about", "into", "than", "them", "then", "what", "your",
    }
    words = re.findall(r'\b[A-Za-z]{4,}\b', text)
    word_freq: dict[str, int] = {}
    for w in words:
        wl = w.lower()
        if wl not in stopwords:
            word_freq[wl] = word_freq.get(wl, 0) + 1

    # Sort by frequency and pick top candidates
    candidates = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    # Platform-specific hashtag count targets
    max_tags = {"twitter": 3, "linkedin": 5, "threads": 5, "instagram": 15, "facebook": 3}
    target = max_tags.get(platform, 5)

    for word, _ in candidates:
        if len(hashtags) >= target:
            break
        if word not in seen:
            seen.add(word)
            hashtags.append(word)

    return hashtags


def _analyze_engagement(text: str) -> dict:
    """Analyze engagement signals in the formatted text."""
    has_question = bool(re.search(r'\?', text))
    has_cta = bool(re.search(
        r'\b(?:click|learn|discover|check\s+out|sign\s+up|subscribe|follow|'
        r'share|comment|reply|tag|join|try|download|read\s+more|visit|grab|get)\b',
        text,
        re.IGNORECASE,
    ))
    # Detect emoji by checking for characters in common emoji Unicode ranges
    has_emoji = bool(re.search(
        r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001FA00-\U0001FA6F'
        r'\U0001FA70-\U0001FAFF\U00002702-\U000027B0]',
        text,
    ))

    # Assess hook strength based on the first line
    first_line = text.split('\n')[0].strip()
    hook_strength = _assess_hook(first_line)

    return {
        "has_question": has_question,
        "has_cta": has_cta,
        "has_emoji": has_emoji,
        "hook_strength": hook_strength,
    }


def _assess_hook(first_line: str) -> str:
    """Rate the hook strength of the opening line."""
    strong_signals = 0

    # Starts with a number or statistic
    if re.match(r'^\d', first_line):
        strong_signals += 1

    # Contains a question
    if '?' in first_line:
        strong_signals += 1

    # Uses power words
    power_words = r'\b(?:secret|surprising|proven|ultimate|essential|'
    power_words += r'mistake|myth|truth|hack|game.?changer|shocking|'
    power_words += r'unpopular|controversial|nobody|everyone)\b'
    if re.search(power_words, first_line, re.IGNORECASE):
        strong_signals += 1

    # Short and punchy (under 60 chars)
    if len(first_line) < 60:
        strong_signals += 1

    # Contains emoji
    if re.search(r'[\U0001F300-\U0001F9FF]', first_line):
        strong_signals += 1

    if strong_signals >= 3:
        return "strong"
    if strong_signals >= 1:
        return "medium"
    return "weak"


def _platform_tips(platform: str, text: str, engagement: dict) -> list[str]:
    """Generate platform-specific optimization tips."""
    tips: list[str] = []

    base_tips = {
        "twitter": [
            "Front-load the hook — first 50 chars are most visible in feeds",
            "Use line breaks to create visual breathing room",
            "Quote tweets get 2-3x more engagement than plain retweets",
        ],
        "linkedin": [
            "First 2 lines appear above the 'see more' fold — make them count",
            "Posts with 1-2 line paragraphs get more engagement",
            "Personal stories outperform corporate announcements",
            "Tag relevant people to boost distribution",
        ],
        "threads": [
            "Keep it conversational — Threads rewards authentic voice",
            "Reply to your own post with additional context or links",
            "Avoid putting URLs in the main post — use a reply instead",
        ],
        "instagram": [
            "First line is the hook — it shows in feeds before 'more'",
            "Use 5-10 relevant hashtags (not 30) for best reach",
            "Separate hashtags from caption with line breaks",
            "Include a clear CTA (save, share, comment)",
        ],
        "facebook": [
            "Posts with 40-80 characters get the highest engagement",
            "Native video gets 10x more reach than link posts",
            "Ask questions to boost comment engagement",
        ],
    }

    tips.extend(base_tips.get(platform, []))

    # Dynamic tips based on content analysis
    if not engagement["has_question"]:
        tips.append("Consider adding a question to encourage comments")
    if not engagement["has_cta"]:
        tips.append("Add a call-to-action to tell readers what to do next")
    if engagement["hook_strength"] == "weak":
        tips.append("Strengthen your opening line — try leading with a bold claim, number, or question")
    if len(text) < 50 and platform in ("linkedin", "instagram"):
        tips.append("Consider adding more context — longer posts often perform better on this platform")

    return tips
