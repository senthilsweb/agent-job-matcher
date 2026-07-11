"""
File Name: test_match_banding.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Match-band boundary eval (no LLM) — ports match_banding.eval.ts.

This suite pins the bands by:
1. Totals 100, 80, 79, 65, 64, 50, 49, 35, 34, 0 mapping exactly to
   strong, strong, good, good, moderate, moderate, weak, weak, no_match,
   no_match (lower edge of each band inclusive).
2. Recommendation strings byte-identical to the fixed lookup — the
   prompt_injection HARD criterion compares against these.
"""

# Import necessary libraries
import pytest

from job_matcher.scoring import RECOMMENDATIONS, match_band_for, recommendation_for

BOUNDARY_CASES = [
    (100, "strong_match"),
    (80, "strong_match"),
    (79, "good_match"),
    (65, "good_match"),
    (64, "moderate_match"),
    (50, "moderate_match"),
    (49, "weak_match"),
    (35, "weak_match"),
    (34, "no_match"),
    (0, "no_match"),
]


@pytest.mark.parametrize("total,band", BOUNDARY_CASES)
def test_band_boundaries(total, band):
    assert match_band_for(total) == band


def test_recommendation_is_deterministic_lookup():
    for band, text in RECOMMENDATIONS.items():
        assert recommendation_for(band) == text


def test_every_band_has_a_recommendation():
    assert set(RECOMMENDATIONS) == {"strong_match", "good_match", "moderate_match", "weak_match", "no_match"}
