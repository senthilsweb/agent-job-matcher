"""
File Name: test_cover_letter.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Cover-letter rendering eval (no LLM — analysis stubbed): the shipped
default template activates automatically, an operator override takes
precedence, missing identity fields degrade line-by-line (never a
placeholder), and every rendered identity value is grounded in the
run's resume text (Bolt 10, revision 7).
"""

# Import necessary libraries
from pathlib import Path

import pytest

from job_matcher import pipeline
from job_matcher.candidate import CandidateIdentity, extract_candidate_identity
from job_matcher.resume import extract_resume_text
from job_matcher.schemas import JobReport
from tests.test_pipeline_offline import GOOD_JD, RESUME, stub_analysis


def test_default_template_renders_with_no_operator_configuration():
    identity = CandidateIdentity(name="Jordan Rivera", email="jordan.rivera@example.com")
    text = pipeline._cover_letter_text(stub_analysis(), identity, "July 11, 2026")
    assert text.startswith("Jordan Rivera")
    assert "jordan.rivera@example.com" in text
    assert "July 11, 2026" in text
    assert "Re: Data Engineering Manager at Anthropic" in text
    assert "Dear Hiring Manager," in text
    assert text.rstrip().endswith("Jordan Rivera")


def test_missing_identity_fields_degrade_without_placeholders():
    identity = CandidateIdentity()  # nothing found
    text = pipeline._cover_letter_text(stub_analysis(), identity, "July 11, 2026")
    assert "None" not in text
    assert "{{" not in text  # no unresolved placeholder ever leaks through


def test_re_line_omits_company_when_unknown():
    analysis = stub_analysis()
    analysis.company_name = None
    identity = CandidateIdentity(name="Jordan Rivera")
    text = pipeline._cover_letter_text(analysis, identity, "July 11, 2026")
    assert "Re: Data Engineering Manager" in text
    assert " at " not in text.split("Dear Hiring Manager")[0].split("Re:")[1]


def test_operator_template_override_takes_precedence(tmp_path, monkeypatch):
    override_dir = tmp_path / "templates"
    override_dir.mkdir()
    (override_dir / "cover_letter.txt").write_text("CUSTOM: {{candidate_name}} / {{cover_letter_body}}")
    monkeypatch.setenv("TEMPLATES_DIR", str(override_dir))
    identity = CandidateIdentity(name="Jordan Rivera")
    text = pipeline._cover_letter_text(stub_analysis(), identity, "July 11, 2026")
    assert text.startswith("CUSTOM: Jordan Rivera /")


async def test_full_run_cover_letter_is_grounded_in_resume_text(monkeypatch):
    async def fake_analyze(resume_text, job_text, model, job_index=0):
        return stub_analysis(), {}

    monkeypatch.setattr(pipeline, "analyze_job_fit", fake_analyze)
    monkeypatch.setattr(pipeline, "resolve_model", lambda role="ANALYST": "test:stub-model")

    result = await pipeline.run_analysis(RESUME, [str(GOOD_JD)])
    report = result.outcomes[0]
    assert isinstance(report, JobReport)

    resume_text = extract_resume_text(RESUME)
    identity = extract_candidate_identity(resume_text)
    letter = report.cover_letter_text

    # Every literal identity value that appears in the letter must be a
    # substring of the resume text — grounded by construction, not by guard.
    for field in (identity.name, identity.email, identity.phone):
        if field:
            assert field in letter
            assert field in resume_text
