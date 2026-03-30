# Dashboard Lane Introduction

## Purpose

Introduces each dashboard lane to the user during onboarding by sequentially spotlighting the STAGE headers with explanatory coach marks, providing context about the three-lane timetable layout. Each phase waits for a user tap anywhere on the screen to advance. The HOME phase pauses to collect the user's home area selection before displaying the dynamic coach mark text.

## Requirements

### Requirement: Sequential Lane Header Spotlight

The system SHALL introduce each dashboard lane by sequentially spotlighting the STAGE headers with explanatory coach marks. Each phase waits for a user tap **anywhere on the screen** to advance. The HOME phase pauses to collect the user's home area selection before displaying the dynamic coach mark text. Spotlight activation SHALL be deferred until concert data has loaded and the stage header elements are rendered in the DOM.

#### Scenario: Lane introduction begins after Dashboard load

- **WHEN** the user is at Step `'dashboard'`
- **AND** the Dashboard page loads
- **AND** `ConcertService/ListWithProximity` has returned 1 or more date groups
- **AND** the stage header elements (`[data-stage]`) are present in the DOM
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
- **AND** the spotlight SHALL NOT be activated until concert data has loaded and the HOME STAGE header element is present in the DOM

#### Scenario: HOME STAGE phase — Home Selector opens without spotlight

- **WHEN** the lane introduction sequence begins
- **AND** `guest.home` or `user.home` is not yet set (`needsRegion` is true)
- **THEN** the system SHALL open the Home Selector bottom-sheet immediately
- **AND** the system SHALL NOT activate the spotlight (no coach-mark overlay)
- **AND** the HOME phase SHALL NOT advance until `onHomeSelected` fires (user selects a home area)

#### Scenario: HOME STAGE phase — spotlight activates after data load

- **WHEN** the user has selected their home area via the Home Selector
- **AND** `loadData()` has completed and `dateGroups.length > 0`
- **AND** Aurelia has rendered the stage header elements in the DOM (post-render queue flush)
- **THEN** the system SHALL activate the spotlight on `concert-highway [data-stage="home"]`
- **AND** the coach mark tooltip SHALL display the selected prefecture name with concert context
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the NEAR phase

#### Scenario: HOME STAGE phase — region already set

- **WHEN** the lane introduction sequence begins
- **AND** `guest.home` or `user.home` is already set
- **THEN** the system SHALL NOT open the Home Selector
- **AND** the system SHALL await data load completion in the `loading()` lifecycle hook
- **AND** the coach mark tooltip SHALL immediately display the prefecture-specific concert message after DOM rendering
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the NEAR phase

#### Scenario: NEAR STAGE header spotlight

- **WHEN** the HOME phase tap is received
- **THEN** the system SHALL spotlight the NEAR STAGE header element (`concert-highway [data-stage="near"]`)
- **AND** the coach mark SHALL display the nearby concerts message
- **AND** the system SHALL wait for a tap anywhere on the screen to advance to the AWAY phase

#### Scenario: AWAY STAGE header spotlight

- **WHEN** the NEAR phase tap is received
- **THEN** the system SHALL spotlight the AWAY STAGE header element (`concert-highway [data-stage="away"]`)
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

### Requirement: Auto-advance timer (2-second per phase) (REMOVED)

**Reason**: Auto-advance gives users insufficient time to read coach mark text and prevents them from absorbing the lane structure at their own pace. Tap-to-advance respects user agency and is architecturally simpler (no timer to cancel on interrupt).

**Migration**: Remove `scheduleLaneIntroAdvance()` and the 2-second `setTimeout`. Each phase now calls `advanceLaneIntro()` only from the tap callback.

### Requirement: Transition to first card spotlight after lane intro (REMOVED)

**Reason**: The card spotlight step (phase: `'card'`) is removed. After AWAY phase, the sequence proceeds directly to Celebration. The Celebration overlay replaces the card spotlight as the transition point to free exploration.

**Migration**: Remove the `'card'` phase from `laneIntroPhase` type. Remove card spotlight activation. The `laneIntroPhase: 'done'` state now transitions to Celebration open instead of card spotlight.

### Requirement: Lane Introduction State Management

The lane introduction sequence SHALL be managed locally within the dashboard component, not persisted in the onboarding service. Nav-tab dimming SHALL be delegated to an injectable `INavDimmingService` rather than performed via direct DOM queries, enabling the state machine to be unit-tested without a real DOM. Reactive data observation SHALL be used to coordinate spotlight activation with data availability.

#### Scenario: Lane intro state is ephemeral

- **WHEN** the dashboard component manages the lane introduction
- **THEN** the intro state SHALL be a local variable (e.g., `laneIntroPhase: 'home' | 'waiting-for-home' | 'near' | 'away' | 'done'`)
- **AND** the state SHALL NOT be written to `liverty:onboardingStep` in LocalStorage

#### Scenario: Page reload during lane introduction

- **WHEN** the user reloads the page during the lane introduction sequence
- **THEN** the system SHALL restart the lane introduction from the beginning (HOME STAGE)
- **AND** the celebration overlay SHALL NOT replay (it uses a separate one-time flag)

#### Scenario: Data loading drives spotlight activation reactively

- **WHEN** `dateGroups` transitions from empty to non-empty (length changes from 0 to >0)
- **AND** the lane intro is in an active phase awaiting data
- **THEN** Aurelia's `@watch` decorator SHALL detect the `dateGroups.length` change
- **AND** the system SHALL defer spotlight activation to the next render cycle via `queueTask()`

#### Scenario: queueTask ensures DOM readiness

- **WHEN** `dateGroups` changes and the `@watch` callback fires
- **THEN** `queueTask()` SHALL schedule spotlight activation after Aurelia completes its template update cycle
- **AND** the `if.bind="dateGroups.length > 0"` on the stage header SHALL have been evaluated
- **AND** `concert-highway [data-stage="home"]` SHALL be present in the DOM when the spotlight activates

#### Scenario: Nav tabs are dimmed via INavDimmingService
- **WHEN** the lane introduction starts
- **THEN** `INavDimmingService.setDimmed(true)` SHALL be called
- **AND** the component SHALL NOT directly query `[data-nav]` elements from the DOM

#### Scenario: Nav tabs are undimmed on completion or dismissal
- **WHEN** the lane introduction completes or the celebration is dismissed
- **THEN** `INavDimmingService.setDimmed(false)` SHALL be called

#### Scenario: Nav tab dimming is expressed via data attribute, not inline style
- **WHEN** `INavDimmingService.setDimmed(true)` is called on a `[data-nav]` element
- **THEN** the element SHALL receive a `data-dimmed` attribute (via `toggleAttribute`)
- **AND** the visual treatment (opacity, transition) SHALL be applied via CSS (`[data-nav][data-dimmed]` rule in the exception layer)
- **AND** no `style.setProperty` or `aria-disabled` manipulation SHALL occur

### Requirement: Data loading awaited before lane intro decision (polling loop) (REMOVED)

**Reason:** The `while (isLoading) await sleep(100)` polling loop is replaced by Aurelia 2's `@watch` decorator observing `dateGroups.length`. Reactive observation is more efficient, eliminates busy-waiting, and naturally coordinates with the DOM rendering cycle when combined with `queueTask()`.

**Migration:** Remove the `while (this.isLoading)` polling loop from `startLaneIntro()`. Add `@watch((vm: DashboardRoute) => vm.dateGroups.length)` to reactively trigger spotlight activation. Use `queueTask()` to defer activation until after DOM updates.
