# Spec: README documentation additions

## Requirement: A compact REST endpoints table
The README SHALL include a Markdown table listing every currently
implemented REST route across the backend (`api.py`) and the agent
service (`app.py`) — method, path, one-line purpose — matching the
existing "Surfaces" table's terse style. Each entry SHALL be accurate
to the routes that exist in code at time of writing (not aspirational).

## Requirement: A "Key environment variables" section
The README SHALL include a grouped (not exhaustive) table of the most
relevant `.env` variables — model/provider keys, pipeline tuning,
telemetry activation, agent-service/upload configuration — with a
pointer to `.env.example` as the authoritative full list. No variable
listed SHALL carry an example value that looks like a real credential.

## Requirement: A "Cover letter templates" section
The README SHALL document the package-default cover-letter template
(`job_matcher/templates/cover_letter.txt`), its placeholder tokens, and
the confirmed override mechanism (the `TEMPLATES_DIR` environment
variable, resolved the same way as prompt overrides in `prompts.py`) —
verified against the actual `prompts.py`/`pipeline.py` behavior, not
assumed.
