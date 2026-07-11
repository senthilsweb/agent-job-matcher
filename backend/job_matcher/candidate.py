"""
File Name: candidate.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Deterministic candidate-identity extraction for cover-letter rendering
(add-job-matcher-cli revision 7, Bolt 10). No LLM call: email, phone,
GitHub/LinkedIn/website, and name all follow strong-enough textual
conventions that regex parsing is more reliable than a model call,
strictly cheaper, and structurally ungroundable-wrong — a regex match
is by definition a literal substring of the source text. This also
keeps the system at exactly two LLM operations (see ADR 0001) — this
is not a third.

This module extracts identity by:
1. email() / phone(): standard regex patterns over the resume text.
2. github() / linkedin() / website(): scans URL-like tokens (schemed
   or bare domain/path) and classifies by hostname; the first
   unclassified URL becomes "website".
3. name(): the first non-blank line, accepted only if short, digit-free,
   and not itself an email/URL — the standard resume convention of
   leading with the candidate's name.
4. Every field is Optional[str]; a miss is None, never a guess.
   contact_line() joins whichever fields were found with " · " — an
   absent field is simply omitted, never a placeholder.
"""

# Import necessary libraries
from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+")
_PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
# URL-like token: optional scheme, one or more "label." groups, a TLD, an
# optional path. The lookbehind excludes '@' and word characters so an
# email's own domain (e.g. "...@example.com") is never re-matched as a URL.
_URL_TOKEN_RE = re.compile(
    r"(?<![\w@])(?:https?://)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s,|]*)?"
)
_MAX_NAME_LENGTH = 60


@dataclass
class CandidateIdentity:
    """Whatever contact fields were found in the resume text — never a guess."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    github: str | None = None
    linkedin: str | None = None
    website: str | None = None


def _find_email(text: str) -> str | None:
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else None


def _find_phone(text: str) -> str | None:
    match = _PHONE_RE.search(text)
    return match.group(0) if match else None


def _find_urls(text: str) -> tuple[str | None, str | None, str | None]:
    """Classify URL-like tokens into (github, linkedin, website)."""
    github: str | None = None
    linkedin: str | None = None
    website: str | None = None
    for token in _URL_TOKEN_RE.findall(text):
        lowered = token.lower()
        if "github" in lowered:
            github = github or token
        elif "linkedin" in lowered:
            linkedin = linkedin or token
        else:
            website = website or token
    return github, linkedin, website


def _find_name(text: str) -> str | None:
    """The first non-blank line, if it looks like a name, not a contact field."""
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        if len(candidate) > _MAX_NAME_LENGTH:
            return None
        if any(ch.isdigit() for ch in candidate):
            return None
        if "@" in candidate or "http" in candidate.lower():
            return None
        return candidate
    return None


def extract_candidate_identity(resume_text: str) -> CandidateIdentity:
    """Extract whatever contact fields the resume text contains, deterministically."""
    # Blank out every email match before URL scanning — otherwise an
    # email's local-part (e.g. "sam.lee" in "sam.lee@example.com") can
    # look like its own bare "domain.tld" token and get misclassified
    # as a website.
    text_without_emails = _EMAIL_RE.sub(" ", resume_text)
    github, linkedin, website = _find_urls(text_without_emails)
    return CandidateIdentity(
        name=_find_name(resume_text),
        email=_find_email(resume_text),
        phone=_find_phone(resume_text),
        github=github,
        linkedin=linkedin,
        website=website,
    )


def contact_line(identity: CandidateIdentity) -> str:
    """Join whichever fields were found with ' · ' — an absent field is simply omitted."""
    parts = [
        value
        for value in (identity.email, identity.phone, identity.linkedin, identity.github, identity.website)
        if value
    ]
    return " · ".join(parts)
