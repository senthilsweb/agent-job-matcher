"""
File Name: test_pipeline_offline.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Service-layer eval (no LLM — the analyze step is stubbed): async
per-job fan-out, graceful failure isolation, the typed array contract,
and CLI-mode persistence, all against the committed fixtures.

This suite pins the pipeline by:
1. Mixed run (1 good JD + 2 JS-shell failures) → 3 outcomes: 1 report +
   2 failures; exactly 1 analysis call; run completes.
2. All-failed run → failure outcomes only, zero analysis calls, no crash.
3. Fan-out: 3 good JDs → 3 analysis calls, one per job.
4. Persistence contract: resume.txt, jobs/<n>.txt for ok fetches,
   fetch-attempts.json (one attempt per source), per-job files matching
   the filename regex, results.json (validated array), ranking.md,
   summary.json. API mode (out_dir=None) persists nothing.
"""

# Import necessary libraries
import json
from pathlib import Path

import pytest

from job_matcher import pipeline
from job_matcher.report import REPORT_FILENAME_RE
from job_matcher.schemas import JobAnalysis, JobFetchFailure, JobReport, SkillMatch

FIXTURES = Path(__file__).parent.parent / "evals" / "data"
RESUME = FIXTURES / "resume" / "synthetic-resume.pdf"
GOOD_JD = FIXTURES / "jobs" / "data-engineering-manager-product-anthropic.txt"
GOOD_JD_2 = FIXTURES / "jobs" / "expert-senior-manager-ai-engineering-bain.txt"
GOOD_JD_3 = FIXTURES / "jobs" / "senior-manager-solutions-architecture-growth-temporal.txt"
BROKEN_1 = FIXTURES / "jobs" / "failures" / "adp-workforcenow-566276.extracted.txt"
BROKEN_2 = FIXTURES / "jobs" / "failures" / "senior-manager-ai-agents-and-automation-jerry-ai.extracted.txt"


def stub_analysis() -> JobAnalysis:
    return JobAnalysis(
        job_title="Data Engineering Manager",
        company_name="Anthropic",
        required_skills=[SkillMatch(skill="python", matched=True, evidence="Python, SQL")],
        preferred_skills=[],
        experience_alignment="close",
        experience_years_context="resume shows 12 years",
        domain_alignment="related",
        strengths=["platforms"], gaps=[], resume_improvements=[], ats_keywords_missing=[],
        cover_letter_angle="platforms", cover_letter_paragraphs=["One.", "Two."],
        summary="Fit.",
    )


@pytest.fixture()
def stubbed_analyze(monkeypatch):
    calls = []

    async def fake_analyze(resume_text, job_text, model, job_index=0):
        calls.append({"job_index": job_index, "model": model})
        return stub_analysis(), {"input_tokens": 100, "output_tokens": 50}

    monkeypatch.setattr(pipeline, "analyze_job_fit", fake_analyze)
    monkeypatch.setattr(pipeline, "resolve_model", lambda role="ANALYST": "test:stub-model")
    return calls


async def test_mixed_run_isolates_failures(stubbed_analyze, tmp_path):
    result = await pipeline.run_analysis(
        RESUME, [str(GOOD_JD), str(BROKEN_1), str(BROKEN_2)], out_dir=tmp_path
    )
    assert len(result.outcomes) == 3
    reports = [o for o in result.outcomes if isinstance(o, JobReport)]
    failures = [o for o in result.outcomes if isinstance(o, JobFetchFailure)]
    assert len(reports) == 1 and len(failures) == 2
    assert len(stubbed_analyze) == 1  # broken sources never reached the LLM
    assert all("extractable words" in f.reason for f in failures)


async def test_all_failed_run_completes_cleanly(stubbed_analyze, tmp_path):
    result = await pipeline.run_analysis(RESUME, [str(BROKEN_1), str(BROKEN_2)], out_dir=tmp_path)
    assert all(isinstance(o, JobFetchFailure) for o in result.outcomes)
    assert stubbed_analyze == []


async def test_fanout_one_analysis_call_per_good_job(stubbed_analyze):
    result = await pipeline.run_analysis(RESUME, [str(GOOD_JD), str(GOOD_JD_2), str(GOOD_JD_3)])
    assert len(stubbed_analyze) == 3
    assert sorted(c["job_index"] for c in stubbed_analyze) == [0, 1, 2]
    assert all(isinstance(o, JobReport) for o in result.outcomes)


async def test_analysis_exception_isolated_to_its_job(monkeypatch, tmp_path):
    async def flaky_analyze(resume_text, job_text, model, job_index=0):
        if job_index == 0:
            raise RuntimeError("model exploded")
        return stub_analysis(), {}

    monkeypatch.setattr(pipeline, "analyze_job_fit", flaky_analyze)
    monkeypatch.setattr(pipeline, "resolve_model", lambda role="ANALYST": "test:stub-model")
    result = await pipeline.run_analysis(RESUME, [str(GOOD_JD), str(GOOD_JD_2)])
    kinds = sorted(type(o).__name__ for o in result.outcomes)
    assert kinds == ["JobFetchFailure", "JobReport"]
    failure = next(o for o in result.outcomes if isinstance(o, JobFetchFailure))
    assert "analysis failed" in failure.reason


async def test_cli_mode_persistence_contract(stubbed_analyze, tmp_path):
    result = await pipeline.run_analysis(
        RESUME, [str(GOOD_JD), str(BROKEN_1)], out_dir=tmp_path
    )
    run_dir = result.run_dir
    assert run_dir and run_dir.parent == tmp_path

    assert (run_dir / "resume.txt").is_file()
    assert (run_dir / "jobs" / "0.txt").is_file()          # ok fetch persisted
    assert not (run_dir / "jobs" / "1.txt").exists()       # failed fetch has no text

    attempts = json.loads((run_dir / "jobs" / "fetch-attempts.json").read_text())
    assert len(attempts) == 2                              # exactly one attempt per source
    assert {a["status"] for a in attempts} == {"ok", "failed"}

    per_job = [p.name for p in run_dir.glob("*_*.json") if p.name not in ("results.json", "summary.json")]
    assert len(per_job) == 2
    assert all(REPORT_FILENAME_RE.match(n) for n in per_job)
    assert sum(n.endswith(".failed.json") for n in per_job) == 1

    results = json.loads((run_dir / "results.json").read_text())
    assert isinstance(results, list) and len(results) == 2

    assert (run_dir / "ranking.md").is_file()
    summary = json.loads((run_dir / "summary.json").read_text())
    assert summary["run_id"] == result.run_id
    assert len(summary["jobs"]) == 2


async def test_api_mode_persists_nothing(stubbed_analyze, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = await pipeline.run_analysis(RESUME, [str(GOOD_JD)])
    assert result.run_dir is None
    assert not (tmp_path / "runs").exists()
    # The payload contract still holds
    parsed = json.loads(result.outcomes_json())
    assert parsed[0]["fetch_status"] == "ok"
    assert parsed[0]["score_breakdown"]["total_score"] >= 0
