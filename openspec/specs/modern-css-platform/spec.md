# Modern CSS Platform

## Purpose

Defines the modern CSS platform standards for the Liverty Music frontend, leveraging 2026 Web Platform Baseline features including Container Queries, View Transitions API, `:has()` selectors, CSS Logical Properties, Anchored Container Queries, `@starting-style`, `transitionend`-based cleanup, `overscroll-behavior`, and `scrollIntoView` + `scrollend` patterns for responsive, performant, and internationalization-ready styling.

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
Route change animations SHALL use the View Transitions API (Baseline 2024) to run transitions off the main thread. No CSS keyframe fallback is required for non-supporting browsers.

#### Scenario: Forward navigation transition
- **WHEN** the user navigates forward to a new route
- **THEN** the old view SHALL fade out and the new view SHALL fade in using `::view-transition-old(root)` and `::view-transition-new(root)` pseudo-elements
- **AND** the transition SHALL NOT block the main thread
- **AND** View Transition styles SHALL NOT be gated behind `@supports` feature queries

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

### Requirement: Anchored Container Query for position-dependent child styling
Components that use CSS Anchor Positioning with fallback positions SHALL use `container-type: anchored` and `@container anchored(fallback: ...)` to style descendant elements based on which fallback was applied, instead of JavaScript-based position detection.

#### Scenario: Tooltip arrow toggles when position flips
- **WHEN** a tooltip is anchored to a target using `position-anchor` and flips via `position-try-fallbacks: flip-block`
- **THEN** `@container anchored(fallback: flip-block)` SHALL toggle which arrow SVG is visible (above vs below)
- **AND** no JavaScript SHALL read `getBoundingClientRect()`, use `requestAnimationFrame`, or set `data-flipped` attributes to determine arrow direction

#### Scenario: Anchored container query graceful degradation
- **WHEN** a browser does not support `container-type: anchored`
- **THEN** the default `position-area` SHALL render the tooltip in a usable position
- **AND** the default arrow (`.coach-arrow-above`) SHALL display

### Requirement: CSS `@starting-style` for entry animations on dynamic elements
Elements inserted into the DOM dynamically SHALL use `@starting-style` to define initial animation state instead of `requestAnimationFrame` deferrals.

#### Scenario: Toast notification entry animation
- **WHEN** a toast notification element is inserted into the DOM
- **THEN** the element SHALL transition from `@starting-style` values (e.g., `opacity: 0`, `translateY(-1rem)`) to its resting state using CSS `transition`
- **AND** no `requestAnimationFrame` SHALL be used to defer visibility or class changes for animation triggering

#### Scenario: Popover entry animation
- **WHEN** child elements are inserted into a visible popover container shown via `showPopover()`
- **THEN** each child's entry animation SHALL use `@starting-style` on the child element's rule
- **AND** no JavaScript SHALL delay the `showPopover()` call with `requestAnimationFrame`

### Requirement: `transitionend` event for post-animation DOM cleanup
DOM removal or state cleanup after CSS exit transitions SHALL use the `transitionend` event instead of `setTimeout` with hardcoded durations.

#### Scenario: Toast removal after exit transition
- **WHEN** a toast notification's exit transition completes (opacity reaches 0)
- **THEN** the `transitionend` event on `propertyName === 'opacity'` SHALL trigger DOM removal of the toast element
- **AND** no `setTimeout` SHALL be used to estimate when the transition finishes

#### Scenario: Overlay cleanup after fade-out transition
- **WHEN** a full-screen overlay's fade-out transition completes
- **THEN** the `transitionend` event SHALL trigger the `onComplete` callback and state cleanup
- **AND** the overlay SHALL remain visible until the transition actually finishes (not after a hardcoded delay)

#### Scenario: Reduced motion bypasses transitionend
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled AND `transition: none` is applied
- **THEN** the component SHALL detect reduced motion and perform cleanup immediately without waiting for `transitionend`

### Requirement: `overscroll-behavior: contain` for scroll isolation
Scrollable containers inside overlays, sheets, or modals SHALL use `overscroll-behavior: contain` to prevent scroll chaining to the page behind.

#### Scenario: Bottom sheet scroll isolation
- **WHEN** the user scrolls to the top or bottom boundary of a sheet's scrollable content area
- **THEN** the scroll SHALL NOT propagate to the viewport or page behind the sheet
- **AND** the CSS property `overscroll-behavior: contain` SHALL be applied to the scrollable container

### Requirement: `scrollIntoView` + `scrollend` for scroll-then-act patterns
Components that need to scroll an element into view before performing an action SHALL use `element.scrollIntoView()` with a `scrollend` event listener instead of manual viewport detection with `getBoundingClientRect()`.

#### Scenario: Coach mark scrolls target into view
- **WHEN** a coach mark spotlight activates on a target element
- **THEN** the component SHALL call `target.scrollIntoView({ behavior: 'smooth', block: 'center' })`
- **AND** the component SHALL wait for the `scrollend` event before showing the spotlight overlay
- **AND** a failsafe timeout (≤ 1000ms) SHALL resolve if `scrollend` does not fire

#### Scenario: Target already in viewport
- **WHEN** the target element is already fully visible in the viewport
- **THEN** `scrollIntoView` SHALL be called (it is a no-op when element is visible)
- **AND** the failsafe timeout SHALL still apply (no `scrollend` fires, so the timeout resolves after its full duration, ≤ 1000ms)
- **AND** no `getBoundingClientRect()` or `isInViewport()` helper SHALL gate the scroll call

### Requirement: `data-state` attribute for CSS animation state
Elements with enter/exit CSS transitions SHALL use a `data-state` attribute (e.g., `entering`, `exiting`, `active`) to drive CSS selectors instead of JavaScript class toggling.

#### Scenario: Exit state triggers CSS transition
- **WHEN** an element transitions from active to exiting state
- **THEN** the element SHALL set `data-state="exiting"` as the attribute value
- **AND** the CSS selector `[data-state="exiting"]` SHALL apply exit transition properties (e.g., `opacity: 0`)
- **AND** no JavaScript SHALL directly manipulate `classList` for animation state changes
