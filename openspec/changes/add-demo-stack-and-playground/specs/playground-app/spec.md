# Spec: `playground/` Next.js app

## Requirement: Left pane collects a resume and one-to-many job links
The playground SHALL provide a left sidebar with: a resume file
drop-zone/picker accepting the backend's supported extensions
(`job_matcher.resume.SUPPORTED_EXTENSIONS`), a dynamic list of job-link
text inputs (add-row and remove-row controls, minimum one row), and a
Submit button. Submit SHALL be disabled until a resume file is present
and at least one non-empty job link exists.

## Requirement: Submit calls the existing `/analyze` endpoint, no new backend code
Submitting SHALL send the resume file and job links as a single
multipart request to the backend's existing `POST /analyze` (via a
Next.js server-side route handler that proxies to `API_URL`, keeping
the container-network backend address out of client-side code) and
render exactly the returned typed job-report array — no client-side
re-scoring, re-deriving, or re-labeling of any score or match band.

## Requirement: Results render as compact, accordion-style report cards in a carousel
The right pane SHALL render one card per job report: job title as the
visible/accordion header, a match-band badge colored 1:1 from
`MatchStatus`'s five literal values, the total score, and a compact bar
visualization of the four sub-scores (`required_skills_score`,
`preferred_skills_score`, `experience_score`, `domain_score`, each
rendered against its own scale — required's max varies with preferred-
skill reallocation). Clicking a card (or its header) SHALL expand it in
place to show the full report (evidence quotes, gaps) while collapsing
any other currently-expanded card. The collapsed state SHALL show all
job titles/badges/scores at a glance without scrolling past a
reasonable number of jobs (e.g. up to 6) on a standard desktop viewport.

## Requirement: Per-job failures are isolated
If one job in a multi-job submission fails (fetch failure, guard
rejection, etc.), its card SHALL render a clear per-job error state;
the other jobs' successful reports SHALL still render normally — no
single failure blanks the whole result set.

## Requirement: Slack-purple brand theme
The playground SHALL use the same `#4A154B`-anchored Tailwind color
ramp already established in `privacyshield` and `mcp-chat-client`'s
demo page for headers, accents, active/selected states, and the
`strong_match` badge color — visual consistency across the demo suite,
not a new palette.

## Requirement: No secrets in client-visible code
`API_URL`/backend addresses resolve server-side only (Next.js route
handlers / server components); no API key or credential is ever sent
to or embedded in the browser bundle (none are required for `/analyze`
today, but the pattern SHALL hold regardless).
