# ADR 0002 — Governed agent architecture

> Status: **Proposed** — 2026-09-26 (owner to accept, amend, or reject)
> Relates to: `openspec/changes/propose-governed-agent-architecture/`
> Would amend: [ADR 0001](0001-agent-service-chat-bridge.md) — the
> "exactly two LLM operations" invariant

## Context

ADR 0001 fixed the system at two model operations: typed extraction in the
backend core (LLM-1) and chat orchestration in the agent service (LLM-2).
That kept cost predictable and scoring deterministic.

The owner wants to move the job-fit decision to a governed agent
pattern: a typed decision contract, hard constraints evaluated
first on a cheap model, and a markdown-defined reasoning agent that runs
only when those pass, with soft constraints for scoring and narratives on
every result.

## Options considered

1. **Keep the single extraction call.** Cheapest to maintain, but rules stay
   in Python and prompts, and clearly unsuitable jobs still pay for a full
   analysis.
2. **Add a gate in front of the existing call.** Cheaper rejections, but the
   reasoning step stays an unversioned prompt with no self-check.
3. **Gate plus markdown-defined agent (proposed).** Rules and agent
   become versioned markdown artefacts that non-developers can review;
   rejections are cheap and explained; code checks the agent's output
   against the rubric.

## Decision (proposed)

Adopt option 3 behind `DECISION_ENGINE=governed`, keeping the legacy engine
as default until parity is shown. Replace ADR 0001's invariant with:

- **Models extract, judge constraints, and reason. Code scores.** No model
  output becomes a number without passing through `scoring.py`.
- **Every model operation is named and bounded:** the HC gate (one call
  per job), the reasoning agent (one call per accepted job), and chat
  orchestration (LLM-2, unchanged).
- **No model is called for a job that failed a hard constraint.**

## Consequences

- More model calls per accepted job, fewer per rejected job. Cost per
  completed job is measured before the default flips.
- Slightly higher latency for accepted jobs: two calls instead of one.
- No new deployment surface: the bundle ships inside the backend package.
- MCP server and agent service are unaffected.
