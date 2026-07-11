"""
File Name: conftest.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Shared plumbing for the live eval suites (`pytest -m live`): fixture
paths, a call-counting wrapper around the REAL analysis call, and the
normalization used by every grounding assertion.

This module supports the live evals by:
1. run_live_counted() — runs the real pipeline (real model from .env,
   mini tier per the cost policy) while counting analyze_job_fit
   invocations, the assertable proxy for one-LLM-call-per-job.
2. normalize() — whitespace/case normalization; grounding checks are
   substring tests over normalized text per the rubric.
3. Module-scoped result fixtures so each live run's tokens are spent
   once and asserted many times.
"""

# Import necessary libraries
import asyncio
import re
from pathlib import Path

from job_matcher import pipeline

FIXTURES = Path(__file__).parent.parent.parent / "evals" / "data"
RESUME = FIXTURES / "resume" / "synthetic-resume.pdf"
JD_ANTHROPIC = FIXTURES / "jobs" / "data-engineering-manager-product-anthropic.txt"
JD_BAIN = FIXTURES / "jobs" / "expert-senior-manager-ai-engineering-bain.txt"
JD_TEMPORAL = FIXTURES / "jobs" / "senior-manager-solutions-architecture-growth-temporal.txt"
JD_GUSTO = FIXTURES / "jobs" / "staff-software-engineer-ai-developer-tools-gusto.txt"
ADVERSARIAL = FIXTURES / "adversarial" / "prompt-injection-jd.txt"
BROKEN_1 = FIXTURES / "jobs" / "failures" / "adp-workforcenow-566276.extracted.txt"
BROKEN_2 = FIXTURES / "jobs" / "failures" / "senior-manager-ai-agents-and-automation-jerry-ai.extracted.txt"


def normalize(text: str) -> str:
    """Whitespace/case normalization — the rubric's grounding comparison space."""
    return re.sub(r"\s+", " ", text).strip().lower()


def run_live_counted(job_sources: list[str], out_dir=None):
    """Run the REAL pipeline while counting analysis calls. Returns (result, calls)."""
    calls: list[int] = []
    real = pipeline.analyze_job_fit

    async def spy(resume_text, job_text, model, job_index=0):
        calls.append(job_index)
        return await real(resume_text, job_text, model, job_index=job_index)

    pipeline.analyze_job_fit = spy
    try:
        result = asyncio.run(pipeline.run_analysis(RESUME, job_sources, out_dir=out_dir))
    finally:
        pipeline.analyze_job_fit = real
    return result, calls
