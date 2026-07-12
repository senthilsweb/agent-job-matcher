# Design — `fix-playground-ui-parity`

## 1. Header + chrome parity

Model: `mcp-chat-client/src/demo/DemoApp.tsx`'s `useBackendStatus()` hook
(polls `${apiEndpoint}/health` every 5s, three states `checking` /
`online` / `offline`, colored ring-badge with a dot) — same shape as
`privacyshield/frontend/src/App.tsx`'s static "Online" pill, but real
and polling rather than hardcoded, which is the better of the two
existing patterns and the one to copy exactly.

The playground has no client-side backend URL to poll directly (Bolt 3
deliberately keeps `API_URL` server-side only, in `app/api/analyze/
route.ts`). Add a small `GET /api/health` route handler (same proxy
shape as `/api/analyze`) that forwards to `${API_URL}/health` — the
browser polls this app's own route, never the backend directly, so the
"API_URL never reaches the browser" invariant from the original Bolt 3
spec holds.

Header layout copies `DemoApp.tsx`'s structure directly: icon (`Bot`
already used elsewhere in this suite, or `Briefcase` — keep the
existing `Briefcase` icon already in the playground's header) + title +
subtitle on the left, status pill on the right, `h-16` header bar,
bottom border.

Form pane: wrap `SidebarForm`'s contents in shadcn `Card` /
`CardHeader` / `CardTitle` (icon + "Analyze fit") / `CardDescription`,
each input paired with a `Label` — the exact composition
`privacyshield/frontend/src/features/Detect.tsx` uses for its form
Card. Sidebar width goes from `lg:w-80` (320px) to `lg:w-96` (384px).

## 2. Sticky submit button

Root cause: `SidebarForm`'s outer `flex h-full flex-col gap-5 p-5` with
`mt-auto` on the Button assumes the column never exceeds the viewport
height — false once enough job-link rows are added. Fix: split the
form into a scrollable content region (`flex-1 overflow-y-auto`) and a
non-scrolling footer that's always `sticky bottom-0` with its own
background and top border — the same "pinned action bar" shape
`mcp-chat-client`'s `ChatInput` and `privacyshield`'s Card footers both
use (an always-visible action row, never inside the scrolling region).

## 3. Wide accordion + visible expand affordance

`results-panel.tsx`'s wrapping `<div className="mx-auto max-w-3xl">`
in `app/page.tsx` moves to `max-w-none` (full available width of the
main content area) — "wide accordion" per the owner's literal wording.

`report-card.tsx`'s `AccordionTrigger` gains: a hover background
(`hover:bg-accent/40`), a persistent small "Click to expand full
report" hint (`text-muted-foreground`, right-aligned next to the
chevron, hidden on very small viewports), and the chevron itself
enlarged (the shadcn default is `size-4`; bump to `size-5` with a
rotate transition already built into the installed `Accordion`
primitive). The whole trigger row also gets an explicit `Card`-style
container (border + shadow already present; adding a `hover:shadow-md
transition-shadow` makes the whole row read as an interactive control).

## 4. Industry-standard match-status colors

Replace `MATCH_STATUS_CLASSES` in `lib/types.ts` with the standard
5-step green→red grading scale (credit-score/ATS convention — best is
always green, never brand purple):

| Status | Old | New |
|---|---|---|
| `strong_match` | `bg-brand-700` (purple) | `bg-emerald-600` |
| `good_match` | `bg-emerald-500` (green) | `bg-lime-500` |
| `moderate_match` | `bg-amber-500` | `bg-amber-500` (unchanged) |
| `weak_match` | `bg-orange-500` | `bg-orange-500` (unchanged) |
| `no_match` | `bg-red-500` | `bg-red-500` (unchanged) |

Brand purple (`brand-700`) stays reserved for chrome (header icon tile,
sidebar accents, active states) — never used as a score-quality signal,
matching how `privacyshield` uses its brand color for UI chrome and a
separate semantic palette (`entity-styles.ts`) for data-quality signals.

## 5. Cover letter — collapsible + copy-to-clipboard

Add a `Collapsible`/`CollapsibleTrigger`/`CollapsibleContent` (shadcn,
installed this change) section inside `report-card.tsx`'s
`AccordionContent`, collapsed by default, trigger reads "Cover letter"
with a chevron. Content is the raw `cover_letter_text` in a
`whitespace-pre-wrap` block (it's already fully rendered text from the
backend, matching `privacyshield`'s `OutputCard`'s
`whitespace-pre-wrap` treatment for pre-formatted text).

Copy button: same pattern as `privacyshield/frontend/src/components/
Workspace.tsx`'s `OutputCard.handleCopy` — `navigator.clipboard.
writeText(text)`, local `copied` state toggling a Lucide `Copy`/`Check`
icon for ~1.5s. No toast library is added (`sonner` isn't installed in
this app and one button's own icon-swap is a sufficient confirmation
for a single, low-stakes action) — a deliberate, smaller-scope choice
than privacyshield's toast, not an oversight.
