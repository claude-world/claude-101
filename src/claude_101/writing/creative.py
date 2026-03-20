"""Creative writing structure tool — story beats, tension curves, and genre conventions."""

from __future__ import annotations

import re

from .._utils import word_count


def structure_story(
    genre: str = "general",
    elements: str = "",
    structure: str = "three-act",
    text: str = "",
) -> dict:
    """Generate a story structure with beats, tension curve, and templates.

    Args:
        genre: Story genre — general, fantasy, sci-fi, mystery, romance,
               thriller, horror, literary, comedy.
        elements: Free-text describing characters, setting, and conflict.
        structure: Narrative structure — three-act, heros-journey, five-act.
        text: Optional existing story text to analyze for pacing,
              dialogue ratio, and scene transitions.
    """
    genre = genre.lower().strip()
    structure = structure.lower().strip().replace("'", "").replace("\u2019", "")

    if genre not in _GENRE_CONVENTIONS:
        genre = "general"
    if structure not in _STRUCTURES:
        structure = "three-act"

    total_words = 5000
    struct_spec = _STRUCTURES[structure]

    # --- Build story beats ---
    beats = _build_beats(struct_spec, total_words)

    # --- Generate tension curve ---
    tension_curve = _build_tension_curve(struct_spec)

    # --- Character arc template ---
    character_arc = _character_arc_template(genre)

    # --- Genre conventions ---
    conventions = _GENRE_CONVENTIONS[genre]

    # --- Parse elements ---
    elements_parsed = _parse_elements(elements)

    result = {
        "genre": genre,
        "structure": structure,
        "beats": beats,
        "tension_curve": tension_curve,
        "total_target_words": total_words,
        "character_arc_template": character_arc,
        "genre_conventions": conventions,
        "elements_parsed": elements_parsed,
    }

    if text.strip():
        result["text_analysis"] = {
            "word_count": word_count(text),
            "pacing": _analyze_pacing(text, beats),
            "dialogue": _analyze_dialogue_ratio(text),
            "scene_transitions": _detect_scene_transitions(text),
            "character_mentions": _analyze_character_mentions(text, elements_parsed),
        }

    return result


# ---------------------------------------------------------------------------
# Structure definitions
# ---------------------------------------------------------------------------

