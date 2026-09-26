# Tasks — `propose-governed-agent-architecture`

Proposal stage. Nothing below starts until the owner approves the proposal
and answers the open questions in `design.md` §15.

## Bolt 0 — prerequisites
- [ ] Restore `backend/evals/data/` fixtures, including clean and injected pairs
- [ ] Owner answers design §15; ADR 0002 accepted or amended

## Bolt 1 — contract and markdown configuration (no behaviour change)
- [ ] `JobFitRequest` v1 and `GovernedJobDecision` v1; JSON Schema export and drift test
- [ ] `hard-constraints.md`, `rubric.md`, `scoring.md` with validated front matter
- [ ] Scoring reads `scoring.md`; parity test proves identical scores with today's values
- [ ] Offline test: every governing field resolves in the schema

## Bolt 2 — inputs, caching, and the gate
- [ ] `job_text` input alongside URLs
- [ ] Job text cache and job-only gate result cache; trace records hits
- [ ] Hidden-text stripping and pattern pre-scan for both inputs
- [ ] Deterministic checks, then one gate call for semantic checks
- [ ] Rejections with narratives behind `DECISION_ENGINE=governed`

## Bolt 3 — markdown-defined reasoning agent
- [ ] Bundle loader with `AGENT_BUNDLE_DIR` override; version and hash in trace
- [ ] One typed reasoning call
- [ ] Output validation: completeness, verbatim quotes, consistency

## Bolt 4 — chat and tool text
- [ ] Chat prompt reports decisions, narratives, and failed checks
- [ ] Analyze tool description mentions rejection before scoring

## Bolt 5 — parity and rollout
- [ ] Both engines on the fixtures; review every band disagreement
- [ ] Injection fixtures: rejected, or scored the same as the clean version
- [ ] Cost and time per completed job
- [ ] Docs, then flip the default
