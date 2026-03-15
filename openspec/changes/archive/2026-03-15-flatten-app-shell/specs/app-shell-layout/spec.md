## MODIFIED Requirements

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be visible on all pages except the Landing Page and auth callback.

#### Scenario: App shell uses CSS Grid layout with height containment
- **WHEN** the application shell renders
- **THEN** the root container SHALL use CSS Grid with `grid-template-rows: minmax(0, 1fr) min-content`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** `<au-viewport>` SHALL be a direct child of the root container (no intermediate wrapper div)
- **AND** `<au-viewport>` SHALL use CSS Grid (`grid-template-rows: minmax(0, 1fr)`) to provide a definite, constrained height to route components
- **AND** `<bottom-nav-bar>` SHALL occupy the `min-content` row as a normal flow child
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API

#### Scenario: Navigation hidden on Landing Page and auth callback only
- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the system SHALL NOT display the bottom navigation bar
- **AND** the `minmax(0, 1fr)` row SHALL expand to fill the full `100dvh` height

#### Scenario: Navigation shown during onboarding (discover, dashboard, my-artists)
- **WHEN** the user is on the Artist Discovery, Dashboard, or My Artists route during onboarding
- **THEN** the system SHALL display the bottom navigation bar
- **AND** navigation SHALL be restricted by the existing route guards (`AuthHook.canLoad()`)
- **AND** the system SHALL NOT apply additional click prevention on the navigation bar

#### Scenario: Navigation shown on post-onboarding routes
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display the bottom navigation bar in the `min-content` grid row
- **AND** the navigation bar SHALL include tab icons and labels for Home, Discover, My Artists, Tickets, and Settings

#### Scenario: Navigation remains visible beneath area setup dialog
- **WHEN** the first-visit area setup dialog is displayed on the Dashboard
- **THEN** the area setup dialog SHALL render via `<dialog>` `showModal()` in the browser's Top Layer
- **AND** the bottom navigation bar SHALL remain in its normal grid position beneath the Top Layer
- **AND** the `::backdrop` pseudo-element SHALL visually dim the entire page including the navigation bar

#### Scenario: Dashboard icon data attribute for coach mark targeting
- **WHEN** the bottom navigation bar renders
- **THEN** the Dashboard tab link SHALL include a `data-nav-dashboard` attribute
- **AND** the My Artists tab link SHALL include a `data-nav-my-artists` attribute

#### Scenario: Pages do not compensate for navigation bar height
- **WHEN** any route component renders inside the `<au-viewport>` element
- **THEN** the route component SHALL NOT apply viewport-relative height constraints (e.g., `100dvh`, `100vh`) or bottom padding to account for the navigation bar
- **AND** the CSS Grid layout SHALL ensure the route content fills the available space within the `minmax(0, 1fr)` track

## ADDED Requirements

### Requirement: Route components own page structure
Each route component SHALL define its own HTML document structure using semantic landmark elements. The app shell SHALL NOT provide a shared page layout wrapper.

#### Scenario: Route provides header and main landmarks
- **WHEN** a route component renders inside `<au-viewport>`
- **THEN** the route template SHALL contain exactly one `<main>` element as a top-level child
- **AND** the route template MAY contain one `<header>` element as a top-level sibling before `<main>`
- **AND** top-layer elements (`<dialog>`, popover components) MAY appear as top-level siblings after `<main>`

#### Scenario: Route main element fills available space
- **WHEN** the route's `<main>` element renders inside the Grid area
- **THEN** `<main>` SHALL receive its height from Grid stretch (no `block-size: 100%` needed)
- **AND** `<main>` SHALL use `overflow-y: auto` when its content may exceed the available height

#### Scenario: No page-shell wrapper
- **WHEN** any route component renders
- **THEN** the route template SHALL NOT use a `<page-shell>` custom element
- **AND** the `page-shell` component SHALL NOT exist in the codebase

### Requirement: Semantic HTML structure
Route components SHALL use semantic HTML elements per web.dev accessibility structure and MDN document structuring guidelines.

#### Scenario: Lists use list elements
- **WHEN** a route displays a collection of items (artists, tickets, search results)
- **THEN** the collection SHALL be wrapped in `<ul role="list">`
- **AND** each item SHALL be wrapped in `<li>`

#### Scenario: Page headers use header element
- **WHEN** a route has a page title with optional actions
- **THEN** the title and actions SHALL be in a `<header>` element at the route's top level
- **AND** the title SHALL use an `<h1>` element

#### Scenario: Search UI uses search element
- **WHEN** a route contains a search input
- **THEN** the search input and associated controls SHALL be wrapped in a `<search>` element

#### Scenario: Supplementary banners use aside element
- **WHEN** a route displays a non-critical informational banner (e.g., stale data warning)
- **THEN** the banner SHALL use an `<aside>` element

#### Scenario: Loading states use ARIA busy
- **WHEN** a route displays a loading indicator
- **THEN** the loading container SHALL include `aria-busy="true"` and `role="status"`

## REMOVED Requirements

### Requirement: App shell uses CSS Grid layout with height propagation
**Reason**: Replaced by the updated "Conditional Navigation Display" requirement. The previous spec required a `<main>` element at the app-shell level wrapping prompts and `<au-viewport>`. The new design removes the app-shell-level `<main>` — routes provide their own `<main>` landmark. The `<au-viewport>` is now a direct child of the root Grid container.
**Migration**: Remove `<main>` from app-shell template. Remove `.app-viewport` wrapper div. Routes provide `<main>` in their own templates.
