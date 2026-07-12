"""
File Name: test_schema_conformance.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Schema-conformance eval (no LLM) — recorded-fixture version of
schema_conformance.eval.ts: the typed contracts hold without a live run.

This suite pins the contracts by:
1. SkillMatch cross-field rule: matched=True ⇔ non-empty evidence.
2. A full JobReport fixture round-trips validation; JobOutcome
   discriminates report vs fetch-failure on fetch_status.
3. build_job_report assembles a valid report whose score fields came
   from the deterministic scorer (never free-typed).
"""

# Import necessary libraries
import pytest
from pydantic import TypeAdapter, ValidationError

from job_matcher.report import build_job_report
from job_matcher.schemas import JobAnalysis, JobFetchFailure, JobOutcome, JobReport, SkillMatch
from job_matcher.scoring import match_band_for, recommendation_for, score_analysis


def make_analysis() -> JobAnalysis:
    return JobAnalysis(
        job_title="Senior Data Engineer",
        company_name="Acme",
        required_skills=[
            SkillMatch(skill="python", matched=True, evidence="Built Python pipelines for 6 years"),
            SkillMatch(skill="rust", matched=False),
        ],
        preferred_skills=[SkillMatch(skill="dbt", matched=True, evidence="Modeled marts in dbt")],
        experience_alignment="close",
        experience_years_context="resume shows 9 years; JD asks for 8-10",
        domain_alignment="related",
        strengths=["data platform ownership"],
        gaps=["rust"],
        resume_improvements=["quantify pipeline scale"],
        ats_keywords_missing=["rust"],
        cover_letter_angle="platform reliability",
        cover_letter_paragraphs=["Para one.", "Para two."],
        summary="Solid fit with one gap.",
    )


def test_matched_skill_requires_evidence():
    with pytest.raises(ValidationError):
        SkillMatch(skill="python", matched=True, evidence="")


def test_unmatched_skill_forbids_evidence():
    with pytest.raises(ValidationError):
        SkillMatch(skill="python", matched=False, evidence="stray quote")


def test_job_report_round_trips():
    analysis = make_analysis()
    breakdown = score_analysis(analysis)
    band = match_band_for(breakdown.total_score)
    report = build_job_report(
        run_id="run-1",
        job_source="https://jobs.example.com/123",
        resume_file="resume.pdf",
        models={"analyst": "test:model"},
        analysis=analysis,
        score_breakdown=breakdown,
        match_status=band,
        recommendation=recommendation_for(band),
        cover_letter_text="Para one.\n\nPara two.",
    )
    # Serialize → validate → identical
    assert JobReport.model_validate_json(report.model_dump_json()) == report


def test_outcome_union_discriminates_on_fetch_status():
    adapter = TypeAdapter(JobOutcome)
    failure = JobFetchFailure(
        run_id="run-1",
        generated_at="2026-07-11T00:00:00Z",
        job_source="https://jobs.example.com/broken",
        reason="page appears to be a JavaScript shell (8 extractable words)",
        attempted_at="2026-07-11T00:00:00Z",
    )
    parsed = adapter.validate_python(failure.model_dump())
    assert isinstance(parsed, JobFetchFailure)

    analysis = make_analysis()
    breakdown = score_analysis(analysis)
    band = match_band_for(breakdown.total_score)
    report = build_job_report(
        run_id="run-1",
        job_source="https://jobs.example.com/123",
        resume_file="resume.pdf",
        models={"analyst": "test:model"},
        analysis=analysis,
        score_breakdown=breakdown,
        match_status=band,
        recommendation=recommendation_for(band),
        cover_letter_text="x",
    )
    parsed = adapter.validate_python(report.model_dump())
    assert isinstance(parsed, JobReport)


def test_analysis_schema_has_no_score_field():
    # The structural prompt-injection defense: no numeric score field exists
    # in the one schema an LLM fills in.
    fields = set(JobAnalysis.model_fields)
    assert not any("score" in f for f in fields)


def test_salary_range_defaults_to_none_and_accepts_a_verbatim_string():
    # Most postings won't state one — the field must be optional, never a
    # required extraction that forces the model to invent a number.
    assert make_analysis().salary_range is None
    stated = make_analysis().model_copy(update={"salary_range": "$160,000-$190,000/year"})
    assert stated.salary_range == "$160,000-$190,000/year"
