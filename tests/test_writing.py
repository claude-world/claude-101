"""Tests for writing tools."""

from claude_101._utils import (
    formality_score,
    detect_named_entities,
    count_pattern_matches,
    text_structure_check,
)
from claude_101.writing.email import draft_email
from claude_101.writing.blog import draft_blog_post
from claude_101.writing.meeting import parse_meeting_notes
from claude_101.writing.social import format_social_content
from claude_101.writing.techdoc import scaffold_tech_doc
from claude_101.writing.creative import structure_story


class TestDraftEmail:
    def test_basic(self):
        r = draft_email("follow-up to client meeting about Q3 proposal")
        assert "sections" in r
        assert "subject_suggestions" in r
        assert len(r["subject_suggestions"]) >= 1
        assert "tone_guide" in r
        assert r["word_count"] > 0

    def test_tone_friendly(self):
        r = draft_email("thank colleague for help", tone="friendly")
        assert r["tone_guide"]["formality"] in ("low", "medium")

    def test_format_brief(self):
        r = draft_email("quick update", format="brief")
        assert "sections" in r

    def test_pre_send_checklist(self):
        r = draft_email("proposal to investor")
        assert len(r["pre_send_checklist"]) >= 3


class TestDraftBlogPost:
    def test_basic(self):
        r = draft_blog_post("Introduction to Machine Learning")
        assert r["topic"] == "Introduction to Machine Learning"
        assert r["target_words"] == 1500
        assert len(r["outline"]) >= 3
        assert r["reading_time_minutes"] > 0

    def test_custom_words(self):
        r = draft_blog_post("Short post", target_words=500)
        assert r["target_words"] == 500

    def test_seo_fields(self):
        r = draft_blog_post("SEO tips for developers")
        assert "seo_fields" in r
        assert "slug" in r["seo_fields"]

    def test_style_listicle(self):
        r = draft_blog_post("10 Python Tips", style="listicle")
        assert r["style"] == "listicle"


class TestParseMeetingNotes:
    def test_basic(self):
        notes = """
        Attendees: Alice, Bob, Charlie
        10:00 Alice presented the Q3 roadmap.
        TODO: Bob to update the timeline by Friday.
        DECISION: We agreed to use React for the frontend.
        ACTION: Charlie to set up the dev environment.
        """
        r = parse_meeting_notes(notes)
        assert r["metrics"]["attendee_count"] >= 1
        assert r["metrics"]["action_item_count"] >= 1
        assert r["metrics"]["decision_count"] >= 1

    def test_action_only_format(self):
        notes = "TODO: Alice to review PR\nACTION: Bob to deploy"
        r = parse_meeting_notes(notes, format="action-only")
        assert len(r["action_items"]) >= 1


class TestFormatSocialContent:
    def test_twitter(self):
        r = format_social_content(
            "Just shipped a new feature! Check it out.", platform="twitter"
        )
        assert r["platform"] == "twitter"
        assert r["char_limit"] == 280
        assert r["within_limit"] is True

    def test_over_limit(self):
        long_text = "This is a test sentence. " * 50
        r = format_social_content(long_text, platform="twitter")
        assert r["within_limit"] is False
        assert len(r["chunks"]) > 1

    def test_engagement_signals(self):
        r = format_social_content("What do you think about AI?", platform="threads")
        assert r["engagement_signals"]["has_question"] is True

    def test_linkedin(self):
        r = format_social_content("Professional update", platform="linkedin")
        assert r["char_limit"] == 3000


class TestScaffoldTechDoc:
    def test_readme(self):
        r = scaffold_tech_doc("readme", "My Project")
        assert r["doc_type"] == "readme"
        assert len(r["sections"]) >= 3
        assert "template" in r

    def test_adr(self):
        r = scaffold_tech_doc("adr", "Use PostgreSQL")
        assert r["doc_type"] == "adr"

    def test_custom_sections(self):
        r = scaffold_tech_doc("readme", "Test", sections="overview,install,usage")
        assert len(r["sections"]) >= 3


class TestStructureStory:
    def test_three_act(self):
        r = structure_story(structure="three-act")
        assert r["structure"] == "three-act"
        assert len(r["beats"]) >= 3
        assert len(r["tension_curve"]) >= 3

    def test_heros_journey(self):
        r = structure_story(structure="heros-journey")
        assert r["structure"] == "heros-journey"
        assert len(r["beats"]) >= 10

    def test_with_elements(self):
        r = structure_story(
            genre="mystery", elements="protagonist: detective, setting: 1920s Chicago"
        )
        assert r["genre"] == "mystery"
        assert len(r["genre_conventions"]) >= 1


# ---------------------------------------------------------------------------
# New: Shared utility tests
# ---------------------------------------------------------------------------


class TestFormalityScore:
    def test_formal_text(self):
        text = "Regarding the proposal, please review the attached document. Therefore, we sincerely appreciate your consideration."
        score = formality_score(text)
        assert 50 < score <= 100

    def test_informal_text(self):
        text = "Hey gonna grab some stuff lol. Yeah that's cool btw."
        score = formality_score(text)
        assert 0 <= score < 50

    def test_empty_text(self):
        assert formality_score("") == 50.0

    def test_range(self):
        for text in ["hello", "Dear Sir, Regarding the matter...", "hey gonna wanna"]:
            s = formality_score(text)
            assert 0 <= s <= 100


