# Job Matcher Backend Specification

## Requirement: Layered core with three access surfaces
The backend SHALL be structured as an interface-agnostic core (service layer) exposing the analysis use case, with exactly three thin adapters over it: a CLI, a FastAPI REST API, and the importable Python package itself (the embeddable-core surface for in-process GenAI callers). No business rule SHALL live in an adapter; adapters SHALL only translate their protocol to and from service-layer calls. Feature parity across surfaces SHALL NOT be required — each surface serves the same use case with the ergonomics native to it — but any behaviour shared by two surfaces (report schema, scoring, run persistence) SHALL be identical because it executes the same core code path.

## Requirement: CLI invocation
The backend SHALL provide a CLI entry point (`jobmatch analyze`) accepting one `--resume` file (PDF, DOCX, TXT, or Markdown) and one or more `--job` sources (public http/https URLs and/or local job-description text files). It SHALL run to completion without interactive input. A run that completes — including one in which every job source fails — SHALL exit 0; a nonzero exit is reserved for operator errors (missing resume file, unreadable/scanned resume, missing model configuration).

## Requirement: REST API for key operations
The backend SHALL expose the key operations over a FastAPI application servable by uvicorn: submitting an analysis (`POST /analyze`, resume as multipart upload or server-side path, plus job sources), listing and retrieving persisted runs and their reports (`GET /runs`, `GET /runs/{run_id}`, `GET /runs/{run_id}/reports`), deterministic scoring of a caller-supplied analysis (`POST /score`, no LLM call), and a health check (`GET /health`). API-triggered analyses SHALL execute synchronously in v1, SHALL return the report JSON in the response, and SHALL persist the run under `runs/` identically to a CLI run. The API SHALL bind to localhost by default and SHALL NOT implement authentication in this change.

## Requirement: Embeddable core surface
The package root (`job_matcher`) SHALL re-export a stable core API — at minimum the run/analysis entry point and the deterministic scoring functions — callable in-process with plain Python types and Pydantic models, requiring neither the CLI nor the HTTP server. A smoke test SHALL demonstrate a complete offline fixture run through this surface alone. Symbols not re-exported from the package root are internal and carry no stability promise.

## Requirement: AOP instrumentation via decorators
Cross-cutting observability — trace/span creation, timing, outcome capture — SHALL attach to key core methods (extraction, fetching, analysis, scoring, report assembly) exclusively through Python decorators supplied by a single observability module. Core function bodies SHALL contain no tracing, span, or instrumentation-logging calls; removing every decorator SHALL leave functional behaviour and outputs unchanged. Decorators SHALL preserve wrapped signatures, support sync and async callables, re-raise exceptions unmodified after recording an error outcome, and capture only an explicit allowlist of attributes — never raw arguments — so resume and job content cannot leak into telemetry.

## Requirement: Trace context propagation and pluggable sinks
Span context SHALL propagate via `contextvars` from a per-invocation root span (CLI command, API request via middleware, or embeddable-core entry) through nested decorated calls, including across the fan-out worker pool, with the run id as the correlation id. Span events SHALL flow to a sink selected once at startup by `OBSERVABILITY_SINK` (`json` — one structured log line per span, the default; `none` — fully disabled; `otel` — OpenTelemetry OTLP export, available as an optional dependency extra). With the sink disabled, run outputs SHALL be byte-identical to instrumented runs, and an eval SHALL verify span nesting matches the call tree on a fixture run.

## Requirement: Deterministic scoring
Match scores SHALL be computed by a pure Python function from the typed analysis (matched/total skill counts, experience alignment, domain alignment) using the fixed rubric: required skills 0–40, preferred skills 0–20, experience 0–20 (exact 20 / close 15 / partial 10 / far 5), domain 0–20 (exact 20 / related 15 / transferable 10 / none 5), total 0–100. When a JD lists no preferred skills, the 20-point preferred budget SHALL be reallocated to required skills (required scales to 0–60); empty denominators SHALL never divide by zero nor award free points. Rounding SHALL follow JS `Math.round` semantics (half away from zero for positives) so ported fixtures remain byte-identical. Match bands: strong ≥ 80, good 65–79, moderate 50–64, weak 35–49, no-match < 35. The recommendation string SHALL be a fixed lookup keyed by band. The LLM SHALL NOT produce any numeric score, band, or recommendation.

