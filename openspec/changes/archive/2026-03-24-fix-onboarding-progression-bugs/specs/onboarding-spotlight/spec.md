## MODIFIED Requirements

### Requirement: Click-Blocker Layer via Transparent Anchor-Positioned Divs

The coach mark SHALL use four transparent click-blocker divs (top, right, bottom, left) positioned with CSS `anchor()` functions to block interactions outside the target element.

#### Scenario: Clicks outside spotlight are blocked

- **WHEN** the coach mark overlay is active
- **AND** the user taps an area covered by a click-blocker div
- **THEN** the tap SHALL be intercepted by the blocker (`pointer-events: auto`)
- **AND** the tap SHALL NOT reach the underlying page content

#### Scenario: Clicks inside spotlight reach the target

- **WHEN** the coach mark overlay is active
- **AND** the user taps inside the spotlight cutout area
- **THEN** the tap SHALL pass through to the actual target element
- **AND** the target element SHALL receive the click event natively

#### Scenario: Target interceptor invokes onTap callback

- **WHEN** the coach mark overlay is active with an `onTap` callback registered
- **AND** the user taps the target interceptor overlay
- **THEN** the `onTap` callback SHALL be invoked
- **AND** the caller MAY use the callback to deactivate the spotlight (e.g., `deactivateSpotlight()`)

#### Scenario: Click-blockers cover the entire viewport except target bounds

- **WHEN** the coach mark overlay is active
- **THEN** `.mask-top` SHALL cover from viewport top to `anchor(target top)`
- **AND** `.mask-bottom` SHALL cover from `anchor(target bottom)` to viewport bottom
- **AND** `.mask-left` SHALL cover from viewport left to `anchor(target left)`, between target top and bottom
- **AND** `.mask-right` SHALL cover from `anchor(target right)` to viewport right, between target top and bottom

#### Scenario: My Artists step provides onTap dismissal callback

- **WHEN** the onboarding step is `my-artists`
- **AND** `activateSpotlight` is called for the `[data-hype-header]` target
- **THEN** an `onTap` callback SHALL be provided that calls `deactivateSpotlight()`
- **AND** after the spotlight is dismissed, the hype sliders SHALL be interactive
- **AND** the user SHALL be able to change a hype level to complete onboarding
