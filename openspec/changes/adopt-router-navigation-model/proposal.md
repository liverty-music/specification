## Why

The shell header title and the active bottom-nav tab are driven by a hand-rolled
page-identity state (`IPageHeaderState`): an optimistic write on
`navigation-start`, a reconcile on `navigation-end`, a rollback on
`navigation-error`, and a route-table path matcher duplicated from the router.
It was introduced (`instant-page-switch`) to make the header and nav switch
"at navigation intent", but it never achieved that: writing state earlier does
not paint earlier, because the incoming route renders in the same task and the
browser paints once, after it. The machinery costs code and a second source of
routing truth without delivering its purpose.

Aurelia's router already provides page identity as framework state — the
navigation model (the tab routes, each with its `isActive`) and the current
route (its `RouteConfig`, including `data`). Binding the shell to that is the
framework's documented pattern and removes the custom state entirely.

## What Changes

- The bottom-nav tabs are declared once, in the route configuration
  (`nav: true`, with icon and label in the route's data), and the bar renders
  them from the router's navigation model. The active tab is the router's
  `isActive`, not a path comparison written in the component.
- The shell header title comes from the current route's configuration.
- **BREAKING (behavior)**: page identity is updated when navigation completes,
  not optimistically when it starts. There is no optimistic write, reconcile or
  rollback: a failed navigation leaves the displayed route, and therefore its
  identity, unchanged by construction. In practice nothing visible is lost —
  the optimistic write never reached the screen ahead of the incoming route.
- **BREAKING (behavior)**: the dashboard's header title is fixed to the route's
  title in both modes. The My Timetable ↔ All Nearby title swap and its title
  morph are removed; the active mode is shown by the mode toggle itself.
- `concerts/:id` keeps highlighting the Home tab.
- The shell's own route flag for hiding the chrome (`data.nav: false`) is
  renamed, because it collides in name with the router's `nav` property that
  now carries meaning.
- Removed: the page-identity state service, its navigation-start / error
  subscriptions, the duplicated path matcher, and the bottom nav's own tab
  list and active-tab logic.

Out of scope: the render cost of the dashboard timetable that holds the first
paint on tab switch. That is `reduce-timetable-render-cost`.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `components/infrastructure/fan/web/global/page-header`: page identity follows
  the displayed route instead of an optimistically-updated shared state; the
  in-place dynamic title and title morph are removed.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: the active tab
  reflects the displayed route, including sub-paths that belong to a tab
  (`concerts/:id` → Home).
- `components/infrastructure/fan/web/route/dashboard`: the header title stays
  the dashboard's title in both modes; the mode is conveyed by the toggle.

## Impact

- **Frontend only.** `app-shell.ts` / `.html` (route table gains `nav: true`
  and tab data; header binds to the current route; subscriptions removed),
  `bottom-nav-bar` (renders the navigation model), `page-header`
  (morph bindable removed), `dashboard-route.ts` (title writes removed),
  `services/page-header-state.ts` deleted with its spec.
- **Tests**: `e2e/functional/instant-page-switch.spec.ts` asserts the removed
  optimistic behavior and is rewritten to assert that identity matches the
  displayed route (including after a failed navigation and on `concerts/:id`).
  Unit tests for the page-identity state are deleted; shell and bottom-nav
  tests move to the router-backed source.
- **Two unknowns to settle by spike before building** (design.md): whether the
  navigation model's `isActive` covers `concerts/:id` when both paths are one
  route, and whether the bottom nav — which sits outside `<au-viewport>` —
  resolves the root route context's navigation model.
