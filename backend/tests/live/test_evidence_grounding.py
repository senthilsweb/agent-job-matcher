"""
File Name: test_evidence_grounding.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Live evidence-grounding eval (real model) — evals/rubrics.md
"evidence grounding": the no-hallucination guarantee.

This suite pins grounding by:
1. HARD — every skill with matched=true carries evidence that appears
   (whitespace/case-normalized substring) in the extracted resume text.
2. HARD — every unmatched skill carries empty evidence (schema-enforced;
   re-asserted on live output).
3. SOFT — re-running the same JD lands within ±1 band (logged, not
   asserted).
"""

# Import necessary libraries
import pytest
import structlog

from job_matcher.resume import extract_resume_text
from job_matcher.schemas import JobReport
from tests.live.conftest import JD_ANTHROPIC, RESUME, normalize, run_live_counted

pytestmark = pytest.mark.live
log = structlog.get_logger("live-evals")

BANDS = ["no_match", "weak_match", "moderate_match", "good_match", "strong_match"]


@pytest.fixture(scope="module")
def grounding_run():
    result, _ = run_live_counted([str(JD_ANTHROPIC)])
    report = result.outcomes[0]
    assert isinstance(report, JobReport), f"fixture JD unexpectedly failed: {report}"
    return report


def test_hard_matched_evidence_is_verbatim_from_resume(grounding_run):
    resume_text = normalize(extract_resume_text(RESUME))
    skills = grounding_run.analysis.required_skills + grounding_run.analysis.preferred_skills
    matched = [s for s in skills if s.matched]
    assert matched, "live run produced no matched skills to ground"
    ungrounded = [s.skill for s in matched if normalize(s.evidence) not in resume_text]
    assert not ungrounded, f"evidence not found verbatim in resume for: {ungrounded}"


def test_hard_unmatched_skills_carry_no_evidence(grounding_run):
    skills = grounding_run.analysis.required_skills + grounding_run.analysis.preferred_skills
    assert all(not s.evidence.strip() for s in skills if not s.matched)


def test_soft_rerun_band_stability(grounding_run):
    result, _ = run_live_counted([str(JD_ANTHROPIC)])
    rerun = result.outcomes[0]
    assert isinstance(rerun, JobReport)
    delta = abs(BANDS.index(grounding_run.match_status) - BANDS.index(rerun.match_status))
    if delta > 1:
        log.warning("soft_criterion_miss", eval="rerun_band_stability",
                    first=grounding_run.match_status, second=rerun.match_status)
    log.info("soft_observation", eval="rerun_band_stability",
             first=grounding_run.match_status, first_total=grounding_run.score_breakdown.total_score,
             second=rerun.match_status, second_total=rerun.score_breakdown.total_score)
