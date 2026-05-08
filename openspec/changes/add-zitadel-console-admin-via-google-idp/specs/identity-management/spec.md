## MODIFIED Requirements

### Requirement: Manage Zitadel Organization

The system SHALL manage Zitadel organization topology via Infrastructure as
Code so that the instance always exposes a clear separation between
operator (admin) and product identities. The instance SHALL contain
exactly two top-level organizations:

- An **`admin`** role org, created by Zitadel at first-instance bootstrap
  via the configmap setting `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`,
  brought into Pulumi state via a one-time `pulumi import
  zitadel:index/org:Org admin <admin-org-id>` (see Migration Plan in
  design.md), and pinned with `protect: true`. This org holds operator
  identities only (machine users used by IaC and the Login V2 service,
  plus human admins who manage the instance) and is the **Zitadel
  default org** so that the Console (which omits `org_id` in its OIDC
  AuthN) routes to its `LoginPolicy`.

- A **`liverty-music`** product org, created by Pulumi as a `zitadel.Org`
  resource with `isDefault: false`. This org holds the product Project,
  applications, end-user login policy, and end-user accounts. The
  frontend SPA's `ApplicationOidc` carries an explicit `client_id`
  whose owning org Zitadel resolves to `liverty-music`, so the
  default-org choice does not affect end-user OIDC routing.

#### Scenario: Provision admin role org via bootstrap + import

- **WHEN** the Zitadel instance bootstraps for the first time in any
  environment
- **THEN** the configmap SHALL set `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`
- **AND** Zitadel SHALL create an organization named `admin` containing
  the `pulumi-admin` machine user
- **AND** an operator SHALL run `pulumi import zitadel:index/org:Org
  admin <admin-org-id>` (with `--provider liverty-music-provider=...`)
  to bring the admin org into Pulumi state
- **AND** the Pulumi declaration SHALL set `isDefault: true` and
  `{ protect: true }` on the admin org
- **AND** no Pulumi rename step SHALL be required to reach the intended
  name

#### Scenario: Provision product org via Pulumi

- **WHEN** Pulumi stack is applied
- **THEN** a `zitadel.Org` resource named `liverty-music` SHALL exist
  with `isDefault: false`
- **AND** all product resources (Project, ApplicationOidc, end-user
  LoginPolicy, end-user HumanUsers) SHALL live in this org

#### Scenario: Console login routes to the admin org's policy

- **WHEN** an operator opens
  `https://auth.dev.liverty-music.app/ui/console`
- **THEN** the Zitadel Console's OIDC AuthN SHALL hit Login V2 without
  an explicit `org_id`
- **AND** Login V2 SHALL render the **default org's `LoginPolicy`**,
  which is the admin org's policy (Google IdP enabled,
  `userLogin = false`)
- **AND** the operator SHALL see a "Sign in with Google" button
  immediately, without needing to type a username first

#### Scenario: No third org

- **WHEN** the instance is fully provisioned
- **THEN** exactly two orgs SHALL exist (`admin` and `liverty-music`)
- **AND** any additional org found via `POST /admin/v1/orgs/_search` SHALL
  be treated as drift and reverted on the next Pulumi apply

#### Scenario: Admin org cannot be accidentally destroyed

- **WHEN** any operator runs `pulumi destroy` against the dev stack
- **THEN** Pulumi SHALL refuse to remove the `admin` org because of
  `protect: true`
- **AND** removing the protection SHALL require a code change in a
  reviewable PR
- **AND** this protection SHALL prevent the cascading loss of the
  `pulumi-admin` machine user, which would lock the
  `@pulumiverse/zitadel` provider out of the instance

### Requirement: Manage Zitadel Project

The system SHALL manage the `liverty-music` project within the
**`liverty-music` product org** to group product-related resources. The
project SHALL NOT live in the `admin` role org.

#### Scenario: Provision Project in product org

- **WHEN** Pulumi stack is applied
- **THEN** a project named `liverty-music` SHALL exist in the
  `liverty-music` product org

