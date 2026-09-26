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
- **Rules as data.** `hard-constraints.md` and `rubric.md` hold the HC and SC
  catalogue, each rule with an id, the governing fields it reads, its
  pass/fail condition, and a narrative template.
- **HC gate.** Deterministic HCs run in code first (free). Semantic HCs run
  as one OpenAI Responses API call on a small model with structured output.
  Any hard failure short-circuits to a typed failure decision with
  narratives.
- **Reasoning agent.** Defined entirely by the markdown bundle and run by
  the backend through the existing provider-neutral model layer, it does the
  evidence-grounded analysis, SC assessment, and cover-letter work. It
  returns the typed response directly. Code then validates it against the
  rubric's completeness rules.
- **Scoring stays deterministic.** SCs return typed levels with evidence and
  narrative; `scoring.py` still turns levels into points. No model produces
  a number.
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
6. On the committed eval fixtures, the governed path's match band agrees
   with the legacy path on at least an agreed share of jobs, and every
   disagreement has an HC or SC narrative that explains it.
