## Why

The bottom-nav-bar and page headers scroll with content instead of staying fixed. Despite existing specs (`app-shell-layout`, `shell-layout`) defining height containment via `au-viewport { display: grid }`, the actual height-constraint chain breaks at route component CE boundaries — `<dashboard>`, `<my-artists-page>`, etc. lack `:scope` layout definitions, so `overflow` never activates and the entire page scrolls.

The root cause is a design flaw: `app-shell.css` externally styles child custom elements (`au-viewport`, `live-highway`), violating CUBE CSS methodology. When an intermediate CE (the route component) has no explicit `display` or `block-size`, the height chain breaks regardless of what the parent or grandchild declares.

## What Changes

- **Remove external CE styling from app-shell**: Delete `au-viewport` and `live-highway` layout rules from `app-shell.css`. Each component owns its own display and sizing.
- **Require `:scope` grid layout on every route component**: Each route page declares its own structure using `display: grid` + `grid-template-areas` + `block-size: 100%` + `min-block-size: 0`. This makes the height chain explicit at every CE boundary.
- **Move `live-highway` display to its own CSS**: `live-highway.css` `:scope` declares its own display instead of inheriting from app-shell.
- **Convert dashboard stale-banner to fixed overlay**: The stale-data warning is a transient notification, not a structural page region. Move it to `position: fixed` overlay, consistent with `toast-notification` and `error-banner`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `app-shell-layout`: Remove requirement for app-shell to style `au-viewport` with CSS Grid. App-shell only styles itself. Route components own their own height chain. Update `grid-template-rows` to use `grid-template-areas`.
- `shell-layout`: Remove requirement for `live-highway` to receive `block-size: 100%` from app-shell. `live-highway` owns its own `:scope` display.

## Impact

- **Frontend CSS**: `app-shell.css`, `dashboard.css`, `my-artists-page.css`, `tickets-page.css`, `settings-page.css`, `discover-page.css`, `live-highway.css`
- **Frontend HTML**: `dashboard.html` (stale-banner becomes fixed overlay)
- **Specs**: `app-shell-layout/spec.md`, `shell-layout/spec.md` (height chain requirements updated)
- **No backend, proto, or cloud-provisioning changes**
