## MODIFIED Requirements

### Requirement: Sequential Lane Header Spotlight

The system SHALL introduce each dashboard lane by sequentially spotlighting the STAGE headers with explanatory coach marks. Each phase waits for a user tap to advance. The HOME phase pauses to collect the user's 居住エリア selection before displaying the dynamic coach mark text.

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

#### Scenario: HOME STAGE phase — Home Selector opens inline

- **WHEN** the lane introduction sequence begins
- **THEN** the system SHALL spotlight the HOME STAGE header element (`[data-stage="home"]`)
- **AND** if `guest.home` or `user.home` is not yet set, the system SHALL open the Home Selector bottom-sheet immediately
- **AND** the coach mark tooltip SHALL display: "居住エリアのライブが並びます。居住エリアはどこですか？"
- **AND** the HOME phase SHALL NOT advance until `onHomeSelected` fires (user selects a 居住エリア)

#### Scenario: HOME STAGE phase — after region selected

- **WHEN** the user has selected their 居住エリア
- **AND** the Home Selector bottom-sheet closes
- **THEN** the coach mark tooltip SHALL update to: "{{prefecture}}のライブ" (dynamically interpolated with selected prefecture name)
- **AND** the system SHALL wait for a tap to advance to the NEAR phase

#### Scenario: HOME STAGE phase — region already set

- **WHEN** the lane introduction sequence begins
- **AND** `guest.home` or `user.home` is already set
- **THEN** the system SHALL NOT open the Home Selector
- **AND** the coach mark tooltip SHALL immediately display: "{{prefecture}}のライブ"
- **AND** the system SHALL wait for a tap to advance to the NEAR phase

#### Scenario: NEAR STAGE header spotlight

- **WHEN** the HOME phase tap is received
- **THEN** the system SHALL spotlight the NEAR STAGE header element (`[data-stage="near"]`)
- **AND** the coach mark SHALL display: "少し足を伸ばせば行けるライブ"
- **AND** the system SHALL wait for a tap to advance to the AWAY phase

#### Scenario: AWAY STAGE header spotlight

- **WHEN** the NEAR phase tap is received
- **THEN** the system SHALL spotlight the AWAY STAGE header element (`[data-stage="away"]`)
- **AND** the coach mark SHALL display: "遠征ライブ！"
- **AND** the system SHALL wait for a tap to proceed to Celebration

#### Scenario: Transition to Celebration

- **WHEN** the AWAY phase tap is received
- **THEN** the system SHALL open the Celebration Overlay
- **AND** the Lane Intro sequence SHALL be complete

## REMOVED Requirements

### Requirement: Auto-advance timer (2-second per phase)

**Reason**: Auto-advance gives users insufficient time to read coach mark text and prevents them from absorbing the lane structure at their own pace. Tap-to-advance respects user agency and is architecturally simpler (no timer to cancel on interrupt).

**Migration**: Remove `scheduleLaneIntroAdvance()` and the 2-second `setTimeout`. Each phase now calls `advanceLaneIntro()` only from the tap callback.

### Requirement: Transition to first card spotlight after lane intro

**Reason**: The card spotlight step (phase: `'card'`) is removed. After AWAY phase, the sequence proceeds directly to Celebration. The Celebration overlay replaces the card spotlight as the transition point to free exploration.

**Migration**: Remove the `'card'` phase from `laneIntroPhase` type. Remove card spotlight activation. The `laneIntroPhase: 'done'` state now transitions to Celebration open instead of card spotlight.
