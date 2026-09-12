## ADDED Requirements

### Requirement: Instant page-identity switch on navigation intent

The system SHALL switch page identity — the page header title and the active
bottom-nav tab — at navigation intent, independent of the incoming route's
loading and entrance transition. Page identity SHALL be driven by a single
shared reactive state that both the shell-hosted page header and the bottom
navigation bar read from, and SHALL NOT be derived by reading the router's route
tree directly in the navigation bar.

The shared state SHALL be updated optimistically when navigation begins,
confirmed when navigation completes, and rolled back if navigation fails, so the
tap is acknowledged immediately while content continues to load or animate.

#### Scenario: Header title and active tab switch on tap before content loads
- **WHEN** the user taps a bottom-nav tab
- **THEN** the bottom-nav highlight SHALL move to the tapped tab immediately, before the incoming route's content has attached or finished its entrance transition
- **AND** the page header title SHALL change to the target page's title in the same immediate step
- **AND** the previous page's content MAY still be visible or animating out during this step

#### Scenario: Optimistic switch on navigation start
- **WHEN** an `au:router:navigation-start` event fires (from a tap, an in-app link, a programmatic load, or browser back/forward)
- **THEN** the shared page-identity state SHALL be set from the target route so the header title and active tab reflect the destination immediately

#### Scenario: Confirmation on navigation end
- **WHEN** an `au:router:navigation-end` event fires
- **THEN** the shared page-identity state SHALL be reconciled to the resolved current route
- **AND** the reconciled value SHALL take precedence over the optimistic value so redirects, fallback routes, and dynamic titles are reflected correctly

#### Scenario: Rollback on navigation error
- **WHEN** an `au:router:navigation-error` event fires
- **THEN** the shared page-identity state SHALL be restored to the last confirmed page identity
- **AND** the header title and active tab SHALL match the route that remains displayed

#### Scenario: Header and nav are not gated by the content transition
- **WHEN** the incoming route content performs its entrance transition (fade/slide)
- **THEN** the page header and the bottom navigation bar SHALL NOT be subject to that transition
- **AND** the header title and active tab SHALL already reflect the target page while the content transition is still in progress

#### Scenario: Dynamic route titles update the shared state
- **WHEN** a route changes its own title while it is the active route (e.g. the dashboard My Timetable ↔ All Nearby swap)
- **THEN** the route SHALL update the shared page-identity state
- **AND** the shell-hosted page header SHALL reflect the new title, preserving any opted-in title View-Transition morph

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
Each route component SHALL define its own HTML document structure using semantic landmark elements AND its own CSS layout using `:scope` grid declarations. The app shell SHALL own exactly one shared page header for the current route's title; apart from that header, the app shell SHALL NOT provide a shared page layout wrapper or style route child custom elements.

#### Scenario: Route provides header and main landmarks
- **WHEN** a route component renders inside `<au-viewport>`
- **THEN** the route template SHALL contain exactly one `<main>` element as a top-level child
- **AND** the route template SHALL NOT render a `<page-header>` custom element or a top-level `<header>` for the page title — the page title header is owned by the app shell
- **AND** top-layer elements (`<dialog>`, popover components) MAY appear as top-level siblings after `<main>`

#### Scenario: Route `:scope` declares grid layout with areas
- **WHEN** a route component's CSS is loaded
- **THEN** the `:scope` rule SHALL declare `display: grid` with `grid-template-areas` naming every structural region it owns (e.g. `content`, `controls`)
- **AND** the `:scope` rule SHALL NOT declare a `header` grid area — the header is positioned by the shell grid, not the route grid
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
- **THEN** the file MAY assign `grid-area` to `<au-viewport>` to place it in the shell grid, but SHALL NOT otherwise style `<au-viewport>` and SHALL NOT contain selectors targeting `live-highway` or any route component custom element
- **AND** the shell's own direct children — the shared `<page-header>`, `<bottom-nav-bar>`, and overlay elements (`pwa-install-prompt`, `toast-notification`, `error-banner`, `coach-mark`) — MAY be styled in `app-shell.css`
