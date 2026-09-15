## Why

The shell already switches page identity (header title + active bottom-nav tab)
optimistically at navigation intent — `AppShell` subscribes to
`au:router:navigation-start` and calls `pageHeaderState.setOptimistic(...)`, and
the `<page-header>` / `<bottom-nav-bar>` live in the shell grid (outside
`au-viewport`), bound to that observable state. So the **state** is decoupled
from the incoming route's render.

But on **dashboard tab-switch re-entry**, the header/nav do not visually switch
until the whole timetable finishes rendering (a real-device trace showed the
re-entry as a single ~2.6 s Rendering block; INP 2,536 ms). Confirmed root cause
(verified against Aurelia's own docs, Context7 `/aurelia/aurelia`, 2026-09-15):

- The router `loading()` hook **runs after navigation is approved but before the
  component is rendered**, and the router awaits it before the view swap.
- `DashboardRoute.loading()` fires `void this.loadData()`, whose **cache
  fast-path assigns `this.dateGroups = cachedDateGroups` synchronously** (the
  re-entry path — "paint the previous render instantly"). No `await` precedes it.
- Because `loading()` is a pre-render hook, the component's **first render already
  contains all ~23 date groups**. Aurelia flushes the shell's optimistic
  header/nav binding update and this heavy timetable render in the **same
  rendering task**, so the browser produces a **single paint after the timetable
  is built** — the header/nav paint is starved by the render.

So the optimistic switch is decoupled at the state level but NOT at the paint
level, purely because the re-entry render is driven from a pre-paint lifecycle
hook. Aurelia's own troubleshooting guidance is to move heavy/non-blocking work
out of the pre-render hooks (`canLoad`/`loading`) to `attached()` + the Task
Queue (`queueAsyncTask`). The cold-load path already does the right thing (it
shows an `isLoading` skeleton and fills in after the async fetch); only the
**cache fast-path** skips that separation by assigning render state synchronously.

## What Changes

- Defer the dashboard re-entry **cache fast-path** render so the shell (header +
  nav) paints first, then the cached timetable fills in on a subsequent frame —
  by moving the render-driving `dateGroups` assignment out of the pre-render
  `loading()` path and yielding one frame via the Aurelia Task Queue
  (`queueAsyncTask`) after activation.
- Cover the one-frame gap with the existing **skeleton** (`state-placeholder`
  loading), NOT the empty-state, so re-entry shows header/nav instantly + a brief
  skeleton instead of a 2.5 s freeze, and never flashes an "empty" state.
- Preserve the existing behaviors anchored to the load path: the background
  refresh (`refreshInBackground`), the `timetableLoaded` → celebration /
  onboarding-completion latch, and the `/concerts/:id` deep-link resolution.

Out of scope:

- List **virtualization** / the group→lane→card structural flatten (the deferred
  P4 from `optimize-dashboard-render-cost`) — this change only relocates WHEN the
  cached render runs, not HOW MUCH is rendered. If, after this change, the
  post-skeleton timetable render is still a multi-second task on the reference
  profile, virtualization is the follow-up.
- The CSS render-cost work (P1 shipped, P2 reverted) in
  `optimize-dashboard-render-cost`.

## Capabilities

### New Capabilities

- `dashboard-timetable-rendering`: this capability does not yet exist under
  `openspec/specs/` — it is created by the in-flight `optimize-dashboard-render-cost`
  change (still unmerged; "Tab-switch re-entry does not freeze on rendering" is a
  *scenario* there, not a requirement). This change layers an ADDED requirement
  onto it: page identity (header title + active nav tab) is painted at navigation
  intent **independent of** the timetable render — i.e. the re-entry render must
  not be driven from a pre-first-paint lifecycle hook. Ordering: `openspec sync`
  (tasks 5.1) depends on the sibling change syncing this capability into
  `openspec/specs/` first (or on the two deltas being reconciled at sync time).

## Impact

- **Frontend only**, one file: `frontend/src/routes/dashboard/dashboard-route.ts`
  (only `loadData()`'s cache fast-path branch — wrap its synchronous assignment in
  `queueAsyncTask`; `loading()` keeps calling `loadData()` unchanged, and the cold
  path is untouched). Possibly a small template/skeleton tweak if needed to avoid
  the empty flash.
- **Behavior change**: re-entry now paints header/nav + a brief skeleton
  immediately, then the cached timetable (previously: instant cached timetable
  but a multi-second header/nav freeze). Net UX win; the "instant cached paint"
  becomes "instant shell + one-frame-later cached paint".
- **Risks** (see design): empty-state flash, `isLoading` double-duty (skeleton
  vs `refreshInBackground` guard), and the `timetableLoaded` latch timing — all
  must be preserved.
- **Verification**: device-only (headless passkey auth is infeasible) — a
  reference-profile re-entry trace must show the header/nav paint BEFORE the
  timetable render block, with INP substantially below the pre-change baseline
  and no empty-state flash.
