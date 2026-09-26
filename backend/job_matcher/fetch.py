"""
File Name: fetch.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
Job-source fetching with guards — ported from the Eve reference's
fetch_job_postings tool. Exactly ONE attempt per source, code-enforced:
there is no retry loop in this module and none may be added (the
no-retry rule is business logic, not an aspect).

This module fetches job content by:
1. Local-file mode: a source that is an existing file path is read
   directly (same byte cap and word guard) — also how offline evals run.
2. URL mode: http/https scheme allowlist; hostname blocklist (loopback,
   private ranges, link-local metadata) checked BEFORE connecting and
   re-checked on the post-redirect URL; browser UA; response byte cap;
   HTML → text extraction; minimum-extractable-words guard (the
   JavaScript-shell detector — the committed failure captures are the
   regression fixtures).
3. ATS mode: a URL on a known applicant-tracking system (see ats.py and
   the ats_rules/ folders) is fetched through that system's public
   posting API instead of its JavaScript page. The API request REPLACES
   the page request — still exactly one attempt, no page fallback.
4. Returning a typed FetchResult (ok/failed + reason) — a failure is
   recorded, never retried, never fabricated into an analysis.

Known residual risk (documented, accepted for the single-user CLI threat
model, same posture as the Eve security baseline): DNS rebinding — the
hostname check does not pin the resolved IP at connect time. Revisit
before any multi-tenant deployment.

Environment Variables (.env at repo root):
- JOB_MIN_WORDS: minimum extractable words (default: 100)
- MAX_FETCH_BYTES: response byte cap (default: 2000000)
"""

# Import necessary libraries
from __future__ import annotations

import html
import ipaddress
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
import structlog
from bs4 import BeautifulSoup

from job_matcher import ats
from job_matcher.config import job_min_words, max_fetch_bytes
from job_matcher.observability import traced

log = structlog.get_logger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0", "::1", "ip6-localhost"}
FETCH_TIMEOUT_SECONDS = 20.0


@dataclass
class FetchResult:
    """The outcome of the single fetch attempt for one job source."""

    job_source: str
    ok: bool
    attempted_at: str
    text: str | None = None
    words: int = 0
    reason: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _blocked_host_reason(host: str | None) -> str | None:
    """Pre-connect SSRF guard: loopback/private/link-local/reserved targets."""
    if not host:
        return "URL has no hostname"
    if host.lower() in BLOCKED_HOSTNAMES:
        return f"blocked hostname: {host}"
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return None  # a DNS name outside the literal blocklist — see module docstring on rebinding
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved or ip.is_unspecified:
        return f"blocked IP range: {host}"
    return None


