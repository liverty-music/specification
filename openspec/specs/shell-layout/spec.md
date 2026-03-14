# shell-layout Specification

## Purpose

Defines the PWA shell layout structure for `my-app`, ensuring overlay custom elements are excluded from CSS Grid flow so that `bottom-nav-bar` stays pinned at the viewport bottom and `position: sticky` headers work correctly within scroll containers.
## Requirements
### Requirement: Overlay elements excluded from grid flow
All overlay custom elements (`pwa-install-prompt`, `notification-prompt`, `toast-notification`, `error-banner`, `coach-mark`) SHALL be removed from normal document flow so they do not create implicit CSS Grid rows in the `my-app` shell layout.

#### Scenario: Bottom nav stays at viewport bottom
- **WHEN** the dashboard page has enough events to require scrolling
- **THEN** `bottom-nav-bar` SHALL remain visible and pinned at the bottom of the viewport at all times

#### Scenario: Stage header sticks on scroll
- **WHEN** the user scrolls the live-highway event list downward
- **THEN** the stage header (HOME STAGE / NEAR STAGE / AWAY STAGE) SHALL remain fixed at the top of the scroll container and not scroll away

#### Scenario: Overlay elements remain functional
- **WHEN** an overlay element activates (e.g., toast notification, coach-mark spotlight)
- **THEN** the overlay SHALL render correctly via the browser top-layer API, unaffected by the flow removal

