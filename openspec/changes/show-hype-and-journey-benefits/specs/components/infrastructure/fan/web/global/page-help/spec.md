## MODIFIED Requirements

### Requirement: Help seen flags cleared on onboarding reset

The system SHALL clear all per-page help-seen flags, and the per-level flags that record which hype snacks My Artists has shown, when the guest's local data is reset, at sign-in and when sign-up completes, so that contextual help auto-opens and each hype snack appears again for the next session. Tapping [Get Started] on Welcome SHALL NOT clear them.

#### Scenario: Help-seen flags cleared on fresh onboarding

- **WHEN** the guest's local data is reset at sign-in or when sign-up completes
- **THEN** the system SHALL clear all `onboarding.helpSeen:*` keys from localStorage
- **AND** tapping [Get Started] on Welcome SHALL NOT clear them

#### Scenario: Hype snack flags cleared at sign-up

- **WHEN** a guest who saw the hype snack for Away completes sign-up and then sets an artist to Away
- **THEN** the hype snack for Away appears again
