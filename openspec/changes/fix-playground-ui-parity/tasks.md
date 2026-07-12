# Tasks — `fix-playground-ui-parity`

Owner-directed, found during real UAT (2026-07-12) against
http://localhost:3011. Approved for immediate fix + implementation in
the same request. **All 5 bolts implemented and verified 2026-07-12.**

## Bolt 1 — Header + chrome parity ✅

- [x] `app/api/health/route.ts` — proxy to `${API_URL}/health`
- [x] `lib/use-backend-status.ts` — polls `/api/health` every 5s, three
      states, mirrors `mcp-chat-client`'s `useBackendStatus()` exactly
- [x] `components/playground/status-pill.tsx` — colored ring-badge +
      dot, mirrors both `privacyshield` and `mcp-chat-client`'s header
      pill shape
- [x] `app/page.tsx` header — icon + title + subtitle + the live status
      pill, `h-16` bar with bottom border, matching both references'
      structure
- [x] `sidebar-form.tsx` — rebuilt as a `Card`/`CardHeader`/`CardTitle`/
      `CardDescription` composition with `Label`-paired inputs, same
      shape as `privacyshield/frontend/src/features/Detect.tsx`
- [x] Sidebar width `lg:w-80` (320px) → `lg:w-96` (384px)

## Bolt 2 — Sticky submit button ✅

- [x] `sidebar-form.tsx` — split into a scrollable `CardContent` region
      (`min-h-0 flex-1 overflow-y-auto`) and a non-scrolling
      `sticky bottom-0` footer for the Submit button
- [x] **Verified (2026-07-12, real Playwright):** added 6 job-link
      rows — Submit button's bounding box (`y: 902, height: 32` in a
      950px-tall viewport) confirmed fully on-screen, no scroll needed;
      previously this exact scenario buried the button below the fold

## Bolt 3 — Wide accordion + expand affordance ✅

- [x] `app/page.tsx` — removed the `mx-auto max-w-3xl` wrapper entirely
      in the rebuild; results now use the full main-content width
- [x] `report-card.tsx` — trigger gained `hover:bg-accent/40`, a
      persistent "Click to expand full report" hint row, and the whole
      card gained `hover:shadow-md transition-shadow`
- [x] `components/ui/accordion.tsx` — chevron icon `size-4` → `size-5`,
      recolored to `text-brand-700` (shared primitive, only usage in
      this app, safe to bump app-wide)

## Bolt 4 — Industry-standard match-status colors ✅

- [x] `lib/types.ts` — `MATCH_STATUS_CLASSES`: `strong_match` purple →
      `emerald-600` (green), `good_match` → `lime-500` (lighter green,
      was already emerald — now distinct from strong), moderate/weak/
      no_match unchanged (amber/orange/red already correct). Brand
      purple no longer used as a quality signal anywhere in the cards

## Bolt 5 — Cover letter: collapsible + copy-to-clipboard ✅

- [x] `npx shadcn add collapsible label`
- [x] `components/playground/cover-letter-section.tsx` — collapsed by
      default, `cover_letter_text` rendered `whitespace-pre-wrap`,
      chevron rotates on open via Base UI's `data-panel-open` attribute
- [x] Copy button — `navigator.clipboard.writeText`, icon swaps
      Copy→Check for 1.5s, no toast library (matches
      `privacyshield`'s `OutputCard.handleCopy` pattern, minus the
      toast since `sonner` isn't installed here and wasn't needed)

## Verification

- [x] **Real Playwright run against the live backend (2026-07-12, not
      assumed):** header status pill shows genuine "Backend online"
      (polling `/api/health`); Card-composed form with wider (w-96)
      sidebar confirmed visually; 6-job-link-row sticky-submit test
      passed; full-width results with visible "Click to expand full
      report" hint confirmed; `strong_match` renders emerald green
      (82/100, Gusto) and `good_match` renders lime (79/100, Anthropic)
      — visually distinct now; cover letter renders collapsed by
      default, expands on click, chevron flips, copy button confirmed
      via `navigator.clipboard.readText()` returning the real 1209-char
      letter plus the checkmark icon rendering. Regression check: a
      two-job submission (one bad path, one real job) still isolates
      the failure correctly, and the required-score reallocation
      (0 preferred skills → 44/60 scale) still renders correctly
- [x] Docker image rebuilt and reverified standalone
      (`API_URL=http://host.docker.internal:8000`) — `/api/health`
      returns `{"status":"online"}` inside the container
