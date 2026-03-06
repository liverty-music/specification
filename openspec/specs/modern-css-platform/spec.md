# Modern CSS Platform

## Purpose

Defines the modern CSS platform standards for the Liverty Music frontend, leveraging 2026 Web Platform Baseline features including Container Queries, View Transitions API, `:has()` selectors, and CSS Logical Properties for responsive, performant, and internationalization-ready styling.

## Requirements

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
Layout, spacing, and positioning properties SHALL use CSS Logical Properties for internationalization readiness. Compliance SHALL be enforced by Stylelint via `property-disallowed-list`.

#### Scenario: Margin and padding use logical properties
- **WHEN** a CSS file contains margin or padding declarations
- **THEN** the declarations SHALL use `margin-inline`, `margin-block`, `padding-inline`, `padding-block` (or their `-start`/`-end` longhands) instead of physical `margin-left`, `margin-top`, etc.
- **AND** Stylelint SHALL reject physical margin/padding properties as errors

#### Scenario: Border and positioning use logical properties
- **WHEN** a CSS file contains border or positioning declarations
- **THEN** the declarations SHALL use `border-inline-start`, `inset-inline`, `inset-block-end`, etc. instead of physical equivalents
- **AND** Stylelint SHALL reject physical border/positioning properties as errors

#### Scenario: All existing physical properties migrated
- **WHEN** the Stylelint configuration is applied to the codebase
- **THEN** all existing physical directional properties SHALL have been migrated to logical equivalents
- **AND** `stylelint --fix` or manual migration SHALL have resolved all violations

### Requirement: OKLCH color enforcement
All color definitions in CSS SHALL use the `oklch()` function. Legacy color functions and hex notation SHALL be rejected by Stylelint.

#### Scenario: OKLCH used for solid colors
- **WHEN** a CSS property requires a color value (e.g., `color`, `background-color`, `border-color`)
- **THEN** the value SHALL use `oklch()` notation
- **AND** Stylelint SHALL reject `rgb()`, `rgba()`, `hsl()`, `hsla()`, and hex colors

#### Scenario: OKLCH used for transparency
- **WHEN** a color requires an alpha/transparency component
- **THEN** the value SHALL use `oklch(L C H / alpha)` syntax
- **AND** legacy `rgba(R G B / alpha)` SHALL be rejected

#### Scenario: Tailwind theme colors exempt
- **WHEN** a color value is provided via Tailwind `theme()` function or CSS custom properties (e.g., `var(--color-brand-primary)`)
- **THEN** the value SHALL not be subject to color function linting
