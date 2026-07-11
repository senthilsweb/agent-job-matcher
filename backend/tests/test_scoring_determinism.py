"""
File Name: test_scoring_determinism.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Scoring-formula determinism eval (no LLM) — ports the Eve reference's
scoring_determinism.eval.ts fixtures byte-for-byte.

This suite pins the formula by:
1. all-matched → 100 and none-matched → 10 exact breakdowns.
2. Empty-preferred reallocation (required budget scales to 60).
3. Rounding edges: 7/9 * 40 → 31, and the exact-.5 case 1/8 * 20 = 2.5
   → 3 (JS Math.round semantics, inception decision Q4).
4. Same input twice → identical output (pure function).
"""

# Import necessary libraries
from job_matcher.schemas import SkillMatch
from job_matcher.scoring import js_round, score_job_fit


def mk_skills(matched: int, total: int) -> list[SkillMatch]:
    """Fixture helper — mirrors the Eve eval's mkSkills()."""
    assert matched <= total, "matched cannot exceed total in a fixture"
    return [
        SkillMatch(
            skill=f"skill_{i}",
            matched=i < matched,
            evidence=f"resume quote for skill_{i}" if i < matched else "",
        )
        for i in range(total)
    ]


def test_all_matched_scores_100():
    result = score_job_fit(mk_skills(5, 5), mk_skills(3, 3), "exact", "exact")
    assert result.model_dump() == {
        "required_skills_score": 40,
        "preferred_skills_score": 20,
        "experience_score": 20,
        "domain_score": 20,
        "total_score": 100,
    }


def test_none_matched_scores_floor():
    result = score_job_fit(mk_skills(0, 4), mk_skills(0, 2), "far", "none")
    assert result.model_dump() == {
        "required_skills_score": 0,
        "preferred_skills_score": 0,
        "experience_score": 5,
        "domain_score": 5,
        "total_score": 10,
    }


def test_empty_preferred_reallocates_to_required():
    # 5/6 required against the reallocated 60-point budget: js_round(50.0) = 50
    result = score_job_fit(mk_skills(5, 6), [], "close", "related")
    assert result.model_dump() == {
        "required_skills_score": 50,
        "preferred_skills_score": 0,
        "experience_score": 15,
        "domain_score": 15,
        "total_score": 80,
    }


def test_rounding_edges_including_exact_half():
    # 7/9 * 40 = 31.111... → 31; 1/8 * 20 = 2.5 exactly → pins js_round(2.5) = 3 forever
    result = score_job_fit(mk_skills(7, 9), mk_skills(1, 8), "partial", "transferable")
    assert result.model_dump() == {
        "required_skills_score": 31,
        "preferred_skills_score": 3,
        "experience_score": 10,
        "domain_score": 10,
        "total_score": 54,
    }


def test_zero_required_never_divides_by_zero():
    result = score_job_fit([], mk_skills(2, 2), "exact", "exact")
    assert result.required_skills_score == 0
    assert result.preferred_skills_score == 20


def test_same_input_twice_is_identical():
    args = (mk_skills(7, 9), mk_skills(1, 8), "partial", "transferable")
    assert score_job_fit(*args) == score_job_fit(*args)


def test_js_round_semantics():
    assert js_round(2.5) == 3
    assert js_round(2.4999) == 2
    assert js_round(31.111) == 31
