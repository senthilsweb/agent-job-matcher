# Design: ATS rules engine

## Two rules per ATS, HTTP stays in code

An ATS needs two decisions with a network call between them, so it is two
rule files rather than one graph:

```
job URL ─▶ resolve rule ─▶ {ats, api_url, job_id}
                              │  Python: guards + ONE GET
                              ▼
API JSON ─▶ extract rule ─▶ {title, location, parts[], format, pay?}
                              │  Python: unescape/strip HTML, word guard
                              ▼
                        FetchResult (existing type)
```

The rules only decide *what to fetch* and *where the text is*. Fetching,
size caps, SSRF checks, and the word guard remain ordinary Python.

## Rule format

GoRules JDM JSON. `resolve` is a decision table (hit policy `first`) with
one row per URL shape; an unmatched input yields an empty result. `extract`
is an expression node; each expression is self-contained, because keys
produced in one expression are not visible to the next.

**Not-found contract:** the engine drops any expression that fails, so an
`extract` rule that cannot find the job returns no `title`. Python treats a
missing `title` as "job not on the board".

`format` is one of `plain`, `html`, `html_escaped` (Greenhouse returns
entity-escaped HTML). Python does the conversion so rules stay declarative.

## Safety

- URL segments are validated against `^[A-Za-z0-9._~-]+$` before they reach
  a rule. Any other character means no match, so a crafted URL cannot
  change the host or path of the API call.
- The rule-produced `api_url` must be `https` and passes the existing
  blocked-host check. The post-redirect re-check applies as before.
- Rule files are trusted operator config, like prompt files. An
  `ATS_RULES_DIR` override is therefore an operator choice, not user input.

## The one-attempt rule

`fetch.py` guarantees exactly one attempt per source. For a known ATS the
API request *replaces* the page request. If it fails, the failure is
recorded with an ATS-specific reason. There is no fallback to the page:
that would be a second attempt, and the page is known to be a shell.

## Failure taxonomy

| Case | Result |
|---|---|
| Host not in any rule | existing HTML path, unchanged |
| Host known, path malformed | existing HTML path, unchanged |
| API HTTP error / oversize / blocked | failed, reason names the ATS |
| Job id absent from the board | failed, "not found on the <ats> board" |
| Extracted text under the word minimum | failed, existing word-guard reason |
| Rule engine error | failed, "ATS rule error", logged, never raised |

## Telemetry and logging

Structured log events only (`ats_matched`, `ats_extract_empty`). No
instrumentation calls inside function bodies: the new public functions
carry `@traced`.

## Alternatives considered

- **Python branch per ATS** — simplest today, but every board is a code
  change and an image rebuild.
- **JSONata / JMESPath** — fine for extraction, weak for URL routing.
- **Golang or JavaScript engine** — the backend is Python; ZEN's Python
  binding runs the same JDM files, so no second runtime is needed.
