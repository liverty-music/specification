# Notification Prompt

## Purpose

Prompts a signed-in user, once onboarding is complete, to grant push-notification permission, limiting itself to one prompt per session, taking priority over other disruptive prompts, and never reappearing once dismissed.

## Requirements

### Requirement: Notification Prompt Placement

The notification prompt SHALL be rendered at the app shell level (`my-app.html`) rather than within the dashboard route template. This ensures the prompt is available on any post-onboarding route, not only the dashboard.

#### Scenario: Notification prompt rendered in app shell when eligible

- **WHEN** the user is authenticated (`auth.isAuthenticated === true`)
- **AND** onboarding is completed (`onboarding.isCompleted === true`)
- **AND** the navigation bar is visible (`showNav === true`)
- **THEN** the system SHALL render the `<notification-prompt>` component in the app shell
- **AND** the prompt SHALL appear above the main content area, below any app-level banners

#### Scenario: Notification prompt hidden during onboarding routes

- **WHEN** the user is on a fullscreen route (Landing Page, Auth Callback)
- **OR** the user is not authenticated
- **OR** onboarding is not completed
- **THEN** the system SHALL NOT render the `<notification-prompt>` component

#### Scenario: Notification prompt removed from dashboard route

- **WHEN** the dashboard route template is rendered
- **THEN** the template SHALL NOT contain a `<notification-prompt>` element
- **AND** the notification prompt import SHALL be removed from the dashboard template

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

### Requirement: Dismissed notification prompt does not reappear

When the user dismisses the notification prompt, the system SHALL persist the dismissal and SHALL NOT show that prompt again. The `pwa-install-banner` has no dismiss of its own (see Pwa Install Banner).

#### Scenario: User dismisses notification prompt

- **WHEN** the user taps the dismiss control on the notification prompt
- **THEN** the system SHALL write the dismissal to `localStorage`
- **AND** the notification prompt SHALL NOT appear on subsequent sessions

### Requirement: The permission answer is reported

After the fan answers the browser's push-permission request, the fan app SHALL send one usage analytics event with the answer (granted, denied, or dismissed without an answer) and where the request started: the push offer after a hype change (the notification prompt), the post-signup sheet, Settings, or checkout.

#### Scenario: Fan denies
- **WHEN** the fan presses 「オンにする」 on the push offer and then blocks notifications in the browser's request
- **THEN** one event is sent with the answer denied and the notification prompt as its start
