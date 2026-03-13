## ADDED Requirements

### Requirement: Scroll-driven Animations for scroll-linked effects
Scroll-linked visual effects (progress indicators, parallax, shadow-on-scroll) SHALL use CSS Scroll-driven Animations instead of JavaScript scroll event listeners.

#### Scenario: Scroll progress indicator
- **WHEN** a scrollable container needs a visual progress indicator
- **THEN** the indicator element SHALL use `animation-timeline: scroll()` with a `@keyframes` rule
- **AND** no JavaScript `scroll` event listener SHALL be used for this purpose

#### Scenario: Sticky header shadow on scroll
- **WHEN** a sticky header needs to show a shadow after the user scrolls past a threshold
- **THEN** the shadow SHALL be driven by `animation-timeline: scroll()` or `animation-timeline: view()`
- **AND** no JavaScript SHALL toggle a class or data attribute based on `scrollTop`

#### Scenario: Graceful degradation for unsupported browsers
- **WHEN** a browser does not support `animation-timeline: scroll()`
- **THEN** the element SHALL display in its default (non-animated) state
- **AND** `@supports (animation-timeline: scroll())` SHALL gate scroll-driven animation rules

### Requirement: @starting-style for all entry animations
Elements inserted into the DOM dynamically SHALL use `@starting-style` for entry animations instead of `requestAnimationFrame` or two-step class toggling.

#### Scenario: List item entry animation
- **WHEN** a new item is added to a `repeat.for` list
- **THEN** the item SHALL define `@starting-style` with initial values (e.g., `opacity: 0`)
- **AND** the element's `transition` property SHALL animate from the starting style to the resting state
- **AND** no `requestAnimationFrame` SHALL be used to defer a class or attribute change

#### Scenario: Popover content entry
- **WHEN** `showPopover()` is called on a popover element
- **THEN** the popover's content SHALL use `@starting-style` for entry transition
- **AND** no JavaScript SHALL delay `showPopover()` with `requestAnimationFrame` for animation purposes

### Requirement: CSS :has() for parent-state styling
Parent elements SHALL use `:has()` pseudo-class to style themselves based on child or sibling state, instead of JavaScript-driven parent class toggling.

#### Scenario: Navigation parent highlights active child
- **WHEN** a navigation list contains a child with `[data-active]` or `[aria-current]`
- **THEN** the parent navigation item SHALL style itself via `:has([data-active])` or `:has([aria-current])` selector
- **AND** no JavaScript SHALL set a class or attribute on the parent element for this purpose

#### Scenario: Form group highlights on invalid child
- **WHEN** a form field within a group becomes invalid
- **THEN** the parent group element SHALL style itself via `:has(:invalid)` or `:has([aria-invalid="true"])`
- **AND** no JavaScript validation watcher SHALL toggle a parent class

## MODIFIED Requirements

### Requirement: Container Queries for component-level responsive design
Components that render in variable-width containers SHALL use CSS Container Queries instead of viewport-based media queries for layout adaptation. All responsive components SHALL be audited and converted.

#### Scenario: Event card adapts to lane width
- **WHEN** an `event-card` renders inside a `live-highway` lane
- **THEN** the lane element SHALL declare `container-type: inline-size`
- **AND** the card layout SHALL adapt using `@container` rules based on the lane's available width

#### Scenario: Container query fallback
- **WHEN** a browser does not support Container Queries
- **THEN** the component SHALL fall back to a reasonable default layout
- **AND** the `@supports (container-type: inline-size)` feature query SHALL gate container-specific rules

#### Scenario: All responsive components use Container Queries
- **WHEN** any component has layout that adapts to available space
- **THEN** the component SHALL use `@container` queries, not `@media (min-width: ...)` or `@media (max-width: ...)`
- **AND** stylelint SHALL enforce this via `media-feature-name-disallowed-list`
