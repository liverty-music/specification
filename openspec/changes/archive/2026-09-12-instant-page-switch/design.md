## Context

See proposal.md — Why. Two facts about the current codebase shape the approach:

1. **The page header lives inside each route.** Every route renders its own
   `<page-header title-key="…">` in its own `header` grid area, and `<au-viewport>`
   swaps the whole route on navigation. So the header cannot appear before the
   incoming route module loads, its `canLoad` resolves, and its entrance
   transition (`app-shell-layout` → Page Transition Animations, 250–350ms fade)
   begins. All route headers are already title-only — page action controls were
   already moved to the FAB action launcher — so the header carries no
   route-specific slotted content today.

2. **The nav highlight reads router state.** `bottom-nav-bar` computes the active
   tab from `router.routeTree.root.children[0]`, which updates during navigation
   processing, not at the moment of intent.

Aurelia router facts (verified against the docs and this app):
- `au:router:navigation-start` fires at navigation intent and exposes the target
  via `event.instructions`; `navigation-end` / `navigation-error` bracket it.
- `ICurrentRoute` is authoritative but only updated at `navigation-end`.
- Routed components cannot project into an ancestor shell's `au-slot` — a shell
  header driven by route content must go through shared state, not slotting.
- The only route guard, `AuthHook.canLoad`, never redirects or rejects (it
  returns `true`, awaiting auth readiness first). So an optimistic target set at
  `navigation-start` is essentially always confirmed at `navigation-end`.

## Goals / Non-Goals

**Goals:**
- Page identity (header title + active tab) switches at navigation intent,
  decoupled from route module loading and the content entrance transition.
- One source of truth for header title and nav highlight; both become pure
  functions of that state, so both are unit-testable without a router mock.
- Preserve the dashboard's dynamic title and its title View-Transition morph.

**Non-Goals:**
- Reducing the content load latency itself (route chunk prefetching) — a
  separate, orthogonal improvement, explicitly out of scope here.
- Changing the content entrance transition. Content keeps its fade/slide; only
  the identity layer is lifted out of it.
- Relocating page action controls (already in the FAB launcher).

## Decisions

### D1: Hoist the page header into the shell (single instance) — reverses "routes own the header"
`app-shell-layout` currently mandates that routes own their page structure and
the shell provides no shared layout. We carve out the header region: the shell
grid gains a `header` row and hosts one persistent `<page-header>`; routes drop
their `<page-header>` and `header` grid area.

- **Why:** The header physically cannot precede content while it lives in the
  swapped viewport. A single shell-hosted instance is the only way to make the
  title switch independent of load/transition, and it never unmounts, so the
  title can animate in place.
- **Alternative — transient shell overlay title shown only during load
  (rejected):** keep the route header untouched, show a shell-level "instant
  title" from navigation-start until the route header mounts, then hand off. This
  keeps route templates unchanged but introduces two title sources that must stay
  in sync, an imperative handoff whose hide-timing is fragile, and pixel-exact
  position matching to avoid a flicker. Higher risk, worse testability. Since all
  route headers are already title-only, the hoist has almost no migration cost,
  so the cleaner model wins.

### D2: Drive identity from router lifecycle events, not a click handler
A `IPageHeaderState` singleton holds observable `titleKey`, `morphTitle`, and
`activePath`. The shell subscribes to the three router events (extending the
subscriptions it already holds): set optimistically on `navigation-start`,
reconcile from `ICurrentRoute` on `navigation-end`, restore the last confirmed
snapshot on `navigation-error`.

- **Why over a nav-tab click handler setting a pending path:** the router event
  is the framework-native intent signal and uniformly covers taps, in-app links,
  programmatic `load()`, and browser back/forward — a click handler covers only
  taps. It also composes with the existing event subscriptions already in the
  shell.
- **Reconcile-on-end matters** for redirects (`'' → welcome`), the not-found
  fallback, and dynamic titles: the authoritative value overrides the optimistic
  guess.

### D3: Per-route title source = route `data.titleKey`
The optimistic set at `navigation-start` needs the target's title key. Colocate
it with the route definition as `data.titleKey` in `app-shell.ts`, resolved from
the target instruction. The bottom-nav `tabs` array remains the source for
`path → icon/tab` (highlight). This keeps title and tab concerns separate and
each in one place; adding a page is a one-line edit.

- **Alternative — a standalone `path → titleKey` map (rejected):** duplicates
  knowledge already adjacent to the route definitions.

### D4: bottom-nav reads `activePath` from the state
Replace the `router.routeTree` read with `IPageHeaderState.activePath`.
`isActive(path)` becomes a pure comparison (keeping the existing sub-path rules,
e.g. `concerts/:id` highlights Home). This is what makes the highlight instant
and removes the routeTree mock from its tests.

### D5: Dashboard writes its dynamic title to the state
The My Timetable ↔ All Nearby swap sets `IPageHeaderState.setTitle(key, { morph:
true })` instead of binding a local `modeTitleKey` on a route-owned header.
Because the shell header is a single persistent element with a stable
`view-transition-name`, the existing title morph keeps working.

## Risks / Trade-offs

- **Identity leads content between navigation-start and navigation-end.** →
  Mitigated by reconcile-on-end and rollback-on-error; and by the fact that
  `AuthHook` never redirects/rejects, so the optimistic value is almost always
  correct for the tab routes. Worst case (a redirect) self-corrects at
  navigation-end within the same navigation.
- **Architectural reversal of a documented decision (routes own structure).** →
  Scoped narrowly to the header region only; routes still own `main`/`controls`
  and their grids. The spec delta states the new boundary explicitly so the
  reversal is intentional and reviewable, not implicit.
- **Two components under `src/components/` change (bottom-nav, page-header).** →
  Storybook stories are a component-change contract; story updates are in the
  task list, keeping visual/a11y baselines honest.
- **Title flash on first paint / direct deep-link load.** → The state initializes
  from the first `navigation-start`/`navigation-end`; on a cold deep-link the
  header renders once the first navigation resolves, same as any other shell
  content gated on `showNav`.

## Migration Plan

Frontend-only, no backend/proto/API coupling, so it ships as a single fan-web
change. Order: (1) add `IPageHeaderState` + register it; (2) add the shell
`header` row, render the shared `<page-header>`, wire the three router events and
`data.titleKey`; (3) repoint `bottom-nav-bar` to `activePath`; (4) remove
`<page-header>` and the `header` grid area from each route, and switch the
dashboard to write its title to the state; (5) update stories and tests.
Rollback is a straight revert (no data or schema migration).
