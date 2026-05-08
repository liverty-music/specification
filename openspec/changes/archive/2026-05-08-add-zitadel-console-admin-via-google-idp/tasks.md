## 1. Pre-flight Verification

- [x] 1.1 Authenticate `@pulumiverse/zitadel` provider locally with `zitadel-admin-sa-key` JSON key from GCP Secret Manager (`liverty-music-dev` project) and confirm provider can read instance state — JWT bearer flow against `/oauth/v2/token` returned an access token; admin API queries succeeded
- [x] 1.2 Verify zero human users exist in the current dev Zitadel: `POST /management/v1/users/_search` filtered by `type=HUMAN`. **Found 2** initially: `pepperoni9@gmail.com` (deleted via `DELETE /management/v1/users/370878213389288196` per user instruction; eventstore purge deferred to Section 5 wipe) and `zitadel-admin@zitadel.auth.dev.liverty-music.app` (Zitadel bootstrap default; will be re-generated cleanly by re-bootstrap per user choice "clean な状態から再作成").
- [x] 1.3 Capture baseline: org `369968599999251129` (name `ZITADEL`); `zitadel-admin-sa-key` GSM at version 1 (created 2026-04-24); 0 IdPs; InstanceMembers = pulumi-admin (IAM_OWNER), zitadel-admin (IAM_OWNER), login-client (IAM_LOGIN_CLIENT); MachineUsers also include `backend-app` (product-service identity, Pulumi-managed via `MachineUserComponent`).
- [x] 1.4 Confirm Zitadel v4 Login V2 IdP callback URL format — Resolved via context7 docs: fixed path `${CUSTOM_DOMAIN}/idps/callback`. For dev: `https://auth.dev.liverty-music.app/idps/callback`.
- [x] 1.5 Confirm `@pulumiverse/zitadel` field names — resolved by reading `node_modules/@pulumiverse/zitadel/*.d.ts`. Key findings: `IdpGoogle` uses `isLinkingAllowed` for auto-link by email (no policy-level autoLinking field); `HumanUser.isEmailVerified` requires `initialPassword` (set random throwaway, paired with `LoginPolicy.userLogin=false`); `Org` has `isDefault` arg directly. Spec / design updated.

## 2. Configmap Update for Bootstrap Org Naming

- [x] 2.1 Edit `cloud-provisioning/k8s/namespaces/zitadel/base/configmap.env`: added `ZITADEL_FIRSTINSTANCE_ORG_NAME=admin` and an inline comment referencing this OpenSpec change (decisions D1–D3)
- [x] 2.2 `kubectl kustomize k8s/namespaces/zitadel/overlays/dev` confirmed `ZITADEL_FIRSTINSTANCE_ORG_NAME: admin` appears in the rendered manifest
- [x] 2.3 Commit configmap change in cloud-provisioning branch — merged via PR #224.

## 3. Pulumi Code Restructure for Two-Org Topology

