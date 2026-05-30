## MODIFIED Requirements

### Requirement: Step Sequence

The onboarding step sequence SHALL be LP → DISCOVERY → DASHBOARD → MY_ARTISTS → … → COMPLETED. The DETAIL step is removed. The DASHBOARD step SHALL complete on dashboard arrival (no Lane Intro sequence). The MY_ARTISTS → COMPLETED transition is out of scope for this change (owned by the consent-step flow).

#### Scenario: Step sequence excludes DETAIL

- **WHEN** `onboardingStep` is `'dashboard'`
- **AND** the Dashboard page is attached
- **THEN** the system SHALL advance `onboardingStep` to `'my-artists'`
- **AND** the system SHALL NOT pass through any intermediate `'detail'` step

#### Scenario: Legacy localStorage value migration

- **WHEN** the system reads `liverty:onboardingStep` from localStorage
- **AND** the stored value is `'detail'`
- **THEN** the system SHALL treat it as `'dashboard'` for routing and step logic
