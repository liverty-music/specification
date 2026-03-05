## MODIFIED Requirements

### Requirement: Linear Step Progression

#### Scenario: Step 1 - Artist Discovery completion

- **WHEN** a user is at Step 1 (Artist Discovery / Bubble UI)
- **AND** the user has followed 3 or more artists via bubble taps
- **THEN** the system SHALL activate and highlight the [Generate Dashboard] CTA button at the bottom of the screen
- **AND** when the user taps the CTA, the system SHALL advance `onboardingStep` to 3 (DASHBOARD), skipping Step 2 (LOADING)
- **AND** the system SHALL navigate directly to the Dashboard (`/dashboard`)

> **Delta:** Previously, the CTA advanced `onboardingStep` to 2 (LOADING) and navigated to `/onboarding/loading`. The CTA now skips Step 2 entirely and advances directly to Step 3 (DASHBOARD).

#### Scenario: Step 2 - Loading sequence (deprecated for onboarding)

- **WHEN** a user is at Step 2 (LOADING)
- **THEN** this step is no longer entered during the onboarding flow
- **AND** the `OnboardingStep.LOADING` enum value (2) SHALL be retained for backward compatibility with existing localStorage state
- **AND** if a user has `onboardingStep=2` in localStorage from a prior session, the route guard SHALL redirect them appropriately (to discover if no followed artists, or to dashboard otherwise)

> **Delta:** Previously, Step 2 displayed a 3-second loading animation before advancing to Step 3. This step is no longer part of the onboarding progression. The enum value is kept but never actively entered.
