# Hosted Login

## Purpose

Manage identity, authentication, and authorization policies for the Liverty Music platform.

## Requirements

### Requirement: Configure Login Policy

The system SHALL establish a login policy on the **`liverty-music` product
org** (the org that hosts the OIDC application and end-user accounts) that
enforces passwordless authentication to improve user security and
eliminate reliance on passwords. This policy SHALL apply ONLY to the
`liverty-music` product org and MUST NOT be inherited by the `admin` role
org, which has its own admin-oriented login policy governed by separate
requirements.

#### Scenario: Apply Strict Passkeys Policy on product org

- **WHEN** Pulumi stack is applied
- **THEN** the login policy for the `liverty-music` product org SHALL be
  configured
- **AND** `PasswordlessType` SHALL be "ALLOWED"
- **AND** `UserLogin` SHALL be false (Enforces Passkeys-only)
- **AND** `AllowExternalIdp` SHALL be false

#### Scenario: Admin org isolation

- **WHEN** the `liverty-music` product org login policy is applied
- **THEN** the policy SHALL NOT be applied to the `admin` role org
- **AND** the `admin` role org SHALL retain a separate login policy that
  allows external IdP sign-in (see "Configure Admin Org Login Policy")

### Requirement: Configure Login UI Branding

The system SHALL configure Liverty Music brand colors for the hosted Login UI v2 of the `liverty-music` product application, so its login flow presents product branding instead of the default Zitadel appearance. Because Zitadel defines branding only at instance or organization level (there is no application-level label policy), the system SHALL define an org-level label policy on the product org AND enforce it for the product application via the project's private-labeling setting. Branding SHALL be provisioned declaratively via the Zitadel Pulumi provider and activated.

#### Scenario: Brand colors on the product org label policy

- **WHEN** the Zitadel resources for the `liverty-music` product org are provisioned
- **THEN** a label policy SHALL be applied to that org with the Liverty Music brand colors (primary, background, font, warn — including dark variants) sourced from the product's brand palette
- **AND** the policy SHALL set `disableWatermark` so no Zitadel watermark is shown
- **AND** the policy SHALL be activated (set active) so the hosted Login UI v2 renders it

#### Scenario: Enforce product branding per application

- **WHEN** the product `Project` is provisioned
- **THEN** its private-labeling setting SHALL be `ENFORCE_PROJECT_RESOURCE_OWNER_POLICY`
- **AND** the product application's login flow SHALL render the product org's label policy regardless of the logging-in user's organization
- **AND** the separate admin/console org login SHALL remain unaffected (it is a different org)

#### Scenario: Hosted Login UI v2 reflects the brand colors

- **WHEN** an end user reaches the hosted login screen (`/ui/v2/login/*`) through the product OIDC flow
- **THEN** the screen SHALL display the Liverty Music brand colors (buttons, links, background, text)
- **AND** it SHALL NOT display the default unbranded Zitadel colors or watermark

#### Scenario: Light and dark themes are branded

- **WHEN** the login screen is rendered in either light or dark mode
- **THEN** the corresponding brand colors SHALL be applied for that theme

#### Scenario: Logo and login text remain out of scope

- **WHEN** the login branding is applied
- **THEN** only brand colors and theme SHALL be customized
- **AND** no login logo SHALL be set (deferred until a brand logo asset exists)
- **AND** login interface text strings SHALL remain the Zitadel Login UI v2 defaults except where a later capability (Localize Login UI Text for the Product) provisions a translation override

### Requirement: Configure OIDC Token Lifetimes

The system SHALL manage Zitadel instance-level OIDC token lifetimes explicitly via Infrastructure as Code, rather than relying on Zitadel built-in defaults. The configured values SHALL be:

| Setting | Value | Purpose |
|---|---|---|
| `accessTokenLifetime` | `30m` | Short-lived access token limits exposure if leaked; cannot be revoked before expiry once issued. |
| `refreshTokenIdleExpiration` | `30d` | Inactivity window — a refresh token unused for 30 days becomes invalid. |
| `refreshTokenExpiration` | `90d` | Absolute lifetime — after 90 days the user must re-authenticate regardless of activity. |

**Rationale**: A never-miss-a-live notification app benefits from long-lived sessions so fans stay signed in across gaps, while a short access-token lifetime keeps the security exposure window small. Pinning these values in IaC makes the intent durable and reviewable instead of implicitly inheriting whatever Zitadel ships as defaults.

#### Scenario: OIDC token lifetimes provisioned via IaC

- **WHEN** the Zitadel Pulumi stack is applied in an environment
- **THEN** the instance-level OIDC settings SHALL set `accessTokenLifetime` to `30m`
- **AND** SHALL set `refreshTokenIdleExpiration` to `30d`
- **AND** SHALL set `refreshTokenExpiration` to `90d`

#### Scenario: Access token rejected after its lifetime

- **WHEN** an access token is older than `30m`
- **THEN** the backend JWT validation SHALL reject requests bearing that token as expired
- **AND** the client SHALL obtain a fresh access token via the refresh-token grant

#### Scenario: Session ends after refresh token absolute expiry

- **WHEN** a refresh token reaches its `90d` absolute expiration
- **THEN** Zitadel SHALL reject further refresh-token grants for that token
- **AND** the user SHALL be required to re-authenticate

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

### Requirement: A fan signs in with their email as before

The product organization SHALL keep its identities' sign-in names equal to their emails, unique across the identity provider's product and admin organizations, so a fan keeps signing in by typing their email and their passkey shows that email, whatever an Organizer's Organization does with the same email.

#### Scenario: Fan whose email also runs an Organizer

- **WHEN** a fan whose email is also the owner email of an Organizer signs in to the fan app with that email
- **THEN** they sign in to their fan account with its passkey, and the sign-in name shown is their email

### Requirement: Login Screen Follows the Language the App Requests

The hosted login screen SHALL choose its language with one rule: the language the app asked for when it redirected to the hosted login, else the browser's preferred language when the hosted login supports it, else English. A language remembered by the hosted login from an earlier visit (including one picked with the in-login language selector) SHALL NOT win over the language the app asks for. A language the app asks for that the hosted login does not allow SHALL be ignored, and the rest of the rule applies. The rule is the same for every app that sends users to the shared hosted login (fan app, organizer console, admin app).

#### Scenario: App language wins over the browser language

- **WHEN** the app asks for Japanese
- **AND** the browser's preferred language is English
- **THEN** the hosted login screen is in Japanese

#### Scenario: App language wins over a language remembered from an earlier visit

- **WHEN** a user picked English with the in-login language selector on an earlier visit
- **AND** the app now asks for Japanese
- **THEN** the hosted login screen is in Japanese

#### Scenario: No language requested

- **WHEN** the app redirects to the hosted login without asking for a language
- **AND** the browser's preferred language is Japanese
- **THEN** the hosted login screen is in Japanese

#### Scenario: Unsupported browser language and no request

- **WHEN** the app redirects to the hosted login without asking for a language
- **AND** the browser's preferred language is one the hosted login does not offer
- **THEN** the hosted login screen is in English

#### Scenario: App in English on a browser in another supported language

- **WHEN** the fan app, showing English on a browser whose preferred language is German, sends the user to the hosted login
- **THEN** the hosted login screen is in English, matching the app
