## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL guide the user forward through onboarding steps. The DASHBOARD step has no Lane Intro sequence, blocker divs, or scroll lock — arriving at the dashboard completes the step. The MY_ARTISTS step completes on arrival. After dashboard arrival the user explores freely.

> **Note on Step numbering**: The "Step N" labels mirror the `onboardingStep` state-machine values (`'lp'` = Step 0, `'discovery'` = Step 1, `'dashboard'` = Step 3, `'my-artists'` = Step 5, `'completed'` = Step 7, per `frontend-route-guard`).

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

#### Scenario: Step 3 - Dashboard arrival completes the step

- **WHEN** a user is at Step `'dashboard'`
- **AND** the Dashboard page is attached
- **THEN** the system SHALL advance `onboardingStep` to `'my-artists'`
- **AND** the system SHALL NOT run any Lane Intro sequence, blocker divs, or scroll lock
- **AND** all nav tabs SHALL be fully interactive

#### Scenario: Step 3 - Concert card tap opens Detail Sheet

- **WHEN** a user taps a concert card on the dashboard during onboarding
- **THEN** the system SHALL open the EventDetailSheet for that concert
- **AND** the system SHALL NOT advance any onboarding step

#### Scenario: Step 5 - My Artists first visit auto-opens help

- **WHEN** a user at Step `'my-artists'` navigates to the My Artists page
- **THEN** the PageHelp bottom-sheet SHALL auto-open (first visit, per `onboarding-page-help` spec)
- **AND** the sheet SHALL explain hype levels

#### Scenario: Step 5 - My Artists arrival completes onboarding

- **WHEN** a user at Step `'my-artists'` arrives at the My Artists page (its `attached()` lifecycle runs)
- **THEN** the system SHALL deactivate any active spotlight
- **AND** the system SHALL advance `onboardingStep` to `'completed'`
- **AND** completion SHALL NOT require the user to change a hype level
- **AND** the My Artists unfollow control SHALL become available (onboarding no longer in progress)

#### Scenario: Step 1 spotlight cleanup on non-target navigation

- **WHEN** the Step 1 coach mark spotlight is active on the Dashboard icon
- **AND** the user navigates away from Discovery by means other than tapping the spotlighted target
- **THEN** the spotlight SHALL be deactivated via the route's `detaching()` lifecycle hook (per `onboarding-spotlight` "Route Detach Spotlight Cleanup")
- **AND** no time-based fade timer SHALL be involved in the cleanup path

## REMOVED Requirements

### Requirement: Non-spotlighted Nav Tabs Visually Disabled During Lane Intro

**Reason**: The Lane Intro sequence has been removed from the dashboard implementation; there is no phase during which nav tabs are dimmed. The `nav-dimming-service` is being deleted (it was only ever called with `setDimmed(false)`).

**Migration**: Remove `nav-dimming-service` and its single caller in `dashboard-route.ts`. No replacement — nav tabs are always interactive after dashboard arrival.
