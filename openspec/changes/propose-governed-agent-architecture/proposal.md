# Proposal: governed agent architecture (hard constraints → markdown-defined reasoning agent)

> Status: **PROPOSED** (2026-09-26) — proposal only, nothing implemented.
> Owner: @senthilsweb
> Supersedes on approval: the "exactly two LLM operations" invariant of
> [ADR 0001](../../adr/0001-agent-service-chat-bridge.md) — see
> [ADR 0002 (draft)](../../adr/0002-governed-agent-architecture.md).

## Why

The job matcher already follows the governed pattern in spirit: typed
contracts, a model that extracts but never scores, and deterministic code
that computes the number. It does it as one Python pipeline with one
generative step, so the *rules* live in Python and prompts, and there is no
gate that stops a clearly unsuitable job before the expensive call.

This proposal moves the project to a stronger form of the same pattern:
agents working inside a **decision contract** — governing rules plus
strictly typed request and response schemas — where:

1. **Hard constraints (HC)** run first on a cheap, fast model. A failure
   stops the request before any expensive token is spent.
2. Only a request that passes every HC reaches the **reasoning agent**
   for the evidence-grounded analysis and the real task.
3. **Soft constraints (SC)** drive scoring and ranking of what passed.
4. **Every result carries a narrative** — each HC, each SC, and the overall
   decision, for success and failure alike.
5. HC and SC rules **reference governing fields of the typed schema by
   name**, so a rule is checkable against the contract, not free text.
6. The agent is a set of **portable markdown artefacts** (`AGENTS.md`,
   `SKILL.md`, `hard-constraints.md`, `rubric.md`, `agent.yaml`). The
   backend loads the bundle and runs it; no hosted agent platform is
   involved, and any runtime that reads these files can reuse them.

Porting the job matcher to this shape makes the rules reviewable by a
non-developer, makes rejections cheap and explainable, and turns the
project into a reference implementation of the pattern.

## What changes

- **Decision contract.** A versioned request schema and response schema.
  The response is a `GovernedJobDecision` with `hard_constraints[]`,
  `soft_constraints[]`, the existing deterministic `score_breakdown`,
  `decision`, and `narrative`. Governing fields are named JSON paths into
  these schemas.
- **Inputs stay minimal.** A resume, plus each job as a URL or as full
  text. Every rule must be decidable from those two inputs.
- **Rules and scoring as markdown.** `hard-constraints.md`, `rubric.md`, and
  `scoring.md` hold the checks, soft constraints, weights, points, and
  bands. Code reads their front matter and validates it at startup. They
  change only by deployment: a new image, or an override folder mounted at
  deploy time.
- **HC gate.** Deterministic checks and an injection pre-scan run in code
  first, at no cost. Semantic checks run as one call to a small OpenAI
  model with structured output. Any blocking failure short-circuits to a
  rejection with narratives.
- **Layered injection guardrails.** Detection in the gate, plus structural
  defences that hold even if every model is fooled: no model can write a
  score, and every matched skill needs a verbatim resume quote.
- **Caching.** Fetched job text is cached by normalised URL for a set
  lifetime. Job-only gate results are cached too. A full result cache is
  available but off by default, because it stores personal data.
- **Reasoning agent.** Defined entirely by the markdown bundle and run by
  the backend through the existing provider-neutral model layer, it does the
  evidence-grounded analysis, SC assessment, and cover-letter work. It
  returns the typed response directly. Code then validates it against the
  rubric's completeness rules.
- **Scoring stays deterministic and becomes configurable.** SCs return typed
  levels with evidence and narrative; code turns levels into points using
  `scoring.md`. No model produces a number.
- **Opt-in engine.** `DECISION_ENGINE=legacy|governed` selects the path. The
  existing pipeline stays the default until the governed path passes parity
  evals.

## Out of scope

- **MCP server and agent service:** untouched. They call the REST API and
  receive the richer response additively.
- **Playground:** a later change renders narratives and HC results.
- **Fetch and ATS rules:** unchanged. They run before the HC gate.
- **Resume → JSON Resume conversion:** stays on the legacy path.
- **Moving the HC gate to Claude:** possible later; the gate is behind a
  provider-neutral interface.

## Acceptance criteria (for the eventual implementation)

1. A job failing any hard constraint returns a typed failure with one
   narrative per evaluated HC and **makes no reasoning-agent call**.
2. A passing job returns HC results, SC results, the deterministic score,
   the decision, and an overall narrative. Every HC and SC has a non-empty
   narrative; every evidence quote appears verbatim in the resume.
3. Every rule in `hard-constraints.md` and `rubric.md` names at least one
   governing field, and every named field exists in the schema. An offline
   test enforces this.
4. With `DECISION_ENGINE=legacy` behaviour and output are byte-identical to
   today.
5. The reasoning agent's instructions come only from the committed
   markdown bundle, or an operator override folder. No prompt text for the
   governed path lives in Python, and the bundle version is recorded in
   every response.
6. A resume or job containing an instruction aimed at the evaluator cannot
   raise the score: the adversarial fixtures are rejected or score the same
   as their clean versions.
7. A repeated request for a cached job makes no fetch, and the response
   trace says so.
8. With `scoring.md` holding today's values, scores are identical to the
   legacy engine; an invalid `scoring.md` stops startup.
9. On the committed eval fixtures, the governed path's match band agrees
   with the legacy path on at least an agreed share of jobs, and every
   disagreement has an HC or SC narrative that explains it.
