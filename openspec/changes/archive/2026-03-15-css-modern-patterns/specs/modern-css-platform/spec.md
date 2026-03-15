## ADDED Requirements

### Requirement: CSS scroll snap for bottom sheet dismiss gestures
Bottom sheets that support swipe-to-dismiss SHALL use CSS scroll snap instead of JavaScript touch event handlers.

#### Scenario: User swipes down to dismiss the event detail sheet
- **WHEN** a bottom sheet is open and the user swipes downward
- **THEN** the sheet container SHALL use `scroll-snap-type: y mandatory` with two snap points (content and dismiss zone)
- **AND** the browser's native scroll mechanics SHALL handle the drag gesture, snap-back, and momentum
- **AND** a `scrollend` event handler SHALL detect when the dismiss zone is reached and call `close()`
- **AND** no JavaScript `touchstart`/`touchmove`/`touchend` handlers SHALL be used for drag tracking

#### Scenario: User swipes partially and releases
- **WHEN** the user swipes down less than the dismiss threshold and releases
- **THEN** CSS scroll snap SHALL automatically snap the sheet back to the content position
- **AND** no JavaScript animation or `requestAnimationFrame` SHALL be used for the snap-back

#### Scenario: Non-dismissable mode (onboarding)
- **WHEN** the sheet is in non-dismissable mode (`popover="manual"`)
- **THEN** the scroll snap dismiss zone SHALL be hidden or disabled
- **AND** the user SHALL NOT be able to dismiss the sheet by swiping

### Requirement: No JS-to-CSS variable bridge custom attributes
Custom attributes that solely set a CSS custom property from a JavaScript value (e.g., `drag-offset` setting `--_drag-y`, `swipe-offset` setting `--_swipe-x`) SHALL NOT exist. These are unnecessary abstraction layers.

#### Scenario: Removing bridge custom attributes
- **WHEN** a custom attribute exists only to call `element.style.setProperty('--_name', value)`
- **THEN** the underlying JS pattern SHALL be replaced with a CSS-native approach (e.g., scroll snap)
- **AND** the custom attribute SHALL be deleted

#### Scenario: Custom attributes with computation are valid
- **WHEN** a custom attribute performs computation (e.g., hashing a string to derive a color value)
- **THEN** the custom attribute SHALL be retained as it provides genuine logic encapsulation

### Requirement: Scroll-driven Animations for scroll-linked effects
Scroll-linked visual effects (progress indicators, parallax, shadow-on-scroll) SHALL use CSS Scroll-driven Animations instead of JavaScript scroll event listeners.

#### Scenario: Scroll progress indicator
- **WHEN** a scrollable container needs a visual progress indicator
- **THEN** the indicator element SHALL use `animation-timeline: scroll()` with a `@keyframes` rule
- **AND** no JavaScript `scroll` event listener SHALL be used for this purpose

#### Scenario: Graceful degradation for unsupported browsers
- **WHEN** a browser does not support `animation-timeline: scroll()`
- **THEN** the element SHALL display in its default (non-animated) state
- **AND** `@supports (animation-timeline: scroll())` SHALL gate scroll-driven animation rules

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

## MODIFIED Requirements

### Requirement: Container Queries for component-level responsive design
Components that render in variable-width containers SHALL use CSS Container Queries instead of viewport-based media queries for layout adaptation. All responsive components SHALL be audited and converted.

#### Scenario: All responsive components use Container Queries
- **WHEN** any component has layout that adapts to available space
- **THEN** the component SHALL use `@container` queries, not `@media (min-width: ...)` or `@media (max-width: ...)`
- **AND** stylelint SHALL enforce this via `media-feature-name-disallowed-list`
