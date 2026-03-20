"""Analysis tools — data, text, financial, legal, survey, and competitive analysis."""

from .competitive import build_comparison_matrix
from .data import analyze_data
from .financial import analyze_financials
from .legal import review_legal_document
from .summarize import summarize_document
from .survey import analyze_survey

__all__ = [
    "analyze_data",
    "analyze_financials",
    "analyze_survey",
    "build_comparison_matrix",
    "review_legal_document",
    "summarize_document",
]
