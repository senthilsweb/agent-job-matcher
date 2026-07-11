"""
File Name: test_api.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
FastAPI surface eval (no LLM — the analyze step is stubbed): the
stateless contract, the typed-array payload, and surface parity with
the CLI schema.

This suite pins the API by:
1. GET /health → 200 with version.
2. POST /analyze (server-path and multipart) → typed array,
   schema-identical to what the CLI persists for the same inputs.
3. Statelessness: nothing written under runs/; no /runs, no /score.
4. Operator errors → 422 with a clear detail.
"""

# Import necessary libraries
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from job_matcher import pipeline
from job_matcher.api import app
from job_matcher.schemas import JobReport
from tests.test_pipeline_offline import stub_analysis

FIXTURES = Path(__file__).parent.parent / "evals" / "data"
RESUME = FIXTURES / "resume" / "synthetic-resume.pdf"
GOOD_JD = FIXTURES / "jobs" / "data-engineering-manager-product-anthropic.txt"
BROKEN = FIXTURES / "jobs" / "failures" / "adp-workforcenow-566276.extracted.txt"

client = TestClient(app)


@pytest.fixture(autouse=True)
def stubbed(monkeypatch):
    async def fake_analyze(resume_text, job_text, model, job_index=0):
        return stub_analysis(), {"input_tokens": 1, "output_tokens": 1}

    monkeypatch.setattr(pipeline, "analyze_job_fit", fake_analyze)
    monkeypatch.setattr(pipeline, "resolve_model", lambda role="ANALYST": "test:stub-model")


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok" and body["version"]


def test_analyze_server_path_returns_typed_array(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # prove nothing is persisted in cwd either
    response = client.post(
        "/analyze",
        data={"jobs": [str(GOOD_JD), str(BROKEN)], "resume_path": str(RESUME)},
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list) and len(body) == 2
    statuses = {o["fetch_status"] for o in body}
    assert statuses == {"ok", "failed"}
    ok = next(o for o in body if o["fetch_status"] == "ok")
    # Schema parity with the CLI persistence contract
    assert JobReport.model_validate(ok)
    assert ok["run_id"] == body[1]["run_id"]
    # Statelessness
    assert not (tmp_path / "runs").exists()


def test_analyze_multipart_upload():
    response = client.post(
        "/analyze",
        data={"jobs": [str(GOOD_JD)]},
        files={"resume": ("synthetic-resume.pdf", RESUME.read_bytes(), "application/pdf")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body[0]["fetch_status"] == "ok"
    assert body[0]["resume_file"].endswith(".pdf")


def test_exactly_one_resume_input_required():
    both = client.post(
        "/analyze",
        data={"jobs": [str(GOOD_JD)], "resume_path": str(RESUME)},
        files={"resume": ("r.pdf", RESUME.read_bytes(), "application/pdf")},
    )
    neither = client.post("/analyze", data={"jobs": [str(GOOD_JD)]})
    assert both.status_code == 422
    assert neither.status_code == 422


def test_operator_error_maps_to_422(tmp_path):
    response = client.post(
        "/analyze",
        data={"jobs": [str(GOOD_JD)], "resume_path": str(tmp_path / "missing.pdf")},
    )
    assert response.status_code == 422
    assert "not found" in response.json()["detail"]


def test_unsupported_upload_format_rejected():
    response = client.post(
        "/analyze",
        data={"jobs": [str(GOOD_JD)]},
        files={"resume": ("resume.rtf", b"x", "application/rtf")},
    )
    assert response.status_code == 422


def test_no_workflow_endpoints_exist():
    assert client.get("/runs").status_code == 404
    assert client.get("/runs/abc").status_code == 404
    assert client.post("/score", json={}).status_code == 404
