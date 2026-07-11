"""
File Name: scoring.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
The scoring formula — the one and only place a job-fit score is computed.
Behaviour-identical port of the Eve reference's agent/lib/scoring.ts;
evals/rubrics.md §0 is the canonical statement both implement.

This module computes deterministic scores by:
1. required skills 0-40, preferred 0-20, experience 0-20, domain 0-20;
   when a JD lists no preferred skills the 20-point preferred budget is
   reallocated to required (scales to 0-60) — never divide by zero,
   never award free points.
2. Rounding with JS Math.round semantics (floor(x + 0.5): 2.5 → 3) so
   the ported eval fixtures stay byte-identical (inception decision Q4).
3. Mapping totals to match bands (strong ≥ 80, good 65-79, moderate
   50-64, weak 35-49, no_match < 35) and band-keyed recommendation
   strings. No LLM call ever produces a number here.
"""

# Import necessary libraries
import math
from collections.abc import Sequence

from job_matcher.observability import traced
from job_matcher.schemas import (
    DomainAlignment,
    ExperienceAlignment,
    JobAnalysis,
    MatchStatus,
    ScoreBreakdown,
    SkillMatch,
)

# Fixed lookup tables — never ratios
EXPERIENCE_SCORES: dict[ExperienceAlignment, int] = {"exact": 20, "close": 15, "partial": 10, "far": 5}
DOMAIN_SCORES: dict[DomainAlignment, int] = {"exact": 20, "related": 15, "transferable": 10, "none": 5}

RECOMMENDATIONS: dict[MatchStatus, str] = {
    "strong_match": "Strong match — prioritize applying and tailor the resume to the few remaining gaps.",
    "good_match": "Good match — worth applying; address the missing skills in the cover letter.",
    "moderate_match": "Moderate match — apply if the role is a priority, but expect to close real gaps first.",
    "weak_match": "Weak match — significant gaps against this posting's requirements; consider other roles first.",
    "no_match": "Not a match — the resume does not currently support this posting's requirements.",
}


def js_round(x: float) -> int:
    """Round half away from zero for positives — JS Math.round semantics (2.5 → 3)."""
    return math.floor(x + 0.5)


def _count_matched(skills: Sequence[SkillMatch]) -> int:
    return sum(1 for s in skills if s.matched)


@traced("score_job_fit")
def score_job_fit(
    required_skills: Sequence[SkillMatch],
    preferred_skills: Sequence[SkillMatch],
    experience_alignment: ExperienceAlignment,
    domain_alignment: DomainAlignment,
) -> ScoreBreakdown:
    """Compute the 100-point breakdown from typed counts and alignment levels.

    Pure and deterministic: identical input always yields identical output.
    """
    total_required = len(required_skills)
    total_preferred = len(preferred_skills)
    matched_required = _count_matched(required_skills)
    matched_preferred = _count_matched(preferred_skills)

    # Empty-preferred reallocation: required budget grows to 60, preferred drops to 0
    required_budget = 60 if total_preferred == 0 else 40
    preferred_budget = 0 if total_preferred == 0 else 20

    required_score = 0 if total_required == 0 else js_round(matched_required / total_required * required_budget)
    preferred_score = 0 if total_preferred == 0 else js_round(matched_preferred / total_preferred * preferred_budget)

    experience_score = EXPERIENCE_SCORES[experience_alignment]
    domain_score = DOMAIN_SCORES[domain_alignment]

    return ScoreBreakdown(
        required_skills_score=required_score,
        preferred_skills_score=preferred_score,
        experience_score=experience_score,
        domain_score=domain_score,
        total_score=required_score + preferred_score + experience_score + domain_score,
    )


def score_analysis(analysis: JobAnalysis) -> ScoreBreakdown:
    """Convenience wrapper: score a full JobAnalysis."""
    return score_job_fit(
        analysis.required_skills,
        analysis.preferred_skills,
        analysis.experience_alignment,
        analysis.domain_alignment,
    )


def match_band_for(total_score: int) -> MatchStatus:
    """Map a total score (0-100) to its band; boundaries inclusive on the lower edge."""
    if total_score >= 80:
        return "strong_match"
    if total_score >= 65:
        return "good_match"
    if total_score >= 50:
        return "moderate_match"
    if total_score >= 35:
        return "weak_match"
    return "no_match"


def recommendation_for(match_status: MatchStatus) -> str:
    """Deterministic recommendation text keyed off the match band — never an LLM output."""
    return RECOMMENDATIONS[match_status]
