# Tasks — `propose-governed-agent-architecture`

Proposal stage. Nothing below starts until the owner approves the proposal
and answers the open questions in `design.md` §12.

## Bolt 0 — prerequisites
- [ ] Restore `backend/evals/data/` fixtures (required for parity evals)
- [ ] Owner answers design §12 questions; ADR 0002 accepted or amended

## Bolt 1 — contract and rules as data (no behaviour change)
- [ ] `JobFitRequest` v1 and `GovernedJobDecision` v1; JSON Schema export
- [ ] `hard-constraints.md`, `rubric.md` with governing-field references
- [ ] Offline test: every governing field resolves in the schema

## Bolt 2 — hard-constraint gate
- [ ] Deterministic HCs in code
- [ ] `ConstraintGate` interface; OpenAI Responses implementation
- [ ] `DECISION_ENGINE=governed` returns rejections with narratives

## Bolt 3 — markdown-defined reasoning agent
- [ ] Bundle `agents/job-fit/`: `AGENTS.md`, `SKILL.md`, `rubric.md`, `agent.yaml`
- [ ] Bundle loader with `AGENT_BUNDLE_DIR` override; version and hash in trace
- [ ] Reasoning call with typed output; completeness validator in code

## Bolt 4 — parity and rollout
- [ ] Shadow run on eval fixtures; disagreement review
- [ ] Package the bundle as package data; schema drift test in CI
- [ ] Docs: architecture page and configuration