def html_to_text(html: str) -> str:
    """Visible-text extraction: scripts, styles, and noscript stripped."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def _word_guard(text: str, source: str) -> FetchResult:
    words = len(text.split())
    if words < job_min_words():
        return FetchResult(
            job_source=source,
            ok=False,
            attempted_at=_now(),
            words=words,
            reason=(
                f"only {words} extractable words (minimum {job_min_words()}) — "
                "page may require JavaScript or a login"
            ),
        )
    return FetchResult(job_source=source, ok=True, attempted_at=_now(), text=text, words=words)


def _fetch_local(path: Path, source: str) -> FetchResult:
    if path.stat().st_size > max_fetch_bytes():
        return FetchResult(
            job_source=source, ok=False, attempted_at=_now(),
            reason=f"file exceeds the {max_fetch_bytes()} byte cap",
        )
    text = " ".join(path.read_text(encoding="utf-8", errors="replace").split())
    return _word_guard(text, source)


def _render_posting(posting: ats.AtsPosting) -> str:
    """Turn a rule-extracted posting into the plain text the analyst reads."""
    joined = "\n\n".join(part for part in posting.parts if part)
    if posting.format == "html_escaped":
        joined = html.unescape(joined)
    body = html_to_text(joined) if posting.format != "plain" else " ".join(joined.split())
    header = [posting.title]
    if posting.location:
        header.append(f"Location: {posting.location}")
    if posting.pay:
        header.append(f"Compensation: {posting.pay}")
    return "\n".join(header) + "\n\n" + body


@traced("fetch_job_source")
async def fetch_job_source(source: str, client: httpx.AsyncClient | None = None) -> FetchResult:
    """Make the one and only fetch attempt for a job source. Never retries."""
    # Local-file mode — offline evals and the JS-shell fixtures use this path
    candidate = Path(source)
    if "://" not in source and candidate.is_file():
        try:
            return _fetch_local(candidate, source)
        except OSError as exc:
            return FetchResult(job_source=source, ok=False, attempted_at=_now(), reason=str(exc))

    parsed = urlparse(source)
    if parsed.scheme not in ("http", "https"):
        return FetchResult(
            job_source=source, ok=False, attempted_at=_now(),
            reason=f"unsupported scheme {parsed.scheme!r} (http/https only, or an existing local file)",
        )
    if reason := _blocked_host_reason(parsed.hostname):
        return FetchResult(job_source=source, ok=False, attempted_at=_now(), reason=reason)

    # ATS mode — a known ATS is fetched through its API instead of its page
    try:
        target = ats.resolve(source)
    except ats.AtsRuleError as exc:
        log.warning("ats_rule_error", job_source=source, error=str(exc))
        return FetchResult(job_source=source, ok=False, attempted_at=_now(), reason=f"ATS rule error: {exc}")
    fetch_url, label = source, ""
    if target:
        api = urlparse(target.api_url)
        if api.scheme != "https" or (reason := _blocked_host_reason(api.hostname)):
            return FetchResult(
                job_source=source, ok=False, attempted_at=_now(),
                reason=f"{target.ats} rule produced an unusable API URL",
            )
        fetch_url, label = target.api_url, f"{target.ats} API: "

    own_client = client is None
    client = client or httpx.AsyncClient(follow_redirects=True, timeout=FETCH_TIMEOUT_SECONDS)
    try:
        headers = {"User-Agent": USER_AGENT}
        if target:
            headers["Accept"] = "application/json"
        response = await client.get(fetch_url, headers=headers)
        # Post-redirect re-check: a redirect must not land on a blocked target
        if reason := _blocked_host_reason(response.url.host):
            return FetchResult(
                job_source=source, ok=False, attempted_at=_now(),
                reason=f"{label}redirected to a blocked target — {reason}",
            )
        if response.status_code >= 400:
            return FetchResult(
                job_source=source, ok=False, attempted_at=_now(),
                reason=f"{label}HTTP {response.status_code}",
            )
        if len(response.content) > max_fetch_bytes():
            return FetchResult(
                job_source=source, ok=False, attempted_at=_now(),
                reason=f"{label}response exceeds the {max_fetch_bytes()} byte cap",
            )
        if not target:
            return _word_guard(html_to_text(response.text), source)

        # ATS mode continues: parse the API JSON, run the extract rule, guard the words
        try:
            body = response.json()
        except ValueError:
            return FetchResult(
                job_source=source, ok=False, attempted_at=_now(),
                reason=f"{label}response was not valid JSON",
            )
        try:
            posting = ats.extract(target, body)
        except ats.AtsRuleError as exc:
            log.warning("ats_rule_error", job_source=source, error=str(exc))
            return FetchResult(job_source=source, ok=False, attempted_at=_now(), reason=f"ATS rule error: {exc}")
        if posting is None:
            return FetchResult(
                job_source=source, ok=False, attempted_at=_now(),
                reason=f"job {target.job_id} not found on the {target.ats} board — it may have been closed",
            )
        return _word_guard(_render_posting(posting), source)
    except httpx.HTTPError as exc:
        log.info("job_fetch_failed", job_source=source, error=str(exc))
        return FetchResult(job_source=source, ok=False, attempted_at=_now(), reason=f"{label}fetch error: {exc}")
    finally:
        if own_client:
            await client.aclose()