class TestDetectNamedEntities:
    def test_finds_names(self):
        text = "John Smith met with Alice Johnson at the conference."
        entities = detect_named_entities(text)
        assert "John Smith" in entities or "Alice Johnson" in entities

    def test_empty(self):
        assert detect_named_entities("") == []


class TestCountPatternMatches:
    def test_counts(self):
        assert count_pattern_matches("hello world hello", ["hello"]) == 2

    def test_case_insensitive(self):
        assert count_pattern_matches("Hello HELLO", ["hello"]) == 2


class TestTextStructureCheck:
    def test_found(self):
        r = text_structure_check(
            "Dear John, please review.",
            {"greeting": ["dear"], "cta": ["please review"]},
        )
        assert r["greeting"] is True
        assert r["cta"] is True

    def test_not_found(self):
        r = text_structure_check(
            "Hello world", {"greeting": ["dear"], "cta": ["please review"]}
        )
        assert r["greeting"] is False


# ---------------------------------------------------------------------------
# New: Email text analysis tests
# ---------------------------------------------------------------------------


class TestDraftEmailAnalysis:
    def test_text_analysis_present(self):
        r = draft_email("Please review the attached proposal regarding Q3 budget.")
        assert "text_analysis" in r
        ta = r["text_analysis"]
        assert "formality_score" in ta
        assert 0 <= ta["formality_score"] <= 100

    def test_formality_computed(self):
        r = draft_email("Hey gonna check that stuff out real quick")
        assert r["text_analysis"]["formality_score"] < 70

    def test_structure_detection(self):
        r = draft_email("Hi team, please review by Friday. Thanks, John")
        struct = r["text_analysis"]["structure"]
        assert struct["has_greeting"] is True

    def test_readability_present(self):
        r = draft_email("This is a simple message about the project update.")
        rd = r["text_analysis"]["readability"]
        assert "flesch_score" in rd
        assert "flesch_grade" in rd

    def test_tone_words(self):
        r = draft_email("Thank you for the excellent work on this amazing project.")
        tw = r["text_analysis"]["tone_words"]
        assert tw["dominant"] == "positive"

    def test_sentence_stats(self):
        r = draft_email("First sentence here. Second sentence there. Third one now.")
        ss = r["text_analysis"]["sentence_stats"]
        assert ss["count"] >= 2


# ---------------------------------------------------------------------------
# New: Blog content analysis tests
# ---------------------------------------------------------------------------


class TestBlogContentAnalysis:
    def test_topic_analysis(self):
        r = draft_blog_post("Introduction to Machine Learning with Python")
        assert "topic_analysis" in r
        assert len(r["topic_analysis"]["primary_keywords"]) >= 1

    def test_readability_target(self):
        r = draft_blog_post("Tutorial Topic", style="tutorial")
        assert "readability_target" in r
        assert r["readability_target"]["min"] >= 50

    def test_heading_validation(self):
        r = draft_blog_post("Some Topic")
        assert "heading_validation" in r
        assert r["heading_validation"]["h1_count"] == 1
        assert r["heading_validation"]["valid"] is True

    def test_content_gaps(self):
        r = draft_blog_post("Quick Tips", style="educational")
        assert "content_gaps" in r
        assert isinstance(r["content_gaps"], list)


# ---------------------------------------------------------------------------
# New: Tech doc analysis tests
# ---------------------------------------------------------------------------


class TestScaffoldTechDocAnalysis:
    def test_effort_estimate(self):
        r = scaffold_tech_doc("readme", "My Project")
        assert "effort_estimate" in r
        assert r["effort_estimate"]["min_hours"] > 0

    def test_code_analysis(self):
        code = "def hello():\n    pass\n\nclass Foo:\n    pass\n"
        r = scaffold_tech_doc("readme", "My Project", content=code)
        assert "analysis" in r
        assert "code_structure" in r["analysis"]
        assert "hello" in r["analysis"]["code_structure"]["functions"]

    def test_readme_completeness(self):
        content = "# My Project\n## Installation\npip install foo\n## Usage\nfoo bar\n## License\nMIT"
        r = scaffold_tech_doc("readme", "My Project", content=content)
        assert "analysis" in r
        assert "completeness" in r["analysis"]
        assert r["analysis"]["completeness"]["score"] > 0

    def test_no_analysis_without_content(self):
        r = scaffold_tech_doc("readme", "My Project")
        assert "analysis" not in r


# ---------------------------------------------------------------------------
# New: Story text analysis tests
# ---------------------------------------------------------------------------


class TestStructureStoryAnalysis:
    def test_no_analysis_without_text(self):
        r = structure_story()
        assert "text_analysis" not in r

    def test_text_analysis_present(self):
        text = '"Hello," said John. "How are you?" asked Mary. Later that evening, they met again.'
        r = structure_story(text=text)
        assert "text_analysis" in r
        ta = r["text_analysis"]
        assert ta["word_count"] > 0
        assert "dialogue" in ta
        assert ta["dialogue"]["ratio"] > 0

    def test_scene_transitions(self):
        text = "Part one content here.\n\n***\n\nPart two content here. Later that evening things changed."
        r = structure_story(text=text)
        assert r["text_analysis"]["scene_transitions"]["count"] >= 1

    def test_character_mentions(self):
        r = structure_story(
            elements="characters: Alice, Bob",
            text="Alice walked in. Bob followed Alice. Alice turned around.",
        )
        cm = r["text_analysis"]["character_mentions"]
        assert cm["mentions"]["Alice"] >= 2
