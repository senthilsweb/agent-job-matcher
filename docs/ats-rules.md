# ATS rules

At the end you will know which job boards are read through their own API,
how each one is described in a small rule file, and how to add another
without touching Python.

Ashby, Greenhouse, and Lever draw their job pages with JavaScript, so a
plain page fetch sees an empty shell and fails the minimum-words guard.
Each of them also serves the same posting as public JSON. The fetcher
recognizes their URLs and reads that JSON instead.

## What is supported

| ATS | Example URL | Reads from |
|---|---|---|
| Ashby | `jobs.ashbyhq.com/<company>/<job-id>` | the company's public job board API |
| Greenhouse | `job-boards.greenhouse.io/<company>/jobs/<id>` | the public boards API |
| Lever | `jobs.lever.co/<company>/<job-id>` | the public postings API |

Anything else takes the normal page fetch. If that page is a JavaScript
shell you still get the same readable failure as before.

## How a rule set works

Each ATS is a folder of two JSON files in `backend/job_matcher/ats_rules/`:

| File | Question it answers | Input | Output |
|---|---|---|---|
| `resolve.json` | Is this URL mine, and where is its API? | host and path segments | `ats`, `api_url`, `job_id` |
| `extract.json` | Where is the posting in the response? | API JSON and job id | `title`, `location`, `parts`, `format`, `pay` |

The rules only decide what to fetch and where the text sits. The request,
size cap, blocked-host check, and word guard stay in Python, and a known
ATS still gets exactly one request with no fallback to the page.

The files use the [GoRules](https://gorules.io) decision format, run by the
`zen-engine` package. `resolve.json` is a decision table with one row per
URL shape. `extract.json` is a list of expressions.

## Add an ATS

1. Find the ATS's public posting API and save one real response under
   `backend/tests/fixtures/ats/`.
2. Copy an existing folder, for example `ashby`, to `ats_rules/<name>/`.
3. Edit the host, the API address, and the field paths in the two files.
4. Add a fetch test beside the existing ones and run `pytest backend -m "not live"`.

To try a rule set without touching the package, put the folder anywhere and
point `ATS_RULES_DIR` at its parent. A folder with the same name as a
packaged one replaces it.

## When a fetch fails

| Reason shown | Meaning |
|---|---|
| `ashby API: HTTP 404` | the company board does not exist or is private |
| `job <id> not found on the ashby board` | the posting was closed or the id is wrong |
| `ATS rule error: ...` | a rule file is broken; the message names it |
| `only N extractable words ...` | the posting was found but is too short |

Next: [Runbook](runbook.md).
