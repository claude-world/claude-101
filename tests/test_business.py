"""Tests for business tools."""

from claude_101.business.planning import plan_project
from claude_101.business.interview import prepare_interview
from claude_101.business.proposal import scaffold_proposal
from claude_101.business.support import build_support_response
from claude_101.business.prd import scaffold_prd
from claude_101.business.decision import evaluate_decision


class TestPlanProject:
    def test_basic(self):
        r = plan_project("Build a REST API for user management")
        assert r["team_size"] == 1
        assert r["duration_weeks"] == 4
        assert len(r["phases"]) >= 3
        assert len(r["milestones"]) >= 1

    def test_custom_params(self):
        r = plan_project("Launch marketing website", team_size=3, duration_weeks=8)
        assert r["team_size"] == 3
        assert r["duration_weeks"] == 8
        assert r["total_hours"] > 0

    def test_has_risks(self):
        r = plan_project("Migrate database to cloud")
        assert len(r["risks"]) >= 1


class TestPrepareInterview:
    def test_basic(self):
        r = prepare_interview("software engineer")
        assert len(r["preparation"]["questions"]) >= 5
        assert "time_allocation" in r
        assert "preparation_checklist" in r

    def test_senior_level(self):
        r = prepare_interview("software engineer", level="senior")
        assert r["level"] == "senior"

    def test_with_focus(self):
        r = prepare_interview("data scientist", focus="machine learning")
        assert r["role"] == "data scientist"


class TestScaffoldProposal:
    def test_business(self):
        r = scaffold_proposal("business", "Cloud Migration Proposal")
        assert r["type"] == "business"
        assert len(r["sections"]) >= 3
        assert "persuasion_framework" in r
        assert r["total_target_words"] > 0

    def test_sales(self):
        r = scaffold_proposal("sales", "Enterprise Plan Upgrade", audience="executive")
        assert r["audience"] == "executive"

    def test_objections(self):
        r = scaffold_proposal("business", "New Project")
        assert len(r["objection_templates"]) >= 1


class TestBuildSupportResponse:
    def test_billing(self):
        r = build_support_response("I was charged twice for my subscription")
        assert r["issue_classification"]["category"] in ("billing", "account")
        assert "response_scaffold" in r
        assert len(r["empathy_phrases"]) >= 1

    def test_technical(self):
        r = build_support_response(
            "The app crashes when I try to upload files", channel="chat"
        )
        assert r["issue_classification"]["category"] in ("technical", "bug")

    def test_complaint(self):
        r = build_support_response(
            "I am extremely frustrated with your terrible service"
        )
        assert r["issue_classification"]["severity"] in ("medium", "high", "critical")
        assert r["issue_classification"]["sentiment"] in ("negative", "angry")


class TestScaffoldPrd:
    def test_basic(self):
        r = scaffold_prd(
            "TaskFlow", "Teams struggle to track project progress across tools"
        )
        assert r["product_name"] == "TaskFlow"
        assert len(r["sections"]) >= 5
        assert len(r["user_stories"]) >= 1
        assert "prioritization" in r

    def test_with_users(self):
        r = scaffold_prd(
            "ChatBot",
            "Customer support is too slow",
            target_users="small business owners, support agents",
        )
        assert len(r["target_users"]) >= 2

    def test_success_metrics(self):
        r = scaffold_prd("Analytics", "No visibility into user behavior")
        assert len(r["success_metrics"]) >= 1


class TestEvaluateDecision:
    def test_with_scores(self):
        r = evaluate_decision(
            "React,Vue,Svelte",
            "Performance,DX,Ecosystem",
            "0.3,0.4,0.3",
            "React:Performance=8,DX=7,Ecosystem=9;Vue:Performance=8,DX=9,Ecosystem=7;Svelte:Performance=9,DX=9,Ecosystem=5",
        )
        assert len(r["rankings"]) == 3
        assert r["winner"]["option"] in ("React", "Vue", "Svelte")
        assert r["winner"]["margin"] >= 0

    def test_without_scores(self):
        r = evaluate_decision("Option A, Option B", "Cost, Speed, Quality")
        assert len(r["options"]) == 2
        assert len(r["criteria"]) == 3
        # No scores → no rankings
        assert r["rankings"] == [] or r["winner"] is None

    def test_equal_weights(self):
        r = evaluate_decision("A, B, C", "X, Y")
        # Equal weights when not specified
        for w in r["weights"].values():
            assert abs(w - 0.5) < 0.01

    def test_sensitivity(self):
        r = evaluate_decision(
            "A,B",
            "Speed,Cost",
            "0.5,0.5",
            "A:Speed=9,Cost=5;B:Speed=5,Cost=9",
        )
        assert len(r["sensitivity_analysis"]) >= 1


# ---------------------------------------------------------------------------
# New: Support response risk scoring tests
# ---------------------------------------------------------------------------


