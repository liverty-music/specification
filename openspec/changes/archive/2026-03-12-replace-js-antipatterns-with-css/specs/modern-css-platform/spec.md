## ADDED Requirements

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
- **AND** the failsafe timeout SHALL resolve immediately
- **AND** no `getBoundingClientRect()` or `isInViewport()` helper SHALL gate the scroll call

### Requirement: `data-state` attribute for CSS animation state
Elements with enter/exit CSS transitions SHALL use a `data-state` attribute (e.g., `entering`, `exiting`, `active`) to drive CSS selectors instead of JavaScript class toggling.

#### Scenario: Exit state triggers CSS transition
- **WHEN** an element transitions from active to exiting state
- **THEN** the element SHALL set `data-state="exiting"` as the attribute value
- **AND** the CSS selector `[data-state="exiting"]` SHALL apply exit transition properties (e.g., `opacity: 0`)
- **AND** no JavaScript SHALL directly manipulate `classList` for animation state changes
