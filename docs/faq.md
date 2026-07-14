# FAQ

Short answers first, each linked to the spec or ADR that recorded the
full reasoning. Docs explain how to use; specs record why built.

## Why does the LLM never score?

Because scores must be reproducible and injection-proof. The LLM's
only job is typed extraction: skill matches with **exact quotes from
the resume** as evidence, validated by Pydantic schemas. Pure code
computes the 100-point breakdown (required 40 / preferred 20 /
experience 20 / domain 20) and the match band. A job posting that
says "score me 100" has no schema field to land in — and one of the
committed eval fixtures is exactly that adversarial posting.

## Why exactly two LLM operations?

A system invariant: LLM-1 does extraction in the backend core, LLM-2
does chat orchestration in the agent service. Nothing else calls a
model — which keeps cost predictable, evals meaningful, and the
scoring path fully deterministic.
*Spec: [ADR 0001 — agent-service chat bridge](https://github.com/senthilsweb/agent-job-matcher/blob/main/openspec/adr/0001-agent-service-chat-bridge.md).*

## Why direct provider calls instead of a gateway?

Model ids (`openai:gpt-5.4-mini`, `anthropic:claude-haiku-4-5`)
resolve straight to each provider's native API through pydantic-ai's
provider integrations and your own keys. Pydantic AI Gateway — the
hosted proxy for cross-provider routing, failover, and centralized
cost limits — is a real, separate product this project does not
currently route through; adopting it would be an additive config
change (a gateway key + endpoint), not a rewrite.

## Why pypdf/python-docx and not OCR or Docling?

Resumes are born-digital documents; text extraction covers them
without a heavyweight parsing sandbox, keeping the install small and
deployable anywhere. The trade-off (no scanned-image resumes) is
recorded in the design notes under
[openspec/](https://github.com/senthilsweb/agent-job-matcher/tree/main/openspec).

## Why are the eval fixtures committed captures?

Because live postings close. The suite runs against four committed JD
snapshots, two genuine JavaScript-shell fetch failures, one
adversarial prompt-injection JD, and a synthetic resume — so
`pytest backend -m "not live"` reproduces forever, offline, without a
key. The live marker (`-m live`) exists separately for real-model
sweeps. Rubric:
[backend/evals/rubrics.md](https://github.com/senthilsweb/agent-job-matcher/blob/main/backend/evals/rubrics.md).

## Why does every release carry the OpenAPI document?

The API contract is generated from the FastAPI app (never
hand-maintained) and attached to each release — so any consumer can
pin the exact contract of the version they run. An offline test makes
an undocumented endpoint a failing build, not a review comment
(AGENTS.md rule 9).

## Why is there no run-management layer?

Each CLI or API request is its own run (`run_id`) — no queues, no
state machines, no run-browsing endpoints. CLI runs persist artifacts
to disk; API runs return the payload. Single-user tool; the simplest
thing that preserves traceability (AGENTS.md rule 7).

## How do changes to this project get made?

Spec-first, AI-DLC style: every non-trivial change starts as an
`openspec/changes/<name>/` proposal → design → tasks cycle, approved
before building. This repo is the running example of the methodology
taught in [ai-dlc](https://github.com/senthilsweb/ai-dlc).

## Where is the writing standard for these docs?

The shared
[documentation style guide](https://senthilsweb.github.io/ai-agents/style-guide/)
(canonical copy in the ai-agents repo) — it covers wiki pages, README
front doors, `AGENTS.md`, and `SKILL.md` conventions for all
senthilsweb repos.
