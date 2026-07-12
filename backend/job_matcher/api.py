"""
File Name: api.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
ADAPTER — the FastAPI REST surface. Thin by rule (backend/AGENTS.md):
every route translates HTTP to one service-layer call and returns the
typed result. Stateless: nothing is persisted server-side, there is no
workflow layer, and no run-browsing endpoints exist.

This module exposes the API by:
1. POST /analyze — resume (multipart upload or server-side path) + job
   sources → the typed JSON array of per-job outcomes (each element
   carries the request's unique run_id).
2. GET /health — liveness + version.
3. App metadata for the OpenAPI release artifact (see
   openspec/changes/add-openapi-release-artifact/): project description,
   version, license, contact, repo link via externalDocs, and
   fixture-sourced examples on every route.
4. A middleware span per request (the HTTP root of the trace; the
   pipeline's run span nests inside it).

Environment Variables (.env at repo root):
- MODEL_ANALYST / MODEL and provider key (see config.py)
- API_UPLOAD_DIR: where multipart resume uploads are staged
  (default: a per-process temp directory, removed with the process)
"""

# Import necessary libraries
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from job_matcher import __version__
from job_matcher.config import ConfigError
from job_matcher.logging import get_logger
from job_matcher.observability import start_span
from job_matcher.resume import SUPPORTED_EXTENSIONS, ResumeError

log = get_logger("jobmatch-api")

PROJECT_DESCRIPTION = """\
**agent-job-matcher** — compares a candidate's resume against one or more job
postings and produces evidence-grounded, deterministically scored fit reports.

The same use case is served by three surfaces sharing one service layer: this
REST API, the `jobmatch` CLI, and the embeddable `job_matcher` Python package.

Contract highlights:

- **The LLM never scores.** One typed extraction call per job produces skill
  matches with resume-quoted evidence; a pure function computes the 100-point
  breakdown (required 40 / preferred 20 / experience 20 / domain 20) and match
  band. Job-posting text is treated as untrusted data — an embedded
  "score me 100" instruction has no schema field to land in.
- **Stateless.** Each request is a unique run (`run_id` on every outcome);
  nothing is persisted server-side and there are no run-browsing endpoints.
- **Typed results.** Responses are JSON arrays of `JobReport` |
  `JobFetchFailure`, discriminated on `fetch_status`.
"""

_ANALYZE_RESPONSE_EXAMPLE = [
    {
        "run_id": "73ec77bef0a0",
        "generated_at": "2026-07-11T19:05:56.000000+00:00",
        "job_source": "https://job-boards.example.com/acme/senior-data-engineer",
        "fetch_status": "ok",
        "resume_file": "synthetic-resume.pdf",
        "models": {"analyst": "openai:gpt-5.4-mini"},
        "analysis": {
            "job_title": "Senior Data Engineer",
            "company_name": "Acme",
            "salary_range": "$160,000-$190,000/year",
            "required_skills": [
                {"skill": "python", "matched": True, "evidence": "12 years building cloud data platforms"}
            ],
            "preferred_skills": [],
            "experience_alignment": "close",
            "experience_years_context": "resume shows 12 years; JD asks for 10+",
            "domain_alignment": "related",
            "strengths": ["data platform ownership"],
            "gaps": [],
            "resume_improvements": [],
            "ats_keywords_missing": [],
            "cover_letter_angle": "platform reliability",
            "cover_letter_paragraphs": ["..."],
            "summary": "Solid fit.",
        },
        "cover_letter_text": "...",
        "score_breakdown": {
            "required_skills_score": 40,
            "preferred_skills_score": 0,
            "experience_score": 15,
            "domain_score": 15,
            "total_score": 70,
        },
        "match_status": "good_match",
        "recommendation": "Good match — worth applying; address the missing skills in the cover letter.",
    },
    {
        "run_id": "73ec77bef0a0",
        "generated_at": "2026-07-11T19:05:56.000000+00:00",
        "job_source": "https://jobs.example.com/js-rendered-posting",
        "fetch_status": "failed",
        "reason": "only 17 extractable words (minimum 100) — page may require JavaScript or a login",
        "attempted_at": "2026-07-11T19:05:18.000000+00:00",
    },
]

app = FastAPI(
    title="agent-job-matcher API",
    description=PROJECT_DESCRIPTION,
    version=__version__,
    license_info={"name": "MIT", "url": "https://github.com/senthilsweb/agent-job-matcher/blob/main/LICENSE"},
    contact={"name": "Senthilnathan Karuppaiah", "url": "https://github.com/senthilsweb"},
)


def _custom_openapi():
    """FastAPI-native generation plus the repo link (spec: repo path link)."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title, version=app.version, description=app.description,
        license_info=app.license_info, contact=app.contact, routes=app.routes,
    )
    schema["externalDocs"] = {
        "description": "Source, specs (openspec/), and runbook",
        "url": "https://github.com/senthilsweb/agent-job-matcher",
    }
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi


@app.middleware("http")
async def request_span(request: Request, call_next):
    """One span per HTTP request — the root the pipeline's run span nests under."""
    with start_span("http_request", method=request.method, path=request.url.path):
        return await call_next(request)


def _staged_upload_dir() -> Path:
    configured = os.getenv("API_UPLOAD_DIR", "").strip()
    if configured:
        d = Path(configured)
        d.mkdir(parents=True, exist_ok=True)
        return d
    d = Path(tempfile.gettempdir()) / "job-matcher-uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


