## Purpose

Define the guided first-run onboarding tutorial: the linear step progression through landing, artist discovery, dashboard arrival, and My Artists, including how spotlights and coach marks steer the user. The dashboard Lane Intro sequence (blocker divs, scroll lock, nav dimming) has been removed; arriving at the dashboard completes that step.
## Requirements
### Requirement: Coach Mark Navigation Delegation

The system SHALL delegate navigation from coach mark taps to the target element's native href, not to a separate `router.load()` call.

#### Scenario: Nav tab tap through coach mark

- **WHEN** a coach mark spotlight is active on a nav tab
- **AND** the user taps the spotlighted nav tab
- **THEN** the nav tab's native click event SHALL handle navigation
- **AND** the system SHALL NOT call `router.load()` from the `onTap` callback

