## MODIFIED Requirements

### Requirement: Auto-open on First Page Visit

The system SHALL automatically open the help bottom-sheet on the user's first visit to each page during onboarding.

#### Scenario: First visit to Discovery during onboarding

- **WHEN** the user arrives at the Discovery page for the first time during onboarding
- **AND** `localStorage['onboarding.helpSeen:discovery']` is not set
- **THEN** the help bottom-sheet SHALL open automatically
- **AND** the system SHALL set `localStorage['onboarding.helpSeen:discovery']` to `'1'`

#### Scenario: First visit to My Artists during onboarding

- **WHEN** the user arrives at the My Artists page for the first time during onboarding
- **AND** `localStorage['onboarding.helpSeen:my-artists']` is not set
- **THEN** the help bottom-sheet SHALL open automatically
- **AND** the system SHALL set `localStorage['onboarding.helpSeen:my-artists']` to `'1'`

#### Scenario: Subsequent visits do not auto-open

- **WHEN** the user visits a page where `localStorage['onboarding.helpSeen:<page>']` is already set
- **THEN** the help bottom-sheet SHALL NOT open automatically
- **AND** the user MAY open it manually by tapping the `?` icon

### Requirement: Help seen flags cleared on onboarding reset

The system SHALL clear all per-page help-seen flags when the user restarts onboarding, so that contextual help auto-opens again for the fresh session.

#### Scenario: Help-seen flags cleared on fresh onboarding

- **WHEN** the user starts a fresh onboarding session (taps [Get Started] on Welcome)
- **THEN** the system SHALL clear all `onboarding.helpSeen:*` keys from localStorage
