<!-- spec: prompt-timing | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: PWA Install Prompt Blocked During Onboarding -->
<!-- implementation names to remove: PwaInstallService -->

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
