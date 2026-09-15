## Context

See proposal.md. Root cause is confirmed: the re-entry cache fast-path assigns
`dateGroups` synchronously inside the pre-render `loading()` hook, so the heavy
timetable render lands in the same rendering task as the shell's optimistic
header/nav update and the browser paints once, after the render.

The fix is a lifecycle relocation, not a rewrite: move the render-driving
assignment past the first paint. The subtlety is that the surrounding behaviors
are wired through the same path and must be preserved.

Aurelia facts this design relies on (confirmed against Context7 `/aurelia/aurelia`,
2026-09-15):

- Navigation order: `canUnload` → `canLoad` → `unloading` → `loading` →
  component hooks (`binding`→`bound`→`attaching`→`attached`). `loading()` runs
  before the component renders.
- `attached()` runs bottom-up after the subtree is mounted but is **still inside
  the activation task, before the browser's first paint**. So moving work to
  `attached()` alone does NOT push a *synchronous* assignment past the paint.
- To actually land the assignment on a LATER frame you need a **macrotask hop**
  (`queueAsyncTask`, `setTimeout`) or a **double** `requestAnimationFrame`. A
  SINGLE `requestAnimationFrame` is NOT sufficient — its callback runs just
  before that same frame's paint, so a synchronous `dateGroups` assignment inside
  one rAF would still coalesce the heavy render into the same paint as the shell
  update (reproducing this bug). Do not treat a single rAF as equivalent.
- `queueAsyncTask` (from `aurelia`) is the idiomatic deferral primitive and
  returns an awaitable/cancelable Task; it is the one used below.

## Goals / Non-Goals

**Goals:**

- On re-entry, paint the shell (header title + active nav tab) at navigation
  intent, independent of the timetable render.
- No empty-state flash; no lost background refresh; celebration/onboarding latch
  and deep-link resolution unchanged.

**Non-Goals:**

- Reducing how much the timetable render costs (virtualization / P4).
- Touching the cold-load path (already separated by the `isLoading` skeleton).
- Any CSS / P1 / P2 work.

## Decisions

- **Decision: Defer only the cache fast-path render; leave the cold path alone.**
  The cold path already shows a skeleton and fills in after an awaited fetch, so
  it never blocks the shell paint. Only the fast-path assigns render state
  synchronously in `loading()`. Scope the change to that branch.

- **Decision: Yield only the cached-assignment branch with `queueAsyncTask`; do
  NOT relocate the whole load trigger.** `loading()`'s single call is
  `void this.loadData()`, and `loadData()` is the one entry point for BOTH the
  cache fast-path and the cold fetch. Moving that trigger to `attached()` would
  also delay the cold-path fetch kickoff — violating the Non-Goal / Decision 1
  ("leave the cold path alone"). So keep `loading() → void this.loadData()` as-is,
  and inside `loadData()` wrap ONLY the cache fast-path's synchronous
  `this.dateGroups = cachedDateGroups` (and its `timetableLoaded` flip) in
  `queueAsyncTask(() => { … })`, so that render lands on the frame AFTER the
  shell's first paint. The Task Queue macrotask hop is the load-bearing part;
  `attached()` alone would not help (it is pre-paint), and relocating the trigger
  is neither necessary nor in scope. The cold path is untouched — its awaited
  fetch already yields, and its `isLoading` skeleton already separates the shell
  paint from the timetable fill.

- **Decision: Cover the one-frame gap with the skeleton, not the empty state.**
  Between the shell paint and the deferred cached render there is one frame with
  no `dateGroups`. The template must render the `state-placeholder` loading
  skeleton for that frame, never the "no concerts" empty state (which is only
  correct after a settled load returns zero groups). This likely means gating the
  empty state on a "load has settled" flag rather than on `dateGroups.length ===
  0 && !isLoading`.

- **Decision: Do not overload `isLoading` for the skeleton on the fast path.**
  `isLoading` also guards `refreshInBackground()` (`if (this.needsRegion ||
  this.isLoading) return`). Setting `isLoading = true` on the fast path to show
  the skeleton would suppress the background refresh. Use a separate, dedicated
  latch for "cached paint pending" (e.g. `pendingCachePaint`) that drives the
  skeleton for the one frame and does NOT gate the refresh — or sequence the
  refresh kickoff after clearing the flag.

## Risks / Trade-offs

- **Empty-state flash** → Mitigation: skeleton-gates-on-settled (above); add a
  test asserting the empty state never renders while a cached paint is pending.
- **`isLoading` double-duty breaking `refreshInBackground`** → Mitigation:
  dedicated `pendingCachePaint` latch; unit-test that the background refresh still
  fires on the fast path.
- **`timetableLoaded` latch timing** (celebration + onboarding completion +
  deep-link) is anchored to `timetableLoaded` flipping true → Mitigation: flip
  `timetableLoaded` inside the deferred task, after `dateGroups` is assigned, so
  the ordering the latch relies on is unchanged; keep the existing
  `timetableLoadedChanged` handler untouched. Cover with the existing
  celebration/latch tests.
- **A cancelled navigation mid-defer** (user taps away before the queued task
  runs) → Mitigation: cancel the queued task in `detaching()` / on a new load, so
  a stale cached paint never writes into a torn-down or re-navigated route
  (mirror the existing `abortController` discipline).
- **Perceived regression of "instant cached paint"** → the cached timetable now
  appears one frame later behind a skeleton. Accept: trading a sub-frame delay of
  the list for an instant, responsive header/nav is the whole point, and the
  current behavior freezes the shell for seconds.

## Migration Plan

- Single-file behavior change in `dashboard-route.ts` (+ possibly a template
  gate for the skeleton-vs-empty decision). Reversible by reverting. Ships with
  the normal frontend release, but only after device verification confirms the
  header/nav paint precedes the timetable render.

## Verification (device-only — headless passkey auth is infeasible)

On the reference profile (Pixel 8 or emulation + 4× CPU), signed in with a
populated timetable, from another tab tap the dashboard nav tab and record a
Performance trace:

1. The header `<h1>` and the active nav tab switch (paint) **before** the
   timetable render block — i.e. there is an early paint frame containing the
   switched shell, ahead of the large Rendering block.
2. No empty-state flash during re-entry (skeleton only).
3. INP for the tap is substantially below the pre-change baseline and the shell
   is interactive while the timetable fills.
4. Background refresh still runs (fresh data swaps in), the post-signup / guest
   celebration still fires once when due, and a `/concerts/:id` deep-link still
   opens the detail sheet.

## Open Questions

- Whether a dedicated `pendingCachePaint` latch or reusing the cold-path skeleton
  with a settled-gate reads cleaner in the template — decide during
  implementation against the actual `dashboard-route.html` structure.
