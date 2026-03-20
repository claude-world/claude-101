"""Tests for analysis tools."""

from claude_101.analysis.data import analyze_data
from claude_101.analysis.summarize import summarize_document
from claude_101.analysis.competitive import build_comparison_matrix
from claude_101.analysis.survey import analyze_survey
from claude_101.analysis.financial import analyze_financials
from claude_101.analysis.legal import review_legal_document


class TestAnalyzeData:
    def test_csv_basic(self):
        data = "name,score,age\nAlice,95,25\nBob,87,30\nCharlie,92,28"
        r = analyze_data(data, format="csv")
        assert r["row_count"] == 3
        assert r["column_count"] == 3

    def test_numeric_stats(self):
        data = "value\n10\n20\n30\n40\n50"
        r = analyze_data(data, format="csv")
        numeric_cols = [c for c in r["columns"] if c["type"] == "numeric"]
        assert len(numeric_cols) >= 1
        assert "mean" in numeric_cols[0]["stats"]

    def test_json_format(self):
        data = '[{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]'
        r = analyze_data(data, format="json")
        assert r["row_count"] == 2


class TestSummarizeDocument:
    def test_basic(self):
        text = (
            "Machine learning is a branch of artificial intelligence. "
            "It enables computers to learn from data. "
            "Deep learning is a subset of machine learning. "
            "Neural networks are the foundation of deep learning. "
            "These technologies are transforming many industries. "
            "Healthcare, finance, and transportation are being revolutionized. "
            "The future of AI holds great promise. "
            "However, ethical considerations are important. "
            "We must ensure AI is used responsibly. "
            "Research in this field continues to advance rapidly."
        )
        r = summarize_document(text, max_sentences=3)
        assert r["word_count"] > 0
        assert r["sentence_count"] >= 5
        assert len(r["key_sentences"]) <= 3
        assert r["flesch_score"] > 0

    def test_keywords(self):
        text = "Python Python Python JavaScript JavaScript Ruby"
        r = summarize_document(text)
        assert len(r["keywords"]) >= 1


class TestBuildComparisonMatrix:
    def test_basic(self):
        r = build_comparison_matrix("React, Vue, Angular", "Performance, DX, Ecosystem")
        assert len(r["items"]) == 3
        assert len(r["criteria"]) == 3
        assert abs(sum(r["weights"].values()) - 1.0) < 0.01

    def test_custom_weights(self):
        r = build_comparison_matrix("A, B", "Speed, Cost", weights="0.7, 0.3")
        assert abs(r["weights"]["Speed"] - 0.7) < 0.01
        assert abs(r["weights"]["Cost"] - 0.3) < 0.01


class TestAnalyzeSurvey:
    def test_basic(self):
        data = "respondent,q1,q2,q3\n1,5,4,3\n2,4,5,4\n3,3,3,5\n4,5,4,4\n5,2,3,3"
        r = analyze_survey(data, scale_max=5)
        assert r["response_count"] >= 1
        assert len(r["questions"]) >= 1
        assert "nps" in r


class TestAnalyzeFinancials:
    def test_basic(self):
        data = "metric,Q1,Q2,Q3,Q4\nRevenue,100000,120000,115000,140000\nCOGS,60000,70000,65000,80000"
        r = analyze_financials(data, period="quarterly")
        assert r["periods_analyzed"] >= 2
        assert "metrics" in r

    def test_growth_rates(self):
        data = "metric,2023,2024\nRevenue,1000000,1200000"
        r = analyze_financials(data, period="annual")
        assert "metrics" in r


class TestReviewLegalDocument:
    def test_basic(self):
        text = """
        This Agreement is entered into by and between Company A and Company B.

        1. CONFIDENTIALITY. Each party agrees to maintain the confidentiality of
        all proprietary information disclosed by the other party.

        2. INDEMNIFICATION. Company B shall indemnify and hold harmless Company A
        from any claims arising from Company B's breach of this Agreement.

        3. TERMINATION. Either party may terminate this Agreement with 30 days
        written notice to the other party.

        4. GOVERNING LAW. This Agreement shall be governed by the laws of the
        State of California.

        5. LIMITATION OF LIABILITY. In no event shall either party be liable for
        consequential, incidental, or punitive damages.
        """
        r = review_legal_document(text, doc_type="contract")
        assert r["doc_type"] == "contract"
        assert r["word_count"] > 0
        assert len(r["clauses_found"]) >= 3
        assert r["complexity_score"] > 0
