## MODIFIED Requirements

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be visible on all pages except the Landing Page and auth callback.

#### Scenario: App shell uses CSS Grid layout with named areas
- **WHEN** the application shell renders
- **THEN** the root container SHALL use CSS Grid with `grid-template-areas: "viewport" "nav"` and `grid-template-rows: 1fr auto`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** `<au-viewport>` SHALL be a direct child of the root container (no intermediate wrapper div)
- **AND** `<au-viewport>` SHALL NOT receive any layout styling from `app-shell.css` — its block-size is determined by grid stretch (blockification of grid items)
- **AND** `<bottom-nav-bar>` SHALL occupy the `nav` area as a normal flow child
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API

#### Scenario: Navigation hidden on Landing Page and auth callback only
- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the system SHALL NOT display the bottom navigation bar
- **AND** the `1fr` row SHALL expand to fill the full `100dvh` height

#### Scenario: Navigation shown during onboarding (discover, dashboard, my-artists)
- **WHEN** the user is on the Artist Discovery, Dashboard, or My Artists route during onboarding
- **THEN** the system SHALL display the bottom navigation bar
- **AND** navigation SHALL be restricted by the existing route guards (`AuthHook.canLoad()`)
- **AND** the system SHALL NOT apply additional click prevention on the navigation bar

#### Scenario: Navigation shown on post-onboarding routes
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display the bottom navigation bar in the `nav` grid area
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
- **THEN** the route component SHALL NOT apply viewport-relative height constraints (e.g., `100dvh`, `100vh`) or bottom padding (e.g., `pb-14`) to account for the navigation bar
- **AND** the CSS Grid layout SHALL ensure the route content fills the available space within the `1fr` track

---

### Requirement: Route components own page structure
Each route component SHALL define its own HTML document structure using semantic landmark elements AND its own CSS layout using `:scope` grid declarations. The app shell SHALL NOT provide a shared page layout wrapper or style child custom elements.

#### Scenario: Route provides header and main landmarks
- **WHEN** a route component renders inside `<au-viewport>`
- **THEN** the route template SHALL contain exactly one `<main>` element as a top-level child
- **AND** the route template MAY contain one `<header>` element as a top-level sibling before `<main>`
- **AND** top-layer elements (`<dialog>`, popover components) MAY appear as top-level siblings after `<main>`

#### Scenario: Route `:scope` declares grid layout with areas
- **WHEN** a route component's CSS is loaded
- **THEN** the `:scope` rule SHALL declare `display: grid` with `grid-template-areas` naming every structural region
- **AND** the `:scope` rule SHALL declare `grid-template-rows` matching the areas
- **AND** the `:scope` rule SHALL declare `block-size: 100%` to inherit the definite height from `au-viewport`
- **AND** the `:scope` rule SHALL declare `min-block-size: 0` to allow overflow activation on descendants
- **AND** each structural child element SHALL be assigned to its grid area via `grid-area`

#### Scenario: No page-shell wrapper
- **WHEN** any route component renders
- **THEN** the route template SHALL NOT use a `<page-shell>` custom element
- **AND** the `page-shell` component SHALL NOT exist in the codebase

#### Scenario: App-shell does not style child custom elements
- **WHEN** `app-shell.css` is loaded
- **THEN** the file SHALL NOT contain selectors targeting `au-viewport`, `live-highway`, or any route component custom element
- **AND** overlay elements (`pwa-install-prompt`, `toast-notification`, `error-banner`, `coach-mark`) MAY be styled in `app-shell.css` as they are direct children requiring flow removal

---

### Requirement: Stale-data warning uses overlay pattern
The dashboard stale-data warning SHALL render as a fixed-position overlay, consistent with the application's notification pattern (`toast-notification`, `error-banner`).

#### Scenario: Stale banner appears as fixed overlay
- **WHEN** the dashboard data reload fails and previous data exists (`isStale === true`)
- **THEN** the stale-data warning SHALL render as a `position: fixed` element at the top of the viewport
- **AND** the warning SHALL NOT occupy a grid row in the dashboard layout
- **AND** the warning SHALL appear above page content but below top-layer elements (dialogs, popovers)

#### Scenario: Stale banner does not affect scroll behavior
- **WHEN** the stale-data warning is visible
- **THEN** the `live-highway` scroll area SHALL occupy the full `main` grid area
- **AND** scrolling the concert list SHALL NOT move the stale-data warning
