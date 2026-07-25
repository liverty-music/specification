# shell-layout Specification

## Purpose

Defines the PWA shell layout structure for `app-shell`, ensuring overlay custom elements are excluded from CSS Grid flow so that `bottom-nav-bar` stays pinned at the viewport bottom and `position: sticky` headers work correctly within scroll containers.
## Requirements
### Requirement: Overlay elements excluded from grid flow
All overlay custom elements (`pwa-install-prompt`, `notification-prompt`, `toast-notification`, `error-banner`, `coach-mark`) SHALL be removed from normal document flow so they do not create implicit CSS Grid rows in the `app-shell` shell layout. The bottom navigation bar and page header SHALL stay pinned even under a standalone PWA pull-to-refresh / overscroll gesture, because the document root is a non-scrolling frame and scrolling is confined to the single inner container.

#### Scenario: Bottom nav stays at viewport bottom
- **WHEN** the dashboard page has enough events to require scrolling (20+ concerts across multiple dates)
- **THEN** `bottom-nav-bar` SHALL remain visible and pinned at the bottom of the viewport at all times
- **AND** the `dashboard-route` CE SHALL constrain all descendants to viewport height via a 2-layer height chain: `dashboard-route` (grid, `block-size: 100%`) → `<main>` (scroll container, `overflow-block: auto`)
- **AND** no intermediate element between `au-viewport` and the scroll container SHALL have a rendered height exceeding the `au-viewport` height

#### Scenario: Bottom nav and header stay pinned after a pull-to-refresh gesture
- **WHEN** the app is running as an installed standalone PWA on the dashboard
- **AND** the user performs a pull-to-refresh / downward overscroll gesture
- **THEN** the bottom navigation bar SHALL remain visible and pinned at the bottom of the viewport
- **AND** the page header (the "Timetable" title row) SHALL remain visible and pinned at the top of the viewport
- **AND** the document root SHALL NOT scroll to make the header and the bottom nav bar mutually exclusive on screen

#### Scenario: Stage header stays fixed above scrollable content
- **WHEN** the user scrolls the concert list downward
- **THEN** the stage header (HOME STAGE / NEAR STAGE / AWAY STAGE) SHALL remain fixed above the scrollable content
- **AND** the stage header SHALL be a `<header>` element that is a direct child of `dashboard-route`, outside the `<main>` scroll container
- **AND** `dashboard-route` SHALL use CSS Grid with named areas via the `grid-template` shorthand: `"stage-home stage-near stage-away" auto` / `"lane-home lane-near lane-away" minmax(0, 1fr)` / `1fr 1fr 1fr`
- **AND** the stage header SHALL use `grid-template-columns: subgrid` with `grid-column: stage-home / stage-away` (named area implicit lines)
- **AND** the scroll container and all intermediate elements (`.concert-scroll`, `.date-group-list`, `li`, `.lane-grid`) SHALL use `grid-template-columns: subgrid` to propagate the 3-column layout from the root grid

#### Scenario: Scroll container is properly constrained
- **WHEN** concert data overflows the viewport
- **THEN** the `<main .concert-scroll>` element's `scrollHeight` SHALL be greater than its `clientHeight`
- **AND** the scroll container SHALL be the only scrollable element in the height chain
- **AND** the scroll container SHALL declare `overscroll-behavior: contain` so a scroll-boundary bounce does not chain into the document root

#### Scenario: Overlay elements remain functional
- **WHEN** an overlay element activates (e.g., toast notification, coach-mark spotlight)
- **THEN** the overlay SHALL render correctly via the browser top-layer API, unaffected by the flow removal

### Requirement: Dashboard uses semantic HTML structure
The dashboard route SHALL use semantic HTML elements instead of generic `<div>` elements for its concert timeline layout.

#### Scenario: Date groups rendered as ordered list
- **WHEN** the dashboard displays concert date groups
- **THEN** date groups SHALL be rendered as `<ol>` with `<li>` elements
- **AND** date labels SHALL use `<time>` elements

#### Scenario: Stage lanes rendered as list items
- **WHEN** a date group renders its 3-lane concert grid
- **THEN** the lane grid SHALL be an `<ol>` element with 3 `<li>` children (home, near, away)

#### Scenario: Empty lanes display placeholder via CSS
- **WHEN** a lane contains no concert events
- **THEN** the lane SHALL display a dash placeholder using CSS `:empty` pseudo-element (or `[data-empty]` attribute fallback)
- **AND** no conditional template markup SHALL be used for the empty state

### Requirement: live-highway component eliminated
The `live-highway` custom element SHALL be removed and its responsibilities inlined into `dashboard-route`.

#### Scenario: Event selection handled by dashboard
- **WHEN** a user taps an event card in the concert list
- **THEN** `dashboard-route` SHALL handle the `event-selected` custom event and open the `event-detail-sheet` dialog
- **AND** there SHALL be no `live-highway` custom element in the DOM tree

#### Scenario: Loading and empty states managed by promise.bind
- **WHEN** concert data is loading or empty
- **THEN** the dashboard's `promise.bind` directive SHALL manage pending/then/catch states directly
- **AND** there SHALL be no duplicate loading/empty state management

### Requirement: Document root is a non-scrolling frame
The document root (`html` and `body`) SHALL be a non-scrolling frame so that it is never a scroll source and native overscroll gestures (pull-to-refresh) in a standalone PWA cannot shift the shell chrome. All scrolling SHALL be confined to inner scroll containers.

#### Scenario: Root elements do not scroll
- **WHEN** the application is loaded in any route
- **THEN** `html` and `body` SHALL declare a definite height (`block-size: 100%`)
- **AND** `html` and `body` SHALL declare `overflow: hidden`
- **AND** `body` SHALL NOT declare `min-block-size: 100dvh` (or any rule that makes `body` taller than the visible viewport and thus a scroll source)
- **AND** the `app-shell` grid SHALL remain the single height owner at `block-size: 100dvh`

#### Scenario: Overscroll gesture does not chain to the document
- **WHEN** the user performs a pull-to-refresh or overscroll gesture in the installed standalone PWA
- **THEN** `html` and `body` SHALL declare `overscroll-behavior: none`
- **AND** the document SHALL NOT scroll, bounce, or trigger a native pull-to-refresh reload
- **AND** the bottom navigation bar and the page header SHALL both remain visible and pinned in their positions

#### Scenario: Inner scroll container contains its overscroll
- **WHEN** the user scrolls the concert list to its top or bottom boundary
- **THEN** the concert scroll container SHALL declare `overscroll-behavior: contain`
- **AND** the scroll SHALL NOT chain into the document root

