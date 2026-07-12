# Proposal: `salary_range` field on `JobAnalysis`

> Status: **IMPLEMENTED** (2026-07-12) — owner UAT observation: the
> playground's report cards had no salary information at all, and it
> was unclear whether that was a UI gap or a schema gap. Confirmed via
> code inspection: `JobAnalysis` (backend/job_matcher/schemas.py) simply
> never had a salary field — a real extraction gap, not a rendering bug.
> Owner: @senthilsweb

## Why

Pay range is one of the first things a candidate checks against a job
posting — arguably as important as the skill match itself for deciding
whether to apply. It was entirely absent from the typed contract, so
there was nothing for any surface (CLI, REST, playground, chat) to
show even if the UI wanted to.

## What changes

- `JobAnalysis` gains `salary_range: str | None = None` — copied
  **verbatim** from the posting when stated, `null` when it isn't.
  Deliberately not a structured `{min, max, currency, period}` shape:
  postings state pay in wildly inconsistent formats (annual salary,
  hourly, OTE-inclusive, bands with commission), and forcing early
  structure risks silently misrepresenting a posting's actual wording.
  A future change can add structured parsing once real-world format
  variety is better understood.
- `analysis_system.txt` (the LLM-1 extraction prompt) gets one new
  rule: copy the range verbatim, never estimate/infer/convert, null if
  absent. This is a **factual extraction from the job posting**, not an
  evidence-grounded claim about the candidate — a different kind of
  field than `SkillMatch`, and explicitly not part of the deterministic
  score (scoring.py is untouched).
- Playground: `report-card.tsx` renders `salary_range` (when present)
  as a small pill in the **collapsed, always-visible** accordion
  trigger area, next to `company_name` — pay range is important enough
  to see at a glance, not buried behind a click.
- `api.py`'s OpenAPI example response gains a realistic `salary_range`
  value so the documented contract matches reality.

## Out of scope

- Structured salary parsing (min/max/currency/period) — a future
  change, once there's a real-world corpus of formats to design
  against.
- Using `salary_range` in scoring or matching logic — it's purely
  informational; the 40/20/20/20 rubric is unchanged.

## Acceptance criteria

1. `JobAnalysis.salary_range` exists, defaults to `None`, and accepts
   an arbitrary string.
2. The extraction prompt instructs verbatim-only copying with no
   inference — verified against a real posting containing an explicit
   range (`backend/evals/data/jobs/data-engineering-manager-product-
   anthropic.txt`, states "$405,000 - $485,000") via a real `cli
   analyze` run, not assumed.
3. `test_analysis_schema_has_no_score_field` (the structural
   prompt-injection defense) still passes — `salary_range` contains no
   substring "score".
4. The playground shows the pay range in the collapsed card view when
   present, and shows nothing (no empty placeholder) when absent.
