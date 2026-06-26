## ADDED Requirements

### Requirement: Final onboarding step is a non-blocking analytics transparency notice
The onboarding flow SHALL present a one-time **analytics transparency notice** as its final step, rather than an opt-in consent gate. Because analytics runs under the EU-adequacy opt-out model (see the `analytics-consent` capability), there is no signup decision to collect; the notice exists to satisfy the APPI purpose-of-use notification obligation in-context and to signal where the user can opt out. The notice SHALL name PostHog (Klant Solutions B.V., Netherlands) and the cross-border purpose, SHALL link to the privacy policy and to the settings opt-out, and SHALL NOT block progression or alter the default-on analytics state. It SHALL be shown at most once and SHALL NOT reappear once acknowledged.

This requirement replaces the previously-planned signup consent screen with two opt-in toggles; that design is superseded by the opt-out model and is not implemented.

#### Scenario: New user sees the transparency notice once and proceeds
- **WHEN** a user reaches the final onboarding step for the first time
- **THEN** the application SHALL render a transparency notice naming PostHog and the cross-border purpose
- **AND** the notice SHALL link to the privacy policy and to the settings opt-out control
- **AND** dismissing or acknowledging the notice SHALL advance to the authenticated experience without changing the default-on analytics state

#### Scenario: Notice does not gate analytics or block onboarding
- **WHEN** the transparency notice is displayed
- **THEN** identified analytics SHALL already be enabled by default (the notice is informational, not a gate)
- **AND** the application SHALL NOT require any affirmative action on the notice before proceeding
- **AND** the application SHALL NOT show the notice again on subsequent sessions once acknowledged

#### Scenario: Opt-out remains reachable after the notice
- **WHEN** a user who saw the notice later wants to stop analytics
- **THEN** the user SHALL be able to reach the analytics opt-out from the settings page without re-onboarding
