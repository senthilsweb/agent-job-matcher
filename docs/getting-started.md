# Getting Started

Three paths in. Each takes about five minutes and stands on its own.
All of them need a model configured first:

```bash
git clone https://github.com/senthilsweb/agent-job-matcher && cd agent-job-matcher
cp .env.example .env     # set MODEL_ANALYST + the matching provider key
```

`MODEL_ANALYST` is the extraction model (for example
`openai:gpt-5.4-mini` or `anthropic:claude-haiku-4-5`); set
`OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to match. That is the only
required configuration — details in [Configuration](configuration.md).

## Path 1 — The demo stack (needs only Docker)

At the end you will have a browser form that turns a resume plus job
links into visual fit reports.

```bash
docker compose up -d
open http://localhost:6012      # the playground
```

Upload a resume, add one or more job posting URLs, and read the
rendered 40/20/20/20 breakdown per job. The whole product runs
containerized on one consistent port series:

| Port | Service |
|---|---|
| 6010 | REST backend (`/analyze`) |
| 6011 | agent service (chat bridge + MCP server) |
| 6012 | playground — the visual demo form |
| 6013 | browsable, branded API reference |
| 6014 | chat-widget demo page |

## Path 2 — The CLI

At the end you will have a ranked fit summary in your terminal and
full artifacts on disk.

```bash
pip install -e "backend[dev]"

jobmatch analyze --resume my-resume.pdf \
  --job https://boards.example.com/job/123 \
  --job local-jd.txt
# → ranked summary on stdout; full artifacts under runs/<timestamp>/
```

`--job` accepts URLs and local files, repeated as many times as you
like. Exit code 0 means the run completed.

## Path 3 — One REST call

At the end you will have the typed JSON report array from the API.

```bash
docker compose up -d api        # backend only, on :6010
curl -s http://localhost:6010/health
curl -s -X POST http://localhost:6010/analyze \
  -F "resume=@my-resume.pdf" \
  -F "job=https://boards.example.com/job/123"
```

The response is a JSON array of `JobReport` / `JobFetchFailure`
objects — every field typed and validated. Full request/response
schemas with real examples live in the API's own `/docs` (Swagger UI)
or the branded reference on port 6013.

## What next

- All install options (pip, image, stack) → [Installation](installation.md)
- Every environment variable → [Configuration](configuration.md)
- The four integration surfaces → [Surfaces](surfaces.md)
