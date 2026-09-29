## ADDED Requirements

### Requirement: Page identity follows the displayed route

The page header title and the active bottom-nav tab SHALL always describe the
route that is displayed. Both SHALL be taken from that route's own
configuration, so there is one source of page identity for the whole app and
no second copy of it to keep in step. They SHALL change when a navigation
completes. A navigation that fails or is cancelled leaves the previous route
displayed, and its identity SHALL remain on screen unchanged.

#### Scenario: Header title and active tab match the route shown

- **WHEN** the fan taps a bottom-nav tab and the target route is displayed
- **THEN** the page header SHALL show that route's title
- **AND** the bottom-nav highlight SHALL be on that route's tab

#### Scenario: A failed navigation leaves identity unchanged

- **WHEN** a navigation fails or is cancelled and the previous route remains
  displayed
- **THEN** the page header title and the active tab SHALL still be those of the
  previous route
- **AND** at no point SHALL they have shown the failed target

#### Scenario: Redirects and the fallback route are reflected

- **WHEN** a navigation resolves to a different route than the one requested
  (a redirect, or the not-found fallback)
- **THEN** the page header title and the active tab SHALL be those of the route
  actually displayed

#### Scenario: Routes without a title show no header

- **WHEN** the displayed route declares no page title (legal documents, About,
  not-found)
- **THEN** no page header SHALL be rendered

### Requirement: Page header is a single shell-hosted instance bound to the displayed route
The `page-header` CE SHALL be rendered as a single persistent instance owned by the app shell (not one instance per route), and its title SHALL be bound to the displayed route's configured title rather than authored per route. As the displayed route changes, the header SHALL update in place without being unmounted and remounted across route changes.

#### Scenario: Single shell-hosted instance across route changes
- **WHEN** the user navigates between routes that show the navigation bar
- **THEN** the same `page-header` instance SHALL remain mounted in the shell
- **AND** its `<h1>` text SHALL update to the displayed route's title without the element being destroyed and recreated

#### Scenario: Title bound to the displayed route, not per-route markup
- **WHEN** a route becomes active
- **THEN** the header title SHALL be sourced from that route's configuration
- **AND** no route template SHALL author its own `<page-header>` element to supply the title
- **AND** no route SHALL change the header title while it is displayed

## REMOVED Requirements

### Requirement: Instant page-identity switch on navigation intent
**Reason**: Writing page identity optimistically on navigation start did not make it paint earlier — the incoming route renders in the same task and the browser paints once, after it — so the optimistic state, its reconcile and its rollback added a second source of routing truth without delivering the intent. Identity now follows the displayed route, taken from the router.
**Migration**: Covered by "Page identity follows the displayed route". Painting the shell ahead of an expensive route render is addressed by bounding that render (`reduce-timetable-render-cost`), not by the timing of the identity write. The dashboard's in-place title swap is removed; see the dashboard's "Dashboard Mode Toggle".

### Requirement: Page header is a single shell-hosted instance bound to shared state
**Reason**: The shared page-identity state it binds to is removed, together with the in-place title swap and its title morph.
**Migration**: Replaced by "Page header is a single shell-hosted instance bound to the displayed route", which keeps the single shell-hosted instance and binds its title to the displayed route's configuration.
