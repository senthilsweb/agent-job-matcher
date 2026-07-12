# Proposal: Fix playground UI parity + missing cover letter (UAT findings)

> Status: **IMPLEMENTED** (2026-07-12) — bugs found during the owner's
> own manual UAT of `add-demo-stack-and-playground`'s Bolt 3. All 5
> bolts fixed and verified same-day (owner directed spec + implement in
> one request). The owner's live UAT instance (localhost:3011) has been
> rebuilt with the fix. Pending: owner re-review, then **verified**.
> Owner: @senthilsweb
>
> **Correction (2026-07-12, Bolt 6):** a second UAT pass found the fix
> above still didn't read as the same product as `privacyshield` —
> wrong font (Geist instead of Inter), no colored nav rail, no
> collapsible burger toggle, no fixed GitHub footer, a redundant
> "Fit reports" heading, low-contrast gray text, and the add-job-link
> button in the wrong place/color/shape. Owner's explicit direction:
> "why don't you borrow the template or layout from
> `privacyshield/frontend`" — literally port `Sidebar.tsx`'s structure
> rather than re-derive it, and self-verify against the real running
> reference before reporting done. See Bolt 6 in `tasks.md`.
>
> **Correction (2026-07-12, Bolt 8):** a third UAT pass: sharp corners
> app-wide (not just the add-job button), a scoring-guide legend filling
> the nav rail's empty space, a Clear button, and an investigation into
> a persistently-wrong "Backend unreachable" status pill that turned
> out to be genuine Docker Desktop instability (a multi-day-uptime
> daemon serving 23 containers silently stopped honoring commands) —
> root-caused and resolved by restarting Docker Desktop, not a code
> fix. See Bolt 8 in `tasks.md`.

## Why

The owner ran the playground themselves (http://localhost:3011) against
the live backend and compared it side-by-side with `privacyshield`'s
frontend and `mcp-chat-client`'s demo page — the two established
reference UIs this whole demo suite is supposed to read as one product
with. Seven concrete defects came out of that comparison, all real,
none cosmetic nitpicks:

1. **Chrome doesn't match the established pattern.** Both
   `privacyshield` (`frontend/src/App.tsx`) and `mcp-chat-client`'s demo
   (`src/demo/DemoApp.tsx`) use the same header shape: icon + title +
   subtitle on the left, a **live, polling** backend-status pill
   ("Online"/"checking"/"unreachable", not decorative) on the right.
   The playground's header is a bare `<h1>`/`<p>` with no status
   indicator at all, and the form pane is plain divs instead of a
   proper `Card`/`Label`/`Input` composition like both references use.
2. **Sidebar too narrow** for the content it holds once styled properly
   ("make the left bar slightly bigger").
3. **Submit button gets buried below the fold.** With more than one or
   two job-link rows, `SidebarForm`'s `mt-auto` pushes the button past
   the visible viewport, requiring a scroll to submit — every reference
   UI in this engagement keeps its primary action pinned in view.
4. **Expand/collapse isn't evident, and the report doesn't use
   available width.** The accordion trigger has no visible affordance
   beyond a small chevron, and `results-panel.tsx` caps at `max-w-3xl`
   inside a wide viewport ("make it wide accordion").
5. **Match-status colors aren't industry-standard.** `strong_match` is
   currently brand-purple while `good_match` is green — a purple "best"
   band reads as arbitrary next to a green "second-best" band. The
   standard grading scheme (credit scores, ATS tools, heat maps) runs
   green → amber → red from best to worst.
6. **The cover letter is completely missing from the UI.** `JobReport.
   cover_letter_text` is in every API response and rendered nowhere in
   `report-card.tsx`.
7. **No copy-to-clipboard**, even once the cover letter is added —
   `privacyshield`'s `Workspace.tsx` (`OutputCard`'s `handleCopy`) is
   the established pattern for this across the demo suite.

## What changes

- `playground/app/globals.css` + `app/page.tsx`: sidebar widened, header
  rebuilt to the icon+title+subtitle+live-status-pill shape (polling
  the backend's `/health` via the same proxy pattern as `/api/analyze`),
  form pane rebuilt with shadcn `Card`/`CardHeader`/`CardTitle`/
  `CardDescription`/`Label` composition.
- `sidebar-form.tsx`: submit button becomes a sticky, always-visible
  footer (`sticky bottom-0` inside a scrollable form area), never
  requiring a scroll to reach.
- `results-panel.tsx` + `report-card.tsx`: width constraint widened
  (matches viewport, not a fixed `max-w-3xl`), accordion trigger gets an
  explicit "Click to expand full report" affordance plus a hover state
  and a more prominent chevron.
- `lib/types.ts`'s `MATCH_STATUS_CLASSES`: recolored to the standard
  green→amber→red grading scale.
- `report-card.tsx`: adds a collapsible "Cover letter" section (a
  nested `Collapsible`, shadcn component, installed this change) inside
  the expanded report, with a copy-to-clipboard button matching
  `privacyshield`'s `OutputCard.handleCopy` pattern (icon toggles
  copy/check, no toast library added — a lightweight inline "Copied"
  label instead, since `sonner` isn't installed here and isn't needed
  for a single-button confirmation).

## Out of scope

- Adding a privacyshield-style multi-tab navigation rail — the
  playground is a single-purpose tool (one form, one result view), not
  a multi-tool app; a nav rail would be UI for pages that don't exist.
  "Look and feel parity" here means the header/card/color/spacing
  language, not literally cloning the tab-switcher chrome.
- `openapi-docs` or `chat-demo` — this fix is scoped to `playground/`
  only; the owner's UAT feedback was specific to that app.
- Toast notifications (`sonner`) — not installed in this app; the copy
  button's own inline state change is sufficient for one action.

## Acceptance criteria

1. The playground's header shows an icon, title, subtitle, and a live
   status pill that genuinely reflects backend reachability (checking
   → online/unreachable), not a static label.
2. The form pane is a proper `Card` with `Label`-paired inputs; the
   sidebar is visibly wider than before.
3. With 5+ job-link rows added, the Submit button remains visible
   without scrolling.
4. The results area uses the full available width (no longer capped at
   `max-w-3xl`), and hovering/inspecting an accordion trigger makes it
   obvious it's clickable to expand.
5. `strong_match` renders green, `good_match` a lighter green/teal,
   `moderate_match` amber, `weak_match` orange, `no_match` red.
6. Every successful job report shows its cover letter in a collapsible
   section, collapsed by default, with a working copy-to-clipboard
   button.
7. No regressions: the real `/analyze` proxy flow, per-job error
   isolation, and Docker build all still work — reverified the same
   way Bolt 3 originally was (real Playwright run against the live
   backend, real Docker build/run).
