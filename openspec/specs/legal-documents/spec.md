# Legal Documents

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

### Requirement: Privacy Policy discloses the actual data practices

The Privacy Policy SHALL accurately disclose, at minimum: the categories of personal data collected; the purposes of use; third-party processors and any cross-border transfer; how to withdraw analytics consent; and the contact channel for disclosure / correction / deletion requests. The disclosure SHALL reflect the system's real integrations and SHALL be revised when a new third-party data integration is added.

For cross-border transfers, the Privacy Policy SHALL name each third-party recipient that receives personal data in a foreign country — including PostHog (operated by Klant Solutions B.V., Netherlands), to which usage analytics data is transferred (PostHog Cloud EU) — and SHALL, for that transfer, state the recipient's country (Netherlands), enumerate the categories of data transferred (interaction / usage events captured via cookies and localStorage), and state the purpose of the transfer (product analytics: improving the Service and measuring effectiveness). Whether any particular wording legally suffices under APPI Article 28 is a matter for the policy owner / legal counsel to confirm and is out of scope for this spec.

#### Scenario: Collected data and purposes are stated

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL list the collected personal data categories (account identity, home area, follows, language preference, push subscription, analytics events) and the purpose of each use

#### Scenario: Third-party transfer and cross-border processing are disclosed

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL identify third-party recipients / processors (analytics, email, push, search, artist-metadata)
- **AND** it SHALL disclose the cross-border transfer of analytics data to PostHog Cloud EU

#### Scenario: PostHog is named as a cross-border recipient with country, categories, and purpose

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL name PostHog (operated by Klant Solutions B.V.) as the recipient of a cross-border transfer of usage analytics data
- **AND** it SHALL state the recipient's country (Netherlands)
- **AND** it SHALL enumerate the categories of data transferred to PostHog (interaction / usage events captured via cookies and localStorage)
- **AND** it SHALL state the purpose of that transfer (product analytics: improving the Service and measuring effectiveness)

#### Scenario: Consent withdrawal and rights are explained

- **WHEN** the Privacy Policy is displayed
- **THEN** it SHALL explain that analytics consent can be withdrawn via the Settings privacy toggles
- **AND** it SHALL provide a contact channel for disclosure / correction / deletion requests

### Requirement: Terms of Service disclaims third-party data accuracy

The Terms of Service SHALL include, at minimum: the service description, account and prohibited-conduct terms, a disclaimer that third-party-sourced concert / ticket / sales information is not guaranteed accurate or current, limitation of liability, and governing law / jurisdiction.

#### Scenario: Third-party data disclaimer present

- **WHEN** the Terms of Service is displayed
- **THEN** it SHALL state that concert, ticket, and sales-timing information originates from third parties and is provided without a guarantee of accuracy or timeliness

### Requirement: OSS Licenses content is generated from the shipped dependencies

The OSS Licenses page content SHALL be generated at build time from the production dependency tree, listing each bundled third-party package with its license and required attribution, so that the displayed list reflects what is actually distributed and does not require manual maintenance.

#### Scenario: License list reflects the production bundle

- **WHEN** the OSS Licenses page is displayed
- **THEN** it SHALL list the third-party packages included in the production build with their license names and attribution / copyright notices

#### Scenario: List regenerates on dependency change

- **WHEN** the production dependency set changes and the app is rebuilt
- **THEN** the OSS Licenses content SHALL regenerate to match the new dependency set

### Requirement: In-app legal links resolve to in-app legal routes

In-app references to a legal document (Terms of Service, Privacy Policy, OSS Licenses) — including the onboarding consent notice and the settings screen — SHALL link to the corresponding in-app legal route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`). They SHALL NOT link to an external domain or to a URL that does not resolve (such as `https://liverty.me/privacy`, which does not exist). Because the target is an in-app route, the link SHALL use in-app navigation rather than opening a new browser tab as an external link.

#### Scenario: Consent notice and settings link to the in-app Privacy Policy

- **WHEN** a user activates the Privacy Policy link in the onboarding consent notice or on the settings screen
- **THEN** the application SHALL navigate to the in-app `/legal/privacy` route
- **AND** the link SHALL NOT target the non-existent external `https://liverty.me/privacy` URL

