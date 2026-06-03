# Identity Management

## Purpose

Manage identity, authentication, and authorization policies for the Liverty Music platform.

## Requirements

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
- **AND** the application's `client_id` SHALL be committed to the
  per-environment `web-app-runtime-config` ConfigMap under
  `cloud-provisioning/k8s/namespaces/frontend/overlays/<env>/configmap.yaml`
  (`zitadelClientId` field) alongside the owning org's id
  (`zitadelOrgId` field), so each env's pod serves its own identifiers
  via the runtime `/config.json` endpoint consumed by the SPA at
  bootstrap (see the `frontend-runtime-config` capability). There is
  intentionally no separate "frontend" Pulumi stack consuming the
  value via ESC — the deploy-time ConfigMap model is simpler and keeps
  per-environment divergence in the GitOps tree alongside the rest of
  the cluster config.

#### Scenario: Prod env serves prod identifiers via /config.json

- **WHEN** the prod frontend Deployment is rolled out (image pinned by `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`)
- **THEN** the pod SHALL serve `https://liverty-music.app/config.json` with `zitadelClientId` equal to the `liverty-music` `ApplicationOidc` `client_id` in the **prod** Zitadel `liverty-music` product org
- **AND** the same response SHALL carry `zitadelOrgId` equal to the prod `liverty-music` product org id
- **AND** the response SHALL NOT carry any dev identifiers (no dev client_id, no dev org_id)

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
- **AND** the IdP SHALL set `isLinkingAllowed = true` (defence-in-depth;
  the actual first-sign-in resolution uses the IaC-managed
  `ZitadelUserIdpLink` records — see *Pre-link Google Identity to
  Human Admin via IaC* — because the policy combination disables
  Zitadel's native autoLink prompt)
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
membership and its JSON key in GCP Secret Manager (`zitadel-machine-key-for-pulumi-admin`)
as a break-glass identity that does not depend on Google sign-in being
operational. This requirement protects against total Console lockout if
the Google IdP, OAuth client, or human admin user is misconfigured or
removed.

The GSM name `zitadel-machine-key-for-pulumi-admin` follows the platform-wide convention `zitadel-machine-key-for-<principal>`. The legacy name `zitadel-admin-sa-key` was renamed because (1) it did not encode the binding between the GSM secret and the owning Zitadel principal, and (2) the principal label `admin` did not match the Pulumi `MachineUser` resource id `pulumi-admin`.

#### Scenario: Break-glass identity exists

- **WHEN** Pulumi stack is applied
- **THEN** the `pulumi-admin` machine user SHALL exist in the `admin` role
  org with `IAM_OWNER`
- **AND** its JSON key SHALL be present in GCP Secret Manager as
  `zitadel-machine-key-for-pulumi-admin`
- **AND** neither the user nor its key SHALL be deleted, replaced, or
  rotated as a side effect of provisioning the human admin user, IdP, or
  login policy
- **AND** the only legitimate write to `zitadel-machine-key-for-pulumi-admin` SHALL be
  performed by the in-cluster `bootstrap-uploader` sidecar at
  first-instance bootstrap (idempotent)

#### Scenario: Recover from broken Google sign-in

- **WHEN** the human admin user cannot sign in via Google (IdP outage,
  misconfigured OAuth client, accidentally deleted human user, etc.)
- **THEN** an operator SHALL be able to authenticate the Pulumi
  `@pulumiverse/zitadel` provider with the `zitadel-machine-key-for-pulumi-admin` JSON key
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

### Requirement: Inject Email Claim into Access Tokens via Actions v2

The system SHALL inject the authenticated user's `email` claim into every issued JWT access token by configuring a Zitadel Actions v2 `ExecutionFunction` bound to the `preaccesstoken` function, pointing at the backend `/pre-access-token` webhook Target.

**Rationale**: Zitadel does not include `email` in access tokens by default; the backend JWT validator requires this claim for user provisioning. Injection previously occurred via an Actions v1 JavaScript function (`addEmailClaim`); migrating to Actions v2 aligns with the upstream deprecation of v1 and moves the logic into a testable backend handler.

#### Scenario: Access token issued to a human user contains email

- **WHEN** a human user completes the OIDC authorization flow
- **THEN** the issued JWT access token SHALL contain an `email` claim equal to the user's verified email address

#### Scenario: Access token issued to a machine user omits email

- **WHEN** a machine user obtains an access token via client-credentials
- **THEN** the issued JWT access token SHALL NOT contain an `email` claim
- **AND** the token issuance SHALL succeed

### Requirement: Provision Actions v2 Target and Execution Resources

The system SHALL manage the Zitadel Actions v2 `Target` and `ExecutionFunction` resources for email-claim injection via Infrastructure as Code, using a Pulumi Dynamic Resource that calls the Zitadel REST API because the installed `@pulumiverse/zitadel` provider does not yet expose Actions v2 resource types.

**Rationale**: Managing these resources declaratively alongside existing v1 resources (Project, ApplicationOidc, LoginPolicy) preserves drift detection and reproducibility across rebuilds.

#### Scenario: Pulumi apply creates Actions v2 resources

- **WHEN** the Pulumi stack is applied
- **THEN** a Zitadel Actions v2 Target named `pre-access-token-webhook` SHALL exist pointing at the backend `/pre-access-token` endpoint
- **AND** a Zitadel Actions v2 ExecutionFunction SHALL bind the `preaccesstoken` function to that Target

#### Scenario: Targets use JWT payload authentication

- **WHEN** a Target is created by Pulumi
- **THEN** the Target's `payloadType` SHALL be `PAYLOAD_TYPE_JWT`
- **AND** the Target SHALL NOT be configured with a shared `signingKey`

### Requirement: Dedicated Service User for Login V2 UI

The system SHALL provision a Zitadel `MachineUser` named `login-client` with `IAM_LOGIN_CLIENT` instance-level role and a long-lived `PersonalAccessToken`, mounted into the `zitadel-login` Pod as a file referenced by the `ZITADEL_SERVICE_USER_TOKEN_FILE` environment variable.

**Rationale**: The self-hosted Zitadel Login V2 UI (Next.js, separate container from the Zitadel API) calls privileged settings + cross-org user-search APIs at SSR time and cannot use end-user OIDC tokens. Without a service-user PAT, the Login UI's SSR returns HTTP 500 with `fetch() returned undefined` from every settings call, breaking every login flow. This requirement was missing from the original cutover plan because Zitadel Cloud handles the Login UI's authentication internally; in self-hosted, the Login UI must be registered as a first-class API client. See https://zitadel.com/docs/self-hosting/manage/login-client.

#### Scenario: Login UI authenticates to Zitadel API on every SSR request

- **WHEN** the `zitadel-login` Pod handles a `/ui/v2/login/*` route
- **THEN** the Next.js server SHALL read the PAT from the file referenced by `ZITADEL_SERVICE_USER_TOKEN_FILE`
- **AND** SHALL include it as a Bearer token on outgoing API calls
- **AND** the Zitadel API SHALL accept the token and return the requested settings / user data

#### Scenario: PAT is mounted as a file, not an env var value

- **WHEN** the K8s manifest sets up the PAT
- **THEN** the K8s Secret data key SHALL be projected to a file at `/var/run/zitadel/login-client.pat`
- **AND** the env var `ZITADEL_SERVICE_USER_TOKEN_FILE` SHALL point at that path
- **AND** the env var `ZITADEL_SERVICE_USER_TOKEN` SHALL NOT be set, so that the PAT does not appear in `kubectl describe pod` env dumps

#### Scenario: PAT has no expiration in dev

- **WHEN** Pulumi creates the `login-client` `PersonalAccessToken` for `dev`
- **THEN** `expirationDate` SHALL be omitted (Zitadel treats this as never-expires)
- **AND** an inline comment in the Pulumi component SHALL document that staging / prod must adopt a real expiration + rotation runbook before extending the cutover beyond dev

### Requirement: SMTP Configuration Must Be Activated After Creation

The system SHALL invoke the Zitadel admin API `POST /admin/v1/smtp/{id}/_activate` after creating a `SmtpConfig` resource via a **Pulumi Dynamic Resource (`ZitadelSmtpActivation`)** that fires as a declarative dependency of the `SmtpConfig` resource, because Zitadel v4 ships new SMTP configurations in `SMTP_CONFIG_INACTIVE` state and the `@pulumiverse/zitadel.SmtpConfig` resource does not flip the activation flag.

**Rationale**: An inactive SMTP config silently swallows all outbound notification events. Verification emails, password reset emails, and admin notifications are queued but never delivered to the SMTP provider. The failure mode is invisible — the API call to send the email returns success (202-equivalent), the notification worker logs nothing, and the user-facing UX is "no email arrived." Discovered during the dev cutover smoke test when sign-up succeeded but verification emails never reached Postmark. The implementation contract is pinned to the Dynamic Resource (rather than "Dynamic Resource OR equivalent") so a manual `curl` step cannot be a "valid implementation" — every Zitadel rebuild must activate SMTP declaratively without operator memory.

#### Scenario: Newly provisioned SMTP config is activated automatically

- **WHEN** Pulumi provisions a `SmtpConfig` resource on a fresh Zitadel instance
- **THEN** the `ZitadelSmtpActivation` Dynamic Resource SHALL call `POST /admin/v1/smtp/{id}/_activate` as part of the same `pulumi up`
- **AND** the resulting state SHALL be `SMTP_CONFIG_ACTIVE`
- **AND** subsequent verification emails SHALL be queued AND delivered to the SMTP provider

#### Scenario: First apply against an already-active SMTP succeeds (create-time idempotency)

- **WHEN** Pulumi runs `create()` for `ZitadelSmtpActivation` against an SMTP config that is already in `SMTP_CONFIG_ACTIVE` state (e.g., activated out-of-band by a manual `curl` step prior to this resource being added to the stack)
- **THEN** the `_activate` POST SHALL return Zitadel's "already active" response shape
- **AND** `create()` SHALL treat that response as success
- **AND** the resource SHALL be recorded in Pulumi state with a fresh `activatedAt` timestamp

#### Scenario: Re-apply with unchanged inputs is a Pulumi-graph no-op

- **WHEN** Pulumi re-applies the stack and the `ZitadelSmtpActivation` resource's inputs (`smtpConfigId`, `domain`, `jwtProfileJson`) are unchanged from the previous apply
- **THEN** Pulumi's input diff SHALL be empty
- **AND** no lifecycle handler (`create` / `update` / `delete` / `read`) on `ZitadelSmtpActivation` SHALL be invoked
- **AND** zero HTTP traffic SHALL be generated against the Zitadel admin API
- **AND** the Pulumi state graph SHALL continue to record the resource as up-to-date

#### Scenario: Activation runs on a fresh Zitadel rebuild without operator intervention

- **WHEN** the dev (or future staging / prod) Zitadel instance is destroyed and recreated from scratch
- **AND** Pulumi runs `pulumi up` against the recreated instance
- **THEN** the `SmtpConfig` resource SHALL be recreated
- **AND** the `ZitadelSmtpActivation` resource SHALL fire `_activate` automatically as the next step in the dependency graph
- **AND** the operator SHALL NOT need to run any manual `curl` or `gcloud` step
- **AND** the first user sign-up after the rebuild SHALL receive a verification email

### Requirement: Provision Password-Based E2E Test User in Dev Zitadel

The dev self-hosted Zitadel instance SHALL provision, via Pulumi, a password-based `zitadel.HumanUser` for E2E test automation. The provisioning SHALL be gated to the `dev` Pulumi stack and SHALL NOT execute in any other stack.

**Rationale**: Headless test automation cannot drive a passkey-only login flow (passkey requires a biometric / PIN gesture from a registered device). A Pulumi-managed password-based user provides a credential path the headless capture script can drive end-to-end, unblocking E2E coverage of the post-cutover self-hosted issuer. (Earlier wording referenced "distinct from the existing passkey-only test user" — that wording was inherited from the original `playwright-password-test-user` change but no passkey-only test user exists on the active self-hosted dev Zitadel; the Zitadel-Cloud-era Self-Registration user was wiped by `self-hosted-zitadel §10` and never re-provisioned.)

#### Scenario: Pulumi apply on dev stack provisions the test user

- **WHEN** `pulumi up` runs on the `dev` stack
- **THEN** a `zitadel.HumanUser` resource SHALL be created in the self-hosted Zitadel instance with a recognizable display name and an email under the dev domain
- **AND** the user SHALL have `InitialPassword` set from the ESC value `pulumiConfig.zitadel.e2eTestUser.password` (read via `config.requireSecretObject`)
- **AND** the user SHALL have `isEmailVerified` set to `true` — without this flag Zitadel injects an email-verification step into the OIDC flow that the headless capture script cannot handle
- **AND** the user SHALL have no second-factor (TOTP / SMS / passkey) enrollment

#### Scenario: Non-dev stacks do not provision the test user

- **WHEN** `pulumi up` runs on any stack other than `dev`
- **THEN** the Pulumi program SHALL NOT instantiate the test-user component (today via the outer `if (env === "dev")` check that gates the entire `Zitadel` composition; see Tasks §1.6/§1.8)
- **AND** no `zitadel.HumanUser` resource for `e2e-test-password` SHALL appear in the preview diff
- **AND** the component-internal synthesis guard (`if (env !== "dev") throw …`) and the parent `Zitadel` class guard remain in place as defensive depth — if the outer `if (env === "dev")` check is removed in a future refactor, either guard SHALL throw with a clear "dev-only" error message before any Zitadel API call is made

#### Scenario: `initialPassword` changes do not trigger silent replacement

- **WHEN** an operator changes the ESC value `pulumiConfig.zitadel.e2eTestUser.password`
- **AND** `pulumi preview --stack dev` is run on the next deploy
- **THEN** the preview SHALL show NO change to the e2e-test-user `zitadel.HumanUser` resource (the `ignoreChanges: ['initialPassword']` directive on the resource hides the diff)
- **AND** the captured Playwright `storageState.json` SHALL remain valid until the operator explicitly forces a replacement

#### Scenario: Intentional rotation requires an explicit replace

- **WHEN** an operator runs `pulumi up --replace <urn-of-e2e-test-user>` on the dev stack
- **THEN** the preview SHALL clearly indicate the replacement (`-/+ create replacement`)
- **AND** after apply, the new HumanUser SHALL use the latest ESC `initialPassword` value
- **AND** the operator is then responsible for re-mirroring `.auth/password.md` and re-running the headless capture script to regenerate `.auth/storageState.json`

### Requirement: E2E Test User Password Marked Permanent

The dev self-hosted Zitadel instance SHALL mark the password-based E2E test user's password as permanent (`noChangeRequired = true`) at Pulumi-apply time, via a dedicated Dynamic Resource that calls the Zitadel Management API `POST /management/v1/users/{user_id}/password` immediately after the `zitadel.HumanUser` is created. The dev `e2e-test-password` user SHALL NOT be redirected to `/ui/v2/login/password/change` on its first sign-in or on any subsequent sign-in.

**Rationale**: `@pulumiverse/zitadel.HumanUser` v0.2.0 sets the user's credential state with `changeRequired = true` and exposes no knob to flip this flag at create time. Without an explicit `SetPassword(noChangeRequired = true)` call, Zitadel redirects the user to a password-change page on first sign-in and refuses to issue tokens until the password is changed. Headless E2E automation cannot tolerate this gate without a fragile script-side workaround that depends on Zitadel's default password-history policy remaining unchanged.

#### Scenario: Pulumi apply marks the password permanent

- **WHEN** `pulumi up` runs on the `dev` stack with `E2eTestUserComponent` enabled
- **THEN** a `ZitadelHumanUserPasswordPermanent` Dynamic Resource SHALL be created with `dependsOn: [humanUser]` so it executes only after the `zitadel.HumanUser` for `e2e-test-password` is ready
- **AND** the resource's `create()` handler SHALL POST `/management/v1/users/{user_id}/password` with `{ password, noChangeRequired: true }` against the dev Zitadel domain
- **AND** the resource SHALL receive the same ESC-sourced password the HumanUser was created with (`pulumiConfig.zitadel.e2eTestUser.password`)
- **AND** any 2xx response from Zitadel SHALL be treated as success, including the case where the password was already marked permanent

#### Scenario: First sign-in does not redirect to /password/change

- **WHEN** the `e2e-test-password` user signs in via the OIDC password flow after `pulumi up` completes
- **THEN** the auth host SHALL NOT redirect to `/ui/v2/login/password/change`
- **AND** the OIDC callback SHALL complete directly after the password submission step
- **AND** the captured Playwright `storageState.json` SHALL contain a valid `oidc.user:*` entry

#### Scenario: ESC password rotation re-asserts permanence

- **WHEN** an operator runs `pulumi up --replace <urn-of-humanUser>` on the dev stack with a rotated ESC password value
- **THEN** the `zitadel.HumanUser` SHALL be re-created with the new `initialPassword`
- **AND** the `ZitadelHumanUserPasswordPermanent` resource SHALL be replaced (NOT updated) via its `replaceOnChanges: ['userId']` directive — the HumanUser's new snowflake id flows into the marker's `userId` input, triggering destroy + fresh create rather than `update()` with the stale (ignored) password value
- **AND** the new marker's `create()` SHALL POST `SetPassword` with the new password and `noChangeRequired: true` against the new user
- **AND** after apply, the user SHALL still NOT be redirected to `/password/change` on the next sign-in

#### Scenario: ESC-secret edit without --replace does not silently rotate

- **WHEN** an operator edits the ESC value `pulumiConfig.zitadel.e2eTestUser.password` without running `pulumi up --replace`
- **THEN** the `zitadel.HumanUser` resource SHALL NOT diff (its `ignoreChanges: ['initialPassword']` directive suppresses the input change)
- **AND** the `ZitadelHumanUserPasswordPermanent` marker SHALL NOT diff either (its `ignoreChanges: ['password']` directive mirrors the HumanUser's, preventing the marker from re-POSTing `SetPassword` and silently rotating the live credential)
- **AND** the previously captured Playwright `storageState.json` SHALL remain valid until the operator explicitly forces a replacement via the rotation protocol

#### Scenario: Resource removal does not unset permanence

- **WHEN** the `ZitadelHumanUserPasswordPermanent` resource is removed from Pulumi state (via `pulumi destroy --target` or a code-level removal followed by `pulumi up`)
- **THEN** the resource's `delete()` handler SHALL be a no-op and SHALL NOT call any Management API endpoint
- **AND** the underlying `zitadel.HumanUser` SHALL retain its `noChangeRequired = true` state (there is no inverse Management API verb to flip permanence off, by design)
- **AND** the user SHALL continue to authenticate without a `/password/change` redirect until the HumanUser itself is replaced

### Requirement: Maintain Google OAuth Client in Prod Infrastructure

The system SHALL maintain a Google Cloud OAuth 2.0 Web Application
client in the `liverty-music-prod` GCP project (the same project that
hosts the prod GKE cluster, Cloud SQL instance, and Zitadel workload).
The client's authorised redirect URI MUST point at the prod Zitadel
Login V2 IdP callback path (`https://auth.liverty-music.app/idps/callback`).
The client's `client_id` and `client_secret` MUST be present in Pulumi
ESC under `liverty-music/prod` and MUST never be committed to git.

This is the prod sibling of the existing "Maintain Google OAuth Client
in Dev Infrastructure" requirement; the same operational pattern
(manual GCP Console creation → `esc env set`) applies.

#### Scenario: OAuth client exists with correct redirect URI

- **WHEN** an operator inspects the `liverty-music-prod` GCP project
  Credentials page
- **THEN** a Google OAuth 2.0 Web Application client SHALL exist with
  the application name "Zitadel Admin IdP (prod)" (or equivalent)
- **AND** its authorised redirect URI SHALL include
  `https://auth.liverty-music.app/idps/callback`

#### Scenario: ESC carries the prod credentials

- **WHEN** Pulumi stack `prod` is previewed or applied
- **THEN** ESC `liverty-music/prod` SHALL resolve
  `pulumiConfig.zitadel.googleAdminIdp.clientId` to the prod OAuth
  client's client_id (plaintext, prefixed by the prod project number
  `108947861615-`)
- **AND** SHALL resolve `pulumiConfig.zitadel.googleAdminIdp.clientSecret`
  to the prod OAuth client's client_secret, marked as encrypted

#### Scenario: Dev and prod clients are distinct

- **WHEN** comparing the prod `googleAdminIdp.clientId` to the dev
  `googleAdminIdp.clientId`
- **THEN** the values SHALL be different
- **AND** the prod client SHALL be owned by GCP project number
  `108947861615` (prod), not `1058199000631` (dev)

#### Scenario: No prod OAuth secret in git

- **WHEN** the repository is searched for the prod OAuth client secret value
- **THEN** the secret SHALL NOT appear in any committed file in
  `cloud-provisioning`, `specification`, `backend`, or `frontend`

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

#### Scenario: Client recreation runbook covers prod

- **WHEN** the prod OAuth client is accidentally deleted in the Google
  Cloud Console
- **THEN** the cloud-provisioning runbook (`docs/runbooks/zitadel-oauth-client-recreate.md`)
  SHALL document the manual recreation steps for the prod project
  (Internal consent screen → Web application client → prod redirect
  URI → `esc env set liverty-music/prod`)
- **AND** following the runbook SHALL restore the prod admin Google
  sign-in flow without any spec change