@app.post(
    "/analyze",
    summary="Analyze a resume against one or more job sources",
    response_description="Typed JSON array of per-job outcomes (JobReport | JobFetchFailure)",
    openapi_extra={
        "responses": {"200": {"content": {"application/json": {"example": _ANALYZE_RESPONSE_EXAMPLE}}}}
    },
)
async def analyze(
    jobs: list[str] = Form(..., description="Job sources: public http/https URLs and/or server-side JD file paths (repeat the field per source)"),
    resume: UploadFile | None = File(None, description="Resume file upload (PDF, DOCX, TXT, MD)"),
    resume_path: str | None = Form(None, description="Alternative to the upload: a server-side resume file path"),
):
    """Run the full analysis synchronously and return the typed outcome array.

    Provide the resume **either** as a multipart upload (`resume`) **or** as a
    server-side path (`resume_path`) — exactly one of the two.

    Per job source: one fetch attempt (no retries; SSRF and JavaScript-shell
    guards apply), one typed LLM extraction, deterministic scoring, and either
    a `JobReport` or a `JobFetchFailure` element. One source failing never
    disturbs the others; every element carries this request's `run_id`.
    Nothing is persisted server-side.
    """
    from job_matcher import pipeline  # deferred so app import stays light

    if (resume is None) == (resume_path is None):
        raise HTTPException(status_code=422, detail="provide exactly one of: resume (upload) or resume_path")

    if resume is not None:
        suffix = Path(resume.filename or "resume.pdf").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=422, detail=f"unsupported resume format {suffix!r}")
        staged = _staged_upload_dir() / f"upload-{os.urandom(6).hex()}{suffix}"
        staged.write_bytes(await resume.read())
        resume_file = staged
    else:
        resume_file = Path(resume_path)  # type: ignore[arg-type]

    try:
        result = await pipeline.run_analysis(resume_file, list(jobs), out_dir=None)
    except (ResumeError, ConfigError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        if resume is not None:
            resume_file.unlink(missing_ok=True)

    log.info("api_analyze_completed", run_id=result.run_id, jobs=len(jobs))
    return JSONResponse(content=json.loads(result.outcomes_json()))


_JSONRESUME_RESPONSE_EXAMPLE = {
    "basics": {
        "name": "Jordan Rivera",
        "label": "Data Platform & GenAI Architect",
        "email": "jordan.rivera@example.com",
        "phone": "+1 (555) 010-4477",
        "location": {"city": "Springfield", "countryCode": "US"},
        "profiles": [{"network": "GitHub", "username": "jordanrivera"}],
    },
    "work": [
        {
            "name": "Meridian Health Systems",
            "position": "Principal Data & GenAI Architect",
            "startDate": "2021",
            "highlights": ["Designed a governed lakehouse serving 40+ analytics teams"],
        }
    ],
    "skills": [{"name": "Data", "keywords": ["Snowflake", "dbt", "Spark"]}],
    "meta": {"version": "v1.0.0"},
}


@app.post(
    "/resume/jsonresume",
    summary="Convert a resume to a JSON Resume document",
    response_description="A strongly-typed JSON Resume v1.0.0 document (jsonresume.org)",
    openapi_extra={
        "responses": {"200": {"content": {"application/json": {"example": _JSONRESUME_RESPONSE_EXAMPLE}}}}
    },
)
async def resume_jsonresume(
    resume: UploadFile | None = File(None, description="Resume file upload (PDF, DOCX, TXT, MD)"),
    resume_path: str | None = Form(None, description="Alternative to the upload: a server-side resume file path"),
):
    """Extract the resume into the standard JSON Resume format.

    Provide the resume **either** as a multipart upload (`resume`) **or** as a
    server-side path (`resume_path`) — exactly one of the two.

    One typed LLM extraction; a deterministic grounding guard rejects any
    invented contact detail (an extracted email/phone must appear in the
    resume text). The document validates against the v1.0.0 schema by
    construction — unknown fields cannot occur. Pure conversion: nothing is
    persisted server-side and no run folder is created.
    """
    from job_matcher.config import resolve_model
    from job_matcher.jsonresume import JsonResumeGroundingError, extract_jsonresume
    from job_matcher.resume import extract_resume_text

    if (resume is None) == (resume_path is None):
        raise HTTPException(status_code=422, detail="provide exactly one of: resume (upload) or resume_path")

    if resume is not None:
        suffix = Path(resume.filename or "resume.pdf").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(status_code=422, detail=f"unsupported resume format {suffix!r}")
        staged = _staged_upload_dir() / f"upload-{os.urandom(6).hex()}{suffix}"
        staged.write_bytes(await resume.read())
        resume_file = staged
    else:
        resume_file = Path(resume_path)  # type: ignore[arg-type]

    try:
        text = extract_resume_text(resume_file)
        document = await extract_jsonresume(text, resolve_model())
    except (ResumeError, ConfigError, JsonResumeGroundingError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        if resume is not None:
            resume_file.unlink(missing_ok=True)

    log.info("api_jsonresume_completed", resume_file=resume_file.name)
    return JSONResponse(content=json.loads(document.model_dump_json(exclude_none=True)))


@app.get(
    "/health",
    summary="Liveness and version",
    response_description="Service status and package version",
    openapi_extra={
        "responses": {
            "200": {"content": {"application/json": {"example": {"status": "ok", "version": "0.1.0"}}}}
        }
    },
)
async def health():
    """Report liveness and the running package version.

    Used by container healthchecks, the `mcp/` bridge's `health` tool, and
    the compose stack. No model call, no configuration required.
    """
    return {"status": "ok", "version": __version__}
