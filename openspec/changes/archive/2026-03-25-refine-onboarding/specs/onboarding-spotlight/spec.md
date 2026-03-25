## MODIFIED Requirements

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element. The `aria-label` on the tooltip SHALL be `"Onboarding tip"`. Navigation SHALL be delegated to the target element's native click behavior; the coach mark SHALL NOT call `router.load()`.

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
