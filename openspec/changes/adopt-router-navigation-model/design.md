## Context

See proposal.md — Why. The relevant current code, in `frontend/`:

- `src/services/page-header-state.ts` — `IPageHeaderState` singleton:
  observable `titleKey` / `morphTitle` / `activePath`, with `setOptimistic`,
  `confirm`, `rollback` and `setTitle`.
- `src/app-shell.ts` — subscribes to `navigation-start` (optimistic write via
  `resolvePageIdentity`, which re-implements route matching with
  `normalizePath` / `pathMatches` over the route table), `navigation-error`
  (rollback) and `navigation-end` (confirm + `showNav` from `data.nav`).
- `src/components/bottom-nav-bar/` — its own hard-coded `tabs` array and an
  `isActive(path, activePath)` that special-cases `concerts/*` for Home.
- `src/routes/dashboard/dashboard-route.ts` — `setTitle(modeTitleKey, { morph })`
  inside a View Transition for the My Timetable ↔ All Nearby swap.

Router facts this design relies on, verified in `@aurelia/router` 2.0.0-rc.2:

- `RouterOptions.useNavigationModel` defaults to `true`.
- `IRouteContext.navigationModel.routes` lists every child route configured
  with `nav: true` (and no `redirectTo`), each as a `NavigationRoute` exposing
  `id`, `path` (array), `title`, `data` and `isActive`.
- `NavigationRoute.isActive` is recomputed on `au:router:navigation-end` as
  "does the current route tree contain any of this route's paths".
- `ICurrentRoute` is updated on `au:router:navigation-end`; its
  `parameterInformation[i].config` is the matched `RouteConfig`, so
  `config.data` is reachable.

## Goals / Non-Goals

**Goals:**

- One source of page identity: the route configuration, read through the
  router's own state.
- Delete the custom state, its three event subscriptions and the duplicated
  path matcher.

**Non-Goals:**

- Painting the shell ahead of an expensive route render. That is a render-cost
  problem, owned by `reduce-timetable-render-cost`.
- Changing which tabs exist, their order, icons or labels.
- Using the `load` custom attribute's `active` in place of the navigation
  model. The bar is a list of routes; the navigation model is that list.

## Decisions

### D1. Tabs are route configuration; the bar renders the navigation model

Each tab route gets `nav: true`, and its icon and i18n label key move into the
route's `data` (`data.icon`, `data.labelKey`) next to the existing
`data.titleKey`. The bar resolves `IRouteContext` and repeats over
`navigationModel.routes`, binding `data-active` to `route.isActive` and the
link to the route's first path. Tab order is the order of the route table.

- *Alternative — keep the `tabs` array, only replace the active computation
  with `router.isActive(...)`*: keeps two lists that must agree, which is how
  the current bar and route table already drifted into a hand-written
  `concerts/*` rule. Rejected.
- *Alternative — `load` attribute with `active.bind` per hard-coded link*:
  standard too, but still hard-codes the tab list in the template. Rejected for
  the same reason.

### D2. `concerts/:id` is a second path of the dashboard route

The dashboard and `concerts/:id` already point at the same component and share
identity. They become one route: `path: ['dashboard', 'concerts/:id']`. The
navigation model then treats both as the Home tab, with no special case in the
bar. The route's `id` is set explicitly so the navigation model and any
`load` target have a stable name.

- *Alternative — keep two routes, mark only `dashboard` as `nav`*: Home would
  not be active on a deep-link, which the spec requires. A bar-side rule would
  reintroduce the special case this change removes. Rejected.

**Spike S1 (gates D2)**: `NavigationRoute` builds one instruction per path and
checks `routeTree.contains(instruction, true)`. Whether an instruction built
from the parameterised pattern `concerts/:id` is "contained" by a tree whose
node matched `concerts/abc` is not determinable from the source alone. Verify
in a unit test against the real router. If it does not hold, fall back to:
the dashboard route stays `nav: true` with path `dashboard` only, and
`concerts/:id` becomes a child route of it, which `contains` with
`includeChildren = true` covers by construction.

### D3. Header title comes from the current route's configuration

The shell binds the header to `ICurrentRoute`: the title key is
`parameterInformation[0]?.config?.data?.titleKey`, exposed as one getter on
`AppShell` so the template does not carry the path. `data.titleKey` remains an
i18n key; the route's `title` stays the document title and is not reused,
because the two differ (document title is English and product-suffixed).

**Spike S2 (gates D1 and D3)**: `<bottom-nav-bar>` and `<page-header>` sit
outside `<au-viewport>`, as children of the shell. Confirm that resolving
`IRouteContext` there yields the root context (whose navigation model holds the
top-level routes) and that `ICurrentRoute`'s fields are observed by bindings
(they are reassigned on navigation-end). If the context does not resolve, the
shell resolves it and passes `navigationModel` to the bar as a bindable.

### D4. Identity changes on navigation-end only

No `navigation-start` or `navigation-error` subscription remains for identity.
Rollback is unnecessary because nothing is written before the navigation
succeeds. `showNav` stays derived on `navigation-end` (it gates the whole
chrome, not identity).

### D5. Dashboard title is fixed; the morph goes

`setTitle` and `modeTitleKey` are removed from the dashboard. The mode toggle
already indicates the selection. `page-header` loses its `morph-title`
bindable and the `view-transition-name` it set; the dashboard's mode switch
keeps its own content View Transition, which does not depend on the header.
The now-unused i18n keys for the mode titles are removed from both bundles.

### D6. Rename the chrome-hiding flag

`data.nav: false` becomes `data.chrome: false` (read by `showNav`). The router's
top-level `nav` property now means "appears in the navigation model"; keeping a
`data.nav` with a different meaning next to it invites the wrong one being set.

## Risks / Trade-offs

- [Identity now appears one step later than the optimistic write in the case
  where the incoming route's module is still loading — the first visit to a
  lazily-imported tab] → Accepted. On re-entry the module is cached, and in
  every case the optimistic write was not painted before the route rendered
  anyway. The tab's own pressed state (`:active`) still acknowledges the tap
  immediately.
- [S1 fails and `concerts/:id` becomes a child route] → Changes the dashboard's
  route shape; the deep-link spec scenarios in `route/dashboard` are the
  regression guard and must pass unchanged.
- [Title morph removal is visible] → Agreed product decision (proposal); the
  toggle carries the mode.
- [Coach-mark targets and E2E selectors key off each tab's `data-nav`
  attribute (today bound to the tab's icon)] → The repeated tab link keeps
  emitting `data-nav` with the same values, now from `data.icon`, so existing
  selectors are unaffected.

## Migration Plan

Single frontend release. Rollback is a revert; there is no persisted state.
