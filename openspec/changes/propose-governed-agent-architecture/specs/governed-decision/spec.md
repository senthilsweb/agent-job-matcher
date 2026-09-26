# Spec: governed job decision

## Requirement: Hard constraints gate the expensive step
The governed engine SHALL evaluate every hard constraint before calling the
reasoning agent. If any blocking hard constraint fails or is unknown, the
engine SHALL return a `rejected` decision and SHALL NOT call the reasoning
agent for that job.

## Requirement: Deterministic constraints run before model constraints
Hard constraints computable from typed fields SHALL run in code before the
semantic gate. A deterministic failure SHALL skip the semantic gate.

## Requirement: Every result carries a narrative
Each hard-constraint result, each soft-constraint result, and each decision
SHALL carry a non-empty narrative, for passes and failures alike. A missing
narrative SHALL be a schema validation failure.

## Requirement: Rules reference governing fields
Every rule in `hard-constraints.md` and `rubric.md` SHALL name at least one
governing field as a path into the request or response schema, and every
named path SHALL exist in the exported JSON Schema.

## Requirement: Inputs are a resume and jobs only
The governed engine SHALL accept only a resume and one or more jobs, each
given as a URL or as full text. Every hard and soft constraint SHALL be
decidable from these inputs.

## Requirement: Models never produce scores
Soft constraints SHALL return levels, evidence, and narrative only. Points,
totals, and bands SHALL be computed by code from `scoring.md`.

## Requirement: Rules and scoring are configured only in markdown
Hard constraints, soft constraints, and scoring SHALL be configured in
`hard-constraints.md`, `rubric.md`, and `scoring.md`. They SHALL be loaded
and validated once at startup, and an invalid file SHALL stop startup.
There SHALL be no runtime interface for changing them.

## Requirement: Injected instructions cannot raise a score
Hidden text SHALL be stripped and both inputs pre-scanned before any model
call. Semantic injection checks SHALL run on the gate model. Independently
of detection, every matched skill SHALL require a verbatim resume quote,
and level claims SHALL agree with the evidence counts.

## Requirement: Job text is cached
A successfully fetched job SHALL be cached by normalised URL for
`JOB_CACHE_TTL_HOURS`. A cache hit SHALL make no fetch attempt, failures
SHALL NOT be cached, and each response SHALL record cache hits in its trace.
A result cache that stores resume-derived data SHALL be off by default.

## Requirement: Evidence is verbatim
Every evidence quote attributed to the resume SHALL appear verbatim in the
resume text. A result with an unverifiable quote SHALL be rejected as
invalid, not returned.

## Requirement: The agent is defined by its markdown bundle
The reasoning agent's instructions SHALL be assembled only from the
markdown bundle declared in `agent.yaml`, or from `AGENT_BUNDLE_DIR` when
set. The bundle version and content hash SHALL be recorded in every
governed response.

## Requirement: Invalid agent output is a failure
A reasoning result that fails schema validation or the rubric's
completeness rules SHALL produce a typed failure for that job. It SHALL NOT
be returned as a partial report.

## Requirement: The legacy engine is unchanged
With `DECISION_ENGINE=legacy`, responses SHALL be identical to the current
release.
