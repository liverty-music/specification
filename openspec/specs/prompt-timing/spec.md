# Prompt Timing

## Purpose

Defines the eligibility rules for displaying PWA install and push notification permission prompts. Prompts are gated by authentication state, onboarding completion, and a per-session single-prompt constraint to avoid overwhelming the user.

## Requirements

### Requirement: PWA Install Prompt Blocked During Onboarding

The system SHALL NOT display the `pwa-install-banner` while the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS).

#### Scenario: User is mid-tutorial on the dashboard

- **WHEN** the user is at onboarding step DASHBOARD
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event
- **AND** the system SHALL NOT display the `pwa-install-banner`
- **AND** `PwaInstallService.canShowFab` SHALL remain `false`

#### Scenario: User has not started onboarding (LP step)

- **WHEN** the user is at onboarding step LP
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL NOT display the `pwa-install-banner`

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

### Requirement: Notification Prompt Priority Over Disruptive PWA Prompts

The notification prompt SHALL have higher priority than any disruptive PWA install prompt. The `pwa-install-banner` is passive UI and is not subject to this constraint — it SHALL remain visible regardless of whether the notification prompt is shown.

#### Scenario: Both prompts eligible (first or later post-completion session)

- **WHEN** the user has completed onboarding
- **AND** notification permission is not yet granted
- **AND** the notification prompt has not been dismissed
- **AND** the `pwa-install-banner` is also eligible
- **THEN** the system SHALL display the notification prompt
- **AND** the `pwa-install-banner` SHALL remain visible (it is passive UI and does not compete with the notification prompt)

#### Scenario: Notification prompt already dismissed

- **WHEN** the user has previously dismissed the notification prompt
- **AND** the `pwa-install-banner` is eligible
- **THEN** the system SHALL display the `pwa-install-banner`

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

### Requirement: PWA Install Banner Eligible After Onboarding Completion

The `pwa-install-banner` SHALL be eligible immediately after onboarding completion for authenticated users who have not installed the app.

#### Scenario: First session after completion — authenticated user

- **WHEN** the user has completed onboarding
- **AND** the user IS authenticated
- **AND** the app has not been installed
- **THEN** the system SHALL display the `pwa-install-banner`

#### Scenario: Guest user after onboarding — banner not shown

- **WHEN** the user has completed onboarding
- **AND** the user is NOT authenticated
- **THEN** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: Completion within the same session

- **WHEN** the user transitions to `OnboardingStep.COMPLETED` within the current session
- **AND** the user is authenticated
- **THEN** the banner SHALL become visible immediately in that same session

---

### Requirement: Dismissed Prompts Do Not Reappear

When the user dismisses the notification prompt, the system SHALL persist the dismissal and SHALL NOT show that prompt again. The `pwa-install-banner` supports session-level dismiss: tapping the close button suppresses the banner for the current session only, and it reappears in subsequent sessions until the app is installed.

#### Scenario: User dismisses notification prompt

- **WHEN** the user taps the dismiss control on the notification prompt
- **THEN** the system SHALL write the dismissal to `localStorage`
- **AND** the notification prompt SHALL NOT appear on subsequent sessions

#### Scenario: User dismisses pwa-install-banner (session-level)

- **WHEN** the user taps the close button on the `pwa-install-banner`
- **THEN** the banner SHALL be hidden for the remainder of the current session
- **AND** the dismiss state SHALL be stored in `sessionStorage` only (NOT `localStorage`)
- **AND** the banner SHALL reappear on the next session if the app has not been installed

#### Scenario: Session dismiss is not permanent suppression

- **WHEN** the user has dismissed the `pwa-install-banner` in a previous session
- **AND** a new session begins
- **AND** the app has not been installed
- **THEN** the banner SHALL be shown again (session storage is cleared on new session)
