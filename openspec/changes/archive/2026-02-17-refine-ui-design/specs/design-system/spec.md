## ADDED Requirements

### Requirement: Dark Theme as Default
The system SHALL apply a dark-first visual theme consistently across all screens and components.

#### Scenario: Dark background applied globally
- **WHEN** any screen is rendered
- **THEN** the body background SHALL use a dark gradient or solid dark color from the surface token palette
- **AND** primary text SHALL be white or light gray (meeting WCAG AA contrast ratio against the dark background)

#### Scenario: Dark theme consistency across onboarding
- **WHEN** the user navigates from Landing Page → Artist Discovery → Loading → Dashboard
- **THEN** all screens SHALL use the same dark surface palette
- **AND** there SHALL be no jarring light-to-dark or dark-to-light transitions between screens
