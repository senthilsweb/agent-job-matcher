# Spec: Playground UI parity + cover letter

## Requirement: Header shows a live, polling backend-status indicator
The playground SHALL expose a `GET /api/health` route handler that
proxies to `${API_URL}/health` server-side. The header SHALL poll this
route (same interval convention as `mcp-chat-client`'s demo, 5s) and
render a three-state pill (`checking` / `online` / `offline`) with a
colored dot — never a static "Online" label.

## Requirement: Form pane uses Card/Label/Input composition, wider sidebar
The resume-upload and job-link form SHALL be composed with shadcn
`Card`/`CardHeader`/`CardTitle`/`CardDescription` and `Label`-paired
inputs, matching `privacyshield`'s `Detect.tsx` composition. The
sidebar's width SHALL be `lg:w-96` (widened from `lg:w-80`).

## Requirement: Submit is always visible, never requires scrolling
The Submit button SHALL remain visible in the viewport regardless of
how many job-link rows are present, via a sticky, non-scrolling footer
region distinct from the form's scrollable content area.

## Requirement: Results use full available width with an evident expand affordance
The results panel's container SHALL NOT be constrained to a fixed
narrow max-width (e.g. `max-w-3xl`) — it SHALL use the main content
area's full available width. Each accordion trigger SHALL visibly
signal it is interactive (hover state, a visible "click to expand"
hint, and a clearly-sized chevron).

## Requirement: Match-status colors follow the standard green-to-red grading scale
`MATCH_STATUS_CLASSES` SHALL map the five `MatchStatus` values to a
green→amber→red scale in strictly decreasing quality order:
`strong_match` → emerald (green), `good_match` → lime (lighter green),
`moderate_match` → amber, `weak_match` → orange, `no_match` → red.
Brand purple SHALL NOT be used to represent a match-quality band.

## Requirement: The cover letter is rendered, collapsible, and copyable
Every successful job report (`fetch_status: "ok"`) SHALL render its
`cover_letter_text` inside the expanded report, in a collapsible
section that is collapsed by default (to preserve the report's overall
compactness) and a copy-to-clipboard control that visibly confirms the
copy succeeded (icon swap or equivalent, no silent no-op).

## Requirement: No regression to the existing verified behavior
The real `/analyze` proxy flow, per-job error isolation (`fetch_status:
"failed"` cards), and the Docker build SHALL continue to work exactly
as verified in `add-demo-stack-and-playground`'s Bolt 3 — this change
is additive/corrective to the UI layer only, not the data flow.
