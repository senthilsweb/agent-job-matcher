"""
File Name: test_slug_naming.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Filename-contract eval (no LLM) — the slug and report-name rules from
evals/rubrics.md, including the security property that adversarial job
titles cannot traverse paths.

This suite pins the contract by:
1. slugify strips every character outside [a-z0-9-]; '.' and '/' cannot
   survive it (path traversal impossible by construction).
2. report_filename matches the pinned regex for ok and failed variants.
3. write_json_artifact rejects absolute and '..' paths.
"""

# Import necessary libraries
import pytest
from pydantic import BaseModel

from job_matcher.report import (
    REPORT_FILENAME_RE,
    assert_safe_relative,
    report_filename,
    run_timestamp,
    slugify,
    write_json_artifact,
)


def test_slugify_basic():
    assert slugify("Senior Data Engineer, Acme!") == "senior-data-engineer-acme"


def test_slugify_strips_traversal_characters():
    assert "/" not in slugify("../../etc/passwd")
    assert "." not in slugify("../../etc/passwd")
    assert slugify("../../etc/passwd") == "etc-passwd"


def test_slugify_empty_falls_back():
    assert slugify("!!!") == "job"


def test_report_filename_matches_contract():
    ts = run_timestamp()
    ok = report_filename("Senior Data Engineer, Acme", ts)
    failed = report_filename("https://jobs.example.com/123", ts, failed=True)
    assert REPORT_FILENAME_RE.match(ok), ok
    assert REPORT_FILENAME_RE.match(failed), failed
    assert failed.endswith(".failed.json")


def test_unsafe_artifact_paths_rejected(tmp_path):
    class Payload(BaseModel):
        x: int = 1

    for bad in ("/absolute.json", "../escape.json", "a/../../b.json"):
        with pytest.raises(ValueError):
            assert_safe_relative(bad)
        with pytest.raises(ValueError):
            write_json_artifact(tmp_path, bad, Payload())


def test_write_json_artifact_writes_valid_json(tmp_path):
    class Payload(BaseModel):
        x: int = 1

    target = write_json_artifact(tmp_path, "sub/report.json", Payload())
    assert target.read_text().strip().startswith("{")
