"""
File Name: __init__.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Package root for job_matcher — re-exports the stable embeddable-core API.

This module exposes the public surface by:
1. Publishing the package version (stamped by python-semantic-release).
2. Re-exporting the deterministic scoring functions and Pydantic schemas
   that in-process (GenAI/agent) callers may depend on.
3. Re-exporting the pipeline entry point (run_analysis / RunResult) and
   resume extraction for in-process GenAI callers.

Anything not re-exported here is internal and carries no stability promise.
"""

__version__ = "0.7.1"


def run_analysis(*args, **kwargs):
    """Stable core entry point — lazy import so `import job_matcher` stays light."""
    from job_matcher.pipeline import run_analysis as _run

    return _run(*args, **kwargs)


def extract_resume_text(*args, **kwargs):
    """Stable core re-export of resume extraction (lazy import)."""
    from job_matcher.resume import extract_resume_text as _extract

    return _extract(*args, **kwargs)


def extract_jsonresume(*args, **kwargs):
    """Stable core re-export of JSON Resume extraction (lazy import, async)."""
    from job_matcher.jsonresume import extract_jsonresume as _extract

    return _extract(*args, **kwargs)


# Stable embeddable-core re-exports
from job_matcher.schemas import (  # noqa: F401
    DomainAlignment,
    ExperienceAlignment,
    JobAnalysis,
    JobFetchFailure,
    JobOutcome,
    JobReport,
    MatchStatus,
    ScoreBreakdown,
    SkillMatch,
)
from job_matcher.scoring import (  # noqa: F401
    match_band_for,
    recommendation_for,
    score_analysis,
    score_job_fit,
)

__all__ = [
    "__version__",
    "DomainAlignment",
    "ExperienceAlignment",
    "JobAnalysis",
    "JobFetchFailure",
    "JobOutcome",
    "JobReport",
    "MatchStatus",
    "ScoreBreakdown",
    "SkillMatch",
    "match_band_for",
    "recommendation_for",
    "score_analysis",
    "score_job_fit",
    "run_analysis",
    "extract_resume_text",
    "extract_jsonresume",
]
