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

## Bolt 2 — Correction: multi-location postings, currency-neutral display ✅ (2026-07-12)

Owner tested against a real Bain posting: "I was expecting salary
range but it showed the last salary value... if the salary had $ or
currency in it, I saw two times currency... hope we didn't hard code
the currency."

- [x] **Root cause, confirmed by fetching the real page text, not
      guessed:** the posting doesn't state a min-max range at all — it
      states two different *location-tied* figures ("$258,425" for
      Atlanta/Boston/Texas/Chicago, "$293,500" for California/New
      York/DC/Washington), a pattern required by several US states'
      pay-transparency laws. The original verbatim-only prompt rule
      had no instruction for this shape, so the model picked one
      figure rather than fabricating or merging — which the owner
      correctly read as "showing the last value."
- [x] `analysis_system.txt` + `schemas.py`'s doc comment — explicit
      rule for multi-location disclosures: capture ALL location-tied
      figures with their location context, never collapse to one
      - [x] **Verified: re-ran the exact same Bain URL** — now returns
        both figures with their location context, not just one
- [x] `report-card.tsx` — swapped the `DollarSign` icon (a literal $
      glyph, hardcoding a USD assumption the field itself never made)
      for `Banknote` (currency-neutral) — fixes both the "$ $293,500"
      double-currency rendering the owner saw *and* the hardcoded-USD
      icon problem for non-US postings, in one change. The badge now
      also truncates with the full text in a `title` attribute, since
      multi-location disclosures are much longer than a short range.
- [x] Confirmed no currency is hardcoded anywhere in the extraction
      path itself (schema/prompt were already currency-neutral; only
      the icon was USD-specific) — re-read both files end to end to
      confirm, not assumed
- [x] 111/111 offline tests still pass; playground build clean

## Verification

- [x] All acceptance criteria in proposal.md met with real evidence,
      including the Bolt 2 correction
- [ ] Owner: re-review, then status → **verified** and archive
