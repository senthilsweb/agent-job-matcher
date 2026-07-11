"""
File Name: jsonresume.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
JSON Resume support — a strongly-typed Pydantic mirror of the
jsonresume.org schema v1.0.0 plus the extraction call that converts a
resume file's text into it (add-job-matcher-cli revision 5, Bolt 6).

This module provides the capability by:
1. Modelling every section of the standard (basics/location/profiles,
   work, volunteer, education, awards, certificates, publications,
   skills, languages, interests, references, projects, meta) with
   fields optional exactly where the standard allows and unknown fields
   REJECTED — consumers can trust the shape without re-validating.
2. extract_jsonresume() — one typed LLM call (the same extraction
   pattern and model resolution as the job analysis), followed by a
   deterministic grounding guard: contact fields must appear in the
   resume text, never be invented.
3. Stamping meta.version = "v1.0.0" deterministically in code.

Environment Variables (.env at repo root):
- MODEL_ANALYST / MODEL and provider key (see config.py)
"""

# Import necessary libraries
from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent

from job_matcher.observability import traced
from job_matcher.prompts import load_prompt, render

SCHEMA_VERSION = "v1.0.0"


class _Strict(BaseModel):
    """Base for every section: unknown fields are rejected, all fields optional."""

    model_config = ConfigDict(extra="forbid")


class Location(_Strict):
    address: str | None = None
    postalCode: str | None = None
    city: str | None = None
    countryCode: str | None = None
    region: str | None = None


class Profile(_Strict):
    network: str | None = None
    username: str | None = None
    url: str | None = None


class Basics(_Strict):
    name: str | None = None
    label: str | None = None
    image: str | None = None
    email: str | None = None
    phone: str | None = None
    url: str | None = None
    summary: str | None = None
    location: Location | None = None
    profiles: list[Profile] = []


class Work(_Strict):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    position: str | None = None
    url: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    summary: str | None = None
    highlights: list[str] = []


class Volunteer(_Strict):
    organization: str | None = None
    position: str | None = None
    url: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    summary: str | None = None
    highlights: list[str] = []


class Education(_Strict):
    institution: str | None = None
    url: str | None = None
    area: str | None = None
    studyType: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    score: str | None = None
    courses: list[str] = []


class Award(_Strict):
    title: str | None = None
    date: str | None = None
    awarder: str | None = None
    summary: str | None = None


class Certificate(_Strict):
    name: str | None = None
    date: str | None = None
    issuer: str | None = None
    url: str | None = None


class Publication(_Strict):
    name: str | None = None
    publisher: str | None = None
    releaseDate: str | None = None
    url: str | None = None
    summary: str | None = None


class Skill(_Strict):
    name: str | None = None
    level: str | None = None
    keywords: list[str] = []


class Language(_Strict):
    language: str | None = None
    fluency: str | None = None


class Interest(_Strict):
    name: str | None = None
    keywords: list[str] = []


class Reference(_Strict):
    name: str | None = None
    reference: str | None = None


class Project(_Strict):
    name: str | None = None
    startDate: str | None = None
    endDate: str | None = None
    description: str | None = None
    highlights: list[str] = []
    url: str | None = None
    roles: list[str] = []
    entity: str | None = None
    type: str | None = None
    keywords: list[str] = []


class Meta(_Strict):
    canonical: str | None = None
    version: str | None = None
    lastModified: str | None = None


class JSONResume(_Strict):
    """The full JSON Resume v1.0.0 document — jsonresume.org/schema."""

    basics: Basics | None = None
    work: list[Work] = []
    volunteer: list[Volunteer] = []
    education: list[Education] = []
    awards: list[Award] = []
    certificates: list[Certificate] = []
    publications: list[Publication] = []
    skills: list[Skill] = []
    languages: list[Language] = []
    interests: list[Interest] = []
    references: list[Reference] = []
    projects: list[Project] = []
    meta: Meta | None = None


class JsonResumeGroundingError(ValueError):
    """The extractor invented a contact field that is not in the resume text."""


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def assert_contact_grounded(doc: JSONResume, resume_text: str) -> None:
    """Deterministic guard: email/phone must appear in the source text."""
    text = resume_text.lower()
    basics = doc.basics
    if basics is None:
        return
    if basics.email and basics.email.lower() not in text:
        raise JsonResumeGroundingError(f"extracted email {basics.email!r} not found in the resume text")
    if basics.phone and _digits(basics.phone) and _digits(basics.phone) not in _digits(resume_text):
        raise JsonResumeGroundingError(f"extracted phone {basics.phone!r} not found in the resume text")


@traced("extract_jsonresume", enrich=lambda result, args: {"model": args.get("model")})
async def extract_jsonresume(resume_text: str, model: str) -> JSONResume:
    """Convert resume text to a validated, grounded JSON Resume document."""
    agent = Agent(model, output_type=JSONResume, system_prompt=load_prompt("jsonresume_system"))
    result = await agent.run(render(load_prompt("jsonresume_user"), resume_text=resume_text))
    doc = result.output
    assert_contact_grounded(doc, resume_text)
    # Stamp the standard's version deterministically — never model-supplied
    doc.meta = Meta(version=SCHEMA_VERSION, canonical=doc.meta.canonical if doc.meta else None)
    return doc
