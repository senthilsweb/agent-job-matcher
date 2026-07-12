# Tasks — `add-salary-range-field`

Owner UAT observation (2026-07-12), diagnosed and implemented same-day.

- [x] `backend/job_matcher/schemas.py` — `salary_range: str | None = None`
      on `JobAnalysis`
- [x] `backend/job_matcher/prompts/analysis_system.txt` — verbatim-only
      extraction rule, null when absent
- [x] `backend/job_matcher/api.py` — OpenAPI example response updated
- [x] `backend/tests/test_schema_conformance.py` —
      `test_salary_range_defaults_to_none_and_accepts_a_verbatim_string`
- [x] `playground/lib/types.ts` + `report-card.tsx` — rendered in the
      collapsed accordion trigger, next to company name
- [x] **Verified (2026-07-12):**
      - Offline suite: 111/111 passing (110 pre-existing + 1 new)
      - Real extraction: `docker compose run --rm cli analyze` against
        `evals/data/jobs/data-engineering-manager-product-anthropic.txt`
        (a fixture with a stated range) → `salary_range: "Annual
        Salary: $405,000 - $485,000 USD"`, copied verbatim from the
        posting text
      - Real containerized `/analyze` calls against live postings
        without a stated range correctly returned `salary_range: null`
        (Gusto, Anthropic postings tested) — confirms the field doesn't
        fabricate a value when none exists
      - Playground UI: verified via real Playwright screenshots that
        the field renders as a pill in the collapsed card when present
        and renders nothing when absent

## Verification

- [x] All acceptance criteria in proposal.md met with real evidence
- [ ] Owner: re-review, then status → **verified** and archive
