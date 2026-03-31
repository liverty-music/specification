# Prompt Timing

## Purpose

Defines the eligibility rules for displaying PWA install and push notification permission prompts. Prompts are gated by authentication state, onboarding completion, and a per-session single-prompt constraint to avoid overwhelming the user.

## Requirements

### Requirement: PWA Install Prompt Blocked During Onboarding

The system SHALL NOT display the PWA install FAB while the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS).

#### Scenario: User is mid-tutorial on the dashboard

- **WHEN** the user is at onboarding step DASHBOARD
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event
- **AND** the system SHALL NOT display the PWA install FAB
- **AND** `PwaInstallService.canShowFab` SHALL remain `false`

#### Scenario: User has not started onboarding (LP step)

- **WHEN** the user is at onboarding step LP
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL NOT display the PWA install FAB

---

### Requirement: Notification Prompt Blocked When Not Authenticated

The system SHALL NOT display the push notification prompt when the user is not authenticated.

#### Scenario: Anonymous user on dashboard during tutorial

- **WHEN** the user is not authenticated
- **AND** the user is on the dashboard route
- **THEN** the system SHALL NOT display the notification prompt

#### Scenario: Authenticated user after onboarding

- **WHEN** the user is authenticated
- **AND** onboarding is completed (Step 7)
- **THEN** the notification prompt MAY be eligible to display (subject to other guards)

---

### Requirement: Notification Prompt Blocked During Onboarding

The system SHALL NOT display the push notification prompt during active onboarding steps.

#### Scenario: User at MY_ARTISTS step before sign-up

- **WHEN** the user is at onboarding step MY_ARTISTS
- **THEN** the system SHALL NOT display the notification prompt
- **AND** the notification prompt component SHALL not evaluate visibility

---

### Requirement: Single Prompt Per Session

The system SHALL display at most one permission prompt (PWA install or push notification) per browser session.

#### Scenario: Notification prompt shown first

- **WHEN** the notification prompt has been displayed in the current session
- **AND** the PWA install prompt becomes eligible
- **THEN** the system SHALL NOT display the PWA install prompt in the same session

#### Scenario: PWA install prompt shown first

- **WHEN** the PWA install prompt has been displayed in the current session
- **AND** the notification prompt becomes eligible
- **THEN** the system SHALL NOT display the notification prompt in the same session

#### Scenario: New session resets prompt allowance

- **WHEN** the user reloads the page or opens a new browser session
- **THEN** the single-prompt-per-session constraint SHALL reset
- **AND** one prompt MAY be shown again (subject to dismissal and eligibility rules)

---

### Requirement: Notification Prompt Priority Over PWA Install

The notification prompt SHALL have higher priority than the PWA install prompt. When both prompts are eligible in the same session, the notification prompt SHALL be displayed.

#### Scenario: Both prompts eligible (first or later post-completion session)

- **WHEN** the user has completed onboarding
- **AND** notification permission is not yet granted
- **AND** the notification prompt has not been dismissed
- **AND** the PWA install FAB is also eligible
- **THEN** the system SHALL display the notification prompt
- **AND** the system SHALL NOT display the PWA install prompt in the same session

#### Scenario: Notification prompt already dismissed

- **WHEN** the user has previously dismissed the notification prompt
- **AND** the PWA install FAB is eligible
- **THEN** the system SHALL display the PWA install FAB

---

### Requirement: Notification Prompt Eligible on First Post-Completion Session

The notification prompt SHALL be eligible to display on the first session after onboarding completion, when user motivation is highest.

#### Scenario: User completes onboarding and returns

- **WHEN** the user has completed onboarding (`OnboardingStep.COMPLETED`)
- **AND** the user starts a new session (page load)
- **AND** the user is authenticated
- **AND** the notification prompt has not been dismissed
- **AND** notification permission is not `granted`
- **THEN** the system SHALL display the notification prompt

#### Scenario: User completes onboarding within the same session

- **WHEN** the user transitions to `OnboardingStep.COMPLETED` within the current session
- **THEN** the system SHALL NOT display any notification prompt in the same session as completion
- **AND** the notification prompt SHALL be eligible starting from the next session

---

### Requirement: PWA Install FAB Eligible After Onboarding Completion

The PWA install FAB SHALL be eligible immediately after onboarding completion, regardless of authentication state or session count.

#### Scenario: First session after completion — guest user

- **WHEN** the user has completed onboarding
- **AND** the user is NOT authenticated
- **AND** `beforeinstallprompt` has fired OR the platform is iOS Safari
- **THEN** the system SHALL display the PWA install FAB

#### Scenario: First session after completion — authenticated user

- **WHEN** the user has completed onboarding
- **AND** the user is authenticated
- **AND** `beforeinstallprompt` has fired OR the platform is iOS Safari
- **THEN** the system SHALL display the PWA install FAB

#### Scenario: Completion within the same session

- **WHEN** the user transitions to `OnboardingStep.COMPLETED` within the current session
- **THEN** the FAB SHALL become visible immediately in that same session

---

### Requirement: Dismissed Prompts Do Not Reappear

When the user dismisses a prompt, the system SHALL persist the dismissal and SHALL NOT show that prompt again. This applies to the notification prompt; the PWA install FAB has no dismiss action.

#### Scenario: User dismisses notification prompt

- **WHEN** the user taps the dismiss control on the notification prompt
- **THEN** the system SHALL write the dismissal to LocalStorage
- **AND** the notification prompt SHALL NOT appear on subsequent sessions
