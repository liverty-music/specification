<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner Suppressed While PostSignupDialog Is Open -->

### Requirement: Banner Suppressed While PostSignupDialog Is Open

The banner SHALL NOT be visible while the `PostSignupDialog` is open to avoid visual conflict at the bottom of the screen.

#### Scenario: PostSignupDialog open — banner hidden

- **WHEN** the `PostSignupDialog` is open
- **THEN** the system SHALL suppress the `pwa-install-banner`
- **AND** the banner SHALL NOT be rendered in the DOM

#### Scenario: PostSignupDialog closed — banner visible

- **WHEN** the `PostSignupDialog` is closed (user taps Later/Close)
- **AND** `PwaInstallService.shouldShowInstallBanner` is `true`
- **AND** session-dismiss flag is NOT set
- **THEN** the banner SHALL be rendered

---
