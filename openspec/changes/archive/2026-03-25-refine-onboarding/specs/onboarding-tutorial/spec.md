## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL enforce a guided progression through onboarding steps. During the Lane Intro phase of DASHBOARD, user interaction outside the spotlighted element is blocked via blocker divs and scroll lock. After Celebration dismissal, the user explores freely and navigates to My Artists at their own pace.

#### Scenario: Step 0 - Landing Page entry

- **WHEN** a user is at Step `'lp'`
- **AND** the user taps the [Get Started] CTA
- **THEN** the system SHALL advance `onboardingStep` to `'discovery'`
- **AND** navigate to the Artist Discovery screen

#### Scenario: Step 1 - Artist Discovery completion

- **WHEN** a user is at Step `'discovery'`
- **AND** the progression condition is met (5 follows OR 3 artists with concerts)
- **THEN** the system SHALL activate the coach mark spotlight on the Dashboard icon for 2 seconds, then deactivate it
- **AND** when the user taps the Home/Dashboard icon, the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Step 3 - Dashboard Lane Intro begins

- **WHEN** a user is at Step `'dashboard'`
- **AND** the Dashboard page loads
- **THEN** the system SHALL begin the Lane Intro sequence (see `dashboard-lane-introduction` spec)
- **AND** blocker divs SHALL be active and scroll SHALL be locked during Lane Intro phases

#### Scenario: Step 3 - Celebration opens and DASHBOARD step completes

- **WHEN** the Lane Intro sequence completes all phases (home, near, away)
- **THEN** the system SHALL open the Celebration Overlay
- **AND** opening the Celebration Overlay SHALL advance `onboardingStep` to `'my-artists'`

#### Scenario: Step 3 - Celebration dismissed; free exploration begins

- **WHEN** the Celebration Overlay is dismissed (user taps anywhere)
- **THEN** blocker divs SHALL be deactivated
- **AND** scroll lock SHALL be released
- **AND** all nav tabs SHALL become fully interactive
- **AND** the user SHALL be able to freely browse the timetable and tap concert cards

#### Scenario: Step 3 - Concert card tap opens Detail Sheet

- **WHEN** a user is in free exploration after Celebration dismissal
- **AND** the user taps a concert card
- **THEN** the system SHALL open the EventDetailSheet for that concert
- **AND** the system SHALL NOT advance any onboarding step

#### Scenario: Step 5 - My Artists page first visit

- **WHEN** a user at Step `'my-artists'` navigates to the My Artists page (by their own nav tap)
- **THEN** the PageHelp bottom-sheet SHALL auto-open (first visit, per `onboarding-page-help` spec)
- **AND** the sheet SHALL explain hype levels

#### Scenario: Step 5 - Hype change completes onboarding

- **WHEN** a user at Step `'my-artists'` changes a hype level
- **THEN** the system SHALL persist the hype change (no revert)
- **AND** the system SHALL advance `onboardingStep` to `'completed'`

### Requirement: Non-spotlighted Nav Tabs Visually Disabled During Lane Intro

The system SHALL visually indicate that non-spotlighted nav tabs are inactive during the Lane Intro sequence.

#### Scenario: Nav tabs dimmed during Lane Intro

- **WHEN** the Lane Intro sequence is active (any phase: home, near, away)
- **THEN** nav tabs that are not the current spotlight target SHALL have reduced opacity (0.3)
- **AND** non-target nav tabs SHALL have `aria-disabled="true"` set

#### Scenario: Nav tabs restored after Celebration dismissal

- **WHEN** the Celebration Overlay is dismissed
- **THEN** all nav tabs SHALL return to full opacity
- **AND** all `aria-disabled` attributes SHALL be removed

### Requirement: Coach Mark Navigation Delegation

The system SHALL delegate navigation from coach mark taps to the target element's native href, not to a separate `router.load()` call.

#### Scenario: Nav tab tap through coach mark

- **WHEN** a coach mark spotlight is active on a nav tab
- **AND** the user taps the spotlighted nav tab
- **THEN** the nav tab's native click event SHALL handle navigation
- **AND** the system SHALL NOT call `router.load()` from the `onTap` callback

## REMOVED Requirements

### Requirement: Step 3 - Concert card tap advances to DETAIL step

**Reason**: The DETAIL step is removed. Card taps now open the EventDetailSheet directly. Step progression from DASHBOARD is triggered by Celebration open, not card tap.

**Migration**: Remove `onOnboardingCardTapped()` method's step-advance logic from `dashboard-route.ts`. Replace with `eventDetailSheet.open(concert)` call.

### Requirement: Step 4 - Detail sheet with My Artists tab guidance

**Reason**: DETAIL step is removed. The My Artists spotlight sequence after card tap is replaced by the PageHelp auto-open on first visit to My Artists.

**Migration**: Remove all `isOnboardingStepDetail` checks. Remove the My Artists spotlight activation from the DETAIL → MY_ARTISTS transition.

### Requirement: Step 5 - Passion Level guidance spotlight

**Reason**: Replaced by PageHelp auto-open on first visit to My Artists. The explicit `[data-artist-rows]` spotlight is removed.

**Migration**: Remove `activateSpotlight('[data-artist-rows]', ...)` call from `my-artists-route.ts` loading logic.

### Requirement: Step 5 - Hype dot tap reverts change and completes onboarding

**Reason**: Hype changes are now persisted (not reverted). Onboarding completion is triggered by any hype change without reverting the user's selection.

**Migration**: Remove `artist.hype = prev` revert line. Keep `setStep(COMPLETED)` and `deactivateSpotlight()`.
