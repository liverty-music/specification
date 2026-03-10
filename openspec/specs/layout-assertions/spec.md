### Requirement: Shell layout structural integrity
The layout assertion suite SHALL verify that the app shell Grid layout correctly distributes space between the route viewport and bottom navigation bar at mobile viewport (390×844).

#### Scenario: Shell fills viewport height
- **WHEN** any public route is loaded at 390×844 viewport
- **THEN** the `my-app` element height SHALL equal the viewport height (844px)

#### Scenario: Route viewport stretches to fill available space
- **WHEN** a route with bottom nav is loaded (e.g., `/discover`)
- **THEN** `au-viewport` height + `bottom-nav-bar` height SHALL equal the `my-app` height

#### Scenario: Bottom nav anchored to viewport bottom
- **WHEN** a route with bottom nav is loaded
- **THEN** the bottom edge of `bottom-nav-bar` SHALL equal the viewport height (844px)

#### Scenario: Full-height route without bottom nav
- **WHEN** a fullscreen route without bottom nav is loaded (e.g., `/welcome`)
- **THEN** `au-viewport` height SHALL equal the `my-app` height (no nav row)

### Requirement: Discover page layout containment
The layout assertion suite SHALL verify that the discover page's grid layout correctly sizes the bubble area and Canvas element within the viewport bounds.

#### Scenario: Discover layout fills viewport
- **WHEN** the discover page is loaded at 390×844 viewport
- **THEN** `.discover-layout` width SHALL equal the viewport width (390px)
- **AND** `.discover-layout` height SHALL equal the `au-viewport` height

#### Scenario: Bubble area fills remaining space
- **WHEN** the discover page is in bubble mode (not searching)
- **THEN** `.bubble-area` width SHALL equal `.discover-layout` width
- **AND** `.bubble-area` bottom edge SHALL NOT exceed the bottom-nav top edge

#### Scenario: Canvas fills bubble area
- **WHEN** the dna-orb canvas has initialized
- **THEN** the canvas element width SHALL equal `.bubble-area` width (tolerance: 1px)
- **AND** the canvas element height SHALL equal `.bubble-area` height (tolerance: 1px)

#### Scenario: Search bar stays within viewport
- **WHEN** the discover page is loaded
- **THEN** `.search-bar` right edge SHALL NOT exceed the viewport width

#### Scenario: Search results scrollable in search mode
- **WHEN** the user enters search text and results are displayed
- **THEN** `.search-results` SHALL have `overflow-y` computed value of `auto`
- **AND** `.search-results` height SHALL be less than or equal to the viewport height

### Requirement: Layout test execution performance
The layout assertion suite SHALL execute within a time budget suitable for local development feedback loops.

#### Scenario: Full suite completes within budget
- **WHEN** all layout assertion tests are run
- **THEN** total execution time SHALL be under 5 seconds (excluding browser launch)

### Requirement: Layout tests independent of backend
The layout assertion suite SHALL not depend on a running backend service.

#### Scenario: Tests pass without backend
- **WHEN** layout tests are run with no backend available
- **THEN** all tests SHALL pass using mocked RPC responses via `page.route()`
