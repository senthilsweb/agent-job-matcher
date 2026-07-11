"""
File Name: test_candidate.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Candidate-identity extraction eval (no LLM) — the deterministic
parsing behind cover-letter rendering (Bolt 10, revision 7).

This suite pins the extractors by:
1. The synthetic resume fixture yields the expected name/email/phone/
   profile URLs.
2. Deliberately-missing-field fixtures produce None, never a guess.
3. contact_line() joins only the fields present, in order, with
   " · ", and is empty when nothing was found.
4. Every non-None field is a literal substring of the source text —
   grounding holds by construction, not by a separate guard.
"""

# Import necessary libraries
from pathlib import Path

from job_matcher.candidate import contact_line, extract_candidate_identity
from job_matcher.resume import extract_resume_text

FIXTURES = Path(__file__).parent.parent / "evals" / "data"
RESUME = FIXTURES / "resume" / "synthetic-resume.pdf"


def test_synthetic_resume_identity():
    text = extract_resume_text(RESUME)
    identity = extract_candidate_identity(text)
    assert identity.name == "JORDAN RIVERA"
    assert identity.email == "jordan.rivera@example.com"
    assert identity.phone is not None and "555" in identity.phone
    assert identity.github and "github" in identity.github.lower()
    assert identity.linkedin and "linkedin" in identity.linkedin.lower()


def test_all_fields_are_grounded_in_the_source_text():
    text = extract_resume_text(RESUME)
    identity = extract_candidate_identity(text)
    for field in (identity.name, identity.email, identity.phone, identity.github, identity.linkedin):
        assert field is not None
        assert field in text


def test_missing_phone_and_github_are_omitted_not_guessed():
    text = "Jane Doe\njane.doe@example.com\nlinkedin.example.com/in/janedoe\n\nExperience..."
    identity = extract_candidate_identity(text)
    assert identity.name == "Jane Doe"
    assert identity.email == "jane.doe@example.com"
    assert identity.phone is None
    assert identity.github is None
    assert identity.linkedin is not None


def test_no_contact_fields_at_all():
    text = "Some Body\n\nA resume with no discoverable contact details whatsoever here."
    identity = extract_candidate_identity(text)
    assert identity.email is None
    assert identity.phone is None
    assert identity.github is None
    assert identity.linkedin is None
    assert identity.website is None


def test_name_rejected_when_first_line_is_not_a_name():
    # First line is the email itself — not a name, so name() must decline it
    text = "jane.doe@example.com\nJane Doe\nExperience..."
    identity = extract_candidate_identity(text)
    assert identity.name is None


def test_contact_line_joins_only_present_fields():
    text = "Alex Kim\nalex@example.com\n999-999-9999\n\nSummary line here."
    identity = extract_candidate_identity(text)
    line = contact_line(identity)
    assert line == f"{identity.email} · {identity.phone}"
    assert "None" not in line


def test_contact_line_empty_when_nothing_found():
    identity = extract_candidate_identity("Just Some Words\n\nNo contact info anywhere in this text.")
    assert contact_line(identity) == ""


def test_email_domain_not_misparsed_as_a_separate_website():
    text = "Sam Lee\nsam.lee@example.com\n\nSummary."
    identity = extract_candidate_identity(text)
    assert identity.website is None
