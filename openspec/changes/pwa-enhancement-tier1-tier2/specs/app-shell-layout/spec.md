## MODIFIED Requirements

### Requirement: Brand Identity Elements
The system SHALL display proper brand identity elements across the application.

#### Scenario: Page title displays service name
- **WHEN** any page is loaded
- **THEN** the HTML `<title>` SHALL include "Liverty Music" (e.g., "Liverty Music" or "Liverty Music - [Page Name]")
- **AND** the system SHALL NOT display default scaffold or template names (e.g., "Aurelia", "Vite", "React App")

#### Scenario: Favicon and PWA icons
- **WHEN** the application is loaded
- **THEN** the system SHALL display a brand favicon in the browser tab
- **AND** the system SHALL provide apple-touch-icon for iOS home screen
- **AND** the system SHALL provide a web app manifest with themed icons (including maskable versions) for Android and other PWA-compliant platforms

#### Scenario: PWA install banner placement
- **WHEN** the PWA install banner is triggered
- **THEN** the banner SHALL render within the app shell's main content area, above the page content
- **AND** the banner SHALL NOT overlap with the bottom navigation bar
- **AND** the banner SHALL use the design system's color tokens and surface palette
