# Legal

## Purpose

Defines the in-app Terms of Service, Privacy Policy, and OSS Licenses pages: their stable routes, guest reachability, ja/en localization, the required disclosure content for each document, and the build-time auto-generation of the OSS license list.

## Requirements

### Requirement: Legal documents are served as in-app routes with stable URLs

The system SHALL serve the Terms of Service, Privacy Policy, and OSS Licenses each as a dedicated in-app route with its own stable URL (`/legal/terms`, `/legal/privacy`, `/legal/licenses`). These documents SHALL NOT be served only as modal dialogs or external links, so that each has a URL usable as the App Store Connect / Google Play Privacy Policy URL and for deep linking.

#### Scenario: Each document has its own route

- **WHEN** a user navigates to `/legal/terms`, `/legal/privacy`, or `/legal/licenses`
- **THEN** the system SHALL render the corresponding document as a full page at that URL

#### Scenario: Privacy Policy URL is externally linkable

- **WHEN** the Privacy Policy URL is opened directly (e.g. by a store reviewer or from a store listing)
- **THEN** the page SHALL load and display the Privacy Policy without requiring prior in-app navigation

### Requirement: Legal documents are reachable without authentication

The `/legal/*` routes SHALL be reachable by unauthenticated and guest users, registered as public routes that opt out of the authentication guard.

#### Scenario: Guest opens a legal document

- **WHEN** an unauthenticated user navigates to a `/legal/*` route
- **THEN** the system SHALL render the document
- **AND** the authentication guard SHALL NOT redirect the user away

### Requirement: Legal documents are localized

Each legal document SHALL be available in Japanese and English, following the application's active locale and existing i18n mechanism. Japanese is the primary locale for the legal content.

#### Scenario: Document follows the active locale

- **WHEN** a legal document is displayed while the active locale is Japanese (or English)
- **THEN** the document content SHALL render in that locale

### Requirement: In-app legal links resolve to in-app legal routes

In-app references to a legal document (Terms of Service, Privacy Policy, OSS Licenses) — including the onboarding consent notice and the settings screen — SHALL link to the corresponding in-app legal route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`). Because the target is an in-app route, the link SHALL use in-app navigation rather than opening a new browser tab as an external link.

#### Scenario: Consent notice and settings link to the in-app Privacy Policy

- **WHEN** a user activates the Privacy Policy link in the onboarding consent notice or on the settings screen
- **THEN** the application SHALL navigate to the in-app `/legal/privacy` route
