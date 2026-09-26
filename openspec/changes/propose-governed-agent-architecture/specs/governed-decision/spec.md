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

## Requirement: Models never produce scores
Soft constraints SHALL return levels, evidence, and narrative only. Points
and totals SHALL be computed by `scoring.py`.

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
