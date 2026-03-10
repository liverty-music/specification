## MODIFIED Requirements

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context. The navigation bar SHALL be an in-flow grid child of the app shell, not a fixed-position or top-layer element.

#### Scenario: App shell uses CSS Grid layout with auto-stretch height propagation
- **WHEN** the application shell renders
- **THEN** the root container (`my-app`) SHALL use CSS Grid with `grid-template-rows: 1fr min-content`
- **AND** the container height SHALL be `100dvh` (dynamic viewport height)
- **AND** `au-viewport` SHALL be a direct grid child of `my-app`, occupying the `1fr` row
- **AND** `au-viewport` SHALL use `display: grid` so that route components auto-stretch to fill both axes without explicit `height` declarations
- **AND** a `<main>` element with `display: contents` SHALL wrap `au-viewport` for semantic accessibility (HTML landmark), without creating an additional layout box
- **AND** the `<bottom-nav-bar>` element SHALL occupy the `min-content` row as a normal flow child
- **AND** the navigation bar SHALL NOT use `position: fixed`, `position: absolute`, or the Popover API (`popover` attribute / `showPopover()`)

#### Scenario: Route components receive definite size without height relay
- **WHEN** a route component is rendered inside `au-viewport`
- **THEN** the route component SHALL receive the full width and height of the `1fr` grid track automatically via CSS Grid stretch behavior
- **AND** the route component SHALL NOT need to declare `height: 100%` to fill the available space
- **AND** route components that need vertical scrolling SHALL apply `overflow-y: auto` on their own scrollable container

#### Scenario: Navigation hidden during onboarding
- **WHEN** the user is on the Landing Page, Artist Discovery, or Loading Sequence routes
- **THEN** the system SHALL NOT display the bottom navigation bar
- **AND** the `1fr` row SHALL expand to fill the full `100dvh` height

#### Scenario: Navigation shown on dashboard
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display the bottom navigation bar in the `min-content` grid row
- **AND** the navigation bar SHALL include tab icons and labels for Home, Discover, My Artists, Tickets, and Settings

#### Scenario: Navigation remains visible beneath area setup dialog
- **WHEN** the first-visit area setup dialog is displayed on the Dashboard
- **THEN** the area setup dialog SHALL render via `<dialog>` `showModal()` in the browser's Top Layer
- **AND** the bottom navigation bar SHALL remain in its normal grid position beneath the Top Layer
- **AND** the `::backdrop` pseudo-element SHALL visually dim the entire page including the navigation bar

#### Scenario: Pages do not compensate for navigation bar height
- **WHEN** any route component renders inside the `au-viewport` element
- **THEN** the route component SHALL NOT apply viewport-relative height constraints (e.g., `100dvh`, `100vh`) or bottom padding (e.g., `pb-14`) to account for the navigation bar
- **AND** the CSS Grid layout SHALL ensure the route content fills the available space within the `1fr` track

#### Scenario: Overlay components do not interfere with grid layout
- **WHEN** overlay components (PWA install prompt, notification prompt, error banner) are rendered
- **THEN** they SHALL be placed as direct children of `my-app`, outside `au-viewport`
- **AND** they SHALL use the Popover API (`popover="manual"`) or `<dialog>` for top-layer rendering
- **AND** they SHALL NOT create implicit grid rows or affect the `1fr` / `min-content` grid track sizing

#### Scenario: No class name collisions with CSS framework utilities
- **WHEN** route components define custom CSS classes in light DOM
- **THEN** custom class names SHALL NOT collide with Tailwind CSS utility class names (e.g., `.container`)
- **AND** route-specific layout classes SHALL use component-prefixed names (e.g., `.discover-layout` instead of `.container`)