- [x] The owner's live UAT compose service (`playground` at
      `localhost:3011`) rebuilt and restarted with these fixes so the
      same URL the owner was already testing against now serves the
      corrected UI
- [ ] Owner: re-review at http://localhost:3011, then status →
      **verified** and archive

## Bolt 6 — Correction: literal privacyshield template parity ✅ (2026-07-12)

Second UAT pass, owner direction: stop re-deriving the look — borrow
`privacyshield/frontend`'s actual layout, and self-verify against the
real running reference (http://localhost:7171) before reporting done.

- [x] **Extracted exact reference values first, from the live
      privacyshield container, not guessed:** font `Inter, ui-sans-
      serif, system-ui, sans-serif`; nav rail `rgb(74, 21, 75)` (=
      `#4a154b`) at `240px` (w-60) expanded / `64px` (w-16) collapsed;
      header height `64px`; main-content muted-gray text
      `rgb(113, 113, 122)` (zinc-500); button radius `6px`, input
      radius `8px`; collapsible sidebar via a burger button in the
      header (`aria-label="Collapse sidebar"`); fixed-footer GitHub
      link
- [x] `app/layout.tsx` — swapped `Geist`/`Geist_Mono` for `next/font/
      google`'s `Inter`, matching privacyshield exactly
- [x] `app/globals.css` — **found and fixed a real latent bug while
      investigating the font mismatch:** `--font-sans: var(--font-
      sans)` was circular/self-referential (should have pointed at the
      actual font variable), so the `font-sans` utility was silently
      falling back to the browser default the whole time — part of why
      the page read as "tailwind is missing"/unstyled. Now
      `--font-sans: var(--font-inter)`. Also: `--muted-foreground`
      changed from `oklch(0.556 0 0)` (too light) to `#71717a` (zinc-
      500, matches privacyshield's actual computed color exactly); new
      `--color-slack-green` / `--color-slack-green-dark` tokens
      (`#2eb67d` / `#1d9c68` — Slack's own green brand accent, distinct
      from the brand-purple ramp and from the match-quality colors)
- [x] `components/playground/nav-rail.tsx` (new) — direct structural
      port of `privacyshield/frontend/src/components/Sidebar.tsx`:
      brand-700 background, collapsible width, logo tile, a "Workflow"
      section label, one active nav item (this app has one job, so no
      tab list), fixed-footer GitHub link (`@iconify/react`'s
      `mdi:github` — lucide-react 1.24.0 dropped brand/logo icons
      entirely, confirmed by grepping its package for "github" and
      finding nothing; iconify is the same fallback mcp-chat-client and
      privacyshield itself already use for this exact icon)
- [x] `app/page.tsx` — restructured to `[NavRail][header with burger
      toggle + page title/subtitle + status pill][form Card | results]`,
      matching `privacyshield/frontend/src/App.tsx`'s shape exactly;
      collapse state persisted to `localStorage`, same pattern; removed
      the redundant "Fit reports" / "One evidence-grounded..." heading
      from the results pane (the header already establishes context)
- [x] `components/playground/job-link-list.tsx` — the "add" action is
      now a square (`rounded-none`), Slack-green (`bg-slack-green`)
      icon button placed directly next to the **last** job-link input
      (not a separate full-width block below), only rendered once;
      remove ("×") buttons unchanged
- [x] **Verified (2026-07-12, real Playwright against the live backend,
      compared directly against the real privacyshield container's
      computed styles, not assumed):** body font resolves to `Inter,
      "Inter Fallback"`; nav rail background `rgb(74, 21, 75)` at
      `240px` — both exact matches to the live reference; main-content
      gray text `rgb(113, 113, 122)` — exact match; burger toggle
      collapses/expands the rail correctly (screenshotted both states);
      real end-to-end submission (Temporal's Senior Manager, Solutions
      Architecture JD, real 58/100 moderate-match score) rendered
      correctly with the new layout; the green "+" button adds a row
      (verified 1→2 job-link inputs); re-verified Bolt 4/5's fixes
      (cover letter expand + copy, industry-standard colors) still work
      unchanged after this restructuring
- [x] Docker image rebuilt; owner's live UAT compose service
      (`playground` at `localhost:3011`) rebuilt and restarted with
      this correction
- [ ] Owner: re-review at http://localhost:3011
