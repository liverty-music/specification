## ADDED Requirements

### Requirement: Prod Zitadel Application Stack Provisioned by Pulumi

The Pulumi `prod` stack SHALL provision the full Zitadel application stack required for end-user OIDC sign-in, end-user sign-up email verification, operator Console sign-in, and access-token email-claim propagation, in addition to the backend MachineKey already provisioned by `BackendMachineKeyComponent`. Specifically, the prod stack SHALL contain Pulumi-managed resources for:

1. The prod `admin` org (brought into state via a one-time `pulumi import zitadel:index/org:Org admin <prod-admin-org-id>`), with `isDefault: true` (preserved from the bootstrap) and `protect: true`.
2. A `zitadel.Project` named `liverty-music` in the product org.
3. An `ApplicationOidc` for the frontend SPA (PKCE flow, JWT access tokens) and a product-org `LoginPolicy` (passkey + username/password sign-in, `userLogin=true`, `allowRegister=true`).
4. A `SmtpConfig` (Postmark backend) and a dynamic-resource `SmtpActivation` that calls Zitadel's admin API `_activate` endpoint.
5. An instance-level Actions V2 `Target` (REST webhook to the backend's `/pre-access-token` endpoint) and an `Execution` binding on the `preaccesstoken` flow.
6. A `login-client` `MachineUser` (in the admin org), an instance-level `IAM_LOGIN_CLIENT` role grant, a `PersonalAccessToken` (PAT), and a GSM Secret `zitadel-login-pat` (Pulumi-created Secret + SecretVersion + IAM binding for the ESO Workload Identity SA) carrying the PAT for the in-cluster `zitadel-web` Pod.
7. An instance-level `IdpGoogle` (admin Google IdP) keyed on a separate prod Google OAuth Web Application client (distinct from the dev client).
8. An admin-org `LoginPolicy` (`userLogin=false`, `allowRegister=false`, `idps=[googleIdpId]`) and an instance-level `DefaultLoginPolicy` mirroring it.
9. A `HumanUser` `pannpers@pannpers.dev` in the admin org with `IAM_OWNER` granted via an instance-level `OrgMember`, pre-linked to the prod Google IdP via a dynamic-resource `ZitadelUserIdpLink`.

The prod stack SHALL NOT provision an `E2eTestUserComponent` (deferred to a follow-up change). The dev stack SHALL retain its existing 13-component `Zitadel` class verbatim; this requirement adds parallel prod-side provisioning, not a refactor of dev's assembly.

**Rationale**: The prior `enable-zitadel-prod-pulumi-provider` change covered only the backend MachineKey, leaving prod with no browser sign-in path (operator or end-user), no sign-up email verification, and no access-token email claim. This requirement closes those gaps atomically — partial states (e.g., admin LoginPolicy without the Google IdP) would lock operators out mid-cutover. The 9-component bundle matches dev's proven topology minus E2E test infra, which is intentionally deferred so test-tenant decisions can be made after prod stack verification.

#### Scenario: Prod stack contains the full application stack after apply

- **WHEN** `pulumi up --stack prod` completes successfully against the change introducing this requirement
- **THEN** the prod Pulumi state SHALL contain exactly one `zitadel.Org` named `admin` with `isDefault: true` and `protect: true`
- **AND** exactly one `zitadel.Org` named `liverty-music` (product org) with `isDefault: false`
- **AND** exactly one `zitadel.Project` named `liverty-music` in the product org
- **AND** exactly one `zitadel.ApplicationOidc` for the frontend SPA (PKCE flow, scopes including `email`)
- **AND** exactly one product-org `LoginPolicy` with `userLogin=true` and `allowRegister=true`
- **AND** exactly one `zitadel.SmtpConfig` and exactly one dynamic-resource `ZitadelSmtpActivation`
- **AND** exactly one `zitadel.Target` (REST webhook to the backend's `/pre-access-token` endpoint) and exactly one `zitadel.Execution` on the `preaccesstoken` flow
- **AND** exactly one `login-client` `zitadel.MachineUser` in the admin org with an instance-level `IAM_LOGIN_CLIENT` role grant
- **AND** exactly one `zitadel.PersonalAccessToken` for the `login-client` MachineUser
- **AND** exactly one `gcp.secretmanager.Secret` named `zitadel-login-pat` (with at least one enabled SecretVersion and an IAM accessor binding for the ESO Workload Identity SA)
- **AND** exactly one instance-level `zitadel.IdpGoogle`
- **AND** exactly one admin-org `LoginPolicy` with `userLogin=false`, `allowRegister=false`, and `idps=[googleIdpId]`
- **AND** exactly one instance-level `zitadel.DefaultLoginPolicy` mirroring the admin-org `LoginPolicy`
- **AND** exactly one `zitadel.HumanUser` for `pannpers@pannpers.dev` in the admin org with instance-level `IAM_OWNER`
- **AND** exactly one dynamic-resource `ZitadelUserIdpLink` linking the `pannpers` HumanUser to the prod Google IdP

#### Scenario: Prod stack does NOT contain an E2E test user (deferred)

- **WHEN** the prod Pulumi state is exported after this change is applied
- **THEN** it SHALL NOT contain any `E2eTestUserComponent` ComponentResource
- **AND** it SHALL NOT contain any `zitadel.HumanUser` whose `email` matches the dev E2E test user convention

#### Scenario: Operator can sign in to prod Console via Google IdP

- **WHEN** the operator visits `https://auth.liverty-music.app/ui/console` after the prod stack is applied
- **THEN** the Login V2 UI SHALL present a "Sign in with Google" button (sourced from the admin-org `LoginPolicy.idps`)
- **AND** completing the Google OAuth flow with `pannpers@pannpers.dev` SHALL resolve to the `pannpers` HumanUser via the pre-linked `ZitadelUserIdpLink`
- **AND** the resulting Console session SHALL have IAM_OWNER authority at the instance level

#### Scenario: End user can complete OIDC sign-up via SPA with email verification

- **WHEN** an end user visits `https://liverty-music.app` after the prod stack is applied and chooses sign-up
- **THEN** the SPA SHALL redirect to the prod Zitadel `ApplicationOidc` authorize endpoint
- **AND** the Login V2 UI SHALL present passkey + username/password sign-up (sourced from the product-org `LoginPolicy`)
- **AND** completing sign-up SHALL trigger a verification email sent via Postmark SMTP (sourced from the activated `SmtpConfig`)
- **AND** verifying the email SHALL allow the user to sign in and obtain an access token containing the `email` claim (sourced from the Actions V2 `preaccesstoken` flow execution against the backend webhook)

### Requirement: Prod ZitadelProdStackComponent Wraps the Nine Leaf Components

The prod Pulumi stack SHALL implement the 9 components listed in the previous requirement via a single top-level `pulumi.ComponentResource` named `ZitadelProdStackComponent` (URN `zitadel:liverty-music:ZitadelProdStack`), which SHALL internally instantiate the 9 leaf components in dependency order. The `src/index.ts` prod block SHALL be a single `new ZitadelProdStackComponent(...)` invocation that replaces the prior `new BackendMachineKeyComponent(...)` line; the new component SHALL internally wrap the backend MachineKey provisioning logic so the existing `zitadel-machine-key-for-backend-app` GSM Secret + IAM binding are preserved (no destroy-replace, no URN churn for those subordinate resources).

**Rationale**: A top-level wrapper preserves the thin-dispatch shape of `src/index.ts` (per `CLAUDE.md` "Main entry point dispatching to GCP and GitHub components") while keeping dev's `Zitadel` class verbatim — no dev URN churn. A `ComponentResource` also enables atomic `pulumi destroy --target` semantics for recovery: a single target removes the entire prod Zitadel application stack subtree, instead of leaving partial state across 9 leaves.

#### Scenario: Prod index.ts dispatches via a single component

- **WHEN** `cloud-provisioning/src/index.ts` is inspected for the prod-environment branch
- **THEN** it SHALL contain exactly one `new ZitadelProdStackComponent(...)` instantiation
- **AND** it SHALL NOT contain any direct instantiations of `FrontendComponent`, `SmtpComponent`, `ActionsV2Component`, `LoginClientComponent`, `GoogleAdminIdpComponent`, `AdminOrgConfigComponent`, `HumanAdminComponent`, `zitadel.Project`, or the imported `zitadel.Org('admin', ...)` outside of `ZitadelProdStackComponent`
- **AND** the prior `new BackendMachineKeyComponent(...)` line SHALL no longer appear at the `index.ts` top level (its responsibility is absorbed into `ZitadelProdStackComponent`)

#### Scenario: Backend MachineKey resources keep their URNs after the wrap

- **WHEN** `pulumi preview --stack prod` runs against the change introducing `ZitadelProdStackComponent`
- **THEN** the `zitadel-machine-key-for-backend-app` GSM Secret, SecretVersion, and IAM accessor binding SHALL NOT be marked for delete or replace
- **AND** the existing backend `MachineUser`, `MachineKey`, and `OrgMember` resources SHALL NOT be marked for delete or replace
- **AND** any URN change SHALL be expressed via Pulumi `aliases: [{ name: 'old-urn' }]` rather than a destroy-replace cycle (per the `reference_pulumi_aliases_urn_rename.md` operating rule)

### Requirement: Prod LoginClient PAT Stored in GSM as zitadel-login-pat

The prod Pulumi stack SHALL persist the `login-client` `PersonalAccessToken` to a Pulumi-managed `gcp.secretmanager.Secret` named `zitadel-login-pat` in project `liverty-music-prod`, with at least one enabled SecretVersion containing the PAT value (wrapped in `pulumi.secret()` before being passed to the SecretVersion's `secretData` argument) and an IAM accessor binding granting `roles/secretmanager.secretAccessor` to the ESO Workload Identity SA (`k8s-external-secrets@liverty-music-prod.iam.gserviceaccount.com`). The in-cluster `zitadel-web` Pod consumes this PAT via an `ExternalSecret` that mirrors the GSM Secret into a K8s Secret named `zitadel-web-pat`; Reloader rolls the `zitadel-web` Deployment on the K8s Secret change.

**Rationale**: Without a `login-client` PAT, the `zitadel-web` (Login V2 UI) container's `ZITADEL_SERVICE_USER_TOKEN_FILE` is unmounted and the Pod stays in `ContainerCreating`. The Console login page returns 401 and the end-user sign-in flow stalls at the UI layer. The `pulumi.secret()` wrap is required because the `@pulumiverse/zitadel` provider's `PersonalAccessToken.token` output is a plain `Output<string>` — without the wrap, the PAT would surface in plaintext in Pulumi state history. GSM-mediated delivery (rather than a direct K8s Secret) matches the dev path and provides audit logging via Cloud Logging.

#### Scenario: GSM Secret created and accessible to ESO

- **WHEN** `pulumi up --stack prod` completes for the change introducing this requirement
- **THEN** the GSM Secret `zitadel-login-pat` (project `liverty-music-prod`) SHALL exist with at least one enabled SecretVersion
- **AND** the SecretVersion's `secretData` SHALL have been written via a Pulumi `pulumi.secret()`-wrapped value (so the PAT does not appear in plaintext in Pulumi state history)
- **AND** an IAM accessor binding (`roles/secretmanager.secretAccessor`) SHALL grant access to `k8s-external-secrets@liverty-music-prod.iam.gserviceaccount.com`

#### Scenario: zitadel-web Pod transitions to Running after ESO sync

- **WHEN** ESO syncs the GSM Secret `zitadel-login-pat` into the K8s Secret `zitadel-web-pat` (namespace `zitadel`)
- **AND** Reloader rolls the `zitadel-web` Deployment
- **THEN** the `zitadel-web` Pod SHALL transition from `ContainerCreating` to `Running` (1/1 Ready)
- **AND** the `zitadel-web` container SHALL successfully read the PAT from the file mounted at `ZITADEL_SERVICE_USER_TOKEN_FILE`

### Requirement: Prod Google OAuth Web Client Provisioned Out-of-Band

The prod Google OAuth 2.0 Web Application client (consumed by `GoogleAdminIdpComponent` as `clientId` + `clientSecret`) SHALL be created manually in Google Cloud Console (project `liverty-music-prod`) as a pre-flight step before the first `pulumi up --stack prod` of the change introducing this requirement. The client SHALL be distinct from the dev Google OAuth client (separate `client_id`, separate `client_secret`) and SHALL list `https://auth.liverty-music.app/ui/v2/login/login/callback` as an authorized redirect URI. The resulting credentials SHALL be seeded into ESC `liverty-music/prod` as `pulumiConfig.zitadel.googleAdminIdp.clientId` (plaintext) and `pulumiConfig.zitadel.googleAdminIdp.clientSecret` (secret-marked). The prod Pulumi stack SHALL consume these via Pulumi config; no Pulumi-managed `gcp.iap.*` or other IaC mechanism SHALL be used to create the OAuth client.

**Rationale**: No Google API supports IaC creation of OAuth clients on a Google Cloud project — the Cloud Console GUI is the only path. A distinct prod client preserves blast-radius separation (a dev client_secret leak must not compromise prod operator sign-in) and matches the dev path's out-of-band creation pattern.

#### Scenario: Prod OAuth client distinct from dev

- **WHEN** the prod Google OAuth client and the dev Google OAuth client are inspected in Google Cloud Console
- **THEN** they SHALL have distinct `client_id` values
- **AND** the prod client's authorized redirect URIs SHALL include `https://auth.liverty-music.app/ui/v2/login/login/callback`
- **AND** SHALL NOT include any `auth.dev.liverty-music.app` URI

#### Scenario: ESC seeded before first pulumi up

- **WHEN** the operator runs `esc env get liverty-music/prod` before the first `pulumi up --stack prod` of the change introducing this requirement
- **THEN** `pulumiConfig.zitadel.googleAdminIdp.clientId` SHALL be a non-empty string
- **AND** `pulumiConfig.zitadel.googleAdminIdp.clientSecret` SHALL be a non-empty string marked secret
- **AND** `pulumiConfig.zitadel.adminGoogleSubs.pannpers` SHALL be a non-empty string (the Google `sub` claim for the human admin, secret-marked)
- **AND** `pulumiConfig.postmark.serverApiToken` SHALL be a non-empty string marked secret (already seeded during the dev cutover; re-used for prod with no separate value)
- **AND** the admin JWT used by `HumanAdminComponent`'s dynamic-resource API call SHALL NOT require a separate ESC entry — it is sourced inside `ZitadelProdStackComponent` from GSM `zitadel-machine-key-for-pulumi-admin` at plan time via `getSecretVersionAccessOutput` (wrapped in `pulumi.secret()`) and routed through `BackendMachineKeyComponent.adminJwt`

## MODIFIED Requirements

### Requirement: Bootstrap Admin Machine Key Stored in Secret Manager

On first startup of an empty database, Zitadel SHALL create an initial admin machine user by consuming `ZITADEL_FIRSTINSTANCE_*` environment variables, write the resulting JWT-profile JSON key to a shared `emptyDir` pod volume, and a `bootstrap-uploader` sidecar container co-located in the same Zitadel API Pod SHALL upload that key to GCP Secret Manager as `zitadel-machine-key-for-pulumi-admin`; subsequent Pulumi stack applies SHALL read the key from Secret Manager as the `jwtProfileJson` for the Zitadel provider. This lifecycle SHALL apply identically in both the dev and prod stacks. After the `complete-zitadel-prod-pulumi-stack` change is applied, both stacks SHALL produce the full set of Zitadel-side resources — admin org (imported), product org (`liverty-music`), Project, Frontend ApplicationOidc, SmtpConfig + activation, Actions V2 Target + Execution, login-client MachineUser + PAT + GSM Secret, Google IdP, admin-org and instance LoginPolicies, human admin (with IdP link), and backend MachineKey + GSM Secret. The dev stack SHALL additionally produce the E2E test user (`E2eTestUserComponent`); the prod stack SHALL NOT produce an E2E test user (deferred to a follow-up change).

**Rationale**: This closes the bootstrap chicken-and-egg — Pulumi needs admin credentials to configure Zitadel, but admin credentials only exist after Zitadel has bootstrapped itself. Shifting the boundary into the cluster avoids manual human steps. A separate Kubernetes `Job` cannot share an `emptyDir` volume with the Zitadel Deployment Pod (volumes are Pod-scoped), so the uploader runs as a sidecar container inside the Zitadel API Pod where the shared volume is naturally accessible. The sidecar idles after the upload (`tail -f /dev/null`) so the Pod stays ready and the upload is idempotent across Pod restarts (it skips re-uploading when the stored GSM version already matches).

The GSM name `zitadel-machine-key-for-pulumi-admin` follows the platform-wide convention `zitadel-machine-key-for-<principal>`, where `<principal>` is the Pulumi `MachineUser` resource id. The legacy name `zitadel-admin-sa-key` was renamed because (1) it did not encode the binding between the GSM secret and the owning Zitadel principal, and (2) the principal label `admin` did not match the Pulumi `MachineUser` resource id `pulumi-admin`.

After the `complete-zitadel-prod-pulumi-stack` change extends prod coverage to dev parity (minus E2E test infra), both stacks SHALL reach the same baseline of Zitadel-side resource counts. The admin org's `IsDefault=true` flag (set by the bootstrap) SHALL be preserved in both stacks; the prod admin org is brought into Pulumi state via a one-time `pulumi import zitadel:index/org:Org admin <prod-admin-org-id>`, while the dev admin org has been Pulumi-managed via the same import pattern since the original dev cutover.

#### Scenario: First boot writes the admin key

- **WHEN** the Zitadel API container starts against an empty database
- **THEN** `ZITADEL_FIRSTINSTANCE_MACHINEKEYPATH` SHALL point to a path on an `emptyDir` volume mounted into both the Zitadel container and the `bootstrap-uploader` sidecar container in the same Pod
- **AND** Zitadel SHALL write a JSON key file at that path
- **AND** the `bootstrap-uploader` sidecar container in the same Pod SHALL upload the file to GCP Secret Manager secret `zitadel-machine-key-for-pulumi-admin`
- **AND** the `bootstrap-uploader` sidecar SHALL unlink the key file from the shared `emptyDir` after a successful GSM upload, so the org-admin private key does not persist in the volume for the Pod's lifetime where any future co-located container with the same `volumeMount` could read it

#### Scenario: Subsequent boots skip bootstrap

- **WHEN** Zitadel starts against an already-initialized database
- **THEN** the `ZITADEL_FIRSTINSTANCE_*` environment variables SHALL be ignored
- **AND** the existing admin machine user and key in Secret Manager SHALL remain unchanged

#### Scenario: Both stacks reach Zitadel-side parity after the prod stack change

- **WHEN** `pulumi up` has been run for both the dev stack and the prod stack against the change introducing this requirement (`complete-zitadel-prod-pulumi-stack`)
- **THEN** each stack's resulting Pulumi state SHALL contain the admin org (imported with `protect: true`), the `liverty-music` product org, a `zitadel.Project`, a frontend `ApplicationOidc` + product-org `LoginPolicy`, a `SmtpConfig` + `ZitadelSmtpActivation`, an Actions V2 `Target` + `Execution`, a `login-client` `MachineUser` + instance role + `PersonalAccessToken` + GSM `zitadel-login-pat`, an instance-level `IdpGoogle`, an admin-org `LoginPolicy` + instance `DefaultLoginPolicy`, a `HumanUser` for the human admin + instance `IAM_OWNER` member + `ZitadelUserIdpLink`, and a backend `MachineUser` + `MachineKey` + GSM `zitadel-machine-key-for-backend-app`
- **AND** the dev stack SHALL additionally contain an `E2eTestUserComponent` (HumanUser + permanent-password dynamic resource)
- **AND** the prod stack SHALL NOT contain an `E2eTestUserComponent`
