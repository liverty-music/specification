## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through tutorial steps. Users SHALL NOT be able to skip steps or navigate freely during the tutorial.

#### Scenario: Step 0 - Landing Page entry

- **WHEN** a user is at Step 0 (LP)
- **AND** the user taps the [Get Started] CTA
- **THEN** the system SHALL advance `onboardingStep` to 1
- **AND** navigate to the Artist Discovery screen

#### Scenario: Step 1 - Artist Discovery completion with concert data gate

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists via bubble taps
- **AND** concert search results have been received for all followed artists (or timed out after 15 seconds per artist)
- **AND** `ConcertService/List` returns at least 1 date group for the followed artists
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard icon in the bottom navigation bar (target: `[data-nav-dashboard]`)
- **AND** the coach mark SHALL display the message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon, the system SHALL advance `onboardingStep` to 3 (DASHBOARD), skipping Step 2 (LOADING)
- **AND** the system SHALL navigate to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Concert searches complete with no results

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists
- **AND** concert search results have been received for all followed artists (or timed out)
- **AND** `ConcertService/List` returns 0 date groups
- **THEN** the system SHALL NOT activate the Dashboard coach mark
- **AND** the system SHALL update the guidance HUD message to: "No upcoming events found yet — try following more artists!"
- **AND** the system SHALL re-evaluate the concert data gate each time a new artist is followed and their concert search completes

#### Scenario: Step 1 - Progress bar display

- **WHEN** a user is at Step 1
- **THEN** the system SHALL display a progress bar showing concert search completion status
- **AND** the progress bar SHALL fill continuously based on the ratio of completed concert searches to total followed artists
- **AND** the progress bar target SHALL require 3 or more artists with completed (or timed-out) concert searches
- **AND** the user MAY continue following more artists after reaching 3

#### Scenario: Step 2 - Loading sequence (deprecated for onboarding)

- **WHEN** a user is at Step 2 (LOADING)
- **THEN** this step is no longer entered during the onboarding flow
- **AND** the `OnboardingStep.LOADING` enum value (2) SHALL be retained for backward compatibility with existing localStorage state
- **AND** if a user has `onboardingStep=2` in localStorage from a prior session, the route guard SHALL redirect them to the Dashboard (`/dashboard`)

#### Scenario: Step 3 - Dashboard reveal with celebration and lane introduction

- **WHEN** a user is at Step 3 (Dashboard)
- **THEN** the system SHALL display the celebration overlay (see `onboarding-celebration` capability)
- **AND** after celebration, the system SHALL display the region selection BottomSheet overlay (if home area not yet set)
- **AND** after region selection, the system SHALL run the lane introduction sequence (see `dashboard-lane-introduction` capability)
- **AND** after lane introduction, the system SHALL disable scrolling
- **AND** the system SHALL apply a spotlight overlay highlighting only the first concert card
- **AND** the system SHALL display a coach mark tooltip: "タップして詳細を見てみよう！"

#### Scenario: Step 3 - Dashboard with no concert data (fallback)

- **WHEN** a user is at Step 3 (Dashboard)
- **AND** `ConcertService/List` returns 0 date groups (e.g., user reached Dashboard via direct nav tap bypassing the concert data gate)
- **THEN** the system SHALL skip the lane introduction sequence entirely
- **AND** the system SHALL advance `onboardingStep` to 4 (DETAIL)
- **AND** the system SHALL activate the spotlight on the [My Artists] tab in the bottom navigation bar
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step 3
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to 4
- **AND** open the concert detail sheet (popover)

#### Scenario: Step 4 - Detail sheet with My Artists tab guidance

- **WHEN** a user is at Step 4 (Detail sheet open)
- **THEN** the system SHALL NOT allow the detail sheet to be dismissed (no swipe-down, no backdrop tap)
- **AND** the system SHALL highlight the [My Artists] tab in the bottom navigation bar
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"

#### Scenario: Step 4 - My Artists tab tap

- **WHEN** a user is at Step 4
- **AND** the user taps the highlighted [My Artists] tab
- **THEN** the system SHALL advance `onboardingStep` to 5
- **AND** navigate to the My Artists screen

#### Scenario: Step 5 - Passion Level guidance

- **WHEN** a user is at Step 5 (My Artists)
- **THEN** the system SHALL highlight the Passion Level toggle of the first artist in the list
- **AND** the system SHALL display a coach mark tooltip: "好きなレベルを設定してみよう！"

#### Scenario: Step 5 - Passion Level changed

See "Requirement: Step 5 Passion Level Explanation Timing" below for the updated behaviour of this scenario.

