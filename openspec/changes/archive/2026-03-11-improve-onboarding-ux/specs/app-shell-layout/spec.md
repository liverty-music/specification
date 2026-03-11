## MODIFIED Requirements

### Requirement: Conditional Navigation Display

The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be visible on all pages except the Landing Page and auth callback.

#### Scenario: App shell uses CSS Grid layout with height propagation

- **WHEN** the application shell renders
- **THEN** the root container SHALL use CSS Grid with `grid-template-rows: 1fr min-content`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** the `<main>` element SHALL occupy the `1fr` row and use CSS Grid (`grid-template-rows: auto auto 1fr`) to arrange prompts and the viewport
- **AND** the `<main>` element SHALL use `overflow: hidden` to prevent scrolling at the main level
- **AND** the `<au-viewport>` element SHALL occupy the `1fr` track within `<main>`, providing a definite height to route components
- **AND** the `<au-viewport>` element SHALL use `overflow-y: auto` as the scrolling container for route content
- **AND** the `<bottom-nav-bar>` element SHALL occupy the `min-content` row as a normal flow child
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API (`popover` attribute / `showPopover()`)

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
- **AND** the My Artists tab link SHALL include a `data-nav-my-artists` attribute (existing)
