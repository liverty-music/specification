## MODIFIED Requirements

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