_STRUCTURES: dict[str, dict] = {
    "three-act": {
        "name": "Three-Act Structure",
        "beats": [
            {"name": "Opening Image", "description": "Establish the protagonist's ordinary world and current state.", "percentage": 2, "tension_level": 1},
            {"name": "Setup", "description": "Introduce characters, setting, tone, and the protagonist's flaw or desire.", "percentage": 8, "tension_level": 2},
            {"name": "Catalyst", "description": "An inciting event disrupts the status quo and demands a response.", "percentage": 3, "tension_level": 4},
            {"name": "Debate", "description": "The protagonist hesitates — should they accept the call to action?", "percentage": 7, "tension_level": 3},
            {"name": "Break Into Act 2", "description": "The protagonist commits to the journey and enters a new world.", "percentage": 5, "tension_level": 5},
            {"name": "B-Story Introduction", "description": "A subplot (often a relationship) begins that mirrors the main theme.", "percentage": 5, "tension_level": 3},
            {"name": "Fun & Games", "description": "The premise is explored — the 'promise of the premise' delivers.", "percentage": 15, "tension_level": 5},
            {"name": "Midpoint", "description": "A false victory or false defeat raises the stakes significantly.", "percentage": 5, "tension_level": 7},
            {"name": "Bad Guys Close In", "description": "External pressures increase and internal doubts grow.", "percentage": 15, "tension_level": 7},
            {"name": "All Is Lost", "description": "The protagonist's lowest point — it seems impossible to win.", "percentage": 5, "tension_level": 9},
            {"name": "Dark Night of the Soul", "description": "The protagonist confronts their deepest fears and flaws.", "percentage": 5, "tension_level": 8},
            {"name": "Break Into Act 3", "description": "A new insight or revelation inspires the final push.", "percentage": 3, "tension_level": 7},
            {"name": "Finale", "description": "The protagonist faces the final challenge using lessons learned.", "percentage": 17, "tension_level": 10},
            {"name": "Final Image", "description": "Show how the protagonist and their world have changed.", "percentage": 5, "tension_level": 3},
        ],
    },
    "heros-journey": {
        "name": "Hero's Journey (12 Stages)",
        "beats": [
            {"name": "Ordinary World", "description": "The hero's normal life before the adventure begins.", "percentage": 8, "tension_level": 1},
            {"name": "Call to Adventure", "description": "A challenge, quest, or problem disrupts the hero's world.", "percentage": 5, "tension_level": 3},
            {"name": "Refusal of the Call", "description": "The hero hesitates or refuses due to fear or obligation.", "percentage": 5, "tension_level": 2},
            {"name": "Meeting the Mentor", "description": "A wise figure provides guidance, tools, or confidence.", "percentage": 5, "tension_level": 3},
            {"name": "Crossing the Threshold", "description": "The hero commits and enters the unfamiliar special world.", "percentage": 7, "tension_level": 5},
            {"name": "Tests, Allies, Enemies", "description": "The hero faces trials, makes allies, and confronts enemies.", "percentage": 15, "tension_level": 5},
            {"name": "Approach to the Inmost Cave", "description": "Preparation for the major ordeal — tension builds.", "percentage": 8, "tension_level": 7},
            {"name": "The Ordeal", "description": "The hero faces their greatest challenge and near-death experience.", "percentage": 10, "tension_level": 10},
            {"name": "Reward (Seizing the Sword)", "description": "The hero claims the prize after surviving the ordeal.", "percentage": 7, "tension_level": 6},
            {"name": "The Road Back", "description": "The hero begins the journey home but faces new dangers.", "percentage": 10, "tension_level": 7},
            {"name": "Resurrection", "description": "A final, climactic test where the hero is fundamentally transformed.", "percentage": 12, "tension_level": 9},
            {"name": "Return with the Elixir", "description": "The hero returns home transformed, bringing a gift or lesson.", "percentage": 8, "tension_level": 3},
        ],
    },
    "five-act": {
        "name": "Five-Act Structure (Freytag's Pyramid)",
        "beats": [
            {"name": "Exposition", "description": "Introduce the setting, characters, and initial situation.", "percentage": 15, "tension_level": 2},
            {"name": "Rising Action", "description": "Complications and conflicts escalate, building tension.", "percentage": 25, "tension_level": 5},
            {"name": "Climax", "description": "The turning point — the moment of highest tension and conflict.", "percentage": 15, "tension_level": 10},
            {"name": "Falling Action", "description": "The consequences of the climax unfold; conflicts begin to resolve.", "percentage": 25, "tension_level": 6},
            {"name": "Denouement", "description": "Final resolution — loose ends tied up, new equilibrium established.", "percentage": 20, "tension_level": 2},
        ],
    },
}


# ---------------------------------------------------------------------------
# Genre conventions
# ---------------------------------------------------------------------------

