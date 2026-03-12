## MODIFIED Requirements

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element with a high-contrast spotlight effect, pulse animation, and large instructional tooltip.

#### Scenario: Spotlight renders for active step

- **WHEN** a tutorial step requires a coach mark
- **THEN** the system SHALL dim the entire screen with a semi-transparent overlay at `oklch(0% 0 0deg / 75%)`
- **AND** the system SHALL cut out a highlight area around the target element
- **AND** the highlight area SHALL have a `2px solid` ring in the brand accent color
- **AND** the ring SHALL animate with a pulse effect (scale 1→1.05→1, 1.5s infinite)
- **AND** the system SHALL display a tooltip with the step's instructional text
- **AND** the tooltip SHALL use `font-size: 16px`, `padding: 16px`, brand accent background color, white text, and `border-radius: 12px`

#### Scenario: Only highlighted element is interactive

- **WHEN** the coach mark overlay is active
- **THEN** only the highlighted target element SHALL accept user interaction (tap/click)
- **AND** all other elements SHALL be blocked by the overlay

#### Scenario: Scroll lock during coach mark

- **WHEN** the coach mark overlay is active
- **THEN** the system SHALL disable scrolling on the `<au-viewport>` scroll container by adding `overflow: hidden`
- **AND** scrolling SHALL be restored when the coach mark is deactivated

#### Scenario: Coach mark target not found

- **WHEN** the target element for a coach mark is not present in the DOM
- **THEN** the system SHALL retry finding the element with exponential backoff (up to 5 seconds)
- **AND** if still not found, the system SHALL display an error message and allow the user to retry the step

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the spotlight pulse animation SHALL be disabled
- **AND** the static ring border SHALL remain visible

#### Scenario: Bring to front for top-layer re-ordering

- **WHEN** the coach mark needs to appear above another popover already in the top layer (e.g., the concert detail sheet at Step 4)
- **THEN** the coach mark SHALL call `hidePopover()` followed by `showPopover()` on its overlay element to re-enter the top layer at the LIFO top position
- **AND** the re-show SHALL be batched within a single animation frame to avoid visual flicker

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through tutorial steps. Users SHALL NOT be able to skip steps or navigate freely during the tutorial.

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step 3
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to 4
- **AND** open the concert detail sheet (popover with `popover="manual"`)

#### Scenario: Step 4 - Detail sheet with My Artists tab guidance

- **WHEN** a user is at Step 4 (Detail sheet open)
- **THEN** the system SHALL NOT allow the detail sheet to be dismissed (no swipe-down, no backdrop tap)
- **AND** the system SHALL highlight the [My Artists] tab in the bottom navigation bar
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"
- **AND** the coach mark popover SHALL re-enter the top layer AFTER the detail sheet popover has been shown, ensuring the coach mark renders above the detail sheet per LIFO stacking rules

#### Scenario: Step 4 - My Artists tab tap

- **WHEN** a user is at Step 4
- **AND** the user taps the highlighted [My Artists] tab
- **THEN** the system SHALL advance `onboardingStep` to 5
- **AND** navigate to the My Artists screen