class TestSupportResponseRiskScoring:
    def test_escalation_risk_present(self):
        r = build_support_response("I was charged twice for my subscription")
        assert "escalation_risk" in r
        assert 0 <= r["escalation_risk"]["score"] <= 100
        assert r["escalation_risk"]["level"] in ("low", "medium", "high", "critical")

    def test_high_escalation_risk(self):
        r = build_support_response(
            "I am furious and will contact my lawyer about this refund"
        )
        assert r["escalation_risk"]["level"] in ("high", "critical")

    def test_resolution_estimate(self):
        r = build_support_response("My app keeps crashing", channel="chat")
        assert "resolution_estimate" in r
        assert r["resolution_estimate"]["min_hours"] >= 0
        assert (
            r["resolution_estimate"]["max_hours"]
            > r["resolution_estimate"]["min_hours"]
        )

    def test_customer_effort(self):
        r = build_support_response(
            "I already contacted you about this issue twice and it's still broken"
        )
        assert "customer_effort" in r
        assert r["customer_effort"]["repeat_contact_signals"] is True

    def test_response_quality_absent_by_default(self):
        r = build_support_response("simple question")
        assert "response_quality" not in r

    def test_response_quality_with_draft(self):
        r = build_support_response(
            "I was double charged",
            draft_response="I understand your frustration. I will resolve this right away and issue a refund within 3 business days.",
        )
        assert "response_quality" in r
        assert 0 <= r["response_quality"]["overall"] <= 100
        assert r["response_quality"]["empathy"] > 0


# ---------------------------------------------------------------------------
# New: Interview skill extraction & STAR validation tests
# ---------------------------------------------------------------------------


class TestInterviewAnalysis:
    def test_difficulty_distribution(self):
        r = prepare_interview("software engineer")
        assert "difficulty_distribution" in r
        dd = r["difficulty_distribution"]
        assert "counts" in dd
        assert "balance_score" in dd
        assert 0 <= dd["balance_score"] <= 100

    def test_per_question_time(self):
        r = prepare_interview("software engineer", level="senior")
        assert "per_question_time" in r
        assert len(r["per_question_time"]) > 0
        assert all(t["minutes"] > 0 for t in r["per_question_time"])

    def test_job_description_parsing(self):
        jd = "5+ years of experience with Python and JavaScript. Proficiency in AWS and Docker."
        r = prepare_interview("software engineer", job_description=jd)
        assert "job_analysis" in r
        assert r["job_analysis"]["years_experience"] == 5
        assert len(r["job_analysis"]["skills"]) >= 1

    def test_no_job_analysis_without_jd(self):
        r = prepare_interview("software engineer")
        assert "job_analysis" not in r

    def test_star_validation(self):
        resp = (
            "In my previous role, the situation was that our API was slow. "
            "My task was to optimize it. I took action by implementing caching. "
            "The result was a 40% improvement in response time."
        )
        r = prepare_interview("software engineer", response=resp)
        assert "star_validation" in r
        assert r["star_validation"]["score"] > 0

    def test_star_validation_incomplete(self):
        r = prepare_interview("software engineer", response="I did some stuff at work.")
        assert "star_validation" in r
        assert r["star_validation"]["score"] < 100
        assert len(r["star_validation"]["feedback"]) > 0


# ---------------------------------------------------------------------------
# New: PRD requirements analysis tests
# ---------------------------------------------------------------------------


class TestPrdRequirementsAnalysis:
    def test_requirements_analysis_present(self):
        r = scaffold_prd(
            "TaskFlow", "Teams struggle to track project progress across tools"
        )
        assert "requirements_analysis" in r
        ra = r["requirements_analysis"]
        assert "completeness" in ra
        assert "story_quality" in ra
        assert "dependencies" in ra

    def test_completeness_score(self):
        r = scaffold_prd(
            "TaskFlow",
            "Teams need a way to search, filter, and collaborate on tasks in real time",
        )
        assert r["requirements_analysis"]["completeness"]["score"] > 0

    def test_moscow_populated(self):
        r = scaffold_prd(
            "Shop", "Users need to search products and checkout with payment"
        )
        cats = r["prioritization"]["categories"]
        total_items = sum(len(v) for v in cats.values())
        assert total_items > 0

    def test_story_quality_scores(self):
        r = scaffold_prd(
            "App",
            "Users need to search and filter items",
            target_users="Developer, Designer",
        )
        sq = r["requirements_analysis"]["story_quality"]
        assert sq["average_score"] > 0
        assert len(sq["stories"]) >= 1


# ---------------------------------------------------------------------------
# New: Proposal analysis tests
# ---------------------------------------------------------------------------


class TestProposalAnalysis:
    def test_aida_coverage(self):
        r = scaffold_proposal("business", "Cloud Migration")
        assert "aida_coverage" in r
        ac = r["aida_coverage"]
        assert 0 <= ac["balance_score"] <= 100

    def test_argument_analysis(self):
        content = "We must migrate to the cloud. Research shows 40% cost reduction. According to Gartner, 85% of companies will adopt cloud by 2025."
        r = scaffold_proposal("business", "Cloud Migration", content=content)
        assert "argument_analysis" in r
        assert r["argument_analysis"]["evidence"] > 0
        assert r["argument_analysis"]["strength"] in (
            "strong",
            "moderate",
            "weak",
            "unsupported",
        )

    def test_no_argument_without_content(self):
        r = scaffold_proposal("business", "Test")
        assert "argument_analysis" not in r

    def test_roi_analysis(self):
        r = scaffold_proposal(
            "business", "New Tool", investment=100000, annual_return=50000
        )
        assert "roi_analysis" in r
        roi = r["roi_analysis"]
        assert roi["roi_percent"] == 50.0
        assert roi["payback_years"] == 2.0
        assert "npv_at_10pct" in roi

    def test_no_roi_without_investment(self):
        r = scaffold_proposal("business", "Test")
        assert "roi_analysis" not in r
