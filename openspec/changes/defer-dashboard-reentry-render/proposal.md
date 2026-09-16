## Why

The fan-web dashboard timetable is the app's slowest surface, and three findings
converge on one cause: **it renders everything, eagerly, inside the navigation's
pre-paint window.**

1. **Re-entry freeze.** A real-device trace showed a dashboard tab-switch
   re-entry as a single ~2.6 s Rendering block (INP 2,536 ms). The shell already
   switches page identity optimistically at `au:router:navigation-start`, but the
   re-entry cache fast-path assigns `dateGroups` synchronously inside the
   pre-render `loading()` hook. The header/nav binding update and the whole
   timetable render therefore land in one rendering task, and the browser paints
   once — after the render. The optimistic switch is decoupled at the state
   level but not at the paint level.

2. **Nothing is scoped to the viewport.** The timetable renders all ~23 date
   groups unconditionally; there is no virtualization anywhere in the frontend.
   The sibling `optimize-dashboard-render-cost` change measured the cost as
   **Layout 46% + Recalculate Style 32%** — dominated by work done for content
   the user cannot see. Its P2 (`content-visibility: auto`) measured a real win
   (forced reflow 751 ms → 528 ms) but was **reverted**: the component chains
   `grid-template-columns: subgrid` four levels deep, and containment severs that
   chain, so cards overflow their lane. The layout structure, not the CSS lever,
   is the blocker.

3. **There is no App Shell.** The parts of the timetable that need no data — the
   HOME/NEAR/AWAY stage header and the lane columns — are gated on
   `dateGroups.length > 0`, so they are absent until data arrives. What shows
   instead is a generic six-bar placeholder whose shape does not match the
   timetable, so the swap to real content shifts layout.

Separately, the merged `non-blocking-menu-navigation` capability names only
**three** bottom-nav routes (My Artists, Dashboard, Discovery). The nav has since
grown to **five** — Tickets and Settings were added and never brought under the
contract. Settings now awaits two RPCs inside `loading()`, so tapping it holds
the previous screen frozen until the network resolves: exactly the failure the
capability exists to prevent. The contract is sound; its scope went stale.

Both load-bearing assumptions behind this change were verified by spike before
the design was written — the CSS flatten (does removing the subgrid chain keep
lane alignment and allow containment?) and the lifecycle placement (does moving
the assignment actually produce an earlier paint?). Several earlier assumptions
did not survive; see design.md → Spike evidence.

## What Changes

**Dashboard — render progressively instead of all-at-once**

- **Flatten the subgrid chain (enabling refactor).** Give each date group its own
  `grid-template-columns` matching the stage header instead of inheriting through
  a four-level `subgrid` chain. The columns are equal fractions, so identical
  per-group definitions produce identical widths — subgrid is not load-bearing
  here. This makes each group independently containable and is the prerequisite
  for everything below.
- **App Shell frame.** Render the stage header and lane columns without data, and
  replace the generic six-bar placeholder with a timetable-shaped skeleton, so a
  tab switch paints the real frame immediately and the data swap causes no layout
  shift.
- **Scope rendering to the viewport.** With the chain flattened, apply
  containment to the date group so off-screen groups skip style, layout and
  paint. Scrolling reveals subsequent dates.
- **Motion belongs to cold load, not re-entry.** Cards animate in on a genuine
  first load. On re-entry the user has already seen this content, so the
  timetable is restored instantly — no entrance animation — and the scroll
  position is preserved. Scroll position is lost today: a new route instance is
  created on every navigation and nothing persists the offset.
- **Place each concern on the lifecycle that owns it.** Starting the fetch stays
  in the route lifecycle (`loading()` + `void`, earliest and blocking nothing).
  Reflecting render state — including the cached fast path — moves to the
  component lifecycle, so the component's first render contains the frame and
  skeleton only. A spike measured that this relocation alone is **not enough**:
  the paint yield has to come from `attaching()` returning a promise that settles
  off the microtask queue, which on cold load is the entrance animation itself.
  See design.md → Spike evidence.

**Cross-route — bring the non-blocking contract up to date**

- Broaden `non-blocking-menu-navigation` from the three originally named routes
  to every bottom-nav tab, and state that a *synchronous render-state assignment*
  inside `loading()` blocks first paint exactly as an `await` does.
- Fix Settings: start its two loads non-blocking.

Out of scope:

- `@aurelia/ui-virtualization` / `virtual-repeat`. Containment on a flattened
  group is the smaller step, and the existing measurement already supports it.
  Revisit only if the post-change trace still shows a multi-second block.
- The CSS render-cost work (P1 shipped, P2 reverted) in
  `optimize-dashboard-render-cost`.
- Loading skeletons for Tickets / Order / Discovery. These are real gaps, but
  they belong to the App Shell concern, not the non-blocking contract this
  change updates.
- `lottery-apply`'s `await` inside `loading()` is deliberate — it parks an
  unverified fan on the `verify-required` step before any card hold — and is
  recorded as a documented exception, not changed.

## Capabilities

### New Capabilities

- `dashboard-timetable-rendering`: this capability does not yet exist under
  `openspec/specs/` — it is created by the in-flight `optimize-dashboard-render-cost`
  change (still unmerged), which owns its `## Purpose`. This change layers ADDED
  requirements onto it: the timetable frame paints without data, rendering is
  scoped to the viewport, entrance motion is limited to first load (re-entry
  restores instantly, scroll included), and page identity paints independent of
  the timetable render. Ordering: `openspec sync` depends on the sibling change
  syncing this capability into `openspec/specs/` first, or on the two deltas
  being reconciled at sync time.

### Modified Capabilities

- `non-blocking-menu-navigation`: broaden the route scope from three named routes
  to every bottom-nav menu tab, and extend the contract to cover the cached
  fast path (a synchronous render-state assignment is as blocking as an `await`)
  and the re-entry loading indicator.

## Impact

- **Frontend only.** Dashboard: `dashboard-route.ts` / `.html` / `.css` /
  `.spec.ts`, `concert-highway.html` / `.css` / `.spec.ts`, `event-card.css`, and
  `concert-store.ts` (scroll-offset persistence alongside the cached groups).
  Cross-route: `settings-route.ts`.
- **Storybook contract.** `concert-highway.stories.ts` carries a regression guard
  asserting there is NO `content-visibility` and that the `<li>` keeps its
  subgrid. That guard encodes the P2 revert and MUST be rewritten as part of the
  flatten, not deleted silently. New visual states (frame-without-data,
  timetable-shaped skeleton) require new named stories per the repo's story
  contract, and committed visual baselines must be regenerated in the pinned
  container.
- **Build-time guard.** `verify:build-templates` asserts route chunks still
  contain template-derived markers; the dashboard template changes here, so run
  `npm run build && npm run verify:build-templates` locally and update
  `ROUTE_MARKERS` if a marker moves.
- **Behavior change.** Re-entry paints the shell and the timetable frame
  immediately, then restores the cached timetable instantly at the previous
  scroll position with no entrance animation. Cold load paints the frame, then
  animates cards in as data arrives. Settings no longer freezes the outgoing
  screen on its RPCs.
- **Risks** (see design): the flatten changing lane alignment, containment
  interacting with the sticky date separator and the scroll-driven laser beams,
  suppressing motion on re-entry without suppressing it on cold load, and
  restoring a scroll offset against a not-yet-rendered list.
- **Verification**: device-only (headless passkey auth is infeasible) — a
  reference-profile trace must show the shell and frame painting ahead of the
  timetable render, INP substantially below the pre-change baseline, no
  empty-state flash, and lane alignment unchanged.
