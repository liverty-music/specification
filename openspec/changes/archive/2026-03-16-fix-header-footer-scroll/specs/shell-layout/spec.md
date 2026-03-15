## MODIFIED Requirements

### Requirement: Overlay elements excluded from grid flow
All overlay custom elements (`pwa-install-prompt`, `notification-prompt`, `toast-notification`, `error-banner`, `coach-mark`) SHALL be removed from normal document flow so they do not create implicit CSS Grid rows in the `app-shell` shell layout.

#### Scenario: Bottom nav stays at viewport bottom
- **WHEN** the dashboard page has enough events to require scrolling
- **THEN** `bottom-nav-bar` SHALL remain visible and pinned at the bottom of the viewport at all times
- **AND** route components SHALL prevent content overflow via `min-block-size: 0` on their `:scope` grid declaration

#### Scenario: Stage header sticks within route scroll container
- **WHEN** the user scrolls the live-highway event list downward
- **THEN** the stage header (HOME STAGE / NEAR STAGE / AWAY STAGE) SHALL remain fixed above the scrollable content
- **AND** the stage header SHALL be a `<header>` element inside the `live-highway` CE, outside the scrollable `.highway-scroll` area
- **AND** the `live-highway` CE SHALL use CSS Grid (`grid-template-rows: auto 1fr`) to separate the fixed header from the scrollable content
- **AND** the `live-highway` CE SHALL declare its own `:scope { display: block; block-size: 100%; min-block-size: 0; }` to inherit height from the route component

#### Scenario: Overlay elements remain functional
- **WHEN** an overlay element activates (e.g., toast notification, coach-mark spotlight)
- **THEN** the overlay SHALL render correctly via the browser top-layer API, unaffected by the flow removal
