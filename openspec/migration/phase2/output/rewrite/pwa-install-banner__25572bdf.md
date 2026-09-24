<!-- spec: pwa-install-banner | target: components/infrastructure/fan/web/global/pwa-install-banner | flags: CLASSNAME | new_name: Banner Suppressed While PostSignupDialog Is Open -->

### Requirement: Banner Suppressed While Post-Signup Dialog Is Open

The banner SHALL NOT be visible while the post-signup dialog is open to avoid visual conflict at the bottom of the screen.

#### Scenario: Post-signup dialog open — banner hidden

- **WHEN** the post-signup dialog is open
- **THEN** the system SHALL suppress the banner
- **AND** the banner SHALL NOT be rendered in the DOM

#### Scenario: Post-signup dialog closed — banner visible

- **WHEN** the post-signup dialog is closed (user taps Later/Close)
- **AND** the system determines the install banner should be shown
- **AND** session-dismiss flag is NOT set
- **THEN** the banner SHALL be rendered
