## ADDED Requirements

### Requirement: Celebration Precedes Post-Signup Dialog

On the post-signup dashboard redirect, the full (confetti) celebration overlay SHALL be shown before the PostSignupDialog. The PostSignupDialog SHALL open when the celebration overlay is dismissed, sequencing the emotional payoff ahead of the functional setup actions.

#### Scenario: Dialog opens after celebration dismissal

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** the full celebration overlay (per `onboarding-celebration` "Two-Tier Celebration Overlay") is shown
- **THEN** the system SHALL NOT display the PostSignupDialog while the celebration overlay is visible
- **AND** the system SHALL display the PostSignupDialog once the celebration overlay is dismissed

#### Scenario: Region selection still precedes both

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** `needsRegion` is `true`
- **THEN** the system SHALL resolve the home-area selection first
- **AND** only then evaluate the celebration overlay, followed by the PostSignupDialog on dismissal
