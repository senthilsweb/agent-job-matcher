"""
File Name: test_ats_rules.py
Author: Senthilnathan Karuppaiah
Date: 26-SEP-2026
Description:
Offline eval of the ATS rules engine (no LLM, no network) — real API
responses committed under tests/fixtures/ats are served through an
httpx MockTransport, so the exact fetch path runs without a connection.

This suite pins the behavior by:
1. Resolve rules: each ATS URL shape maps to its API target; unknown
   hosts, malformed paths, and unsafe path segments match nothing.
2. Fetch: Ashby, Greenhouse, and Lever postings become report-ready text
   with title, location, and compensation, using exactly one request.
3. Failure taxonomy: job missing from the board, HTTP error, invalid JSON
   and broken rules each yield a typed failure — never an exception and
   never a fallback to the JavaScript page.
4. Rules are data: an override folder adds a new ATS with no Python change.
"""

# Import necessary libraries
import json
import shutil
from pathlib import Path

import httpx
import pytest

from job_matcher import ats
from job_matcher.fetch import fetch_job_source

FIXTURES = Path(__file__).parent / "fixtures" / "ats"

ASHBY_URL = "https://jobs.ashbyhq.com/scan-com/9e9e2b43-defd-4444-a469-5b79333e969d"
ASHBY_NO_PAY_URL = "https://jobs.ashbyhq.com/scan-com/bd794304-8343-422c-9919-b7cb044a87d7"
GREENHOUSE_URL = "https://job-boards.greenhouse.io/anthropic/jobs/4461450008"
LEVER_URL = "https://jobs.lever.co/palantir/6ed76ce8-4156-4b60-b120-403538bd66cd"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _client(handler) -> tuple[httpx.AsyncClient, list[httpx.Request]]:
    """An AsyncClient whose every request is recorded and answered by handler."""
    seen: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    return httpx.AsyncClient(transport=httpx.MockTransport(record), follow_redirects=True), seen


def _serve(body: dict, status: int = 200):
    return lambda request: httpx.Response(status, json=body)


# ---- resolve rules ------------------------------------------------------


@pytest.mark.parametrize(
    "url,ats_name,api_url,job_id",
    [
        (ASHBY_URL, "ashby",
         "https://api.ashbyhq.com/posting-api/job-board/scan-com?includeCompensation=true",
         "9e9e2b43-defd-4444-a469-5b79333e969d"),
        (ASHBY_URL + "/application", "ashby",
         "https://api.ashbyhq.com/posting-api/job-board/scan-com?includeCompensation=true",
         "9e9e2b43-defd-4444-a469-5b79333e969d"),
        (GREENHOUSE_URL, "greenhouse",
         "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/4461450008?pay_transparency=true", "4461450008"),
        ("https://boards.greenhouse.io/anthropic/jobs/4461450008?gh_src=x", "greenhouse",
         "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/4461450008?pay_transparency=true", "4461450008"),
        (LEVER_URL, "lever",
         "https://api.lever.co/v0/postings/palantir/6ed76ce8-4156-4b60-b120-403538bd66cd",
         "6ed76ce8-4156-4b60-b120-403538bd66cd"),
    ],
)
def test_resolve_maps_each_ats_url_shape(url, ats_name, api_url, job_id):
    target = ats.resolve(url)
    assert target is not None
    assert (target.ats, target.api_url, target.job_id) == (ats_name, api_url, job_id)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/careers/123",                       # unknown host
        "https://jobs.ashbyhq.com/scan-com",                     # known host, too few segments
        "https://boards.greenhouse.io/anthropic/embed/job_app",  # known host, wrong shape
        "https://jobs.lever.co/",                                # no path at all
        "https://jobs.ashbyhq.com/scan-com/..%2f..%2fadmin",     # unsafe segment
        "https://jobs.ashbyhq.com/scan com/abc",                 # unsafe segment
    ],
)
def test_resolve_returns_none_when_nothing_matches(url):
    assert ats.resolve(url) is None


# ---- fetch through the API ---------------------------------------------


async def test_ashby_posting_becomes_report_ready_text_in_one_request():
    client, seen = _client(_serve(_fixture("ashby_scan-com.json")))
    result = await fetch_job_source(ASHBY_URL, client=client)
    assert result.ok, result.reason
    assert result.words >= 100
    assert result.text.startswith("Senior Engineering Manager\nLocation: New York City\nCompensation: $180K")
    assert len(seen) == 1
    assert str(seen[0].url) == "https://api.ashbyhq.com/posting-api/job-board/scan-com?includeCompensation=true"


async def test_ashby_posting_without_compensation_has_no_compensation_line():
    client, _ = _client(_serve(_fixture("ashby_scan-com.json")))
    result = await fetch_job_source(ASHBY_NO_PAY_URL, client=client)
    assert result.ok, result.reason
    assert "Compensation:" not in result.text


async def test_greenhouse_escaped_html_is_unescaped_to_plain_text():
    client, seen = _client(_serve(_fixture("greenhouse_anthropic_4461450008.json")))
    result = await fetch_job_source(GREENHOUSE_URL, client=client)
    assert result.ok, result.reason
    assert "&lt;" not in result.text and "<div" not in result.text
    assert "Account Executive" in result.text.splitlines()[0]
    assert "Compensation: Annual Salary:" in result.text
    assert len(seen) == 1


