## ADDED Requirements

### Requirement: Container Queries for component-level responsive design
Components that render in variable-width containers SHALL use CSS Container Queries instead of viewport-based media queries for layout adaptation.

#### Scenario: Event card adapts to lane width
- **WHEN** an `event-card` renders inside a `live-highway` lane
- **THEN** the lane element SHALL declare `container-type: inline-size`
- **AND** the card layout SHALL adapt using `@container` rules based on the lane's available width

#### Scenario: Container query fallback
- **WHEN** a browser does not support Container Queries
- **THEN** the component SHALL fall back to a reasonable default layout
- **AND** the `@supports (container-type: inline-size)` feature query SHALL gate container-specific rules

### Requirement: View Transitions API for route animations
Route change animations SHALL use the View Transitions API to run transitions off the main thread.

#### Scenario: Forward navigation transition
- **WHEN** the user navigates forward to a new route
- **THEN** the old view SHALL fade out and the new view SHALL fade in using View Transitions
- **AND** the transition SHALL NOT block the main thread

#### Scenario: Graceful degradation
- **WHEN** the browser does not support the View Transitions API
- **THEN** the route change SHALL fall back to the existing CSS keyframe animation on `au-viewport > *`
- **AND** `@supports (view-transition-name: x)` SHALL gate View Transition styles

#### Scenario: Reduced motion preference
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** view transitions SHALL be suppressed or use instant crossfade (no animation)

### Requirement: CSS `:has()` selector for state-based styling
Parent elements that change styling based on child or sibling state SHALL use `:has()` selectors instead of JavaScript class toggling where feasible.

#### Scenario: Navigation item active state
- **WHEN** a navigation item contains an active indicator element
- **THEN** the parent element's styling SHALL be applied via `:has(.active-indicator)` or `:has([aria-current])` selectors
- **AND** no JavaScript SHALL be required to toggle parent classes for this purpose

#### Scenario: Form validation visual feedback
- **WHEN** a form field enters an invalid state
- **THEN** the parent container SHALL style itself using `:has(:invalid)` or `:has([aria-invalid="true"])`

### Requirement: CSS Logical Properties
Layout and spacing properties SHALL use CSS Logical Properties for internationalization readiness.

#### Scenario: Margin and padding use logical properties
- **WHEN** new CSS rules are written for component spacing
- **THEN** the rules SHALL use `margin-inline`, `margin-block`, `padding-inline`, `padding-block` instead of physical `margin-left`, `margin-top`, etc.
- **AND** existing physical properties SHALL be migrated opportunistically (when the file is already being modified)

#### Scenario: Border and positioning use logical properties
- **WHEN** new CSS rules define borders or positioning
- **THEN** the rules SHALL use `border-inline-start`, `inset-inline`, etc. instead of physical equivalents
