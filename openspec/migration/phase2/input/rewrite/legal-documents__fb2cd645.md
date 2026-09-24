<!-- spec: legal-documents | target: components/infrastructure/fan/web/route/legal | flags: HISTORIC | new_name: In-app legal links resolve to in-app legal routes -->

### Requirement: In-app legal links resolve to in-app legal routes

In-app references to a legal document (Terms of Service, Privacy Policy, OSS Licenses) — including the onboarding consent notice and the settings screen — SHALL link to the corresponding in-app legal route (`/legal/terms`, `/legal/privacy`, `/legal/licenses`). They SHALL NOT link to an external domain or to a URL that does not resolve (such as `https://liverty.me/privacy`, which does not exist). Because the target is an in-app route, the link SHALL use in-app navigation rather than opening a new browser tab as an external link.

#### Scenario: Consent notice and settings link to the in-app Privacy Policy

- **WHEN** a user activates the Privacy Policy link in the onboarding consent notice or on the settings screen
- **THEN** the application SHALL navigate to the in-app `/legal/privacy` route
- **AND** the link SHALL NOT target the non-existent external `https://liverty.me/privacy` URL
