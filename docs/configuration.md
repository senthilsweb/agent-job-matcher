# Configuration

At the end you will know every environment variable, how model ids
resolve, and how to override prompts and the cover-letter template.
Everything is configured through the root `.env` —
[.env.example](https://github.com/senthilsweb/agent-job-matcher/blob/main/.env.example)
is the full, authoritative list. Nothing in source carries a default
credential or endpoint; missing required config is a startup error by
design.

## Models — the resolution chain

Two LLM operations exist in the whole system, each with its own
variable:

| Variable | Operation | Resolution order |
|---|---|---|
| `MODEL_ANALYST` | LLM-1: typed extraction in the backend core (**required**) | `MODEL_ANALYST` → `MODEL` → startup error |
| `MODEL_CHAT` | LLM-2: chat orchestration in the agent service (optional) | `MODEL_CHAT` → `MODEL_ANALYST` → `MODEL` → error |

Model ids are provider-prefixed strings resolved directly against the
provider's native API — `openai:gpt-5.4-mini`,
`anthropic:claude-haiku-4-5` — so set the matching key:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | for `openai:*` model ids |
| `ANTHROPIC_API_KEY` | for `anthropic:*` model ids |

There is no gateway or proxy in the path
([FAQ: direct provider calls](faq.md#why-direct-provider-calls-instead-of-a-gateway)).

## Analysis behavior

| Variable | Purpose |
|---|---|
| `JOB_FANOUT_CONCURRENCY` | max jobs analyzed in parallel per request (default 3) |
| `TEMPLATES_DIR` | directory checked before the package defaults for prompt files and `cover_letter.txt` |

### Cover letter template

Every job report includes `cover_letter_text`, rendered from the LLM's
typed paragraphs through a plain-text template — the LLM never formats
or scores. Placeholders: `{{candidate_name}}`,
`{{candidate_contact_line}}`, `{{date}}`, `{{re_line}}`,
`{{cover_letter_body}}`; unknown placeholders are left intact rather
than erroring. To customize, put your own `cover_letter.txt` in
`TEMPLATES_DIR` — no code change. The shipped default:
[backend/job_matcher/templates/cover_letter.txt](https://github.com/senthilsweb/agent-job-matcher/blob/main/backend/job_matcher/templates/cover_letter.txt).

## Agent service (chat bridge)

| Variable | Purpose |
|---|---|
| `JOBMATCHER_API_URL` | where the MCP server reaches the backend REST API |
| `AGENT_UPLOAD_DIR` | landing directory for uploaded resumes |
| `AGENT_PORT` | agent service port (default 8006 native; 6011 in the compose stack) |

## Telemetry activates by env alone

Structured JSON logs are always on. Adding a remote backend is done by
setting that backend's own variables — never by a code change
(AGENTS.md rule 3). Fill any one block:

| Backend | Variables |
|---|---|
| OpenObserve (REST, no extra deps) | `OPENOBSERVE_URL`, `OPENOBSERVE_ORG`, `OPENOBSERVE_STREAM`, `OPENOBSERVE_USER`, `OPENOBSERVE_PASSWORD` |
| Any OTLP collector | `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS` |
| Arize Phoenix | `PHOENIX_COLLECTOR_ENDPOINT`, `PHOENIX_API_KEY` |
| Arize AX | `ARIZE_SPACE_ID`, `ARIZE_API_KEY`, `ARIZE_PROJECT_NAME` |

The OTLP-shaped backends need `pip install "job-matcher[otel]"`.
`TELEMETRY_RECORD_IO=true` additionally records prompt/response
payloads. Telemetry delivery failures are logged and swallowed — they
never fail a run.

## Where secrets go

Only in `.env` (git-ignored) locally, and in GitHub Actions secrets in
CI — the [Runbook](runbook.md#github-secrets-and-variables-from-the-command-line)
has the one-liner that syncs a key from `.env` to GitHub. Never in
source, comments, examples, or "placeholder" defaults.

Next: [Surfaces](surfaces.md).
