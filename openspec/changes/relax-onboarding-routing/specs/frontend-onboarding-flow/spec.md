## MODIFIED Requirements

### Requirement: Step Sequence

The onboarding step sequence SHALL be LP → DISCOVERY → DASHBOARD → MY_ARTISTS → COMPLETED. The DETAIL step is removed. The DASHBOARD step SHALL complete on dashboard arrival (no Lane Intro sequence), and the MY_ARTISTS step SHALL complete on My Artists arrival (no hype-change requirement).

#### Scenario: Step sequence excludes DETAIL

- **WHEN** `onboardingStep` is `'dashboard'`
- **AND** the Dashboard page is attached
- **THEN** the system SHALL advance `onboardingStep` to `'my-artists'`
- **AND** the system SHALL NOT pass through any intermediate `'detail'` step

#### Scenario: My Artists arrival completes onboarding

- **WHEN** `onboardingStep` is `'my-artists'`
- **AND** the My Artists page is attached (the user has navigated to it)
- **THEN** the system SHALL advance `onboardingStep` to `'completed'`
- **AND** completion SHALL NOT require the user to change a hype level

#### Scenario: Legacy localStorage value migration

- **WHEN** the system reads `liverty:onboardingStep` from localStorage
- **AND** the stored value is `'detail'`
- **THEN** the system SHALL treat it as `'dashboard'` for routing and step logic
