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
- **THEN** the system SHALL activate the coach mark spotlight on the Dashboard icon and SHALL keep it active until the user taps the highlighted target
- **AND** the spotlight SHALL NOT auto-dismiss based on elapsed time
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

#### Scenario: Step 1 spotlight persists across route changes only via cleanup

- **WHEN** the Step 1 coach mark spotlight is active on the Dashboard icon
- **AND** the user navigates away from the Discovery route by means other than tapping the spotlighted target (e.g., browser back, direct nav-tab tap to a different tab)
- **THEN** the spotlight SHALL be deactivated via the route's `detaching()` lifecycle hook (per `onboarding-spotlight` "Route Detach Spotlight Cleanup")
- **AND** no time-based fade timer SHALL be involved in the cleanup path
