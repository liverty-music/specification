## MODIFIED Requirements

### Requirement: Conditional Navigation Display
The system SHALL conditionally show or hide the navigation bar based on the current route context.

#### Scenario: Navigation hidden during onboarding
- **WHEN** the user is on the Landing Page, Artist Discovery, or Loading Sequence routes
- **THEN** the system SHALL NOT display the top navigation bar
- **AND** the full viewport SHALL be available for the onboarding content

#### Scenario: Navigation shown on dashboard
- **WHEN** the user is on the Dashboard or post-onboarding routes
- **THEN** the system SHALL display a minimal, dark-themed navigation bar
- **AND** the navigation bar SHALL include the service logo and user account controls

#### Scenario: Navigation remains visible beneath area setup dialog
- **WHEN** the first-visit area setup dialog is displayed on the Dashboard
- **THEN** the area setup dialog SHALL render via `<dialog>` `showModal()` in the browser's Top Layer
- **AND** the bottom navigation bar SHALL remain in its normal position beneath the Top Layer
- **AND** the dialog SHALL NOT use z-index utilities to compete with the navigation bar's stacking context
- **AND** the `::backdrop` pseudo-element SHALL visually dim the entire page including the navigation bar