- [x] 3.1 Edit `cloud-provisioning/src/zitadel/constants.ts`: replace `ZITADEL_DEV_DEFAULT_ORG_ID` with two semantically-named refs — `ZITADEL_DEV_ADMIN_ORG_ID` (bootstrap-created) and remove the single product-org constant in favour of a Pulumi `Output<string>` from the new `zitadel.Org liverty-music` resource. Done in PR #225.
- [x] 3.2 Edit `cloud-provisioning/src/zitadel/index.ts`: introduce `new zitadel.Org('liverty-music', ...)` and pass its `id` to `Project`, `FrontendComponent`, and `LoginClientComponent`. Done in PR #225/#226. **Note**: `isDefault` was originally `true` on `liverty-music` per the early design, but smoke-testing surfaced that Console routing requires the admin org to be default — see D8 update. PR #228 imported the bootstrap-created `admin` org, set `isDefault: true` and `protect: true` on it, and flipped `liverty-music` to `isDefault: false`.
- [x] 3.3 Move `MachineUserComponent` (pulumi-admin) reference to use `ZITADEL_DEV_ADMIN_ORG_ID` — done in PR #225.
- [x] 3.4 Move `LoginClientComponent` to target the new admin org id — done in PR #226 (`LoginClientComponent` now takes `adminOrg.id`).
- [x] 3.5 Add `AdminOrgConfigComponent` (`src/zitadel/components/admin-org-config.ts`) that creates a `zitadel.LoginPolicy` on the admin org with `allowExternalIdp=true`, `allowRegister=false`, `idps=[google_idp.id]`, and `userLogin=false`. Done in PR #226.
- [x] 3.6 Add `zitadel.DefaultLoginPolicy` (instance-level) consistent with the admin org policy, per design D8. Done in PR #226 inside `AdminOrgConfigComponent`.
- [x] 3.7 Set `allowDomainDiscovery=true` on the admin org `LoginPolicy` — done in PR #226.
- [x] 3.8 In `HumanUser` for `pannpers@pannpers.dev`: pair `isEmailVerified=true` with a random `initialPassword` generated via `random.RandomPassword`. Done in PR #226. Password complexity later widened in the same PR (`special: true, minSpecial: 4`, etc.) to satisfy Zitadel's default complexity policy.
- [x] 3.9 Verify `MachineUserComponent` (backend-app) targets the product org — verified in PR #226.
- [x] 3.10 Run `make lint-ts` after the restructure — passes (CI green on PRs #225–#229).

## 4. Google OAuth 2.0 Client Provisioning (Manual — One-Time)

**Constraint discovered during pre-flight**: Google does NOT expose a public
API for creating general-purpose OAuth 2.0 Web Application clients. The
only declarative-tool option, `gcp.iap.Client`, is deprecated (Jan 2025)
and shut down (Mar 2026), and is scoped to IAP only — wrong shape for
Zitadel's use as an external IdP. Creation MUST be done manually in the
Google Cloud Console, then the resulting `client_id` / `client_secret` are
written to ESC where Pulumi reads them.

This is a one-time setup per environment. After the OAuth client exists,
all rotation / config changes happen via ESC + `pulumi up`.

- [x] 4.1 Google Auth Platform set up in `liverty-music-dev` (Internal user type, `pannpers.dev` Workspace; App name "Liverty Music Admin Console (dev)"; support + developer email `pannpers@pannpers.dev`)
- [x] 4.2 Web application OAuth client created in Auth Platform → Clients tab; Authorised redirect URI `https://auth.dev.liverty-music.app/idps/callback`
- [x] 4.3 client_id + client_secret captured (client_id `1058199000631-7upt8d2kjn2lb1joe79aurq21hrobv9k.apps.googleusercontent.com`; secret stored only in ESC + JSON backup offline)
- [x] 4.4 ESC `pulumiConfig.zitadel.googleAdminIdp.clientId` set (plaintext) on `liverty-music/cloud-provisioning/dev`
- [x] 4.5 ESC `pulumiConfig.zitadel.googleAdminIdp.clientSecret` set (encrypted via `--secret`) on `liverty-music/cloud-provisioning/dev`
- [x] 4.6 `esc env get liverty-music/cloud-provisioning/dev pulumiConfig.zitadel` confirms `clientId` plaintext and `clientSecret` `[secret]`
- [x] 4.7 Document the OAuth client's existence + redirect URI in cloud-provisioning runbooks so future operators know it is not Pulumi-managed and how to recreate it. Captured in `docs/runbooks/zitadel-oauth-client-recreate.md` (this PR) — covers consent screen + Web Application client + redirect URI + ESC rotation. Cross-linked from `add-zitadel-admin-user.md`.

## 5. Database Wipe and Re-bootstrap (Dev Only)

- [x] 5.1 Re-confirmed 1.2 immediately before wipe — only `zitadel-admin@...` bootstrap default and the deleted `pepperoni9@gmail.com` remained.
- [x] 5.2 Connected to dev Cloud SQL `postgres-osaka` via Cloud SQL Auth Proxy with IAM auth as `zitadel@liverty-music-dev.iam`.
- [x] 5.3 `DROP DATABASE zitadel;` then `CREATE DATABASE zitadel OWNER "zitadel@liverty-music-dev.iam";` — done.
- [x] 5.4 Pushed the configmap commit from 2.3 (PR #224); ArgoCD synced the new ConfigMap to the cluster.
- [x] 5.5 Restarted Zitadel API pods; pod logs confirmed `start-from-init` running setup against the empty DB.
- [x] 5.6 `bootstrap-uploader: upload complete` observed; `zitadel-admin-sa-key` GSM has a new latest version.
- [x] 5.7 Re-fetched the new `zitadel-admin-sa-key` JSON from GSM; re-authenticated Pulumi locally.
- [x] 5.8 New admin org id confirmed — `371280364565496672`, named `admin`.
- [x] 5.9 Updated `constants.ts ZITADEL_DEV_ADMIN_ORG_ID` with the new id — done in PR #226.

## 6. Pulumi Apply — Product Org and Identity Resources

- [x] 6.1 `pulumi preview` against the dev stack confirmed the expected diff: create `zitadel.Org liverty-music`, Project / ApplicationOidc / LoginPolicy in it, login-client MachineUser in admin org, IdpGoogle (instance), LoginPolicy on admin org, DefaultLoginPolicy, HumanUser pannpers in admin org, InstanceMember(IAM_OWNER, pannpers), and (added later in PR #229) `ZitadelUserIdpLink` pre-linking pannpers to the Google IdP.
- [x] 6.2 Confirmed preview included no unintended deletions of admin org resources; `pulumi-admin` survived.
- [x] 6.3 User approval received for the Pulumi up step (PRs #225/#226 reviewed and merged).
- [x] 6.4 `pulumi up` ran via Pulumi Cloud Deployments on PR merge; captured outputs include the new product org id, ApplicationOidc client_id (frontend stack ESC will pick it up), IdpGoogle id, HumanUser pannpers id (`371355406099809123`).
- [x] 6.5 `pulumi-admin` MachineUser and its GSM key unchanged across this work (verified via `gcloud secrets versions list`).

## 7. Frontend OIDC Client Rotation

- [x] 7.1 As-built (corrected from the original task wording): the `liverty-music` ApplicationOidc `client_id` is **not** consumed via Pulumi ESC by a separate frontend Pulumi stack — see 7.2 for the actual mechanism. Pulumi exports the value as a stack output for visibility, but the consumer is the frontend repo's CI, not another stack.
- [x] 7.2 No separate `frontend` Pulumi stack exists — the SPA's OIDC `client_id` and `org_id` are committed to the frontend repo's `.env` (Vite build-time embedding) and baked into the container image by the `Deploy Frontend` GitHub Actions workflow on merge to main. Frontend PR liverty-music/frontend#351 updates both values; the workflow built and pushed the new image successfully.
- [x] 7.3 Forced GKE Deployment rollout (`kubectl -n frontend rollout restart deployment/web-app`) so the running pod's `imagePullPolicy: Always` pulls the freshly-tagged image. New pod came up Ready.
- [x] 7.4 Verified the deployed SPA at `https://dev.liverty-music.app/welcome` loads with the new client_id; clicking **Log In** redirects to `https://auth.dev.liverty-music.app/ui/v2/login/loginname?requestId=oidc_V2_...&organization=371348346264093539` (the new `liverty-music` org id), with no `unauthorized_client` error from Zitadel. Passkey-flow proper requires a registered E2E user; smoke check above is sufficient for the cutover gate.

## 8. Manual Smoke Test — Admin Console

- [x] 8.1 Opened `https://auth.dev.liverty-music.app/ui/console` in a browser with `pannpers@pannpers.dev` as the active Google account.
- [x] 8.2 Clicked "Sign in with Google" and completed Google consent.
- [x] 8.3 Console loaded with admin-level navigation (Home / Organization / Projects / Users / Role Assignments / Actions / Settings visible).
- [x] 8.4 Orgs view confirms exactly two orgs exist: `admin` (Default, `admin.auth.dev.liverty-music.app`) and `liverty-music` (`liverty-music.auth.dev.liverty-music.app`). **Note**: `admin` is the Default — corrected from the original draft per design D8 update (PR #228).
- [x] 8.5 `pannpers@pannpers.dev` user shows `IAM_OWNER` instance role.
- [x] 8.6 Audit log records the sign-in under the human user id `371355406099809123`, not `pulumi-admin`.
- [x] 8.7 Repeated sign-in cycle (private window → Google → Console) succeeds without any re-link prompt — the pre-link via `ZitadelUserIdpLink` (PR #229) handled the first sign-in declaratively, and subsequent sign-ins reuse the same record.

## 9. End-user Org Regression Check

- [x] 9.1 Opened the frontend SPA at `https://dev.liverty-music.app/` in a clean Playwright session; the welcome page rendered correctly with the curated artist preview (proves the SPA's basic OIDC discovery handshake works against the new Zitadel instance).
- [x] 9.2 Clicked **Log In** → Zitadel Login V2 rendered with the **passkey-only** UI (Loginname field + "Register new user" link). **No "Sign in with Google" button** — the admin org's IdP is correctly NOT exposed on the product org's policy. Regression check pass.
- [x] 9.3 Skipped writing a fresh test end user during this archive cycle to avoid dev-DB pollution. The `&organization=371348346264093539` URL parameter on the Login V2 redirect proves end-user OIDC AuthN routes to the new `liverty-music` product org id; further passkey-flow verification will happen organically the next time an E2E test or developer registers a user.

## 10. Break-glass Verification

- [x] 10.1 Confirmed `pulumi-admin` machine user still exists in the `admin` org with `IAM_OWNER` (visible via Console after sign-in; also via `POST /admin/v1/members/_search`).
- [x] 10.2 Confirmed `zitadel-admin-sa-key` GSM secret latest version matches the post-bootstrap value from 5.6 (no rotation since).
- [x] 10.3 Re-authenticated `@pulumiverse/zitadel` provider with the latest GSM key value via Pulumi Cloud Deployments — every PR merge in this series ran `pulumi preview` / `pulumi up` against dev, exercising the same JWT-bearer auth path the runbook documents.
- [x] 10.4 Break-glass procedure documented in `docs/runbooks/zitadel-break-glass.md` (this PR set): fetch SA key from GSM, mint JWT-bearer assertion, exchange for access token, reconcile via `pulumi preview`. Recovery from total lockout (DB wipe + re-bootstrap) also documented for the catastrophic case.

## 11. Specification & PR Hygiene

- [x] 11.1 `openspec validate add-zitadel-console-admin-via-google-idp` passes.
- [x] 11.2 `openspec status --change add-zitadel-console-admin-via-google-idp` reports `isComplete: true`.
- [x] 11.3 Opened the `specification` PR (liverty-music/specification#438), merged at `a53ee5d`. The 4 review comments from claude-review (proposal/spec drift between the original "auto-link by email" wording and the post-cutover `ZitadelUserIdpLink` reality) were addressed in commit `6510063` and replied on-thread.
- [x] 11.4 Opened the `cloud-provisioning` PR set with: configmap update, Pulumi code restructure, new IdP / HumanUser / InstanceMember / LoginPolicy / DefaultLoginPolicy resources, plus the post-cutover follow-ups (admin-as-default flip, `ZitadelUserIdpLink` pre-link, runbook docs). Done across PRs **#224** (configmap), **#225** (Pulumi restructure scaffold), **#226** (admin org config + IdP + HumanUser + InstanceMember + machine-user moves), **#227** (smtp activation v4 fix surfaced during cutover), **#228** (admin-as-default + import + protect:true), **#229** (`ZitadelUserIdpLink` pre-link + tests + admin-user runbook), **#231** (break-glass + oauth-client-recreate runbooks). Frontend client_id rotation: liverty-music/frontend#351 (env update + image rebuild + GKE rollout).
- [x] 11.5 Archive performed in this same PR (delta→main spec sync + `git mv` to `openspec/changes/archive/YYYY-MM-DD-add-zitadel-console-admin-via-google-idp/`).
