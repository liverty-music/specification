## MODIFIED Requirements

### Requirement: Brand Identity Elements
The system SHALL display proper brand identity elements across the application.

#### Scenario: Page title displays service name
- **WHEN** any page is loaded
- **THEN** the HTML `<title>` SHALL include "Liverty Music" (e.g., "Liverty Music" or "Liverty Music - [Page Name]")
- **AND** the system SHALL NOT display default scaffold or template names (e.g., "Aurelia", "Vite", "React App")

#### Scenario: Favicon and PWA icons
- **WHEN** the application is loaded
- **THEN** the system SHALL display a brand favicon in the browser tab, served as PNG and ICO assets (no SVG favicon is required)
- **AND** the system SHALL provide an `apple-touch-icon` PNG for the iOS home screen
- **AND** the system SHALL provide a web app manifest with themed PNG icons (including a maskable variant) for Android and other PWA-compliant platforms
- **AND** the web app manifest SHALL NOT reference SVG icon assets

#### Scenario: Theme color is consistent across HTML and manifest
- **WHEN** the application is loaded
- **THEN** the `theme-color` declared in the HTML `<head>` meta tag SHALL equal the `theme_color` declared in the web app manifest
