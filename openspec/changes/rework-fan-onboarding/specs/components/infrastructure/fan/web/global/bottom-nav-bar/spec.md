## MODIFIED Requirements

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be visible on all pages except the Landing Page and auth callback. The shell-hosted page header SHALL follow the same visibility condition as the navigation bar.

#### Scenario: App shell uses CSS Grid layout with named areas
- **WHEN** the application shell renders
- **THEN** the root container SHALL use CSS Grid with `grid-template-areas: "header" "viewport" "nav"` and `grid-template-rows: auto 1fr auto`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** the shell-hosted `<page-header>` SHALL occupy the `header` area
- **AND** `<au-viewport>` SHALL be a direct child of the root container (no intermediate wrapper div) and SHALL be explicitly assigned `grid-area: viewport`
- **AND** `<au-viewport>` SHALL receive ONLY grid-area placement from `app-shell.css` (no other layout styling) — its block-size is determined by the `viewport` row's grid stretch. The explicit placement is required so the viewport never auto-places into the `auto` `header` row when the header/nav are hidden (which would collapse the route to zero block-size)
- **AND** `<bottom-nav-bar>` SHALL be explicitly assigned `grid-area: nav`
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API

#### Scenario: Navigation hidden on Landing Page and auth callback only
- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the system SHALL NOT display the bottom navigation bar
- **AND** the system SHALL NOT display the shell-hosted page header
- **AND** the `1fr` viewport row SHALL expand to fill the full `100dvh` height

#### Scenario: Navigation shown during onboarding (discover, dashboard, my-artists)
- **WHEN** the user is on the Artist Discovery, Dashboard, or My Artists route during onboarding
- **THEN** the system SHALL display the bottom navigation bar
- **AND** navigation SHALL be restricted by the existing route guards (`AuthHook.canLoad()`)
- **AND** the system SHALL NOT apply additional click prevention on the navigation bar

#### Scenario: Navigation shown on post-onboarding routes
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display the bottom navigation bar in the `nav` grid area
- **AND** the navigation bar SHALL include tab icons and labels for Home, Discover, My Artists and Tickets, in that order, two on each side of an empty centre slot reserved for the FAB
- **AND** the navigation bar SHALL NOT include a Settings tab

#### Scenario: Navigation remains visible beneath area setup dialog
- **WHEN** the first-visit area setup dialog is displayed on the Dashboard
- **THEN** the area setup dialog SHALL render in the browser's Top Layer (a `<dialog>` shown with `showPopover()`, the bottom-sheet convention)
- **AND** the bottom navigation bar SHALL remain in its normal grid position beneath the Top Layer
- **AND** the `::backdrop` pseudo-element SHALL visually dim the entire page including the navigation bar

#### Scenario: Dashboard icon data attribute for coach mark targeting
- **WHEN** the bottom navigation bar renders
- **THEN** the Dashboard (Home) tab link SHALL carry `data-nav="home"`, which identifies the tab for tests and analytics (no coach mark targets the navigation bar)
- **AND** the My Artists tab link SHALL carry `data-nav="my-artists"`

#### Scenario: Pages do not compensate for navigation bar height
- **WHEN** any route component renders inside the `<au-viewport>` element
- **THEN** the route component SHALL NOT apply viewport-relative height constraints (e.g., `100dvh`, `100vh`) or bottom padding (e.g., `pb-14`) to account for the navigation bar
- **AND** the CSS Grid layout SHALL ensure the route content fills the available space within the `1fr` track