_GENRE_CONVENTIONS: dict[str, list[str]] = {
    "general": [
        "Focus on character development and relatable themes",
        "Balance internal and external conflict",
        "Use concrete sensory details to ground the reader",
        "Ensure the protagonist changes by the end",
    ],
    "fantasy": [
        "Establish clear magic system rules early",
        "World-building should serve the story, not overwhelm it",
        "Include a map or geography relevant to the quest",
        "The chosen-one trope works best with a twist or subversion",
        "Balance exposition of lore with action and dialogue",
    ],
    "sci-fi": [
        "Ground speculative elements in plausible science or logic",
        "Use technology as a lens to explore human themes",
        "Show societal consequences of technological change",
        "Avoid info-dumping — reveal world rules through action",
        "Consider the ethical implications of your premise",
    ],
    "mystery": [
        "Plant clues fairly — the reader should be able to solve it",
        "Include at least 3 red herrings that logically mislead",
        "The detective's method should match their character",
        "Reveal the solution through deduction, not coincidence",
        "Every suspect needs means, motive, and opportunity",
    ],
    "romance": [
        "The central relationship must drive the plot",
        "Create genuine obstacles, not manufactured misunderstandings",
        "Both characters must change and grow",
        "Include a satisfying emotional payoff (HEA or HFN)",
        "Chemistry should be shown through action, not just told",
    ],
    "thriller": [
        "Open with an immediate hook — danger or mystery",
        "Maintain a relentless pace with short chapters and cliffhangers",
        "The stakes must be clear, personal, and escalating",
        "Include a ticking clock to create urgency",
        "The antagonist should be as competent as the protagonist",
    ],
    "horror": [
        "Build dread through atmosphere before delivering scares",
        "The unknown is scarier than the revealed monster",
        "Isolate the protagonist — remove sources of help",
        "Use sensory details to create visceral unease",
        "The best horror explores real human fears metaphorically",
    ],
    "literary": [
        "Theme and character take priority over plot",
        "Use language with precision and intention",
        "Ambiguity and open endings are acceptable and expected",
        "Subtext should carry as much meaning as dialogue",
        "Every scene should resonate on multiple levels",
    ],
    "comedy": [
        "Establish the comedic tone in the first scene",
        "Use the rule of three: setup, reinforcement, subversion",
        "Character flaws are the engine of comedy",
        "Timing matters — delay or accelerate for effect",
        "The best comedy has an emotional core beneath the laughs",
    ],
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_beats(spec: dict, total_words: int) -> list[dict]:
    """Build beats with word targets from the structure spec."""
    beats: list[dict] = []
    for b in spec["beats"]:
        target_words = round(total_words * b["percentage"] / 100)
        beats.append({
            "name": b["name"],
            "description": b["description"],
            "percentage": b["percentage"],
            "target_words": target_words,
            "tension_level": b["tension_level"],
        })
    return beats


def _build_tension_curve(spec: dict) -> list[dict]:
    """Generate tension curve data points from beats.

    Produces smooth data points at every 5% position, interpolating
    between beat tension levels.
    """
    # Build raw position -> tension mapping from beats
    raw_points: list[tuple[float, int]] = []
    cumulative = 0.0
    for b in spec["beats"]:
        midpoint = cumulative + b["percentage"] / 2.0
        raw_points.append((midpoint, b["tension_level"]))
        cumulative += b["percentage"]

    if not raw_points:
        return []

    # Generate smooth curve via linear interpolation at every 5%
    curve: list[dict] = []
    for pos in range(0, 101, 5):
        tension = _interpolate(raw_points, float(pos))
        curve.append({"position": pos, "tension": round(tension, 1)})

    return curve


def _interpolate(points: list[tuple[float, int]], x: float) -> float:
    """Linear interpolation of tension at position x."""
    if not points:
        return 0.0
    if x <= points[0][0]:
        return float(points[0][1])
    if x >= points[-1][0]:
        return float(points[-1][1])

    # Find surrounding points
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if x0 <= x <= x1:
            if x1 == x0:
                return float(y0)
            t = (x - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)

    return float(points[-1][1])


def _character_arc_template(genre: str) -> dict:
    """Generate a character arc template appropriate for the genre."""
    arcs = {
        "general": {
            "beginning": "The protagonist has a clear flaw or unmet desire that limits them. They exist in a comfortable but incomplete status quo.",
            "middle": "Through escalating challenges, the protagonist is forced to confront their flaw. They try old approaches that fail, pushing them toward growth.",
            "end": "The protagonist integrates the lesson learned, overcomes their flaw, and achieves (or meaningfully fails to achieve) their goal as a changed person.",
        },
        "fantasy": {
            "beginning": "An ordinary person in an extraordinary world (or vice versa) discovers a hidden power or destiny they are unprepared for.",
            "middle": "Through quests and trials, they learn to wield their power while confronting the moral weight of their choices.",
            "end": "They accept their role and sacrifice something personal for the greater good, emerging as a true hero.",
        },
        "sci-fi": {
            "beginning": "The protagonist exists in a world shaped by technology or scientific change, either benefiting from or oppressed by it.",
            "middle": "A discovery or crisis forces them to question the system. They must choose between comfort and truth.",
            "end": "They either reshape the world through their understanding or accept a hard truth about humanity's relationship with technology.",
        },
        "mystery": {
            "beginning": "The detective encounters a puzzle that seems straightforward but hints at deeper complexity.",
            "middle": "Each clue leads to new questions. The detective's assumptions are challenged, and the case becomes personal.",
            "end": "The truth is revealed — often implicating someone unexpected — and the detective is changed by what they've learned about human nature.",
        },
        "romance": {
            "beginning": "Two people meet under circumstances that create both attraction and conflict. Each has emotional walls built from past experiences.",
            "middle": "Growing intimacy is tested by internal fears and external obstacles. Vulnerability and trust are built and broken.",
            "end": "Both characters face their deepest fear about love, choose vulnerability, and commit to each other as changed people.",
        },
        "thriller": {
            "beginning": "An ordinary person is thrust into danger by circumstance or a past mistake catching up with them.",
            "middle": "Survival demands they develop new skills and make morally complex decisions under extreme pressure.",
            "end": "They confront the source of danger directly, using everything they've learned, and emerge tougher but scarred.",
        },
        "horror": {
            "beginning": "The protagonist enters a situation that seems safe but carries subtle wrongness they ignore or cannot perceive.",
            "middle": "The threat reveals itself gradually. Attempts to escape or fight back fail, forcing the protagonist to face their deepest fear.",
            "end": "The protagonist either overcomes the horror through self-understanding or is consumed by it — serving as a warning.",
        },
        "literary": {
            "beginning": "The protagonist exists in a state of quiet dissatisfaction, aware of something missing but unable to name it.",
            "middle": "A series of events — often small and internal — forces a reckoning with identity, relationships, or mortality.",
            "end": "The protagonist arrives at a new understanding of themselves, which may or may not bring resolution. The insight is the reward.",
        },
        "comedy": {
            "beginning": "The protagonist's key flaw (vanity, stubbornness, obliviousness) is established through humorous situations.",
            "middle": "Their flaw creates escalating chaos. Every attempt to fix things makes them worse in increasingly absurd ways.",
            "end": "A moment of humility and self-awareness breaks the cycle. The protagonist embraces their imperfection and finds genuine connection.",
        },
    }
    return arcs.get(genre, arcs["general"])


def _analyze_pacing(text: str, beats: list[dict]) -> list[dict]:
    """Analyze pacing by comparing actual vs target word counts per beat."""
    if not text.strip() or not beats:
        return []
    total_words = word_count(text)
    if total_words == 0:
        return []

    # Split text into segments proportional to beat percentages
    words_list = text.split()
    result: list[dict] = []
    offset = 0
    for beat in beats:
        target = beat.get("target_words", 0)
        pct = beat.get("percentage", 0)
        segment_len = round(total_words * pct / 100) if pct else target
        segment_len = max(1, segment_len)
        actual = min(segment_len, len(words_list) - offset)
        actual = max(0, actual)
        deviation = actual - target if target else 0
        result.append({
            "beat": beat.get("name", ""),
            "target_words": target,
            "actual_words": actual,
            "deviation": deviation,
            "pacing": "on_track" if abs(deviation) < target * 0.2 else (
                "slow" if deviation > 0 else "fast"
            ) if target else "unknown",
        })
        offset += actual
    return result


def _analyze_dialogue_ratio(text: str) -> dict:
    """Analyze dialogue proportion in the text."""
    if not text.strip():
        return {"dialogue_words": 0, "total_words": 0, "ratio": 0.0}

    # Match text inside quotes (double or single)
    dialogue_matches = re.findall(r'["\u201c]([^"\u201d]*)["\u201d]', text)
    dialogue_matches += re.findall(r"'([^']*)'", text)

    dialogue_word_count = sum(len(m.split()) for m in dialogue_matches)
    total = word_count(text)
    ratio = round(dialogue_word_count / total, 4) if total else 0.0

    return {
        "dialogue_words": dialogue_word_count,
        "total_words": total,
        "ratio": ratio,
        "assessment": (
            "heavy_dialogue" if ratio > 0.5 else
            "balanced" if ratio > 0.2 else
            "narrative_heavy"
        ),
    }


def _detect_scene_transitions(text: str) -> dict:
    """Detect scene breaks and transitions."""
    if not text.strip():
        return {"count": 0, "avg_scene_words": 0}

    # Scene break patterns
    breaks = re.findall(r'(?:\n\s*\n\s*\n|\n\s*\*\s*\*\s*\*\s*\n|\n\s*---\s*\n|\n\s*#)', text)
    # Time/location transition phrases
    time_phrases = re.findall(
        r'\b(?:later that|the next|hours later|days later|meanwhile|'
        r'the following|that evening|that night|the next morning|'
        r'across town|back at|elsewhere|at the same time)\b',
        text, re.IGNORECASE,
    )
    total_transitions = len(breaks) + len(time_phrases)
    scenes = total_transitions + 1
    total = word_count(text)
    avg_scene = round(total / scenes) if scenes else total

    return {
        "count": total_transitions,
        "break_markers": len(breaks),
        "time_location_phrases": len(time_phrases),
        "avg_scene_words": avg_scene,
    }


def _analyze_character_mentions(text: str, elements_parsed: dict) -> dict:
    """Count character name mentions to compute screen-time distribution."""
    characters = elements_parsed.get("characters", [])
    if not characters or not text.strip():
        return {}

    mentions: dict[str, int] = {}
    for name in characters:
        count = len(re.findall(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE))
        mentions[name] = count

    total_mentions = sum(mentions.values())
    distribution: dict[str, float] = {}
    if total_mentions > 0:
        distribution = {
            name: round(c / total_mentions, 4) for name, c in mentions.items()
        }

    return {
        "mentions": mentions,
        "total_mentions": total_mentions,
        "distribution": distribution,
    }


def _parse_elements(elements: str) -> dict:
    """Parse free-text elements for characters, setting, and conflict."""
    if not elements.strip():
        return {"characters": [], "setting": "", "conflict": ""}

    characters: list[str] = []
    setting = ""
    conflict = ""

    # Look for explicit labels
    char_match = re.search(
        r'(?:characters?|protagonist|hero|heroine)\s*[:]\s*(.+?)(?:\n|$|;)',
        elements,
        re.IGNORECASE,
    )
    if char_match:
        raw = char_match.group(1)
        characters = [c.strip() for c in re.split(r'[,;]|\band\b', raw) if c.strip()]

    setting_match = re.search(
        r'(?:setting|location|place|world|where)\s*[:]\s*(.+?)(?:\n|$|;)',
        elements,
        re.IGNORECASE,
    )
    if setting_match:
        setting = setting_match.group(1).strip()

    conflict_match = re.search(
        r'(?:conflict|problem|challenge|struggle|theme)\s*[:]\s*(.+?)(?:\n|$|;)',
        elements,
        re.IGNORECASE,
    )
    if conflict_match:
        conflict = conflict_match.group(1).strip()

    # If no explicit labels, try to infer from free text
    if not characters:
        # Look for capitalized names (2+ consecutive capitalized words)
        name_candidates = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', elements)
        # Filter out common non-name words
        skip_words = {
            "The", "This", "That", "There", "They", "Then", "When", "Where",
            "What", "Which", "However", "Also", "Meanwhile", "After", "Before",
        }
        characters = [n for n in name_candidates if n not in skip_words][:5]

    if not setting:
        # Look for location-like phrases
        loc_match = re.search(
            r'\b(?:in|at|on)\s+((?:a\s+)?(?:the\s+)?[A-Za-z\s]{3,30}?(?:city|town|village|forest|castle|ship|space|world|kingdom|school|house|island|mountain))',
            elements,
            re.IGNORECASE,
        )
        if loc_match:
            setting = loc_match.group(1).strip()

    if not conflict:
        # Look for conflict-like phrases
        con_match = re.search(
            r'\b(?:must|against|versus|vs\.?|battle|fight|struggle|overcome|survive|escape|save|stop|prevent|discover)\s+(.+?)(?:\.|$)',
            elements,
            re.IGNORECASE,
        )
        if con_match:
            conflict = con_match.group(1).strip()

    return {
        "characters": characters,
        "setting": setting,
        "conflict": conflict,
    }
