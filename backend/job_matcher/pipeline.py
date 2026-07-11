"""
File Name: pipeline.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
SERVICE LAYER — the single entry point every adapter (CLI, FastAPI,
embeddable core) calls. No business rule lives in an adapter.

This module orchestrates a run by:
1. Minting a unique run_id per request (no workflow layer — each request
   is self-contained; the run_id is also the trace correlation id).
2. Extracting the resume text once, then spawning ONE END-TO-END ASYNC
   TASK PER JOB SOURCE (fetch → analyze → score → outcome), bounded by
   a JOB_FANOUT_CONCURRENCY semaphore. A failure at any stage of one
   task is logged and becomes that job's failure outcome — it never
   disturbs sibling tasks; an all-failed run still completes cleanly.
3. Gathering the typed list[JobOutcome] — the result contract of every
   surface — and, in CLI mode (out_dir given), persisting the run under
   runs/<ts>/: resume.txt, jobs/<n>.txt, fetch-attempts.json, one JSON
   per job, results.json (the array), ranking.md (sources > 1), and
   summary.json (tokens, timing, statuses). API mode persists nothing.

Environment Variables (.env at repo root):
- MODEL_ANALYST / MODEL, JOB_FANOUT_CONCURRENCY (see config.py)
"""

# Import necessary libraries
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import structlog
from pydantic import TypeAdapter

from job_matcher.analyze import analyze_job_fit
from job_matcher.candidate import CandidateIdentity, contact_line, extract_candidate_identity
from job_matcher.config import fanout_concurrency, resolve_model
from job_matcher.fetch import FetchResult, fetch_job_source
from job_matcher.observability import root_span, traced
from job_matcher.prompts import load_template, render
from job_matcher.report import build_job_report, report_filename, run_timestamp, write_json_artifact
from job_matcher.resume import extract_resume_text
from job_matcher.schemas import JobFetchFailure, JobOutcome, JobReport
from job_matcher.scoring import match_band_for, recommendation_for, score_analysis

log = structlog.get_logger(__name__)

_OUTCOMES = TypeAdapter(list[JobOutcome])


@dataclass
class RunResult:
    """What every surface gets back from a run."""

    run_id: str
    outcomes: list[JobOutcome]
    run_dir: Path | None = None
    summary: dict = field(default_factory=dict)

    def outcomes_json(self) -> str:
        """The typed JSON array — the cross-surface result contract."""
        return _OUTCOMES.dump_json(self.outcomes, indent=2).decode()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cover_letter_text(analysis, identity: CandidateIdentity, date_str: str) -> str:
    """Render through the cover-letter template (operator override, else the
    package-shipped default — both resolved by load_template()). The
    identity block is deterministically sourced (candidate.py), computed
    once per run and reused across every job; a missing field is simply
    omitted from the contact line, never a placeholder."""
    body = "\n\n".join(analysis.cover_letter_paragraphs)
    re_line = f"Re: {analysis.job_title}"
    if analysis.company_name:
        re_line += f" at {analysis.company_name}"
    return render(
        load_template("cover_letter"),
        cover_letter_body=body,
        candidate_name=identity.name or "",
        candidate_contact_line=contact_line(identity),
        date=date_str,
        re_line=re_line,
    )


@traced("job_task", capture={"job_index"})
async def _job_task(
    job_index: int,
    source: str,
    resume_text: str,
    resume_file: str,
    model: str,
    run_id: str,
    semaphore: asyncio.Semaphore,
    fetches: dict[int, FetchResult],
    identity: CandidateIdentity,
    date_str: str,
) -> JobOutcome:
    """One job source, end to end. Any failure becomes this job's outcome only."""
    async with semaphore:
        fetch = await fetch_job_source(source)
        fetches[job_index] = fetch
        if not fetch.ok:
            log.info("job_failed", run_id=run_id, job_source=source, stage="fetch", reason=fetch.reason)
            return JobFetchFailure(
                run_id=run_id, generated_at=_now(), job_source=source,
                reason=fetch.reason or "fetch failed", attempted_at=fetch.attempted_at,
            )
        try:
            analysis, usage = await analyze_job_fit(resume_text, fetch.text or "", model, job_index=job_index)
            breakdown = score_analysis(analysis)
            band = match_band_for(breakdown.total_score)
            report = build_job_report(
                run_id=run_id,
                job_source=source,
                resume_file=resume_file,
                models={"analyst": model},
                analysis=analysis,
                score_breakdown=breakdown,
                match_status=band,
                recommendation=recommendation_for(band),
                cover_letter_text=_cover_letter_text(analysis, identity, date_str),
            )
            log.info("job_analyzed", run_id=run_id, job_source=source,
                     total_score=breakdown.total_score, band=band, **usage)
            return report
        except Exception as exc:  # graceful per-job isolation — siblings continue
            log.error("job_failed", run_id=run_id, job_source=source,
                      stage="analysis", error=f"{type(exc).__name__}: {exc}")
            return JobFetchFailure(
                run_id=run_id, generated_at=_now(), job_source=source,
                reason=f"analysis failed: {type(exc).__name__}: {exc}", attempted_at=fetch.attempted_at,
            )


