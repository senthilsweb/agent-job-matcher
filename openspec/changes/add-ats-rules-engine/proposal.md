# Proposal: ATS rules engine for JavaScript-rendered job boards

> Status: **IMPLEMENTED, verified locally** (2026-09-26) — owner UAT observation: an Ashby
> posting (`jobs.ashbyhq.com/scan-com/...`) failed with "only 14
> extractable words — page may require JavaScript or a login". The
> min-words guard is working as designed; the page really is a
> JavaScript shell. Owner: @senthilsweb

## Why

Ashby, Greenhouse, and Lever render job pages client-side, so the HTML
fetcher sees a shell. Each of them also publishes a public, no-login
JSON API for the same posting. Hard-coding one Python branch per ATS
would make every new board a code change, a release, and an image
rebuild. The owner asked for something simple to maintain: a rules or
expression engine with one small rule set per ATS, and a plain failure
for anything unrecognised.

## What changes

- New dependency: `zen-engine` (GoRules ZEN, Python binding, Rust core).
  Wheels exist for linux x86_64 and aarch64, so the Docker images are
  unaffected.
- New module `job_matcher/ats.py` evaluates **two rules per ATS**:
  - `resolve` — input: the job URL's host and path segments; output:
    `ats`, `api_url`, `job_id`. An empty result means "not a known ATS".
  - `extract` — input: the parsed API JSON and the job id; output:
    `title`, `location`, `parts`, `format`, optional `pay`.
- Rules are plain JSON files, one folder per ATS, shipped inside the
  package: `job_matcher/ats_rules/<ats>/{resolve,extract}.json`. An
  optional `ATS_RULES_DIR` env var adds an override folder checked first.
- `fetch.py` calls `ats.resolve` before the HTML path. A known ATS is
  fetched through its API (the HTTP call stays in Python, with every
  existing guard). An unknown site takes today's path unchanged.
- First three rule sets: **Ashby, Greenhouse, Lever**.

## Out of scope

- Any ATS that needs authentication or JavaScript execution.
- Workday, iCIMS, and other boards with no public posting API: they keep
  failing with the existing readable reason ("exception" path).
- Custom career domains that embed Greenhouse via `?gh_jid=`: the host
  does not identify the ATS, so no rule matches.
- Editing rules through a UI. The files are hand-editable JSON.

## Acceptance criteria

1. The Ashby URL from the UAT report resolves to the board API and
   yields a report-ready posting of at least the minimum word count.
2. Greenhouse and Lever URLs do the same, each proven by an offline test
   against a committed real API response.
3. An unrecognised host, a recognised host with a malformed path, and a
   job id that is not on the board each produce a typed failure. None
   raises, and none fabricates text.
4. A known ATS makes exactly one HTTP request. There is no fallback to
   the HTML page after an API failure.
5. Adding a fourth ATS requires only a new rules folder and a fixture.
6. The wheel built from `backend/` contains the rule files, and both
   Docker images built from this repo start and resolve an Ashby URL.
