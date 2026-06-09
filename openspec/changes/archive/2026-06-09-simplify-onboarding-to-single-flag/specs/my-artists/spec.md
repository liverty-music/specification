## MODIFIED Requirements

### Requirement: Hype Change Persisted for Guest Users

The system SHALL persist hype changes made by guest users to localStorage without reverting them, and SHALL keep hype editing fully decoupled from onboarding state. Changing a hype level SHALL NOT advance, complete, or otherwise mutate onboarding state, and a repeated hype change (second tap onward) SHALL always apply.

#### Scenario: Guest user changes hype during onboarding

- **WHEN** a guest user changes a hype level while `OnboardingService.isOnboarding` is `true`
- **AND** the user is not authenticated
- **THEN** the system SHALL persist the hype value in `GuestService` under `liverty:guest:hypes`
- **AND** the system SHALL NOT revert the hype change in the UI
- **AND** the system SHALL NOT mutate onboarding state (no step advance, no completion)
- **AND** the signup-prompt-banner SHALL already have been visible (per the `Signup Banner on My Artists` requirement in the `signup-prompt-banner` capability); no additional banner-visibility mutation is required by this change handler

#### Scenario: Repeated hype change applies every time

- **WHEN** a guest user changes a hype level
- **AND** then changes a hype level a second (or subsequent) time on the same or another artist
- **THEN** every change SHALL apply and persist
- **AND** no change SHALL be reverted due to onboarding state

#### Scenario: Guest user changes hype after onboarding completion

- **WHEN** a guest user (onboarding completed) changes a hype level on the My Artists page
- **THEN** the system SHALL persist the hype value in `GuestService`
- **AND** the system SHALL NOT show a modal dialog
- **AND** the signup-prompt-banner SHALL remain visible (non-modal, persistent per its own capability spec)
