"""
File Name: analyze.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
The ONE generative step in the pipeline — typed extraction of a
JobAnalysis from resume + job text via pydantic-ai (inception decision
Q1). Everything before and after this call is deterministic.

This module performs the extraction by:
1. Building a pydantic-ai Agent with output_type=JobAnalysis — the
   model can only fill the analysis schema, which contains no score
   field (the structural injection defense).
2. Framing both texts as fenced, labeled DATA blocks (prompts are data
   files under job_matcher/prompts/, operator-overridable).
3. Returning the validated JobAnalysis plus a token-usage dict for the
   run summary. A schema-invalid model response raises — a partially
   trusted analysis is never returned.

Environment Variables (.env at repo root):
- MODEL_ANALYST / MODEL: pydantic-ai model id (required; see config.py)
- provider credentials as the model id requires (e.g. ANTHROPIC_API_KEY)
"""

# Import necessary libraries
from __future__ import annotations

import os

from pydantic_ai import Agent

from job_matcher.observability import traced
from job_matcher.prompts import load_prompt, render
from job_matcher.schemas import JobAnalysis


def _usage_dict(result) -> dict[str, int]:
    """Best-effort token accounting across pydantic-ai versions."""
    try:
        usage = result.usage()
        return {
            "input_tokens": getattr(usage, "input_tokens", None) or getattr(usage, "request_tokens", 0) or 0,
            "output_tokens": getattr(usage, "output_tokens", None) or getattr(usage, "response_tokens", 0) or 0,
        }
    except Exception:  # usage is diagnostics, never worth failing an analysis over
        return {"input_tokens": 0, "output_tokens": 0}


def _span_enrichment(result, arguments) -> dict:
    """Declared at the decorator (AOP): token usage + model onto the LLM span;
    prompt/completion payloads only when TELEMETRY_RECORD_IO=true."""
    analysis, usage = result
    attrs: dict = {"model": arguments.get("model"), **usage}
    if os.getenv("TELEMETRY_RECORD_IO", "").strip().lower() == "true":
        attrs["input.value"] = render(
            load_prompt("analysis_user"),
            resume_text=arguments.get("resume_text", ""),
            job_text=arguments.get("job_text", ""),
        )
        attrs["output.value"] = analysis.model_dump_json()
    return attrs


@traced("analyze_job_fit", capture={"job_index"}, enrich=_span_enrichment)
async def analyze_job_fit(
    resume_text: str,
    job_text: str,
    model: str,
    job_index: int = 0,
) -> tuple[JobAnalysis, dict[str, int]]:
    """Extract the typed, evidence-grounded analysis for one job posting."""
    agent = Agent(model, output_type=JobAnalysis, system_prompt=load_prompt("analysis_system"))
    user_prompt = render(load_prompt("analysis_user"), resume_text=resume_text, job_text=job_text)
    result = await agent.run(user_prompt)
    return result.output, _usage_dict(result)