def _persist(
    out_dir: Path, ts: str, run_id: str, model: str, resume_file: str,
    resume_text: str, outcomes: list[JobOutcome], fetches: dict[int, FetchResult],
    duration_ms: float, result: RunResult,
) -> None:
    """CLI-mode persistence of the full run folder (API mode never calls this)."""
    run_dir = out_dir / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "resume.txt").write_text(resume_text, encoding="utf-8")

    attempts = []
    for i in sorted(fetches):
        f = fetches[i]
        attempts.append({"job_source": f.job_source, "attempted_at": f.attempted_at,
                         "status": "ok" if f.ok else "failed", "words": f.words, "reason": f.reason})
        if f.ok and f.text:
            jobs_dir = run_dir / "jobs"
            jobs_dir.mkdir(exist_ok=True)
            (jobs_dir / f"{i}.txt").write_text(f.text, encoding="utf-8")
    import json

    (run_dir / "jobs").mkdir(exist_ok=True)
    (run_dir / "jobs" / "fetch-attempts.json").write_text(json.dumps(attempts, indent=2), encoding="utf-8")

    for outcome in outcomes:
        if isinstance(outcome, JobReport):
            name = report_filename(outcome.analysis.job_title, ts)
        else:
            name = report_filename(outcome.job_source, ts, failed=True)
        write_json_artifact(run_dir, name, outcome)

    (run_dir / "results.json").write_text(result.outcomes_json() + "\n", encoding="utf-8")

    reports = [o for o in outcomes if isinstance(o, JobReport)]
    if len(outcomes) > 1:
        rows = ["# Ranking", "", "| # | Job | Company | Score | Band |", "|---|---|---|---|---|"]
        ranked = sorted(reports, key=lambda r: -r.score_breakdown.total_score)
        for rank, r in enumerate(ranked, 1):
            rows.append(
                f"| {rank} | {r.analysis.job_title} | {r.analysis.company_name or '-'} "
                f"| {r.score_breakdown.total_score} | {r.match_status} |"
            )
        for o in outcomes:
            if isinstance(o, JobFetchFailure):
                rows.append(f"| - | {o.job_source} | - | failed | - |")
        (run_dir / "ranking.md").write_text("\n".join(rows) + "\n", encoding="utf-8")

    summary = {
        "run_id": run_id, "generated_at": _now(), "model": model, "resume_file": resume_file,
        "duration_ms": round(duration_ms, 1),
        "jobs": [
            {"job_source": o.job_source, "status": o.fetch_status,
             "total_score": o.score_breakdown.total_score if isinstance(o, JobReport) else None}
            for o in outcomes
        ],
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    result.run_dir = run_dir
    result.summary = summary


async def run_analysis(
    resume_path: Path | str,
    job_sources: list[str],
    out_dir: Path | str | None = None,
) -> RunResult:
    """Run the full use case. out_dir given → CLI persistence; None → payload only."""
    run_id = uuid.uuid4().hex[:12]
    ts = run_timestamp()
    started = time.time()
    model = resolve_model()

    with root_span("run_analysis", run_id=run_id, job_count=len(job_sources)):
        resume_path = Path(resume_path)
        resume_text = extract_resume_text(resume_path)
        # Deterministic, no LLM call — computed once, reused across every job
        # in the fan-out, never re-run per job (candidate.py).
        identity = extract_candidate_identity(resume_text)
        date_str = datetime.now(timezone.utc).strftime("%B %-d, %Y")

        semaphore = asyncio.Semaphore(fanout_concurrency())
        fetches: dict[int, FetchResult] = {}
        outcomes = list(
            await asyncio.gather(
                *(
                    _job_task(i, source, resume_text, resume_path.name, model, run_id,
                              semaphore, fetches, identity, date_str)
                    for i, source in enumerate(job_sources)
                )
            )
        )

        result = RunResult(run_id=run_id, outcomes=outcomes)
        if out_dir is not None:
            _persist(Path(out_dir), ts, run_id, model, resume_path.name, resume_text,
                     outcomes, fetches, (time.time() - started) * 1000, result)
        log.info("run_completed", run_id=run_id,
                 ok=sum(1 for o in outcomes if isinstance(o, JobReport)),
                 failed=sum(1 for o in outcomes if isinstance(o, JobFetchFailure)))
        return result
