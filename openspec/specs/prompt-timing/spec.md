# Prompt Timing

## Purpose

Defines the eligibility rules for displaying PWA install and push notification permission prompts. Prompts are gated by authentication state, onboarding completion, session count, and a per-session single-prompt constraint to avoid overwhelming the user.

## Requirements

### Requirement: PWA Install Prompt Blocked During Onboarding

The system SHALL NOT display the PWA install prompt while the user is in onboarding Steps 1-6.

#### Scenario: User is mid-tutorial on the dashboard (Step 3)

- **WHEN** the user is at onboarding Step 3 (Dashboard)
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL capture the event
- **AND** the system SHALL NOT display the PWA install banner
- **AND** `PwaInstallService.canShow` SHALL remain `false`

#### Scenario: User has not started onboarding (Step 0)

- **WHEN** the user is at onboarding Step 0 (LP)
- **AND** the browser fires the `beforeinstallprompt` event
- **THEN** the system SHALL NOT display the PWA install banner

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

The system SHALL NOT display the push notification prompt during onboarding Steps 1-6.

#### Scenario: User at Step 5 (My Artists) before sign-up

- **WHEN** the user is at onboarding Step 5
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

#### Scenario: Both prompts eligible on first post-completion session

- **WHEN** the user has completed onboarding
- **AND** notification permission is not yet granted
- **AND** the notification prompt has not been dismissed
- **AND** the PWA install prompt is also eligible
- **THEN** the system SHALL display the notification prompt
- **AND** the system SHALL NOT display the PWA install prompt

#### Scenario: Notification prompt already dismissed

- **WHEN** the user has previously dismissed the notification prompt
- **AND** the PWA install prompt is eligible
- **THEN** the system SHALL display the PWA install prompt

---

### Requirement: Notification Prompt Eligible on First Post-Completion Session

The notification prompt SHALL be eligible to display on the first session after onboarding completion (Step 7), when user motivation is highest.

#### Scenario: User completes onboarding and returns

- **WHEN** the user has completed onboarding (Step 7)
- **AND** the user starts a new session (page load)
- **AND** the user is authenticated
- **AND** the notification prompt has not been dismissed
- **AND** notification permission is not `granted`
- **THEN** the system SHALL display the notification prompt

#### Scenario: User completes onboarding within the same session

- **WHEN** the user completes Step 6 and transitions to Step 7 within the current session
- **THEN** the system SHALL NOT display any prompt in the same session as completion
- **AND** the prompt SHALL be eligible starting from the next session

---

### Requirement: PWA Install Prompt Deferred to Second Post-Completion Session

The PWA install prompt SHALL be eligible starting from the second session after onboarding completion, giving the notification prompt a clear first-session window.

#### Scenario: First session after completion

- **WHEN** the user is on the first session after onboarding completion
- **AND** the `beforeinstallprompt` event has fired
- **THEN** the system SHALL NOT display the PWA install prompt, regardless of notification prompt dismissal state

#### Scenario: Second session after completion

- **WHEN** the user is on the second or later session after onboarding completion
- **AND** the `beforeinstallprompt` event has fired
- **AND** the PWA install prompt has not been dismissed
- **AND** no other prompt has been shown this session
- **THEN** the system SHALL display the PWA install prompt

---

### Requirement: Dismissed Prompts Do Not Reappear

When the user dismisses a prompt, the system SHALL persist the dismissal and SHALL NOT show that prompt again. This is existing behavior preserved by this change.

#### Scenario: User dismisses notification prompt

- **WHEN** the user taps the dismiss control on the notification prompt
- **THEN** the system SHALL write the dismissal to LocalStorage
- **AND** the notification prompt SHALL NOT appear on subsequent sessions

#### Scenario: User dismisses PWA install prompt

- **WHEN** the user taps the dismiss control on the PWA install prompt
- **THEN** the system SHALL write the dismissal to LocalStorage
- **AND** the PWA install prompt SHALL NOT appear on subsequent sessions
