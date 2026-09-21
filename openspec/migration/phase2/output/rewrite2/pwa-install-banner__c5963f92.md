<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner Visible to Authenticated Non-Installed Users After Onboarding -->

### Requirement: Banner Visible to Authenticated Non-Installed Users After Onboarding

The system SHALL display the `pwa-install-banner` to authenticated users who have not installed the PWA, once onboarding is completed. The banner SHALL NOT be shown to unauthenticated (guest) users.

#### Scenario: Authenticated user has not installed the PWA

- **WHEN** the user is authenticated
- **AND** onboarding is completed (`OnboardingStep.COMPLETED`)
- **AND** the app has not been installed
- **AND** the session-dismiss flag is NOT set in `sessionStorage`
- **THEN** the system SHALL display the `pwa-install-banner`

#### Scenario: Guest user is not shown the banner

- **WHEN** the user is NOT authenticated
- **THEN** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: App already installed — banner not shown

- **WHEN** the app has been installed (detected via `localStorage['pwa.installed']`, `navigator.standalone === true`, or `display-mode: standalone`)
- **THEN** the system SHALL determine the banner should not be shown
- **AND** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: Banner not shown during onboarding

- **WHEN** the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS)
- **THEN** the system SHALL NOT display the `pwa-install-banner`
