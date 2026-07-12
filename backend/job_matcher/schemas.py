"""
File Name: schemas.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Pydantic schemas for the job matcher — a behaviour-identical port of the
Eve reference's Zod schemas (ai-agents/agents/job-matcher/agent/lib/schemas.ts).

This module defines the typed contracts by:
1. JobAnalysis — the ONLY schema an LLM call ever fills in. It carries
   skill matches with resume-quoted evidence and alignment levels, never
   a score: no field exists for an injected score to land in (the
   prompt-injection defense is structural, not behavioural).
2. ScoreBreakdown — filled in exclusively by scoring.py, never a model.
3. JobReport / JobFetchFailure / JobOutcome — the per-job result union
   every surface returns (CLI persists, API returns as payload).
4. SkillMatch cross-field rule: matched=True ⇔ non-empty evidence,
   enforced at validation time so hallucinated matches fail loudly.
"""

# Import necessary libraries
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator

# Alignment levels and match bands — fixed vocabularies, identical to the Eve reference
ExperienceAlignment = Literal["exact", "close", "partial", "far"]
DomainAlignment = Literal["exact", "related", "transferable", "none"]
MatchStatus = Literal["strong_match", "good_match", "moderate_match", "weak_match", "no_match"]


class SkillMatch(BaseModel):
    """One skill from the JD with an evidence-grounded matched verdict."""

    skill: str = Field(min_length=1)
    matched: bool
    # A quote drawn from the extracted resume text proving the match; empty when matched is False
    evidence: str = ""

    @model_validator(mode="after")
    def _evidence_matches_flag(self) -> "SkillMatch":
        if self.matched and not self.evidence.strip():
            raise ValueError("evidence must be non-empty when matched is true")
        if not self.matched and self.evidence.strip():
            raise ValueError("evidence must be empty when matched is false")
        return self


class JobAnalysis(BaseModel):
    """The one and only LLM-filled schema — counts and evidence, never a score."""

    job_title: str = Field(min_length=1)
    company_name: str | None = None
    # Verbatim as stated in the posting (e.g. "$120,000-$150,000/year",
    # "$60-75/hr"), never inferred or estimated — null when the posting
    # doesn't state one. Not evidence-grounded against the resume like
    # SkillMatch: this describes the job, not the candidate.
    salary_range: str | None = None
    required_skills: list[SkillMatch]
    preferred_skills: list[SkillMatch]
    experience_alignment: ExperienceAlignment
    # Short free-text grounding, e.g. "resume shows 9 years; JD asks for 8-10"
    experience_years_context: str
    domain_alignment: DomainAlignment
    strengths: list[str]
    gaps: list[str]
    resume_improvements: list[str]
    ats_keywords_missing: list[str]
    cover_letter_angle: str
    # Text content only — v1 does not render a document
    cover_letter_paragraphs: list[str]
    summary: str


class ScoreBreakdown(BaseModel):
    """Filled in exclusively by scoring.py — never by a model call."""

    required_skills_score: int = Field(ge=0, le=60)  # 60 when preferred budget reallocates
    preferred_skills_score: int = Field(ge=0, le=20)
    experience_score: int = Field(ge=0, le=20)
    domain_score: int = Field(ge=0, le=20)
    total_score: int = Field(ge=0, le=100)


class JobFetchFailure(BaseModel):
    """One job source that could not be read — logged, not analyzed, never retried."""

    run_id: str
    generated_at: str
    job_source: str
    fetch_status: Literal["failed"] = "failed"
    reason: str
    attempted_at: str


class JobReport(BaseModel):
    """One job source that was fetched, analyzed, and scored — the self-contained report."""

    run_id: str
    generated_at: str
    job_source: str
    fetch_status: Literal["ok"] = "ok"
    resume_file: str
    models: dict[str, str]
    analysis: JobAnalysis
    # cover_letter_paragraphs rendered as one text block (template-aware in Bolt 3)
    cover_letter_text: str
    score_breakdown: ScoreBreakdown
    match_status: MatchStatus
    recommendation: str


# The shape of any one element in a run's typed result array
JobOutcome = Annotated[Union[JobReport, JobFetchFailure], Field(discriminator="fetch_status")]
