"""
File Name: cli.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
ADAPTER — the Typer CLI surface. Thin by rule (backend/AGENTS.md): no
business logic lives here, only translation to service-layer calls.

This module exposes the command line by:
1. `jobmatch version` — print the package version.
2. `jobmatch analyze --resume <file> --job <url-or-file> [--job ...]
   [--out runs]` — run the pipeline with CLI persistence (runs/<ts>/,
   per-job files, results.json, ranking.md, summary.json). Exit 0 for a
   completed run — even one where every job source failed; nonzero only
   for operator errors (missing/unreadable resume, missing model config).

Environment Variables (.env at repo root):
- (none read directly here; resolution lives in config.py)
"""

# Import necessary libraries
import asyncio
from pathlib import Path

import typer

from job_matcher import __version__
from job_matcher.config import ConfigError
from job_matcher.logging import get_logger
from job_matcher.resume import ResumeError
from job_matcher.schemas import JobReport

app = typer.Typer(help="Job matcher — resume vs job postings, evidence-grounded and deterministically scored.")


@app.callback()
def _root() -> None:
    """Keeps single commands as named subcommands (jobmatch version, jobmatch analyze...)."""


@app.command()
def version() -> None:
    """Print the job-matcher version."""
    log = get_logger("jobmatch")
    log.info("version", version=__version__)
    typer.echo(__version__)


@app.command()
def analyze(
    resume: Path = typer.Option(..., "--resume", help="Resume file (PDF, DOCX, TXT, MD)"),
    job: list[str] = typer.Option(..., "--job", help="Job source: URL or local JD file (repeatable)"),
    out: Path = typer.Option(Path("runs"), "--out", help="Directory for run artifacts"),
) -> None:
    """Analyze the resume against one or more job sources; persist under --out."""
    log = get_logger("jobmatch")
    from job_matcher.pipeline import run_analysis  # deferred: keeps `version` fast

    try:
        result = asyncio.run(run_analysis(resume, list(job), out_dir=out))
    except (ResumeError, ConfigError) as exc:
        log.error("operator_error", error=str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2)

    ranked = sorted(
        (o for o in result.outcomes if isinstance(o, JobReport)),
        key=lambda r: -r.score_breakdown.total_score,
    )
    for r in ranked:
        typer.echo(f"{r.score_breakdown.total_score:>3}  {r.match_status:<15} {r.analysis.job_title}")
    for o in result.outcomes:
        if not isinstance(o, JobReport):
            typer.echo(f"  x  failed          {o.job_source} — {o.reason}")
    typer.echo(f"run {result.run_id} → {result.run_dir}")
    # A completed run exits 0, even when every job source failed (spec: CLI invocation)


@app.command()
def jsonresume(
    resume: Path = typer.Option(..., "--resume", help="Resume file (PDF, DOCX, TXT, MD)"),
    out: Path | None = typer.Option(None, "--out", help="Write the document here (default: stdout)"),
) -> None:
    """Convert a resume into a JSON Resume v1.0.0 document (jsonresume.org)."""
    log = get_logger("jobmatch")
    from job_matcher.config import resolve_model
    from job_matcher.jsonresume import JsonResumeGroundingError, extract_jsonresume
    from job_matcher.resume import extract_resume_text

    try:
        text = extract_resume_text(resume)
        document = asyncio.run(extract_jsonresume(text, resolve_model()))
    except (ResumeError, ConfigError, JsonResumeGroundingError) as exc:
        log.error("operator_error", error=str(exc))
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=2)

    payload = document.model_dump_json(indent=2, exclude_none=True)
    if out is not None:
        out.write_text(payload + "\n", encoding="utf-8")
        typer.echo(f"wrote {out}")
    else:
        typer.echo(payload)


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":
    main()
