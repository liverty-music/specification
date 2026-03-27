## MODIFIED Requirements

### Requirement: Sequential Lane Header Spotlight

The system SHALL introduce each dashboard lane by sequentially spotlighting the STAGE headers with explanatory coach marks. Each phase waits for a user tap **anywhere on the screen** to advance. The HOME phase pauses to collect the user's home area selection before displaying the dynamic coach mark text.

#### Scenario: Lane introduction begins after Dashboard load

- **WHEN** the user is at Step `'dashboard'`
- **AND** the Dashboard page loads
- **AND** `ConcertService/ListWithProximity` has returned 1 or more date groups
- **THEN** the system SHALL begin the lane introduction sequence
- **AND** scrolling SHALL be disabled during the entire sequence
- **AND** blocker divs SHALL be active

#### Scenario: Lane introduction skipped when no concert data

- **WHEN** the Dashboard page loads
- **AND** `ConcertService/ListWithProximity` has returned 0 date groups
- **THEN** the system SHALL NOT begin the lane introduction sequence
- **AND** the system SHALL proceed directly to the Celebration Overlay
- **AND** the system SHALL log a warning: "No concert data available, skipping lane intro"

#### Scenario: Tap anywhere advances to next phase

- **WHEN** a lane intro phase is active (HOME, NEAR, or AWAY)
- **AND** the user taps anywhere on the screen (spotlight target, blocker area, or tooltip)
- **THEN** the system SHALL advance to the next phase
- **AND** the tap SHALL NOT propagate to underlying elements

#### Scenario: HOME STAGE phase — always starts via lane intro

- **WHEN** the user is at Step `'dashboard'`
- **AND** the Dashboard page loads
- **THEN** the system SHALL always begin the lane introduction sequence (not open Home Selector directly)
- **AND** if `guest.home` or `user.home` is not yet set, the system SHALL enter the `'waiting-for-home'` sub-state within the lane intro
- **AND** the HOME STAGE header SHALL be spotlighted while the Home Selector is open

#### Scenario: HOME STAGE phase — Home Selector opens inline

- **WHEN** the lane introduction sequence begins
- **THEN** the system SHALL spotlight the HOME STAGE header element (`[data-stage="home"]`)
- **AND** if `guest.home` or `user.home` is not yet set, the system SHALL open the Home Selector bottom-sheet immediately
- **AND** the coach mark tooltip SHALL display the home area prompt message
- **AND** the HOME phase SHALL NOT advance until `onHomeSelected` fires (user selects a home area)

#### Scenario: HOME STAGE phase — after region selected

- **WHEN** the user has selected their home area
- **AND** the Home Selector bottom-sheet closes
- **THEN** the coach mark tooltip SHALL update to show the selected prefecture name with concert context (dynamically interpolated)
- **AND** the prefecture name SHALL be resolved via the `translationKey()` helper from `entities/user.ts` (e.g., `JP-40` → `fukuoka` → `i18n.tr('userHome.prefectures.fukuoka')`)
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the NEAR phase

#### Scenario: HOME STAGE phase — region already set

- **WHEN** the lane introduction sequence begins
- **AND** `guest.home` or `user.home` is already set
- **THEN** the system SHALL NOT open the Home Selector
- **AND** the coach mark tooltip SHALL immediately display the prefecture-specific concert message
- **AND** the prefecture name SHALL be resolved via the `translationKey()` helper
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the NEAR phase

#### Scenario: NEAR STAGE header spotlight

- **WHEN** the HOME phase tap is received
- **THEN** the system SHALL spotlight the NEAR STAGE header element (`[data-stage="near"]`)
- **AND** the coach mark SHALL display the nearby concerts message
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the AWAY phase

#### Scenario: AWAY STAGE header spotlight

- **WHEN** the NEAR phase tap is received
- **THEN** the system SHALL spotlight the AWAY STAGE header element (`[data-stage="away"]`)
- **AND** the coach mark SHALL display the away/travel concerts message
- **AND** the system SHALL wait for a tap anywhere on the screen to proceed to Celebration

#### Scenario: Transition to Celebration

- **WHEN** the AWAY phase tap is received
- **THEN** the system SHALL open the Celebration Overlay
- **AND** the Lane Intro sequence SHALL be complete

#### Scenario: Onboarding dashboard uses ListWithProximity RPC

- **WHEN** the onboarding dashboard loads concert data
- **THEN** the system SHALL call `ConcertService/ListWithProximity` with the guest's followed artist IDs and selected Home
- **AND** the system SHALL NOT call `ConcertService/List` individually per artist
- **AND** concerts SHALL be distributed across HOME/NEAR/AWAY lanes based on server-provided proximity classification
