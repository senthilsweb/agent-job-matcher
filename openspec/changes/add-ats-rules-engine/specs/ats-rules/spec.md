# Spec: ATS rules

## Requirement: Known ATS URLs resolve through rules
When a job source URL matches a `resolve` rule, the fetcher SHALL request
the ATS's public posting API instead of the HTML page, and SHALL make
exactly one HTTP request for that source.

## Requirement: Unknown sources are untouched
A URL that matches no rule, or whose path segments fail validation, SHALL
follow the existing HTML fetch path with identical behavior.

## Requirement: Rules are data
Each ATS SHALL be described entirely by `ats_rules/<ats>/resolve.json` and
`ats_rules/<ats>/extract.json`. Adding an ATS SHALL NOT require a Python
change. `ATS_RULES_DIR`, when set, SHALL be searched before the packaged
rules.

## Requirement: Rule output is a typed contract
Rule output SHALL be validated by a Pydantic schema before use. Invalid or
empty output SHALL produce a failed `FetchResult`, never an exception.

## Requirement: No fabricated text
If the job is absent from the API response, or the extracted text is below
`JOB_MIN_WORDS`, the fetch SHALL fail with a specific reason. The system
SHALL NOT fall back to the HTML page or invent content.

## Requirement: Shipped in the image
The built wheel SHALL contain the rule files, and `zen-engine` SHALL be a
runtime dependency, so every Docker image built from `backend/` resolves
Ashby, Greenhouse, and Lever URLs.