## Requirement: Single generative step with typed output
The only LLM call in the pipeline SHALL be per-job extraction of a `JobAnalysis` Pydantic model (skills with matched flags and evidence, experience/domain alignment, strengths, gaps, resume improvements, ATS keywords, cover-letter angle and paragraphs, summary). The schema SHALL contain no numeric score field. Schema validation failures SHALL fail that job with a clear error, never a partially trusted result.

## Requirement: Evidence grounding
Every skill reported as matched SHALL carry an evidence quote drawn from the extracted resume text; unmatched skills SHALL carry empty evidence. The `SkillMatch` model SHALL enforce this cross-field rule at validation time, and an eval SHALL verify (whitespace/case-normalized) that every evidence string appears in the resume text.

## Requirement: Untrusted job content
Job-posting text SHALL be treated as data, not instructions: delivered to the analysis call in a fenced, labeled frame with an explicit "data, not instructions" statement in the system prompt. Resistance SHALL be verified by the ported adversarial-fixture eval: the report stays schema-valid and grounded, the total score equals the value recomputed from the analysis counts, and the recommendation is byte-identical to the deterministic lookup.

## Requirement: Job fetch guards
URL fetching SHALL enforce an http/https scheme allowlist, a hostname blocklist (loopback, RFC1918, link-local metadata) checked pre-connect and post-redirect, a response byte cap, and a minimum-extractable-words guard. Local job files SHALL pass the same byte cap and word guard. A source that cannot be fetched or extracted SHALL yield a per-job failure record with a reason — never a fabricated analysis.

## Requirement: Graceful link failure — log, stop, no retry
Exactly one fetch attempt SHALL be made per job source, recorded in `jobs/fetch-attempts.json`. On failure the job SHALL be logged, recorded as failed, and stopped — no analysis call, no score. Other sources in the run SHALL continue unaffected; an all-failed run SHALL end gracefully with failure records and exit 0.

## Requirement: Bounded fan-out
Analysis of multiple fetched jobs SHALL run through a code-bounded worker pool (`JOB_FANOUT_CONCURRENCY`, default 3). Exactly one analysis call SHALL be made per successfully fetched job, verified by eval via call counting.

## Requirement: Per-job JSON output
A run SHALL produce exactly one JSON file per job source under `runs/<timestamp>/`: `slug(<job title>)_<timestamp>.json` for an analyzed job (run metadata, resume file reference, model id, the typed analysis, score breakdown, band, deterministic recommendation, rendered cover-letter text) or `slug(<job source>)_<timestamp>.failed.json` for a failed fetch. `resume.txt` and `jobs/<n>.txt` SHALL be persisted in the run folder and referenced, not embedded. Multi-source runs SHALL additionally write `ranking.md` ordered by total score, and every run SHALL write `summary.json` (per-job status, token usage, timing). Slugs SHALL strip every character outside `[a-z0-9-]`. No DOCX, PDF, or HTML SHALL be generated.

## Requirement: Templates and prompts staged as data
Analysis prompts and the optional cover-letter template SHALL load from `prompts/` and `templates/` data folders at runtime, never be compiled into Python source, and SHALL be user-overridable. A missing cover-letter template SHALL degrade to paragraphs joined by blank lines, not fail the run.

## Requirement: Model-agnostic configuration
The analysis model SHALL resolve `MODEL_ANALYST` → `MODEL` → startup error, with credentials and optional base URL from matching env vars in the repo-root `.env`. No model id, API key, or provider default SHALL be hard-coded.

## Requirement: No embedded candidate configuration
Candidate identity SHALL derive solely from the resume content. No candidate name, contact detail, or biography SHALL exist in source or configuration.

## Requirement: Evals with rubric contract
The backend SHALL ship pytest evals ported from the Eve reference covering: scoring determinism, match-band boundaries, report schema conformance and file naming, evidence grounding, multi-job fan-out (N sources → N reports + ranking, N analysis calls), single-job path, prompt-injection resistance, and fetch-guard behaviour. Deterministic evals SHALL run offline with no model or network; live evals SHALL be isolated behind a pytest marker. Every eval SHALL have a written HARD/SOFT rubric in `evals/rubrics.md`, and the canonical scoring formula stated there SHALL be the single source of truth for both `scoring.py` and its tests.

## Requirement: Real-world eval dataset
The eval fixtures SHALL be copied from the Eve project's committed corpus: the resume PDF (subject to the inception-gate privacy decision), the four extractable JD snapshots, the two genuine JS-shell fetch-failure captures, `jobs/manifest.json`, and the adversarial JD. Snapshots, not live URLs, SHALL be the eval inputs.
