"""Analysis tools — data, text, financial, legal, survey, and competitive analysis."""

from claude_101.analysis.competitive import build_comparison_matrix
from claude_101.analysis.data import analyze_data
from claude_101.analysis.financial import analyze_financials
from claude_101.analysis.legal import review_legal_document
from claude_101.analysis.summarize import summarize_document
from claude_101.analysis.survey import analyze_survey

__all__ = [
    "analyze_data",
    "analyze_financials",
    "analyze_survey",
    "build_comparison_matrix",
    "review_legal_document",
    "summarize_document",
]
