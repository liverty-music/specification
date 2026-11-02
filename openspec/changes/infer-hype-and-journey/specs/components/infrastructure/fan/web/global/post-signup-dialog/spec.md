## ADDED Requirements

### Requirement: Post-signup dialog opens after the celebration

On the post-signup Dashboard redirect, the full (confetti) celebration overlay SHALL be shown before the post-signup dialog. When the celebration overlay is dismissed, the post-signup dialog SHALL open if it has at least one step to show, sequencing the emotional payoff ahead of the setup actions; when it has no step to show, nothing opens after the celebration.

#### Scenario: Dialog opens after celebration dismissal

- **WHEN** a newly signed-up user is redirected to the dashboard
- **AND** the full celebration overlay (per the celebration overlay "Two-Tier Celebration Overlay") is shown
- **AND** the post-signup dialog has at least one step to show
- **THEN** the system SHALL NOT display the post-signup dialog while the celebration overlay is visible
- **AND** the system SHALL display the post-signup dialog once the celebration overlay is dismissed

## REMOVED Requirements

### Requirement: Celebration Precedes Post-Signup Dialog
**Reason**: Replaced by "Post-signup dialog opens after the celebration", which drops the scenario "Region selection still precedes both": every new account has a home area when it is created, so no home-area selection is left to resolve on the Dashboard after sign-up.
**Migration**: None.