async def test_lever_description_and_requirement_lists_are_both_included():
    body = _fixture("lever_palantir_6ed76ce8.json")
    client, _ = _client(_serve(body))
    result = await fetch_job_source(LEVER_URL, client=client)
    assert result.ok, result.reason
    assert body["lists"][0]["text"].strip(" :") in result.text
    assert "<li>" not in result.text


async def test_greenhouse_posting_without_pay_ranges_still_extracts():
    # Regression: live responses omit pay_input_ranges entirely when there is no pay data
    body = {k: v for k, v in _fixture("greenhouse_anthropic_4461450008.json").items() if k != "pay_input_ranges"}
    client, _ = _client(_serve(body))
    result = await fetch_job_source(GREENHOUSE_URL, client=client)
    assert result.ok, result.reason
    assert "Compensation:" not in result.text


async def test_lever_posting_without_requirement_lists_still_extracts():
    body = {k: v for k, v in _fixture("lever_palantir_6ed76ce8.json").items() if k != "lists"}
    client, _ = _client(_serve(body))
    result = await fetch_job_source(LEVER_URL, client=client)
    assert result.ok, result.reason


# ---- failure taxonomy ---------------------------------------------------


async def test_job_missing_from_the_board_is_a_typed_failure():
    missing = "https://jobs.ashbyhq.com/scan-com/00000000-0000-0000-0000-000000000000"
    client, seen = _client(_serve(_fixture("ashby_scan-com.json")))
    result = await fetch_job_source(missing, client=client)
    assert not result.ok
    assert "not found on the ashby board" in result.reason
    assert len(seen) == 1


async def test_api_http_error_fails_with_ats_reason_and_never_falls_back_to_the_page():
    client, seen = _client(lambda request: httpx.Response(500))
    result = await fetch_job_source(ASHBY_URL, client=client)
    assert not result.ok
    assert result.reason == "ashby API: HTTP 500"
    assert len(seen) == 1, "exactly one attempt — no fallback to the HTML page"
    assert seen[0].url.host == "api.ashbyhq.com"


async def test_non_json_api_response_is_a_typed_failure():
    client, _ = _client(lambda request: httpx.Response(200, text="<html>nope</html>"))
    result = await fetch_job_source(LEVER_URL, client=client)
    assert not result.ok
    assert "not valid JSON" in result.reason


async def test_unknown_host_still_takes_the_html_path_unchanged():
    url = "https://careers.example.org/job/123"
    client, seen = _client(lambda request: httpx.Response(200, text="<html><body>tiny page</body></html>"))
    result = await fetch_job_source(url, client=client)
    assert not result.ok
    assert "extractable words" in result.reason
    assert str(seen[0].url) == url


# ---- rules are data ------------------------------------------------------


def _override_dir(tmp_path: Path) -> Path:
    """A rules folder holding a copy of the Ashby rules retargeted to a made-up ATS."""
    packaged = Path(ats.PACKAGED_RULES) / "ashby"
    target = tmp_path / "rules" / "acme"
    shutil.copytree(packaged, target)
    for f in target.glob("*.json"):
        f.write_text(
            f.read_text(encoding="utf-8")
            .replace("jobs.ashbyhq.com", "careers.acme.test")
            .replace("api.ashbyhq.com/posting-api/job-board", "api.acme.test/boards")
            .replace('"ashby"', '"acme"'),
            encoding="utf-8",
        )
    return tmp_path / "rules"


async def test_override_folder_adds_a_new_ats_without_any_python_change(tmp_path, monkeypatch):
    monkeypatch.setenv("ATS_RULES_DIR", str(_override_dir(tmp_path)))
    body = _fixture("ashby_scan-com.json")
    client, seen = _client(_serve(body))
    result = await fetch_job_source(
        "https://careers.acme.test/scan-com/9e9e2b43-defd-4444-a469-5b79333e969d", client=client
    )
    assert result.ok, result.reason
    assert seen[0].url.host == "api.acme.test"
    # the packaged ATS rules keep working alongside the override
    assert ats.resolve(ASHBY_URL).ats == "ashby"


async def test_broken_rule_is_a_typed_failure_not_an_exception(tmp_path, monkeypatch):
    rules = _override_dir(tmp_path)
    (rules / "acme" / "extract.json").write_text('{"nodes": []}', encoding="utf-8")  # not a valid decision
    monkeypatch.setenv("ATS_RULES_DIR", str(rules))
    client, _ = _client(_serve(_fixture("ashby_scan-com.json")))
    result = await fetch_job_source("https://careers.acme.test/scan-com/abc", client=client)
    assert not result.ok
    assert result.reason.startswith("ATS rule error")


def test_packaged_rule_sets_are_complete():
    names = sorted(p.name for p in Path(ats.PACKAGED_RULES).iterdir() if p.is_dir())
    assert {"ashby", "greenhouse", "lever"} <= set(names)
    for name in names:
        for rule in ("resolve.json", "extract.json"):
            assert (Path(ats.PACKAGED_RULES) / name / rule).is_file(), f"{name}/{rule} missing"