#### Scenario: Step 6 - SignUp modal display

- **WHEN** a user is at Step 6
- **THEN** the system SHALL display the Passkey authentication modal
- **AND** the modal SHALL NOT be dismissible (no close button, no backdrop tap, no escape key)
- **AND** the modal message SHALL read: "All set! Create an account to save your preferences and never miss a live show."

#### Scenario: Step 6 - Passkey authentication success

- **WHEN** a user is at Step 6
- **AND** the user completes Passkey authentication successfully
- **THEN** the system SHALL trigger the guest data merge process
- **AND** upon merge completion, set `onboardingStep` to 7 (COMPLETED)
- **AND** remove all tutorial UI restrictions (coach marks, spotlight, interaction locks)
- **AND** navigate to the Dashboard with full unrestricted access

#### Scenario: Step 6 - Page reload

- **WHEN** a user reloads the page with `onboardingStep = 6`
- **THEN** the system SHALL re-display the non-dismissible SignUp modal immediately

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
- **AND** if still not found, the system SHALL fully deactivate the coach mark overlay: close the popover, release scroll lock, clear anchor-name assignments, and log an error
- **AND** no click-blockers, spotlight elements, or scroll locks SHALL remain in the DOM after deactivation

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the spotlight pulse animation SHALL be disabled
- **AND** the static ring border SHALL remain visible

## Test Cases

### Unit Tests (Vitest — discover-page.spec.ts)

#### TC-GATE-01: Dashboard coach mark requires concert data

- **Given** `onboardingStep = 1`, 3+ artists followed, all concert searches completed
- **And** `ConcertService/List` returns 0 date groups
- **When** `showDashboardCoachMark` is evaluated
- **Then** it SHALL be `false`
- **And** `activateSpotlight()` SHALL NOT be called

#### TC-GATE-02: Dashboard coach mark activates when concerts exist

- **Given** `onboardingStep = 1`, 3+ artists followed, all concert searches completed
- **And** `ConcertService/List` returns 1+ date groups
- **When** `showDashboardCoachMark` is evaluated
- **Then** it SHALL be `true`
- **And** `activateSpotlight('[data-nav-dashboard]', ...)` SHALL be called

#### TC-GATE-03: Guidance message updates when no concerts found

- **Given** `onboardingStep = 1`, 3+ artists followed, all concert searches completed
- **And** `ConcertService/List` returns 0 date groups
- **Then** the guidance message SHALL indicate no upcoming events and prompt to follow more artists

### Unit Tests (Vitest — dashboard.spec.ts)

#### TC-GATE-04: Lane intro skipped when dateGroups is empty

- **Given** `onboardingStep = 3`, `dateGroups = []`
- **When** `startLaneIntro()` is called (via `onCelebrationComplete()` or `onHomeSelected()`)
- **Then** `laneIntroPhase` SHALL be `'done'`
- **And** `onboardingService.setStep(4)` SHALL be called (DETAIL)
- **And** `onboardingService.activateSpotlight('[data-nav-my-artists]', ...)` SHALL be called

### Unit Tests (Vitest — coach-mark.spec.ts)

#### TC-GATE-05: Coach mark fully deactivates when target not found after retries

- **Given** the coach mark is active with a selector that matches no DOM element
- **When** 5 seconds of retry have elapsed
- **Then** the popover SHALL be hidden (`hidePopover()`)
- **And** scroll lock SHALL be released (overflow restored on `au-viewport`)
- **And** `anchor-name` SHALL be cleared from any previous target
- **And** no click-blockers SHALL remain visible

### E2E Tests (Playwright)

#### TC-GATE-E2E-01: Dashboard with no concerts skips lane intro without stuck overlay

- **Given** `onboardingStep = 3`, `celebrationShown = 1`, `guest.home` is set
- **And** `ConcertService/List` mock returns `{ dateGroups: [] }`
- **When** the Dashboard page loads
- **Then** no click-blockers SHALL be present in the DOM
- **And** no spotlight overlay SHALL be visible
- **And** `onboardingStep` SHALL advance to `4`

#### TC-GATE-E2E-02: Discovery does not show coach mark when no concerts found

- **Given** `onboardingStep = 1`, 3+ artists followed (via localStorage seed)
- **And** `SearchNewConcerts` mock returns success
- **And** `ConcertService/List` mock returns `{ dateGroups: [] }`
- **When** all concert searches complete
- **Then** no Dashboard coach mark SHALL appear
- **And** the guidance HUD SHALL display a "no upcoming events" message
