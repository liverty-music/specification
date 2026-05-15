## Why

The prior change `enable-zitadel-prod-pulumi-provider` extracted `BackendMachineKeyComponent` for prod, covering only 3 of the 13 components the dev `Zitadel` class instantiates (Provider, productOrg, MachineUserComponent for backend-app). Post-deployment investigation surfaced **9 additional components** that the prod stack still needs before end users can sign in and operators can manage the system. The current prod state: backend ↔ Zitadel JWT auth works (programmatic), but **no human or end-user can sign in via browser**, **no verification emails go out**, and **the Console is operator-locked**.

This change closes those remaining 9 components in a single coherent Pulumi unit so the prod stack reaches dev parity for application-level auth. The 10th component, `E2eTestUserComponent`, is intentionally deferred — E2E test infra is a separate concern, scoped to a follow-up after launch.

## What Changes

- **NEW**: Refactor dev's `Zitadel` class so the 9 components below can be instantiated for prod *without* duplicating the SaaS-only assumptions baked into the existing class. The cleanest path (per design D1) is to extract a new top-level `ZitadelProdStackComponent` that internally wires the 9 components in dependency order, parallel to how `BackendMachineKeyComponent` already does. Dev keeps its existing `Zitadel` class verbatim; no URN churn on dev.
- **NEW**: Pulumi-managed import of the prod `admin` org (auto-created by first-boot bootstrap via `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin`). One-time `pulumi import zitadel:index/org:Org admin <admin-org-id>` so admin-org-side resources (login policy, human admin, login client) can attach.
- **NEW**: `ProjectComponent` (`zitadel.Project` named `liverty-music`) in the prod product org. The frontend SPA's `ApplicationOidc` lives under this project.
- **NEW**: `FrontendComponent` for prod — creates the `ApplicationOidc` OIDC client (PKCE flow, JWT access tokens) + product-org `LoginPolicy` (passkey + username/password, `userLogin=true`, `allowRegister=true`).
- **NEW**: `SmtpComponent` for prod — Postmark SMTP config + activation (the dynamic resource that calls the Zitadel admin API's `_activate` endpoint). Required for sign-up verification emails.
- **NEW**: `LoginClientComponent` for prod — `login-client` MachineUser in admin org + instance-level `IAM_LOGIN_CLIENT` role + PAT. Backed-by GSM secret `zitadel-login-pat`. Required for the `zitadel-web` (Login V2 UI) container to authenticate to the prod Zitadel API; without it, the Console login page returns 401 and end-user login flow stalls at the UI layer.
- **NEW**: `ActionsV2Component` for prod — `zitadel.Target` (REST webhook to backend's `/pre-access-token` endpoint) + `Execution` binding on the `preaccesstoken` flow. Without this, access tokens issued by prod Zitadel lack the `email` claim, which the backend's `ValidateIdentity` code path *requires* (the backend fails closed when `email` is absent — matches the dev behavior the cutover incident chain hardened).
- **NEW**: `GoogleAdminIdpComponent` for prod — instance-level `IdpGoogle` keyed on a separate prod Google OAuth Web client (NOT the dev client). The OAuth client itself is created out-of-band in Google Cloud Console; this change consumes its credentials via ESC.
- **NEW**: `AdminOrgConfigComponent` for prod — admin-org `LoginPolicy` (`userLogin=false`, `allowRegister=false`, `idps=[googleIdpId]`) + instance-level `DefaultLoginPolicy` mirroring it. Confines Console sign-in to the Google IdP path.
- **NEW**: `HumanAdminComponent` for prod — provisions `pannpers@pannpers.dev` as an `IAM_OWNER` HumanUser in the prod admin org, pre-linked to the prod Google IdP via `ZitadelUserIdpLink` (uses the `dynamic/api-client.ts` admin-API client because the user→IdP link is not exposed as a Pulumi-managed Zitadel resource).
- **NEW**: `cloud-provisioning/src/index.ts` prod block — replaces the current single `new BackendMachineKeyComponent(...)` line with a single `new ZitadelProdStackComponent(...)` line that wraps the 9 components above + the existing 3 (Provider/productOrg/MachineUser). The dispatch line stays thin per CLAUDE.md.
- **NEW**: Prod ESC seeding — new entries in `liverty-music/prod` ESC environment: `pulumiConfig.zitadel.googleAdminIdp.clientId` (plaintext) + `pulumiConfig.zitadel.googleAdminIdp.clientSecret` (secret-marked, prod Google OAuth client), and `pulumiConfig.zitadel.adminGoogleSubs.pannpers` (secret-marked, same `sub` claim as dev — pannpers@pannpers.dev). The Postmark API token is already in `liverty-music/prod` ESC at `pulumiConfig.postmark.serverApiToken`. The admin JWT consumed by `HumanAdminComponent`'s dynamic resource is sourced inside `ZitadelProdStackComponent` from GSM `zitadel-machine-key-for-pulumi-admin` via `getSecretVersionAccessOutput` — no separate ESC entry.
- **OUT OF SCOPE**: `E2eTestUserComponent` (CI test infra; tracked as a follow-up `enable-zitadel-prod-e2e-user`). Backend Atlas migration prod overlay (separate backend-repo PR). Frontend `.env.prod` + CI/CD branch→env mapping (separate frontend-repo PR). The 3 operational-debt items from `enable-zitadel-prod-pulumi-provider` archive (cloudsql.client Pulumi adoption, cross-project AR IAM Pulumi adoption, ESO refresh tuning) — separate follow-ups. The Cloudflare apex `liverty-music.app` A record (Pulumi out of scope by `prod-environment-bootstrap` design D2).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `zitadel-self-hosted-deployment`: ADD 3 new requirements covering the full prod application stack (end-user OIDC application, operator console sign-in path, SMTP activation). MODIFY the existing "Bootstrap Admin Machine Key Stored in Secret Manager" requirement narrative to reference both dev and prod and add a scenario asserting both stacks produce the full set of Zitadel-side resources after this change.

## Impact

- **`cloud-provisioning/src/zitadel/components/`**: NEW component file `zitadel-prod-stack.ts` (top-level ComponentResource wrapping the 9 leaf components). The 9 leaf component files (`frontend.ts`, `smtp.ts`, `actions-v2.ts`, `login-client.ts`, `google-admin-idp.ts`, `admin-org-config.ts`, `human-admin.ts`, plus `project` + `adminOrg` instantiations) stay verbatim — used by both dev's `Zitadel` class and the new prod wrapper.
- **`cloud-provisioning/src/index.ts`**: prod block becomes one `new ZitadelProdStackComponent(...)` instantiation (replacing the current `new BackendMachineKeyComponent(...)`). Dev `if (env === 'dev')` block unchanged.
- **Prod Pulumi state after `pulumi up --stack prod`**: ~20-25 new resources. Concretely:
  - 1 `zitadel.Org` imported (admin) — `protect: true`
  - 1 `zitadel.Project` (liverty-music)
  - 1 `zitadel.ApplicationOidc` + 1 product-org `LoginPolicy` (FrontendComponent)
  - 1 `zitadel.SmtpConfig` + 1 `ZitadelSmtpActivation` dynamic resource (SmtpComponent)
  - 1 `zitadel.Target` + 1 `zitadel.Execution` (ActionsV2Component)
  - 1 `zitadel.MachineUser` `login-client` + 1 instance member + 1 `zitadel.PersonalAccessToken` + 1 GSM `Secret`/`SecretVersion`/`SecretIamMember` for `zitadel-login-pat` (LoginClientComponent)
  - 1 `zitadel.IdpGoogle` (instance-level, GoogleAdminIdpComponent)
  - 1 admin-org `LoginPolicy` + 1 instance `DefaultLoginPolicy` (AdminOrgConfigComponent)
  - 1 `zitadel.HumanUser` (pannpers) + 1 instance member granting IAM_OWNER + 1 `ZitadelUserIdpLink` dynamic resource (HumanAdminComponent)
- **`liverty-music/prod` ESC**: 3 new pulumiConfig entries (plaintext `googleAdminIdp.clientId`; secret-marked `googleAdminIdp.clientSecret` and `adminGoogleSubs.pannpers`). No `pulumiJwtProfileJson` entry — admin JWT is sourced from GSM at plan time inside the component.
- **Out-of-band prerequisite**: a Google Cloud Console OAuth 2.0 Web Application client for prod (`https://auth.liverty-music.app/ui/v2/login/login/callback` redirect URI). Created manually before the first `pulumi up --stack prod` of this change; client_id + secret seeded into ESC.
- **Operational unblocks**: after this change deploys, (a) the SPA on `liverty-music.app` can complete OIDC sign-in against prod Zitadel; (b) sign-up verification emails go out via Postmark; (c) backend access tokens include the `email` claim; (d) `pannpers@pannpers.dev` can sign in to `https://auth.liverty-music.app/ui/console` via Google. The `zitadel-web` Pod (currently in `ContainerCreating` waiting for `zitadel-web-pat` K8s Secret) transitions to `Running` once ESO syncs the new `zitadel-login-pat` GSM Secret.
- **Cost**: zero net infra cost. The 25 new resources are all Zitadel-API-level (no GCP compute) except the `zitadel-login-pat` GSM Secret+Version+IAM (sub-cent/mo). Postmark traffic is per-email; expected band ~$0.20-2/mo for the first months of prod sign-ups.
- **Risk**: the `pulumi import` step for the admin org is a one-time operation that needs the operator to fetch the prod admin-org-id first (via the Zitadel admin API using the bootstrap-uploaded JWT). Documented in tasks.md §1 pre-flight.
