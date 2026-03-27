## MODIFIED Requirements

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element. The `aria-label` on the tooltip SHALL be `"Onboarding tip"`. Navigation SHALL be delegated to the target element's native click behavior; the coach mark SHALL NOT call `router.load()`. Target selectors SHALL be scoped to a specific component context (e.g., `concert-highway [data-stage="home"]`) to prevent matching elements in unrelated components.

#### Scenario: Spotlight renders for active step

- **WHEN** an onboarding step requires a coach mark
- **THEN** the system SHALL display the spotlight overlay with instructional text
- **AND** the tooltip `aria-label` SHALL be `"Onboarding tip"`

#### Scenario: Nav tab tap through spotlight delegates to href

- **WHEN** a coach mark spotlight is active on a nav tab element
- **AND** the user taps the spotlighted element
- **THEN** the system SHALL call `currentTarget.click()` to fire the element's native click event
- **AND** the system SHALL call `onTap?.()` callback (for step-advance logic only)
- **AND** the system SHALL NOT call `router.load()` from within the coach mark component or its `onTap` callback

#### Scenario: Blocker divs prevent off-target interaction

- **WHEN** a coach mark spotlight is active
- **THEN** blocker divs SHALL cover the viewport area outside the spotlight target
- **AND** taps on blocker divs SHALL be silently ignored (no navigation, no error)
- **AND** the scroll lock (`overflow: hidden` on `au-viewport`) SHALL remain active while the coach mark is active

#### Scenario: Target selector is scoped to component context

- **WHEN** `activateSpotlight()` is called with a target selector
- **THEN** the selector SHALL include a component-scoped prefix (e.g., `concert-highway [data-stage="home"]` instead of bare `[data-stage="home"]`)
- **AND** `document.querySelector()` SHALL NOT match elements in unrelated components (e.g., `page-help` decorative labels)

## ADDED Requirements

### Requirement: Invisible Target Rejection

The `findAndHighlight()` method SHALL reject target elements that are invisible (zero dimensions or `offsetParent === null`) and continue retry logic as if the element was not found.

#### Scenario: Zero-dimension target is skipped

- **WHEN** `document.querySelector(targetSelector)` returns an element
- **AND** the element has zero width and zero height (`getBoundingClientRect()` returns 0×0)
- **THEN** the system SHALL treat the element as not found
- **AND** the system SHALL continue exponential backoff retry logic

#### Scenario: Hidden element in closed popover is skipped

- **WHEN** a matching element exists inside a closed popover or `display: none` container
- **AND** the element's `offsetParent` is `null`
- **THEN** the system SHALL skip this element
- **AND** the system SHALL retry until a visible matching element appears or timeout is reached
