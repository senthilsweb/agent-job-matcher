"""
File Name: test_embeddable_core.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Embeddable-core eval (no LLM) — the spec's smoke test: a complete
offline fixture run through the package-root surface alone, no CLI, no
HTTP (acceptance criterion 9).

This suite pins the surface by:
1. `from job_matcher import run_analysis, ...` — the stable re-exports.
2. A full offline run (analysis stubbed) returning typed objects.
3. The deterministic pieces being callable standalone in-process.
"""

# Import necessary libraries
from pathlib import Path

from job_matcher import (
    JobReport,
    SkillMatch,
    extract_resume_text,
    match_band_for,
    run_analysis,
    score_job_fit,
)

FIXTURES = Path(__file__).parent.parent / "evals" / "data"


async def test_full_offline_run_via_package_root(monkeypatch):
    from job_matcher import pipeline
    from tests.test_pipeline_offline import stub_analysis

    async def fake_analyze(resume_text, job_text, model, job_index=0):
        return stub_analysis(), {}

    monkeypatch.setattr(pipeline, "analyze_job_fit", fake_analyze)
    monkeypatch.setattr(pipeline, "resolve_model", lambda role="ANALYST": "test:stub-model")

    result = await run_analysis(
        FIXTURES / "resume" / "synthetic-resume.pdf",
        [str(FIXTURES / "jobs" / "data-engineering-manager-product-anthropic.txt")],
    )
    assert len(result.outcomes) == 1
    assert isinstance(result.outcomes[0], JobReport)
    assert result.run_dir is None


def test_deterministic_pieces_standalone():
    text = extract_resume_text(FIXTURES / "resume" / "synthetic-resume.pdf")
    assert "jordan" in text.lower()
    breakdown = score_job_fit(
        [SkillMatch(skill="python", matched=True, evidence="Python, SQL")], [], "exact", "exact"
    )
    assert match_band_for(breakdown.total_score) == "strong_match"