### Requirement: Manage OIDC Application

The system SHALL manage the OIDC application for the frontend SPA within
the `liverty-music` project (in the `liverty-music` product org) to enable
end-user authentication.

#### Scenario: Provision OIDC App in product org

- **WHEN** Pulumi stack is applied
- **THEN** an OIDC application named `liverty-music` SHALL exist in the
  `liverty-music` project
- **AND** the application Type SHALL be "SPA"
- **AND** the Auth Method Type SHALL be "NONE"
- **AND** the application's `client_id` SHALL be exported through Pulumi
  ESC for the frontend stack to consume

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

### Requirement: Auto-Verify Email on Self-Registration

The system SHALL automatically mark a user's email as verified before
account creation during Zitadel Self-Registration in the `liverty-music`
product org, via a Zitadel Action on the
`INTERNAL_AUTHENTICATION / PRE_CREATION` flow that calls
`api.setEmailVerified(true)`.

**Rationale**: Zitadel's Hosted Login blocks the OIDC authorization flow
with an OTP step when SMTP is configured and email is unverified. Setting
email as verified before creation skips this step, allowing the OIDC flow
to complete immediately after passkey registration. The `LoginPolicy`
resource does not expose an email verification toggle.

#### Scenario: New end user registers via Self-Registration

- **WHEN** a new end user completes Self-Registration (email + passkey) in
  the `liverty-music` product org
- **THEN** the `PRE_CREATION` Zitadel Action SHALL call
  `api.setEmailVerified(true)` before user creation
- **AND** the user SHALL be created with email already verified
- **AND** the OIDC authorization flow SHALL complete without an OTP step
- **AND** the user SHALL be redirected to `/auth/callback` immediately

#### Scenario: Action failure in production

- **WHEN** the auto-verify Action fails in staging or production
- **THEN** the registration flow SHALL fail (`allowedToFail: false`)
- **AND** the error SHALL be logged for investigation

#### Scenario: Action failure in development

- **WHEN** the auto-verify Action fails in the dev environment
- **THEN** the registration flow SHALL continue (`allowedToFail: true`)
- **AND** the user MAY see the OTP step as a fallback

## ADDED Requirements

### Requirement: Configure Admin Org Login Policy

