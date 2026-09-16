## Why

The fan-web dashboard timetable is the app's slowest surface, and three findings
converge on one cause: **it renders everything, eagerly, inside the navigation's
pre-paint window.**

1. **Re-entry freeze.** Production traces on a populated account measured a
   dashboard tab-switch re-entry at **INP 64,472 ms** — over a minute of
   unresponsiveness — with 24,556 ms of Rendering in the first 31 s alone, and
   the interaction still running when the recording was stopped. Cold load on
   the same account: 21,352 ms Rendering, 31.6 s total. **Both were recorded
   with CPU throttling off**, so a mid-range phone is worse again. (An earlier
   trace on a smaller account read ~2.6 s / INP 2,536 ms; that figure
   understated the problem by roughly 25x and is superseded.) The shell already
   switches page identity optimistically at `au:router:navigation-start`, but the
   re-entry cache fast-path assigns `dateGroups` synchronously inside the
   pre-render `loading()` hook. The header/nav binding update and the whole
   timetable render therefore land in one rendering task, and the browser paints
   once — after the render. The optimistic switch is decoupled at the state
   level but not at the paint level.

2. **Nothing is scoped to the viewport.** The timetable renders every date group
   unconditionally — **225 of them** on the measured account, roughly seven
   months of concerts, because the query has a lower date bound and no upper
   one. There is no virtualization anywhere in the frontend.
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
- **Reveal progressively, in CSS.** Today every card runs the same entrance
  animation simultaneously. Instead the date group becomes the motion unit, with
  two triggers that cannot collide: a `sibling-index()` stagger reveals the
  groups in view top-to-bottom as data arrives, and a view timeline reveals
  groups as they are scrolled into view. Both are pure CSS, compositor-only, and
  fully suppressed under `prefers-reduced-motion`. On re-entry the fan has
  already seen this content, so it is restored instantly with no motion and at
  the previous scroll position — lost today, because a new route instance is
  created on every navigation and nothing persists the offset.
- **Place each concern on the lifecycle that owns it, and schedule nothing.**
  Starting the fetch stays in the route lifecycle (`loading()` + `void`, earliest
  and blocking nothing); reflecting render state moves to the component
  lifecycle, as the non-blocking contract requires. No scheduling primitive is
  used: spikes measured that the earlier `queueAsyncTask` idea, and yielding from
  `attaching()`, were both treating a symptom — once containment bounds the
  render to the viewport (177.7 ms → 44.2 ms at 4× CPU), a single paint is fast.
  See design.md → Spike evidence.

**Decouple the laser beam from card rendering**

- The beam overlay is positioned by JavaScript that reads every matched card's
  geometry on every frame. That is the `Forced reflow while executing JavaScript
  took 58194ms` in the cold-load trace, and it would force layout of every
  off-screen group once containment lands, cancelling it. Drive the beams from
  their anchor concert's scroll position in CSS instead, deleting the scroll
  listener, the rAF loop and the geometry reads.
- Scroll-driven animations are unavailable in Firefox, so beams are absent there.
  The `beam-effect-toggle` capability defines the beam as a visual effect that is
  off by default and user-toggled, so this is a decorative degradation — and it
  buys every user the removal of a per-frame layout cost.

**Cross-route — bring the non-blocking contract up to date**

- Broaden `non-blocking-menu-navigation` from the three originally named routes
  to every bottom-nav tab, and state that a *synchronous render-state assignment*
  inside `loading()` blocks first paint exactly as an `await` does.
- Fix Settings: start its two loads non-blocking.

Out of scope:

- `@aurelia/ui-virtualization` / `virtual-repeat`. Containment on a flattened
  group is the smaller step, and the existing measurement already supports it.
  Revisit only if the post-change trace still shows a multi-second block.
- **Bounding what is fetched**, as opposed to what is rendered. 225 groups is
  ~7 months of concerts for one view; an upper date bound or paging may be the
  better fix for the fetch side. Rendering-side containment is what this change
  can deliver on its own, and the post-change measurement will show how much of
  the residual is fetch scope.
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

- `beam-effect-toggle`: the beam becomes presentational in the literal sense —
  driven by scroll position in CSS, reading no card geometry and costing no
  per-frame scripting — and absent where the platform cannot drive it, with the
  toggle, the persisted preference and the timetable otherwise unchanged.
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
- **Verification**: a trace on a populated account must show INP for the nav-tab
  tap down from the 64,472 ms baseline to an interactive figure, the frame on
  screen while data loads, no empty-state flash, and lane alignment unchanged.
  Passkey sign-in cannot be driven headlessly, but the repo has a password-based
  E2E user (`npm run auth:capture:password`) that can, so the before/after
  comparison can be automated against the dev environment — noting that the dev
  test account does not carry the 225-group data volume, so the production trace
  remains the authoritative baseline.
