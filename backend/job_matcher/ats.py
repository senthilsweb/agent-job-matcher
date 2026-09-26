"""
File Name: ats.py
Author: Senthilnathan Karuppaiah
Date: 26-SEP-2026
Description:
ATS rules — resolves a job URL on a known applicant-tracking system to
that system's public posting API, and pulls the posting text out of the
API response. The routing and field-picking logic lives in JSON rule
files (GoRules ZEN decisions), one folder per ATS, so supporting a new
ATS means adding a folder, not changing Python. The HTTP call itself
stays in fetch.py with all of its guards.

This module works by:
1. Loading every ats_rules/<ats>/{resolve,extract}.json — the override
   folder $ATS_RULES_DIR first, then the packaged rules — once per process.
2. resolve(url): validating the URL's path segments, then asking each
   ATS's resolve rule in name order; the first non-empty answer wins.
3. extract(target, body): running that ATS's extract rule over the parsed
   API JSON and validating the output as an AtsPosting.
4. Raising AtsRuleError only for a broken rule or invalid rule output —
   "not a known ATS" and "job not on the board" (extract output without a
   title) are ordinary None results.

Requirements:
- zen-engine (GoRules ZEN decision engine, Python binding)

Environment Variables (.env at repo root):
- ATS_RULES_DIR: optional folder of extra/override ATS rule sets
"""

# Import necessary libraries
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import structlog
import zen
from pydantic import BaseModel, ValidationError

from job_matcher.config import ats_rules_dir
from job_matcher.observability import traced

log = structlog.get_logger(__name__)

PACKAGED_RULES = Path(__file__).parent / "ats_rules"
# Path segments must be plain tokens so a crafted URL cannot alter the API call
SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9._~-]+$")


class AtsRuleError(RuntimeError):
    """A rule file is broken or produced output that breaks its contract."""


class AtsTarget(BaseModel):
    """Output contract of a resolve rule: where to fetch and which job."""

    ats: str
    api_url: str
    job_id: str


class AtsPosting(BaseModel):
    """Output contract of an extract rule: the posting, before rendering."""

    title: str
    location: str | None = None
    parts: list[str | None]
    format: Literal["plain", "html", "html_escaped"]
    pay: str | None = None


class _RuleSet:
    """The two compiled decisions of one ATS."""

    def __init__(self, name: str, resolve: Any, extract: Any) -> None:
        self.name = name
        self.resolve = resolve
        self.extract = extract


def _load_folder(base: Path, engine: Any, into: dict[str, _RuleSet]) -> None:
    for folder in sorted(p for p in base.iterdir() if p.is_dir()):
        resolve_file, extract_file = folder / "resolve.json", folder / "extract.json"
        if not (resolve_file.is_file() and extract_file.is_file()):
            continue
        try:
            into[folder.name] = _RuleSet(
                folder.name,
                engine.create_decision(resolve_file.read_text(encoding="utf-8")),
                engine.create_decision(extract_file.read_text(encoding="utf-8")),
            )
        except Exception as exc:  # engine raises a plain RuntimeError for bad JDM
            raise AtsRuleError(f"cannot load ATS rules for {folder.name!r}: {exc}") from exc


@lru_cache(maxsize=4)
def _rule_sets(override_dir: str) -> dict[str, _RuleSet]:
    engine = zen.ZenEngine()
    sets: dict[str, _RuleSet] = {}
    _load_folder(PACKAGED_RULES, engine, sets)
    if override_dir:
        override = Path(override_dir)
        if not override.is_dir():
            raise AtsRuleError(f"ATS_RULES_DIR is not a directory: {override_dir}")
        _load_folder(override, engine, sets)  # same folder name replaces the packaged set
    return dict(sorted(sets.items()))


def _evaluate(decision: Any, payload: dict[str, Any], what: str) -> dict[str, Any]:
    try:
        return decision.evaluate(payload).get("result") or {}
    except Exception as exc:
        raise AtsRuleError(f"{what} rule failed: {exc}") from exc


@traced("ats_resolve")
def resolve(url: str) -> AtsTarget | None:
    """Return the API target for a known-ATS URL, or None when no rule matches."""
    parsed = urlparse(url)
    segments = [s for s in parsed.path.split("/") if s]
    if not parsed.hostname or not segments or not all(SAFE_SEGMENT.match(s) for s in segments):
        return None
    payload = {"url": url, "host": parsed.hostname.lower(), "segments": segments}
    for name, rules in _rule_sets(ats_rules_dir()).items():
        answer = _evaluate(rules.resolve, payload, f"{name} resolve")
        if not answer:
            continue
        try:
            target = AtsTarget.model_validate(answer)
        except ValidationError as exc:
            raise AtsRuleError(f"{name} resolve rule output is invalid: {exc}") from exc
        log.info("ats_matched", ats=target.ats, job_id=target.job_id)
        return target
    return None


@traced("ats_extract")
def extract(target: AtsTarget, body: Any) -> AtsPosting | None:
    """Return the posting from an ATS API body, or None when the job is not in it."""
    rules = _rule_sets(ats_rules_dir()).get(target.ats)
    if rules is None:
        raise AtsRuleError(f"no rule set named {target.ats!r}")
    answer = _evaluate(rules.extract, {"body": body, "job_id": target.job_id}, f"{target.ats} extract")
    # Contract: a rule that cannot find the job leaves `title` out (the engine drops
    # any expression that fails), so a missing title means "not on the board".
    if not answer.get("title"):
        log.info("ats_extract_empty", ats=target.ats, job_id=target.job_id)
        return None
    try:
        return AtsPosting.model_validate(answer)
    except ValidationError as exc:
        raise AtsRuleError(f"{target.ats} extract rule output is invalid: {exc}") from exc
