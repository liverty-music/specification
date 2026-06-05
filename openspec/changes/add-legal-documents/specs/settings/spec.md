## MODIFIED Requirements

### Requirement: About Section
The system SHALL provide access to legal and licensing information via in-app routes.

#### Scenario: Legal links
- **WHEN** the About section is displayed
- **THEN** the system SHALL show links to Terms of Service, Privacy Policy, and OSS Licenses
- **AND** each link SHALL target its in-app route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`) rather than an external URL
- **AND** tapping a link SHALL navigate to the corresponding in-app legal document page
