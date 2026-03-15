## MODIFIED Requirements

### Requirement: Overlay elements excluded from grid flow
All overlay custom elements (`pwa-install-prompt`, `notification-prompt`, `toast-notification`, `error-banner`, `coach-mark`) SHALL be removed from normal document flow so they do not create implicit CSS Grid rows in the app-shell layout.

#### Scenario: Bottom nav stays at viewport bottom
- **WHEN** the dashboard page has enough events to require scrolling
- **THEN** `bottom-nav-bar` SHALL remain visible and pinned at the bottom of the viewport at all times
- **AND** the `minmax(0, 1fr)` Grid track SHALL prevent content from expanding beyond the allocated space

#### Scenario: Stage header sticks within route scroll container
- **WHEN** the user scrolls the live-highway event list downward
- **THEN** the stage header (HOME STAGE / NEAR STAGE / AWAY STAGE) SHALL remain fixed above the scrollable content
- **AND** the stage header SHALL be a `<header>` element inside the `live-highway` CE, outside the scrollable `.highway-scroll` area
- **AND** the `live-highway` CE SHALL use CSS Grid (`grid-template-rows: auto 1fr`) to separate the fixed header from the scrollable content
- **AND** the `live-highway` CE SHALL receive a definite height from the app-shell Grid chain (via `block-size: 100%` on the CE)

#### Scenario: Overlay elements remain functional
- **WHEN** an overlay element activates (e.g., toast notification, coach-mark spotlight)
- **THEN** the overlay SHALL render correctly via the browser top-layer API, unaffected by the flow removal
