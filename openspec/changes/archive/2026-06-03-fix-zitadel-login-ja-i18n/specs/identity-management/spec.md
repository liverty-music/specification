## ADDED Requirements

### Requirement: Localize Login UI Text for the Product

The system SHALL ensure the hosted Login UI v2 for the `liverty-music` product application presents its interface text in Japanese for end users whose login language is Japanese, instead of falling back to English. Because Zitadel's built-in hosted-login default translations omit Japanese (so the Settings API returns English for the `ja` locale and that English overrides the login app's bundled Japanese), the system SHALL provision a Zitadel **Hosted Login Translation** override for the `ja` locale, declaratively via the Settings v2 API, carrying the complete Japanese key set.

#### Scenario: Japanese hosted login translation is provisioned

- **WHEN** the Zitadel resources for the `liverty-music` product org are provisioned
- **THEN** a Hosted Login Translation for the `ja` locale SHALL be applied (Settings v2 `SetHostedLoginTranslation`) scoped to the product org
- **AND** it SHALL contain the complete Japanese key set (no key left to English fallback), sourced from the deployed Zitadel login version's Japanese translations

#### Scenario: Japanese login screen renders Japanese

- **WHEN** an end user reaches the hosted login screen (`/ui/v2/login/*`) through the product OIDC flow with a Japanese language preference (browser `accept-language` or the in-login language selector set to 日本語)
- **THEN** the login interface text (titles, labels, buttons) SHALL be displayed in Japanese
- **AND** it SHALL NOT fall back to English

#### Scenario: Other languages and the default are unaffected

- **WHEN** the Japanese override is applied
- **THEN** users with non-Japanese language preferences (e.g. English, German) SHALL continue to see their existing language unchanged
- **AND** the admin/console org login SHALL remain unaffected (the override is scoped to the product org)

#### Scenario: Override is retired once upstream ships Japanese defaults

- **WHEN** a future Zitadel version includes Japanese in its hosted-login default translations
- **THEN** the product MAY remove the Japanese override
- **AND** the Japanese login SHALL still render Japanese from the upstream defaults
