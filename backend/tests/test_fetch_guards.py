"""
File Name: test_fetch_guards.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Fetch-guard eval (no LLM, no network) — the committed JS-shell captures
are the regression fixtures; every guard must trip BEFORE any network
connection so this suite is safe offline.

This suite pins the guards by:
1. The two real JS-shell captures fail the min-words guard with a clear
   reason; a real JD snapshot passes.
2. Scheme allowlist (http/https/local file only) and SSRF hostname
   blocklist (loopback, private ranges, metadata IP) reject
   pre-connect.
3. Byte cap applies to local files too.
"""

# Import necessary libraries
from pathlib import Path

import pytest

from job_matcher.fetch import fetch_job_source, html_to_text

FIXTURES = Path(__file__).parent.parent / "evals" / "data" / "jobs"

JS_SHELLS = [
    FIXTURES / "failures" / "adp-workforcenow-566276.js-shell.html",
    FIXTURES / "failures" / "senior-manager-ai-agents-and-automation-jerry-ai.js-shell.html",
]


@pytest.mark.parametrize("fixture", JS_SHELLS, ids=lambda p: p.name)
async def test_js_shell_captures_fail_min_words(fixture):
    # The raw HTML shells contain script payloads; the guard applies to the
    # extractable text, mirroring the real fetch path.
    text = html_to_text(fixture.read_text(encoding="utf-8", errors="replace"))
    words = len(text.split())
    assert words < 100, f"fixture unexpectedly rich: {words} words"

    result = await fetch_job_source(str(fixture.with_suffix("").with_suffix("")) + ".extracted.txt")
    assert not result.ok
    assert "extractable words" in (result.reason or "")


async def test_real_jd_snapshot_passes():
    result = await fetch_job_source(str(FIXTURES / "data-engineering-manager-product-anthropic.txt"))
    assert result.ok
    assert result.words >= 100
    assert result.text


@pytest.mark.parametrize(
    "url,fragment",
    [
        ("ftp://example.com/jd.txt", "unsupported scheme"),
        ("file:///etc/passwd", "unsupported scheme"),
        ("http://localhost/jd", "blocked hostname"),
        ("http://127.0.0.1/jd", "blocked IP"),
        ("http://10.0.0.8/jd", "blocked IP"),
        ("http://192.168.1.5/jd", "blocked IP"),
        ("http://169.254.169.254/latest/meta-data", "blocked IP"),
        ("http://0.0.0.0/jd", "blocked"),
    ],
)
async def test_scheme_and_ssrf_guards_block_preconnect(url, fragment):
    result = await fetch_job_source(url)
    assert not result.ok
    assert fragment.lower() in (result.reason or "").lower()


async def test_local_file_byte_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("MAX_FETCH_BYTES", "100")
    p = tmp_path / "huge-jd.txt"
    p.write_text("job requirements " * 500)
    result = await fetch_job_source(str(p))
    assert not result.ok
    assert "byte cap" in (result.reason or "")


async def test_missing_local_file_treated_as_bad_source(tmp_path):
    result = await fetch_job_source(str(tmp_path / "missing-jd.txt"))
    assert not result.ok  # not a file, not a URL scheme we allow


def test_html_to_text_strips_scripts():
    html = "<html><script>var x=1;</script><body><p>Data Engineer role</p></body></html>"
    text = html_to_text(html)
    assert "Data Engineer role" in text
    assert "var x" not in text
