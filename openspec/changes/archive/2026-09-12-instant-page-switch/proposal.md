## Why

When a fan taps a bottom-nav tab, the nav highlight and the page header only
change once the incoming route finishes loading and its fade-in transition
begins. On a cold route chunk, or behind the 250–350ms page-transition fade, the
UI keeps showing the previous tab's highlight and the previous page's title —
the tap feels unacknowledged and the switch feels sluggish. Page identity
(which tab is selected, what page this is) is a navigation-intent signal and
should not wait on content loading or animation.

## What Changes

- Decouple **page identity** (page header title + active nav tab) from
  **content loading**: identity switches at navigation intent, content keeps
  loading/animating behind it.
- Introduce a single reactive page-header state (a `IPageHeaderState`
  singleton exposing observable `titleKey`, `morphTitle`, and `activePath`) as
  the one source of truth for the current page's header and the nav highlight.
- Hoist the page header out of each route and into the app shell as a single,
  persistent instance driven by that state. **BREAKING** (architecture): this
  reverses the current "route components own page structure / the shell provides
  no shared layout" decision for the header region specifically. Routes stop
  rendering `<page-header>` and drop their `header` grid area; the shell grid
  gains a `header` row above `<au-viewport>`.
- Drive both the header title and the nav highlight optimistically from the
  router lifecycle: set them on `au:router:navigation-start` (immediately, from
  the target route), confirm on `au:router:navigation-end` (authoritative,
  covers redirects/fallback/dynamic titles), and roll back on
  `au:router:navigation-error`.
- Move the bottom-nav active-tab computation off the router's `routeTree` and
  onto `IPageHeaderState.activePath`, so the highlight is instant and the
  component becomes a pure function of injected state.
- Preserve dynamic titles: the dashboard's My Timetable ↔ All Nearby title swap
  writes to `IPageHeaderState` and keeps its View-Transition morph.

Out of scope: route chunk prefetching (declined — a separate, orthogonal
latency improvement); relocating any page action controls (already moved to the
FAB action launcher in a prior change).

## Capabilities

### New Capabilities
<!-- none — the behavior lives in the shell, page-header CE, and bottom nav,
     all owned by existing capabilities below. -->

### Modified Capabilities
- `app-shell-layout`: the shell grid gains a `header` row and hosts a single
  page-header instance; routes no longer own the header region; a new
  requirement defines the optimistic, navigation-intent-driven switch of the
  header title and the active nav tab (with reconcile-on-end and
  rollback-on-error).
- `page-header-ce`: the page header becomes a single shell-hosted instance whose
  `title-key`/`morph-title` are bound to `IPageHeaderState` rather than authored
  per route; its `grid-area: header` now resolves inside the shell grid, and
  routes no longer define a `header` grid area for it.

## Impact

- Frontend (fan-web) only. No backend, proto, or API changes.
- `src/app-shell.ts` / `.html` / `.css`: subscribe to the three router lifecycle
  events; add the `header` grid row; render the shell-owned `<page-header>`.
- New `src/services/page-header-state.ts` (`IPageHeaderState` singleton).
- `src/components/bottom-nav-bar/bottom-nav-bar.ts`: read `activePath` from the
  state instead of `router.routeTree`.
- Each route (`dashboard`, `discovery`, `my-artists`, `settings`, and any other
  route rendering `<page-header>`): remove `<page-header>` and the `header` grid
  area from its `.html`/`.css`; the dashboard additionally writes its dynamic
  title to the state.
- Route `data.titleKey` (or an equivalent lookup) supplies the per-route title
  used for the optimistic set at navigation-start.
- Storybook: `bottom-nav-bar` and `page-header` visual-state changes require
  story updates (component-change contract); add/adjust stories accordingly.
- Tests: unit tests for `IPageHeaderState` transitions, router-event → state
  wiring (via `mock-router-events`), and the simplified `bottom-nav-bar`
  highlight; an E2E assertion that title + active tab switch before the incoming
  route's content settles.
