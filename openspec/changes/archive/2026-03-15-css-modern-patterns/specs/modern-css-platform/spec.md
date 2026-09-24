## MODIFIED Requirements

### Requirement: @starting-style for all entry animations
Elements inserted into the DOM dynamically SHALL use `@starting-style` for entry animations instead of `requestAnimationFrame` or two-step class toggling.

#### Scenario: Popover content entry
- **WHEN** `showPopover()` is called on a popover element
- **THEN** the popover's content SHALL use `@starting-style` for entry transition
- **AND** no JavaScript SHALL delay `showPopover()` with `requestAnimationFrame` for animation purposes

#### Scenario: Toast notification entry
- **WHEN** a new toast notification is added to the DOM
- **THEN** the toast SHALL define `@starting-style` with initial values (e.g., `opacity: 0`, `transform: translateY(-1rem)`)
- **AND** the element's `transition` property SHALL animate from the starting style to the resting state

### Requirement: CSS :has() for parent-state styling
Parent elements SHALL use `:has()` pseudo-class to style themselves based on child or sibling state, instead of JavaScript-driven parent class toggling.

#### Scenario: Navigation parent highlights active child
- **WHEN** a navigation list contains a child with `[data-active]` or `[aria-current]`
- **THEN** the parent navigation item SHALL style itself via `:has([data-active])` or `:has([aria-current])` selector
- **AND** no JavaScript SHALL set a class or attribute on the parent element for this purpose

### Requirement: Container Queries for component-level responsive design
Components that render in variable-width containers SHALL use CSS Container Queries instead of viewport-based media queries for layout adaptation. All responsive components SHALL be audited and converted.

#### Scenario: All responsive components use Container Queries
- **WHEN** any component has layout that adapts to available space
- **THEN** the component SHALL use `@container` queries, not `@media (min-width: ...)` or `@media (max-width: ...)`
- **AND** stylelint SHALL enforce this via `media-feature-name-disallowed-list`
