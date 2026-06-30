# legal-documents

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: In-app legal links resolve to in-app legal routes

In-app references to a legal document (Terms of Service, Privacy Policy, OSS Licenses) — including the onboarding consent notice and the settings screen — SHALL link to the corresponding in-app legal route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`). They SHALL NOT link to an external domain or to a URL that does not resolve (such as `https://liverty.me/privacy`, which does not exist). Because the target is an in-app route, the link SHALL use in-app navigation rather than opening a new browser tab as an external link.

#### Scenario: Consent notice and settings link to the in-app Privacy Policy

- **WHEN** a user activates the Privacy Policy link in the onboarding consent notice or on the settings screen
- **THEN** the application SHALL navigate to the in-app `/legal/privacy` route
- **AND** the link SHALL NOT target the non-existent external `https://liverty.me/privacy` URL
