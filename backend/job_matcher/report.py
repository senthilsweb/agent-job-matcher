"""
File Name: report.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Report naming and assembly — the filename contract and per-job report
construction ported from the Eve reference (assemble_report tool).

This module produces run artifacts by:
1. slugify() — strips every character outside [a-z0-9-], which is also a
   security property: an adversarial LLM-generated job title cannot
   produce path traversal because '.' and '/' cannot survive it.
2. report_filename() — slug(<job title>)_<timestamp>.json for analyzed
   jobs, slug(<job source>)_<timestamp>.failed.json for fetch failures
   (regex-pinned by evals).
3. build_job_report() — assembles the typed JobReport from analysis +
   deterministic scoring outputs.
4. write_json_artifact() — path-confined JSON writes under a run folder
   (rejects absolute paths and '..' segments, defense in depth).
"""

# Import necessary libraries
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from job_matcher.observability import traced
from job_matcher.schemas import JobAnalysis, JobReport, MatchStatus, ScoreBreakdown

# The filename contract, pinned by evals/rubrics.md and test_slug_naming.py
TIMESTAMP_FORMAT = "%Y-%m-%dT%H-%M-%SZ"
REPORT_FILENAME_RE = re.compile(
    r"^[a-z0-9]+(-[a-z0-9]+)*_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z(\.failed)?\.json$"
)


def run_timestamp(now: datetime | None = None) -> str:
    """UTC timestamp in the filename-safe contract format."""
    return (now or datetime.now(timezone.utc)).strftime(TIMESTAMP_FORMAT)


def slugify(text: str) -> str:
    """Lowercase; every run of characters outside [a-z0-9] collapses to one hyphen."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "job"


def report_filename(title_or_source: str, timestamp: str, failed: bool = False) -> str:
    """The per-job artifact name: slug + timestamp (+ .failed for fetch failures)."""
    suffix = ".failed.json" if failed else ".json"
    return f"{slugify(title_or_source)}_{timestamp}{suffix}"


def assert_safe_relative(rel_name: str) -> None:
    """Reject absolute paths and traversal segments in artifact names."""
    p = Path(rel_name)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError(f"unsafe artifact path: {rel_name!r}")


@traced("build_job_report")
def build_job_report(
    *,
    run_id: str,
    job_source: str,
    resume_file: str,
    models: dict[str, str],
    analysis: JobAnalysis,
    score_breakdown: ScoreBreakdown,
    match_status: MatchStatus,
    recommendation: str,
    cover_letter_text: str,
    generated_at: str | None = None,
) -> JobReport:
    """Assemble the validated per-job report from typed parts."""
    return JobReport(
        run_id=run_id,
        generated_at=generated_at or datetime.now(timezone.utc).isoformat(),
        job_source=job_source,
        resume_file=resume_file,
        models=models,
        analysis=analysis,
        cover_letter_text=cover_letter_text,
        score_breakdown=score_breakdown,
        match_status=match_status,
        recommendation=recommendation,
    )


@traced("write_json_artifact", capture={"rel_name"})
def write_json_artifact(run_dir: Path, rel_name: str, payload: BaseModel) -> Path:
    """Write a validated model as pretty JSON under the run folder, path-confined."""
    assert_safe_relative(rel_name)
    target = run_dir / rel_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return target
