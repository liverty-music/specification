## MODIFIED Requirements

### Requirement: Localize Login UI Text for the Product

The system SHALL ensure the hosted Login UI v2 for the `liverty-music` product application renders correctly localized, product-branded interface text: Japanese for end users whose login language is Japanese (never falling back to English), and the product "Liverty Music" branding in the English login/register copy.

As of Zitadel v4.17.0 the built-in hosted-login default translations include Japanese, and `GetHostedLoginTranslation` merges any product-org override **over** those defaults, back-filling keys absent from the override from the system default of the requested locale. Therefore the system SHALL rely on the upstream defaults for Japanese and SHALL NOT provision a Japanese Hosted Login Translation override carrying a pinned Japanese key set; it SHALL provision only a minimal English override that carries the product rebrand.

#### Scenario: Japanese hosted login translation is provisioned

- **WHEN** the Zitadel resources for the `liverty-music` product org are provisioned
- **THEN** the product `ja` Hosted Login Translation override SHALL be provisioned as an **empty** payload (Settings v2 `SetHostedLoginTranslation`), neutralizing any historical pinned override
- **AND** no pinned Japanese key set SHALL be applied, because Zitadel's built-in hosted-login defaults include Japanese as of v4.17.0
- **AND** an empty upsert SHALL be used rather than deleting the resource, because Zitadel exposes no reset/delete API for hosted-login translations and the provider's delete is a no-op

#### Scenario: Japanese login screen renders Japanese

- **WHEN** an end user reaches the hosted login screen (`/ui/v2/login/*`) through the product OIDC flow with a Japanese language preference (browser `accept-language` or the in-login language selector set to 日本語)
- **THEN** the login interface text (titles, labels, buttons) SHALL be displayed in Japanese
- **AND** it SHALL NOT fall back to English

#### Scenario: English login copy carries the product rebrand

- **WHEN** an end user reaches the hosted login/register screen with an English language preference
- **THEN** the product-org override SHALL replace the "Zitadel" wording with "Liverty Music" in the login title and the register description
- **AND** the override SHALL carry only those rebrand keys, every other English key being back-filled from the running Zitadel version's English default

#### Scenario: Other languages and the default are unaffected

- **WHEN** the product-org hosted-login overrides are provisioned
- **THEN** users with other language preferences (e.g. German) SHALL continue to see their existing language unchanged
- **AND** the admin/console org login SHALL remain unaffected (the overrides are scoped to the product org)

#### Scenario: Override is retired once upstream ships Japanese defaults

- **WHEN** the deployed Zitadel version includes Japanese in its hosted-login default translations (v4.17.0+)
- **THEN** the product SHALL NOT carry a pinned Japanese override
- **AND** the Japanese login SHALL still render Japanese from the upstream defaults

#### Scenario: Client recreation runbook covers prod

- **WHEN** the prod OAuth client is accidentally deleted in the Google
  Cloud Console
- **THEN** the cloud-provisioning runbook (`docs/runbooks/zitadel-oauth-client-recreate.md`)
  SHALL document the manual recreation steps for the prod project
  (Internal consent screen → Web application client → prod redirect
  URI → `esc env set liverty-music/prod`)
- **AND** following the runbook SHALL restore the prod admin Google
  sign-in flow without any spec change
