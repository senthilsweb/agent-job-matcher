"""
File Name: test_jsonresume.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
JSON Resume eval (no LLM — extraction stubbed where needed): the typed
mirror of the v1.0.0 schema, the strictness rule, the deterministic
grounding guard, and the API endpoint contract.

This suite pins the capability by:
1. A representative document validates; unknown fields are rejected at
   every level (strongly typed per the standard).
2. assert_contact_grounded catches invented email/phone.
3. extract_jsonresume stamps meta.version deterministically.
4. POST /resume/jsonresume returns the document and persists nothing;
   errors map to 422.
"""

# Import necessary libraries
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from job_matcher import jsonresume as jr
from job_matcher.api import app
from job_matcher.jsonresume import (
    Basics,
    JSONResume,
    JsonResumeGroundingError,
    assert_contact_grounded,
)

FIXTURES = Path(__file__).parent.parent / "evals" / "data"
RESUME = FIXTURES / "resume" / "synthetic-resume.pdf"

client = TestClient(app)

SAMPLE = {
    "basics": {
        "name": "Jordan Rivera",
        "email": "jordan.rivera@example.com",
        "phone": "+1 (555) 010-4477",
        "location": {"city": "Springfield", "countryCode": "US"},
        "profiles": [{"network": "GitHub", "username": "jordanrivera"}],
    },
    "work": [{"name": "Meridian", "position": "Architect", "startDate": "2021", "highlights": ["x"]}],
    "education": [{"institution": "State University", "studyType": "B.S.", "area": "CS"}],
    "skills": [{"name": "Data", "keywords": ["Snowflake", "dbt"]}],
    "languages": [{"language": "English", "fluency": "Native"}],
    "meta": {"version": "v1.0.0"},
}


def test_valid_document_round_trips():
    doc = JSONResume.model_validate(SAMPLE)
    assert doc.basics.name == "Jordan Rivera"
    assert JSONResume.model_validate_json(doc.model_dump_json()) == doc


@pytest.mark.parametrize(
    "mutant",
    [
        {**SAMPLE, "totally_unknown": 1},
        {**SAMPLE, "basics": {**SAMPLE["basics"], "salary": "100k"}},
        {**SAMPLE, "work": [{"name": "X", "compensation": "high"}]},
    ],
    ids=["root", "basics", "work"],
)
def test_unknown_fields_rejected_at_every_level(mutant):
    with pytest.raises(ValidationError):
        JSONResume.model_validate(mutant)


def test_grounding_guard_accepts_real_contacts():
    doc = JSONResume(basics=Basics(email="a@b.com", phone="555-010-4477"))
    assert_contact_grounded(doc, "reach me at A@B.com or (555) 010 4477")


def test_grounding_guard_rejects_invented_email():
    doc = JSONResume(basics=Basics(email="invented@nowhere.com"))
    with pytest.raises(JsonResumeGroundingError, match="email"):
        assert_contact_grounded(doc, "resume text without that address")


def test_grounding_guard_rejects_invented_phone():
    doc = JSONResume(basics=Basics(phone="999-999-9999"))
    with pytest.raises(JsonResumeGroundingError, match="phone"):
        assert_contact_grounded(doc, "call me at 555 010 4477")


async def test_extract_stamps_schema_version(monkeypatch):
    class FakeResult:
        output = JSONResume.model_validate(SAMPLE)

    class FakeAgent:
        def __init__(self, *a, **k): ...

        async def run(self, prompt):
            return FakeResult()

    monkeypatch.setattr(jr, "Agent", FakeAgent)
    doc = await jr.extract_jsonresume(
        "Jordan Rivera jordan.rivera@example.com +1 (555) 010-4477", "test:m"
    )
    assert doc.meta.version == "v1.0.0"


def test_api_endpoint_returns_document(monkeypatch, tmp_path):
    async def fake_extract(text, model):
        return JSONResume.model_validate(SAMPLE)

    monkeypatch.setattr("job_matcher.jsonresume.extract_jsonresume", fake_extract)
    monkeypatch.setattr("job_matcher.config.resolve_model", lambda role="ANALYST": "test:m")
    monkeypatch.chdir(tmp_path)
    response = client.post("/resume/jsonresume", data={"resume_path": str(RESUME)})
    assert response.status_code == 200
    body = response.json()
    assert body["basics"]["name"] == "Jordan Rivera"
    assert body["meta"]["version"] == "v1.0.0"
    assert not (tmp_path / "runs").exists()


def test_api_endpoint_operator_error_422(tmp_path):
    response = client.post("/resume/jsonresume", data={"resume_path": str(tmp_path / "nope.pdf")})
    assert response.status_code == 422
