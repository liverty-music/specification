## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: PWA Install Prompt Deferred to Second Post-Completion Session

**Reason**: The FAB is a passive persistent element, not a disruptive Toast. The session-count deferral was designed to give the notification prompt a first-session window, which only applies to the Toast-based prompt. The FAB does not compete with the notification prompt for screen space or attention.

**Migration**: The `StorageKeys.pwaCompletedSessionCount` and `StorageKeys.pwaSessionCount` localStorage keys are no longer written or read by `PwaInstallService`. Existing values are ignored and will be cleaned up lazily.

#### Scenario: Second session after completion

- **WHEN** the user is on the second or later session after onboarding completion
- **AND** the `beforeinstallprompt` event has fired
- **AND** the PWA install prompt has not been dismissed
- **AND** no other prompt has been shown this session
- **THEN** the system SHALL display the PWA install prompt

---

### Requirement: Dismissed Prompts Do Not Reappear (PWA install only)

**Reason**: The FAB has no dismiss action. It is a passive UI element that remains visible until the app is installed. The concept of "dismissing" the install prompt does not apply to the FAB model.

**Migration**: `StorageKeys.pwaInstallPromptDismissed` is no longer written or read. The `PwaInstallService.dismiss()` method is removed. Existing dismissed state in localStorage is ignored.

#### Scenario: User dismisses PWA install prompt

- **WHEN** the user taps the dismiss control on the PWA install prompt
- **THEN** the system SHALL write the dismissal to LocalStorage
- **AND** the PWA install prompt SHALL NOT appear on subsequent sessions
