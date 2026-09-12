## ADDED Requirements

### Requirement: Page header is a single shell-hosted instance bound to shared state
The `page-header` CE SHALL be rendered as a single persistent instance owned by the app shell (not one instance per route), and its `title-key` and `morph-title` bindables SHALL be bound to the shared page-identity state rather than authored per route. As the shared state changes, the header SHALL update in place without being unmounted and remounted across route changes.

#### Scenario: Single shell-hosted instance across route changes
- **WHEN** the user navigates between routes that show the navigation bar
- **THEN** the same `page-header` instance SHALL remain mounted in the shell
- **AND** its `<h1>` text SHALL update from the shared state's current title key without the element being destroyed and recreated

#### Scenario: Title bound to shared state, not per-route markup
- **WHEN** a route becomes active
- **THEN** the header title SHALL be sourced from the shared page-identity state
- **AND** no route template SHALL author its own `<page-header>` element to supply the title

#### Scenario: Title morph preserved for in-place title swaps
- **WHEN** the shared state's title changes while the header stays mounted and `morph-title` is enabled (e.g. the dashboard My Timetable ↔ All Nearby swap)
- **THEN** the `<h1>` SHALL carry the stable `view-transition-name` so the title text can morph across a same-document View Transition

## MODIFIED Requirements

### Requirement: Page header participates in route grid layout
The `page-header` CE host element SHALL set `grid-area: header` so it integrates with the app shell's `grid-template-areas` without additional route-level CSS.

#### Scenario: Header placed in grid area
- **WHEN** the app shell defines `grid-template-areas: "header" "viewport" "nav"`
- **THEN** the `page-header` CE SHALL occupy the `header` grid area of the shell automatically
- **AND** no route-level CSS SHALL be required to position the header

## REMOVED Requirements

### Requirement: All routes using page-header SHALL define grid-template-areas
**Reason**: The page header is no longer rendered inside route templates; it is a single shell-hosted instance positioned by the app shell grid. Routes no longer reference `<page-header>` and therefore no longer need a `header` grid area.

**Migration**: Remove `<page-header>` from every route template and remove the `"header"` area (and its `auto` row) from each route's `grid-template-areas` / `grid-template-rows`. The shell grid supplies the `header` area for the shared header instance. Per-route titles are supplied to the shared page-identity state (e.g. via route `data.titleKey`), and dynamic titles are written to that state by the active route.