The system SHALL configure a `LoginPolicy` on the `admin` role org that
permits external IdP sign-in via the admin Google IdP, disables
username + password sign-in (so the random initial password set on the
human admin is unreachable), and disallows self-registration. IdP-level
linking settings (configured on the Google IdP itself, see "Provision
Google IdP for Admin Sign-in") govern the actual auto-link-by-email
behaviour. The system SHALL also configure the `DefaultLoginPolicy`
(instance-level) consistently so that Console login behaviour does not
depend on Login V2's choice of routing path.

#### Scenario: Apply admin org login policy

- **WHEN** Pulumi stack is applied
- **THEN** the `admin` role org SHALL have a `LoginPolicy` with
  `allowExternalIdp = true`
- **AND** the policy `idps` array SHALL include the id of the admin Google
  IdP
- **AND** the policy `userLogin` SHALL be `false` (disables
  username + password sign-in form)
- **AND** the policy SHALL NOT enable self-registration
  (`allowRegister = false`) so that no anonymous Google identity becomes
  a Zitadel user without explicit Pulumi provisioning

#### Scenario: DefaultLoginPolicy mirrors admin org policy for Console fallback

- **WHEN** Pulumi stack is applied
- **THEN** the IAM-level `DefaultLoginPolicy` SHALL also enable external
  IdP with the admin Google IdP and disallow self-registration
- **AND** the product org's explicit `LoginPolicy` override SHALL take
  precedence for product-org login flows, leaving end-user passkey-only
  behaviour intact

#### Scenario: Admin org enables domain discovery routing

- **WHEN** Pulumi stack is applied
- **THEN** the `admin` role org's `LoginPolicy` SHALL set
  `allowDomainDiscovery = true`
- **AND** when a user types an email address whose domain matches an
  organisation domain registered against the `admin` org, Login V2 SHALL
  resolve to the `admin` org's policy

**Implementation note**: claiming an externally-owned domain like
`pannpers.dev` as a verified Zitadel organisation domain requires DNS-based
proof, which adds friction without functional benefit for a single-admin
setup. This change does NOT register `pannpers.dev` as a verified domain;
the human admin signs in by clicking the "Sign in with Google" IdP button
on the Login V2 UI directly, which routes to the `admin` org via the
DefaultLoginPolicy fallback path. Domain-discovery routing remains
configured (`allowDomainDiscovery = true`) so that a future explicit
verified-domain registration just works.

### Requirement: Provision Google IdP for Admin Sign-in

The system SHALL provision a Google OAuth 2.0 Identity Provider at the
Zitadel **instance** level so that operators can sign in to the Admin
Console using their Google Workspace account. The IdP SHALL be managed via
Pulumi as `zitadel.IdpGoogle` (instance-scoped) and SHALL NOT be created
at the product org level.

#### Scenario: Provision instance-level Google IdP

- **WHEN** Pulumi stack is applied
- **THEN** an `IdpGoogle` resource SHALL exist at the Zitadel instance
  level
- **AND** its `clientId` and `clientSecret` SHALL be sourced from Pulumi
  ESC keys `pulumiConfig.zitadel.googleAdminIdp.clientId` and
  `pulumiConfig.zitadel.googleAdminIdp.clientSecret`
- **AND** the IdP SHALL be referenceable by the `admin` org's
  `LoginPolicy`
- **AND** the IdP SHALL NOT be referenced by the `liverty-music` product
  org's `LoginPolicy`
- **AND** the IdP SHALL set `isLinkingAllowed = true` so that successful
  Google sign-in links to a pre-provisioned local human user with the
  matching verified email
- **AND** the IdP SHALL set `isCreationAllowed = false` and
  `isAutoCreation = false` so that no anonymous Google identity becomes a
  Zitadel user without explicit Pulumi provisioning
- **AND** the IdP `scopes` SHALL request at minimum `openid`, `profile`,
  `email`

#### Scenario: Rotate Google OAuth client secret

- **WHEN** the `pulumiConfig.zitadel.googleAdminIdp.clientSecret` ESC value
  is updated and Pulumi stack is applied
- **THEN** the `IdpGoogle` resource SHALL be updated with the new secret
- **AND** existing admin sessions SHALL remain valid until they expire
  naturally
- **AND** new sign-in attempts SHALL succeed using the rotated secret

### Requirement: Provision Human Admin User in Admin Role Org

The system SHALL provision a human admin user in the `admin` role org via
Pulumi as a `HumanUser` resource. The user SHALL rely exclusively on
linked external IdP sign-in for actual authentication; password-based
local login SHALL be disabled at the org policy level
(`LoginPolicy.userLogin = false` on the `admin` org). The user's email
SHALL be marked verified at creation time so that the IdP-linking flow
proceeds without an OTP step.

**Implementation note**: Zitadel requires a password to be present on the
user before the email can be marked verified at creation time
(documented in the `@pulumiverse/zitadel` `HumanUser` resource caution).
A random, never-disclosed `initialPassword` SHALL be set at creation to
satisfy this constraint. The password is unusable in practice because the
admin org's `LoginPolicy.userLogin = false` disables the username +
password sign-in form entirely.

#### Scenario: Provision Human Admin

- **WHEN** Pulumi stack is applied
- **THEN** a `HumanUser` resource SHALL exist in the `admin` role org with
  `email = pannpers@pannpers.dev`
- **AND** the user SHALL have a Pulumi-generated random `initialPassword`
  that is not exposed outside Pulumi state
- **AND** the user's email SHALL be marked verified
  (`isEmailVerified = true`)
- **AND** the user SHALL have no `userGrant` on the `liverty-music`
  project (admin Console access is granted via instance membership, not
  project role)

#### Scenario: Admin role org is exclusively Pulumi-managed

- **WHEN** any human user is created in the `admin` role org
- **THEN** that user SHALL be declared in Pulumi
- **AND** ad-hoc human users created through the Admin Console SHALL be
  treated as drift and reverted on the next Pulumi apply

#### Scenario: Random initial password is unreachable

- **WHEN** a user attempts username + password sign-in against the `admin`
  role org
- **THEN** the login UI SHALL not present a password input field (because
  `LoginPolicy.userLogin = false`)
- **AND** the random initial password set on the human admin SHALL be
  unreachable for authentication

### Requirement: Grant IAM_OWNER to Human Admin User

The system SHALL grant the `IAM_OWNER` instance role to the provisioned
human admin user via Pulumi as an `InstanceMember` resource so that the
user can perform any operation in the Admin Console after Google sign-in.

#### Scenario: Grant IAM_OWNER

- **WHEN** Pulumi stack is applied
- **THEN** an `InstanceMember` resource SHALL bind the `IAM_OWNER` role to
  the provisioned human admin user's id
- **AND** the user SHALL be able to list, read, and modify all
  instance-level resources via the Admin Console
- **AND** the audit log SHALL record actions taken by this user under
  their human user id (not under `pulumi-admin`)

### Requirement: Pre-link Google Identity to Human Admin via IaC

The system SHALL declare the binding between an external Google identity
and the pre-provisioned local `HumanUser` in Pulumi as a
`ZitadelUserIdpLink` resource, so that the very first Google sign-in
resolves directly to the local user without any interactive prompt. The
link SHALL be keyed by Zitadel's `(idpId, externalUserId)` tuple, where
`externalUserId` is the Google OIDC `sub` claim of the admin's Google
account (a stable numeric identifier immutable for the lifetime of the
Google account).

**Why pre-link, not auto-link by email:** Zitadel's two native
first-sign-in paths both fail in the `admin` org's policy combination:

- *Auto-link by email* (`IdpGoogle.isLinkingAllowed = true`) would prompt
  the user to confirm the link by signing in with the existing local
  user's password. The `admin` org's `LoginPolicy.userLogin = false`
  disables the password sign-in form, so the autoLink prompt has no way
  to authenticate.
- *Auto-creation* (`IdpGoogle.isAutoCreation = true`) would mint a fresh
  local user from the Google profile without any consent prompt. The
  `admin` org's IdP sets `isCreationAllowed = false` to prevent any
  pannpers.dev Google account from implicitly becoming an instance-level
  admin.

Pulumi declaring the `(idpId, sub)` link record up front breaks the
deadlock without weakening either of those guards.

#### Scenario: Pre-link record is provisioned in Zitadel

- **WHEN** Pulumi stack is applied
- **THEN** a `ZitadelUserIdpLink` resource SHALL exist for each
  pre-provisioned human admin
- **AND** the resource SHALL POST `/v2/users/{userId}/links` to Zitadel
  with `idpId` matching the admin Google IdP and `userId` equal to the
  admin's Google `sub` claim sourced from ESC
- **AND** a 409 AlreadyExists response SHALL be treated as success
  (idempotent re-apply)

#### Scenario: First Google sign-in resolves directly to the local user

- **WHEN** `pannpers@pannpers.dev` opens
  `https://auth.dev.liverty-music.app/ui/console` and completes Google
  sign-in for the first time
- **THEN** Zitadel SHALL look up the IdP link record by
  `(idpId, externalUserId=sub)` and resolve to the pre-provisioned local
  `HumanUser` immediately
- **AND** Login V2 SHALL NOT show the `account-not-found`,
  `register new account`, or `link existing account` prompt
- **AND** the Admin Console SHALL load with `IAM_OWNER` privileges
- **AND** no new local user SHALL be created

#### Scenario: Subsequent Google sign-ins reuse the same link

- **WHEN** the same admin signs in via Google a second time
- **THEN** the existing IdP link SHALL be reused without any prompt
- **AND** the audit log SHALL record the sign-in under the same human
  user id

#### Scenario: Identity tuple changes trigger replace, not update

- **WHEN** the `userId`, `idpId`, or `externalUserId` of a
  `ZitadelUserIdpLink` changes in Pulumi code
- **THEN** Pulumi SHALL delete the existing link and create a new one
  (per `replaceOnChanges` declared on the resource class)
- **AND** Pulumi MUST NOT route the change through the no-op `update()`
  callback, because Zitadel keys the link by the tuple and exposes no
  in-place modification endpoint

### Requirement: Provision Admin Google Sub via ESC

The system SHALL store each pre-provisioned admin's Google `sub` claim in
Pulumi ESC under
`pulumiConfig.zitadel.adminGoogleSubs.<userName>`, marked encrypted via
`esc env set --secret`. The `<userName>` segment SHALL match the local
Pulumi-side identifier used in the `HumanAdminComponent` declaration so
the link record can be wired without name lookup at deploy time.

**Why a secret slot for a non-secret value:** the Google `sub` itself is
not sensitive — it is an opaque numeric ID — but storing it under
`--secret` keeps the entire `pulumiConfig.zitadel.*` config tree
uniformly encrypted, simplifying secret-handling audits and matching the
treatment of `googleAdminIdp.clientId` / `clientSecret`.

#### Scenario: ESC carries the sub for each admin

- **WHEN** Pulumi stack is previewed or applied
- **THEN** ESC `liverty-music/dev` SHALL resolve
  `pulumiConfig.zitadel.adminGoogleSubs.<userName>` to a numeric string
  matching the OIDC `sub` claim of that admin's Google account
- **AND** the value SHALL be marked encrypted in ESC

#### Scenario: Admin onboarding workflow

- **WHEN** a new human admin needs `IAM_OWNER` access
- **THEN** the operator SHALL follow the onboarding runbook
  (`docs/runbooks/add-zitadel-admin-user.md` in `cloud-provisioning`) to
  capture the Google `sub`, write it to ESC, declare the user +
  membership + link in Pulumi, and verify Console access
- **AND** the operator SHALL NOT add the admin via direct Console clicks
  (per the *Admin role org is exclusively Pulumi-managed* invariant)

### Requirement: Place Machine Users by Responsibility

The system SHALL place machine users in the org that matches their
responsibility:

- **Operator machine users** (used by infrastructure / IaC tooling and the
  Zitadel-internal Login V2 service) SHALL live in the `admin` role org.
  These are: `pulumi-admin` (IaC authentication and break-glass) and
  `login-client` (Login V2 PAT host).
- **Product service machine users** (used by product application code to
  call Zitadel APIs as part of product features) SHALL live in the
  `liverty-music` product org. The current example is `backend-app`,
  consumed by the backend Go service to call Zitadel Management APIs for
  user-facing features.

This split keeps "who acts on behalf of the platform" separate from "who
acts on behalf of the product", and lets each org's policies, audit logs,
and key rotations be reasoned about independently.

#### Scenario: pulumi-admin lives in admin org

- **WHEN** the Zitadel instance bootstraps for the first time
- **THEN** Zitadel SHALL create the `pulumi-admin` machine user in the
  `admin` role org (because `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin` is set
  in the configmap)

#### Scenario: login-client lives in admin org

- **WHEN** Pulumi stack is applied
- **THEN** the `login-client` machine user (Login V2 PAT host) SHALL exist
  in the `admin` role org, not in the `liverty-music` product org

#### Scenario: backend-app lives in product org

- **WHEN** Pulumi stack is applied
- **THEN** the `backend-app` machine user (backend service identity for
  Zitadel Management API calls) SHALL exist in the `liverty-music`
  product org, not in the `admin` role org

### Requirement: Retain Break-glass Machine User

The system SHALL retain the `pulumi-admin` machine user with `IAM_OWNER`
membership and its JSON key in GCP Secret Manager (`zitadel-admin-sa-key`)
as a break-glass identity that does not depend on Google sign-in being
operational. This requirement protects against total Console lockout if
the Google IdP, OAuth client, or human admin user is misconfigured or
removed.

#### Scenario: Break-glass identity exists

- **WHEN** Pulumi stack is applied
- **THEN** the `pulumi-admin` machine user SHALL exist in the `admin` role
  org with `IAM_OWNER`
- **AND** its JSON key SHALL be present in GCP Secret Manager as
  `zitadel-admin-sa-key`
- **AND** neither the user nor its key SHALL be deleted, replaced, or
  rotated as a side effect of provisioning the human admin user, IdP, or
  login policy
- **AND** the only legitimate write to `zitadel-admin-sa-key` SHALL be
  performed by the in-cluster `bootstrap-uploader` sidecar at
  first-instance bootstrap (idempotent)

#### Scenario: Recover from broken Google sign-in

- **WHEN** the human admin user cannot sign in via Google (IdP outage,
  misconfigured OAuth client, accidentally deleted human user, etc.)
- **THEN** an operator SHALL be able to authenticate the Pulumi
  `@pulumiverse/zitadel` provider with the `zitadel-admin-sa-key` JSON key
- **AND** run Pulumi to restore the human admin user, IdP, or login
  policy
- **AND** Console access via Google SHALL resume after the next Pulumi
  apply

### Requirement: Maintain Google OAuth Client in Dev Infrastructure

The system SHALL maintain a Google Cloud OAuth 2.0 Web Application
client in the `liverty-music-dev` GCP project (the same project that
hosts the GKE cluster, Cloud SQL instance, and Zitadel workload). The
client's authorised redirect URI MUST point at the Zitadel Login V2 IdP
callback path. The client's `client_id` and `client_secret` MUST be
present in Pulumi ESC under `liverty-music/cloud-provisioning/dev` and
MUST never be committed to git.

**Implementation note**: Google does not expose a public API for creating
general-purpose OAuth 2.0 Web Application clients. The client is
therefore created **manually** in the Google Cloud Console as a one-time
operation per environment, then its `client_id` and `client_secret` are
written to ESC via `esc env set` (the latter with `--secret`). Pulumi
reads from ESC and configures the Zitadel `IdpGoogle` resource with
these values. Subsequent rotation is handled via the same ESC keys + a
`pulumi up`.

#### Scenario: OAuth client exists with correct redirect URI

- **WHEN** an operator inspects the `liverty-music-dev` GCP project
  Credentials page
- **THEN** a Google OAuth 2.0 Web Application client SHALL exist with
  the application name "Zitadel Admin IdP (dev)" (or equivalent)
- **AND** its authorised redirect URI SHALL include
  `https://auth.dev.liverty-music.app/idps/callback`

#### Scenario: ESC carries the credentials

- **WHEN** Pulumi stack is previewed or applied
- **THEN** ESC `liverty-music/cloud-provisioning/dev` SHALL resolve
  `pulumiConfig.zitadel.googleAdminIdp.clientId` to the OAuth client's
  client_id (plaintext)
- **AND** SHALL resolve `pulumiConfig.zitadel.googleAdminIdp.clientSecret`
  to the OAuth client's client_secret, marked as encrypted

#### Scenario: No OAuth secret in git

- **WHEN** the repository is searched for the OAuth client secret value
- **THEN** the secret SHALL NOT appear in any committed file in
  `cloud-provisioning`, `specification`, `backend`, or `frontend`

#### Scenario: Client recreation runbook

- **WHEN** the OAuth client is accidentally deleted in the Google Cloud
  Console
- **THEN** the cloud-provisioning runbook SHALL document the manual
  recreation steps (Internal consent screen → Web application client →
  redirect URI → `esc env set` of the new credentials)
- **AND** following the runbook SHALL restore the admin Google sign-in
  flow without any spec change
