## 1. Pre-flight & Confirmations

- [x] 1.1 Verify Cloud SQL `postgres-osaka` `databaseVersion` is `POSTGRES_18` via Pulumi code inspection (no live query needed)
- [x] 1.2 Confirm latest `ghcr.io/zitadel/zitadel` and `ghcr.io/zitadel/login` image tags are `v4.11.0` or later; pin exact version in Helm values
- [ ] 1.3 Take a pre-migration Cloud SQL backup snapshot (manual via console or gcloud) and note the backup id
- [ ] 1.4 Record current Zitadel Cloud tenant export (orgs, projects, applications) for reference during cutover verification

## 2. cloud-provisioning — Cloud SQL & GCP Resources

- [x] 2.1 In `src/gcp/components/postgres.ts`, add a `zitadel` `gcp.sql.Database` resource on `postgres-osaka`
- [x] 2.2 Add a `gcp.sql.User` of type `CLOUD_IAM_SERVICE_ACCOUNT` named `zitadel@liverty-music-dev.iam`
- [x] 2.3 Grant the IAM user ownership of the `zitadel` database via a `gcp.sql.DatabaseIAMGrant` or an equivalent SQL helper (post-deploy task runner) _Implemented as a one-shot Kubernetes Job (`zitadel-db-grant`, see `k8s/namespaces/zitadel/base/job-grant-db.yaml`) instead of a Pulumi resource: Cloud SQL is PSC-only and Pulumi Cloud Deployments runs outside the VPC, so the `postgresql` provider cannot reach the instance. The Job authenticates as the built-in `postgres` superuser via password (pulled from GSM via ESO), then runs `GRANT "zitadel@…iam" TO postgres; ALTER DATABASE zitadel OWNER TO …; GRANT ALL ON SCHEMA public TO …`. The first GRANT is required because Cloud SQL's `postgres` is `cloudsqlsuperuser` (not a true PG SUPERUSER) and PG demands role membership for `ALTER DATABASE OWNER`. Mirrors the atlas-operator pattern already used by backend._
- [x] 2.4 Create GCP service account `zitadel@liverty-music-dev.iam.gserviceaccount.com` with `roles/cloudsql.instanceUser` and `roles/cloudsql.client`
- [x] 2.5 Bind Workload Identity: K8s SA `zitadel/zitadel` → GCP SA `zitadel@liverty-music-dev.iam`
- [x] 2.6 Create DNS A record `auth.dev.liverty-music.app` pointing at the GKE Gateway IP via Cloudflare Pulumi resources _Implemented in **Cloud DNS**, not Cloudflare directly: the `dev.liverty-music.app` zone is delegated from Cloudflare to GCP Cloud DNS (`liverty-music-app-public-zone`), so subdomain records live there. See `zitadel-a-record` and `zitadel-dns-auth-cname` in `src/gcp/components/network.ts`._
- [x] 2.7 Add Google-managed certificate for `auth.dev.liverty-music.app` attached to the existing dev Gateway _Diverged: rather than adding the hostname to the existing shared `api-gateway-cert`, the cert layer was refactored into per-service Certificates (cloud-provisioning#203). GCP Certificate Manager treats `managed.domains` as immutable, so adding a SAN to a cert in use by other CertificateMapEntries forces a delete-blocked-replace deadlock. Per-service certs (`backend-server-cert`, `web-app-cert`, `zitadel-cert`) avoid the deadlock and isolate ACME failures per hostname. The `zitadel-cert` is bound to the existing dev Gateway via a new `zitadel-cert-map-entry` on the shared `api-gateway-cert-map`._

## 3. cloud-provisioning — GCP Secret Manager

- [x] 3.1 Generate a 32-byte random masterkey via `random.RandomString({length:32, special:false})` and write to GSM secret `zitadel-masterkey`
- [x] 3.2 Create placeholder GSM secret `zitadel-admin-sa-key` (value set by bootstrap Job at first run; Pulumi only provisions the secret resource itself and its IAM binding)
- [x] 3.3 Grant ESO service account `roles/secretmanager.secretAccessor` on both new secrets
- [x] 3.4 Retain existing `zitadel-postmark-smtp` GSM secret and its ESO binding unchanged

## 4. cloud-provisioning — Pulumi Dynamic Resource for Actions v2

- [x] 4.1 Create new directory `src/zitadel/dynamic/` with `zitadel-api-client.ts` implementing `getAccessToken(jwtProfileJson)` via OIDC `client_credentials` grant
- [x] 4.2 Implement `ZitadelTarget` class extending `pulumi.dynamic.Resource` with create/read/update/delete calling `/v2/actions/targets`
- [x] 4.3 Implement `ZitadelExecutionFunction` class with create/read/update/delete calling `/v2/actions/executions`
- [x] 4.4 Implement `ZitadelExecutionRequest` class for the auto-verify-email user-creation interception
- [ ] 4.5 Add unit tests for the Dynamic Resource lifecycle using a mocked HTTP client
- [x] 4.6 Export classes from `src/zitadel/dynamic/index.ts`

## 5. cloud-provisioning — Rewrite src/zitadel/ for self-hosted target

_§5.1–5.4 and 5.7 are deferred to the **cutover PR** per the reshape strategy adopted in cloud-provisioning#199 (keep Cloud tenant resources live until cutover; ship `ActionsV2Component` + Dynamic Resources defined-but-unused so cutover is a single-PR provider-domain swap)._

- [ ] 5.1 In `src/zitadel/index.ts`, change provider `domain` input from `config.domain` (cloud) to `auth.dev.liverty-music.app`
- [ ] 5.2 Change `jwtProfileJson` source from Pulumi config to `gcp.secretmanager.getSecretVersion({secret:"zitadel-admin-sa-key"})`
- [ ] 5.3 Remove `src/zitadel/components/token-action.ts` (v1 Action + TriggerActions)
- [ ] 5.4 Remove `src/zitadel/scripts/add-email-claim.js` (v1 JS)
- [x] 5.5 Create `src/zitadel/components/actions-v2.ts` instantiating two `ZitadelTarget`s and their corresponding `ZitadelExecutionFunction` / `ZitadelExecutionRequest`
- [x] 5.6 _Dropped_ — `src/zitadel/components/frontend.ts` redirect URIs require **no change**. Redirect URIs point at the OIDC **client** (frontend SPA at `https://dev.liverty-music.app/auth/callback`), not at the IdP. Only the **issuer** hostname changes (from `dev-svijfm.us1.zitadel.cloud` to `auth.dev.liverty-music.app`); the issuer is configured by the Pulumi provider `domain` input (task 5.1), not by redirect URIs.
- [ ] 5.7 Update `src/index.ts` to pass the new `domain` and `jwtProfileJson` args to the Zitadel component
- [x] 5.8 Run `make lint-ts` and fix any type errors

## 6. cloud-provisioning — Kustomize base for zitadel namespace

- [x] 6.1 Create `k8s/namespaces/zitadel/base/namespace.yaml`
- [x] 6.2 Create `k8s/namespaces/zitadel/base/serviceaccount.yaml` with Workload Identity annotation pointing at `zitadel@...iam.gserviceaccount.com`
- [x] 6.3 Create `k8s/namespaces/zitadel/base/configmap.yaml` with Zitadel YAML config (ExternalDomain, ExternalSecure, TLS mode, Database.postgres.Host/Port/User/Database, Admin.ExistingDatabase, FIRSTINSTANCE env)
- [x] 6.4 Create `k8s/namespaces/zitadel/base/external-secret.yaml` for `zitadel-masterkey` and `zitadel-admin-sa-key`
- [x] 6.5 Create `k8s/namespaces/zitadel/base/deployment-api.yaml` — main container + cloud-sql-proxy sidecar + emptyDir volume for admin-sa key
- [x] 6.6 Create `k8s/namespaces/zitadel/base/deployment-login.yaml`
- [x] 6.7 Create `k8s/namespaces/zitadel/base/service-api.yaml` and `service-login.yaml`
- [x] 6.8 Create `k8s/namespaces/zitadel/base/httproute.yaml` with path split: `/ui/v2/login/*` → zitadel-login, `/*` → zitadel
- [x] 6.9 Create `k8s/namespaces/zitadel/base/pdb.yaml` with `minAvailable: 1` for each Deployment
- [x] 6.10 _Implemented as sidecar_ — rather than a separate K8s Job coordinating with the main Zitadel container via a shared volume (which would require a PVC), the admin-sa-key upload runs as a third container (`bootstrap-uploader`) in the Zitadel API Pod. Shared `emptyDir` works natively in-pod and is idempotent on restarts. See `deployment-api.yaml`.
- [x] 6.11 Create `k8s/namespaces/zitadel/base/kustomization.yaml` referencing all of the above

## 7. cloud-provisioning — Dev overlay

- [x] 7.1 Create `k8s/namespaces/zitadel/overlays/dev/kustomization.yaml`
- [x] 7.2 Create a configmap patch setting `ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS=3` and `_MAXIDLECONNS=1`
- [x] 7.3 Create a deployment patch setting `replicas: 2`, resource `requests`/`limits` sized for `e2-medium` spot, and `podAntiAffinity` on `kubernetes.io/hostname`
- [x] 7.4 Leave readiness/liveness probe defaults from the base; confirm `/debug/ready` works through the sidecar network namespace
- [ ] 7.5 Apply per-Execution `interruptOnError` policy in `actions-v2.ts`: email-claim injection Execution SHALL use `interruptOnError: true` in every environment (email claim is a hard invariant per the identity-management spec — every access token must carry it); auto-verify-email Execution SHALL use `interruptOnError: false` in `dev` only (fall back to the Zitadel OTP step when the webhook is unreachable) and `interruptOnError: true` in `staging` / `prod` _[deferred to cutover PR alongside wiring `ActionsV2Component`]_

## 8. cloud-provisioning — ArgoCD Application & sync-wave

- [x] 8.1 Add `k8s/argocd-apps/dev/zitadel.yaml` registering the `overlays/dev` path
- [x] 8.2 _Obsoleted by §6.10_ — no separate bootstrap Job resource exists; the admin-sa-key upload is a sidecar container in-pod, so no sync-wave ordering is needed.
- [x] 8.3 Run `make lint-k8s` and fix any kube-linter findings

## 9. backend — Webhook Handlers + Internal-Only Exposure

- [x] 9.1 In `backend/internal/adapter/webhook/` (new directory), add `pre_access_token_handler.go` exposing `POST /pre-access-token` and `auto_verify_email_handler.go` exposing `POST /auto-verify-email`
- [x] 9.2 Reuse the existing `internal/infrastructure/auth` JWT validator to verify the incoming Zitadel-signed JWT body. Extend the validator (or wrap it) to pin the expected `aud` claim per endpoint: `urn:liverty-music:webhook:pre-access-token` and `urn:liverty-music:webhook:auto-verify-email`
- [x] 9.3 Parse the `/pre-access-token` payload shape (`user.human.email`, `user_grants`, `org`) and return `{"append_claims":[{"key":"email","value":<email>}]}`. For `/auto-verify-email`, parse the intercepted `AddHumanUser` request and return a mutated request with `email.is_verified = true`
- [x] 9.4 Unit tests: valid JWT with matching aud → success; invalid signature/issuer/expiry/aud → 401; machine user → empty `append_claims`; aud mismatch between endpoints → 401 even when other claims valid
- [x] 9.5 Serve the webhook handlers on a **separate listener** (`:9090`) inside the backend pod process, distinct from the public Connect-RPC listener on `:8080`. The webhook listener has no `authn.Middleware` (the body-JWT verification replaces header-Bearer auth)
- [x] 9.6 Expose port `9090` on the backend `Deployment` `containerPort` list, and create a new `Service` named `server-webhook-svc` (`ClusterIP`, `port: 9090 -> targetPort: 9090`) alongside the existing `server-svc`. The existing `server-route` HTTPRoute continues to reference only `server-svc`, so the webhook paths are unreachable via the GKE Gateway _Implemented: `containerPort: 9090` added to `k8s/namespaces/backend/base/server/deployment.yaml`; new `service-webhook.yaml` registered in `kustomization.yaml`. The `server-route` HTTPRoute is unchanged and references only `server-svc:80`._
- [x] 9.7 Verify external-access rejection: from outside the cluster, `curl https://api.dev.liverty-music.app/pre-access-token` (or equivalent) SHALL return a Gateway-level 404 because no HTTPRoute rule matches that path _Verified — external request is rejected, but with **HTTP 401**, not Gateway-level 404. The existing `server-route` matches `/*` (catch-all) and forwards `/pre-access-token` to `server-svc:80`; the public `:8080` listener has no route for that path, but the `authn.Middleware` runs before the mux and rejects the unauthenticated request with 401. Security objective (external rejection of webhook surface) is met. If a literal 404 is desired, tighten the HTTPRoute path matchers to enumerate only public paths in a follow-up._
- [x] 9.8 Run `make check` — linting and tests pass

## 10. backend — User Data Truncation Migration

- [ ] 10.1 Generate Atlas migration: `atlas migrate diff --env local truncate_users_for_zitadel_migration`
- [ ] 10.2 Edit the generated migration to `TRUNCATE` `users`, `follows`, `user_onboarding_state`, and any other `external_id`-dependent tables (use `--cascade` if needed)
- [ ] 10.3 Verify the down direction is a no-op with a comment explaining the rollback is to leave the empty tables empty
- [ ] 10.4 Apply locally against the dev DB: `atlas migrate apply --env local`; verify schema health via `make test-integration`

## 11. backend — Configmap & Issuer Switch

- [ ] 11.1 In `cloud-provisioning/k8s/namespaces/backend/overlays/dev/server/configmap.env`, change `OIDC_ISSUER_URL` to `https://auth.dev.liverty-music.app`
- [ ] 11.2 In `k8s/namespaces/backend/overlays/dev/consumer/configmap.env`, apply the same change if the consumer reads the issuer
- [ ] 11.3 Confirm backend `email_verifier` integration still targets the correct Zitadel Management API path under the new domain

## 12. frontend — OIDC Config Switch

- [ ] 12.1 In the frontend GitHub Actions `dev` environment, update secrets `VITE_ZITADEL_ISSUER`, `VITE_ZITADEL_CLIENT_ID`, `VITE_ZITADEL_ORG_ID` to the new instance's values (client id and org id become known after Pulumi stack #2 applies)
- [ ] 12.2 Rebuild and redeploy the dev frontend through ArgoCD Image Updater flow

## 13. Cutover Execution

- [ ] 13.1 Pause ArgoCD `dev` auto-sync on `backend` and `frontend` namespaces (UI or `argocd app set --sync-policy none`)
- [ ] 13.2 Apply cloud-provisioning Pulumi stack #1: Cloud SQL DB/user, GSM placeholders, DNS, managed cert (`pulumi up`)
- [ ] 13.3 Resume ArgoCD auto-sync on `zitadel` namespace only; confirm pods come up, bootstrap Job completes, admin-sa-key lands in GSM
- [ ] 13.4 Apply cloud-provisioning Pulumi stack #2: Zitadel Project/App/LoginPolicy/SMTP/MachineUser/MachineKey/OrgMember + Actions v2 resources (`pulumi up`)
- [ ] 13.5 Apply Atlas migration on the dev backend DB to truncate user-scoped tables
- [ ] 13.6 Resume ArgoCD auto-sync on `backend`; rollout picks up new `OIDC_ISSUER_URL`
- [ ] 13.7 Resume ArgoCD auto-sync on `frontend`; rollout picks up new Vite env; verify SPA loads
- [ ] 13.8 Manual smoke test: landing-page Login flow; Tutorial Step-6 Sign-Up flow; verify JWT `email` claim present in backend logs

## 14. E2E Auth Regeneration

- [ ] 14.1 In `frontend`, regenerate Playwright `.auth/` storage state against the new issuer following the existing `.auth/README.md` procedure (use the test users created against the new Zitadel instance)
- [ ] 14.2 Commit updated `.auth/` artifacts
- [ ] 14.3 Run `npx playwright test` locally and verify all existing E2E tests pass

## 15. Cooldown & Cleanup

- [ ] 15.1 Leave Zitadel Cloud tenant active and unchanged for two weeks post-cutover as a rollback target
- [ ] 15.2 Monitor `/debug/metrics` and backend JWT validation logs daily for the first week; document any anomalies
- [ ] 15.3 After two weeks clean run, open a follow-up change (`archive-zitadel-cloud-tenant`) that deletes the Cloud tenant and removes rollback references

## 16. Rollback Readiness (not executed unless needed)

- [ ] 16.1 Document rollback steps in `openspec/changes/self-hosted-zitadel/rollback.md` (optional, inline in design.md is sufficient)
- [ ] 16.2 Verify Pulumi stack can be re-applied with `domain` reverted to Zitadel Cloud if rollback is triggered
- [ ] 16.3 Verify ArgoCD configmap revert to old `OIDC_ISSUER_URL` is a single commit reversal

## 17. Archive Change

- [ ] 17.1 Run `/opsx:verify self-hosted-zitadel` to confirm implementation matches proposal/design/specs
- [ ] 17.2 Run `/opsx:archive self-hosted-zitadel` to move the change into the archive and fold spec deltas into `openspec/specs/`
