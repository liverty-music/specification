# Hosted Login

## Purpose

Manage identity, authentication, and authorization policies for the Liverty Music platform.

## Requirements

### Requirement: Configure Login Policy

The system SHALL establish a login policy on the **`liverty-music` product
org** (the org that hosts the OIDC application and end-user accounts) that
makes passkeys the only sign-in credential for every fan other than the automated end-to-end test fans. This policy SHALL apply ONLY to the
`liverty-music` product org and MUST NOT be inherited by the `admin` role
org, which has its own admin-oriented login policy governed by separate
requirements.

Passkey-only is expressed by allowing passwordless sign-in and never issuing
a fan a password, NOT by disabling local authentication: `UserLogin` gates all
local authentication (email plus passkey or password), and with it off the
hosted login renders no usable form. The product SHALL offer fans no password
sign-up and no password reset (see "The hosted login offers no way to set a
password"). The only identities in the product org with a password are the
automated end-to-end test fans, in every environment that runs them,
production included; they sign in with that password. No request a fan
makes to the Zitadel API SHALL set a password on their identity; only
provisioning sets the end-to-end test fans' passwords.

#### Scenario: Apply Strict Passkeys Policy on product org

- **WHEN** Pulumi stack is applied
- **THEN** the login policy for the `liverty-music` product org SHALL be
  configured
- **AND** `PasswordlessType` SHALL be "ALLOWED"
- **AND** `UserLogin` SHALL be true, because it also gates passkey sign-in
- **AND** `HidePasswordReset` SHALL be true
- **AND** `AllowExternalIdp` SHALL be false

#### Scenario: Admin org isolation

- **WHEN** the `liverty-music` product org login policy is applied
- **THEN** the policy SHALL NOT be applied to the `admin` role org
- **AND** the `admin` role org SHALL retain a separate login policy that
  allows external IdP sign-in (see "Configure Admin Org Login Policy")

#### Scenario: Fan sets a password through the Zitadel API

- **WHEN** a signed-in fan asks the Zitadel API to set, change or reset the password of their own identity, as the Zitadel Console's self-service page does
- **THEN** the request is refused and no password is set
- **AND** provisioning still sets the end-to-end test fans' passwords

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

### Requirement: Fans have a recovery path for lost passkeys

A fan account SHALL never depend on a single passkey with no way back in. A fan SHALL be able to register more than one passkey, and a fan who can use none of them SHALL be able to register a new one through an emailed link sent to the account's verified address (see the passkey recovery screen). Synced passkeys survive the loss of one device, so a second hardware authenticator is NOT required.

#### Scenario: Fan lost every passkey

- **WHEN** a fan with a verified address can use none of their passkeys
- **THEN** they can request a link from the passkey recovery screen, register a new passkey with it and sign in to the same account

### Requirement: The hosted login registers a passkey from a registration link

When a person opens a passkey registration link within its 1-hour validity, the hosted login SHALL let them create a passkey for the identity the link was sent for without signing in first, and SHALL then send them to the fan app, where they sign in with the new passkey. A link that is expired or was already used SHALL register nothing, and the person SHALL be able to request a new link from the passkey recovery screen.

#### Scenario: Valid link

- **WHEN** a fan opens a 10-minute-old registration link on a laptop and confirms a new passkey
- **THEN** the passkey is registered for their identity, they arrive in the fan app and can sign in with that passkey

#### Scenario: Cancelled passkey prompt

- **WHEN** the fan cancels the device's passkey prompt on the link's page
- **THEN** no passkey is registered and the link cannot be used again; the fan requests a new link

### Requirement: A signed-in fan adds a passkey on the device in hand

When the fan app sends a fan who signed in within the last 5 minutes to add a passkey, the hosted login SHALL create a new passkey for that fan's identity on the device in hand, keep the fan's other passkeys, and return the fan to the fan app. A passkey already registered on the same passkey provider SHALL NOT be registered twice.

#### Scenario: Second device

- **WHEN** a fan who signed in on a Windows laptop with their phone's passkey adds a passkey there
- **THEN** the identity has a passkey on the laptop's passkey provider as well as the phone's, and the fan returns to the fan app

#### Scenario: Same provider again

- **WHEN** the fan tries to add a passkey on a provider that already holds one of theirs
- **THEN** no second passkey is created there

### Requirement: The hosted login offers no way to set a password

No page of the hosted login SHALL let a person set a password on an identity:
not on sign-up, not when choosing which credential to set up, not through a
reset code, and not by changing a password after signing in. A page that
would set a password SHALL instead show the hosted login's not-found page,
whether it is reached by a link or by typing its address. A request that
reaches the hosted login's server without going through those pages SHALL be
refused in the same way, so no request to the hosted login sets a password.
An identity that already has a password SHALL still sign in with it.

#### Scenario: Sign-up offers only a passkey

- **WHEN** a person opens the hosted login's sign-up page from the fan app and fills in their name and email
- **THEN** the page offers no Password choice, and continuing takes them to passkey registration

#### Scenario: Choosing a credential to set up offers no password

- **WHEN** the hosted login asks a person which credential to set up for their identity
- **THEN** Passkey is offered and Password is not

#### Scenario: Password pages opened by address

- **WHEN** a person opens the sign-up password step, the set-password page or the change-password page by typing its address, with or without a reset code
- **THEN** the hosted login shows its not-found page and no password is set

#### Scenario: Password sent to the hosted login without its pages

- **WHEN** a request carrying a new password is sent to the hosted login's server directly, for sign-up, a reset code or a signed-in session, without opening any of its pages
- **THEN** the hosted login refuses it and no password is set

#### Scenario: No password reset on the password page

- **WHEN** a person reaches the hosted login's password page
- **THEN** it offers no way to request a password reset

#### Scenario: Existing password still signs in

- **WHEN** an automated end-to-end test fan signs in with their email and password
- **THEN** sign-in succeeds as before
