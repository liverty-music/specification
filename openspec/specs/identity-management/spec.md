# Identity Management

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

### Requirement: SMTP Configuration Must Be Activated After Creation

The system SHALL invoke the Zitadel admin API `POST /admin/v1/smtp/{id}/_activate` after creating a `SmtpConfig` resource via a **Pulumi Dynamic Resource (`ZitadelSmtpActivation`)** that fires as a declarative dependency of the `SmtpConfig` resource, because Zitadel v4 ships new SMTP configurations in `SMTP_CONFIG_INACTIVE` state and the `@pulumiverse/zitadel.SmtpConfig` resource does not flip the activation flag. The activation SHALL additionally be **self-healing**: the resource's `read` handler SHALL query the live SMTP config's activation state, so that a runtime loss of activation (an instance rebuild/reset, or an out-of-band deactivation, that does not change the resource's Pulumi inputs) is surfaced as drift and re-activated on the next refreshing `pulumi up`, without an input change or a manual step.

**Rationale**: An inactive SMTP config silently swallows all outbound notification events. Verification emails, password-reset emails, passkey-registration links, and admin notifications are queued but never delivered to the SMTP provider. The failure mode is invisible — the send API returns success, the notification worker logs nothing, and the user-facing UX is "no email arrived." The original implementation activated once at create time but treated every later reconcile as a no-op (no `read`, no re-check), so once the live activation drifted the outage was permanent and undetectable. This was observed in prod: `SendPasswordlessRegistration` succeeded yet Postmark received zero sends. The contract is therefore strengthened from "activate once" to "activate and keep active."

#### Scenario: Newly provisioned SMTP config is activated automatically

- **WHEN** Pulumi provisions a `SmtpConfig` resource on a fresh Zitadel instance
- **THEN** the `ZitadelSmtpActivation` Dynamic Resource SHALL call `POST /admin/v1/smtp/{id}/_activate` as part of the same `pulumi up`
- **AND** the resulting state SHALL be `SMTP_CONFIG_ACTIVE`
- **AND** subsequent verification emails SHALL be queued AND delivered to the SMTP provider

#### Scenario: First apply against an already-active SMTP succeeds (create-time idempotency)

- **WHEN** Pulumi runs `create()` for `ZitadelSmtpActivation` against an SMTP config that is already in `SMTP_CONFIG_ACTIVE` state (e.g., activated out-of-band prior to this resource being added to the stack)
- **THEN** the `_activate` POST SHALL return Zitadel's "already active" response shape
- **AND** `create()` SHALL treat that response as success
- **AND** the resource SHALL be recorded in Pulumi state with a fresh `activatedAt` timestamp

#### Scenario: Refresh detects a drifted (inactive) SMTP and re-activation heals it

- **WHEN** the live SMTP config has drifted to a non-active state (e.g., after an instance rebuild/reset or an out-of-band deactivation) while the `ZitadelSmtpActivation` resource's Pulumi inputs are unchanged
- **AND** an operator runs a refreshing `pulumi up` (`pulumi up --refresh`, or a stack whose deployment refreshes)
- **THEN** the `read` handler SHALL query the live activation state and report the resource as out-of-date (drifted)
- **AND** the ensuing `pulumi up` SHALL re-invoke `_activate` so the config returns to `SMTP_CONFIG_ACTIVE`
- **AND** no manual `curl`/`gcloud` step and no input change SHALL be required to heal it

#### Scenario: Re-apply with unchanged inputs is a Pulumi-graph no-op

- **WHEN** Pulumi re-applies the stack **without a refresh** and the `ZitadelSmtpActivation` resource's inputs (`smtpConfigId`, `domain`, `jwtProfileJson`) are unchanged from the previous apply
- **THEN** Pulumi's input diff SHALL be empty
- **AND** no lifecycle handler (`create` / `update` / `delete` / `read`) on `ZitadelSmtpActivation` SHALL be invoked (drift detection is the refreshing-apply path above)
- **AND** zero HTTP traffic SHALL be generated against the Zitadel admin API
- **AND** the Pulumi state graph SHALL continue to record the resource as up-to-date

#### Scenario: Activation runs on a fresh Zitadel rebuild without operator intervention

- **WHEN** the dev (or staging / prod) Zitadel instance is destroyed and recreated from scratch
- **AND** Pulumi runs `pulumi up` against the recreated instance
- **THEN** the `SmtpConfig` resource SHALL be recreated
- **AND** the `ZitadelSmtpActivation` resource SHALL fire `_activate` automatically as the next step in the dependency graph
- **AND** the operator SHALL NOT need to run any manual `curl` or `gcloud` step
- **AND** the first user sign-up after the rebuild SHALL receive a verification email

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
