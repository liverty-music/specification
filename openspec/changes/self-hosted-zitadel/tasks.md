## 1. Pre-flight & Confirmations

- [x] 1.1 Verify Cloud SQL `postgres-osaka` `databaseVersion` is `POSTGRES_18` via Pulumi code inspection (no live query needed)
- [x] 1.2 Confirm latest `ghcr.io/zitadel/zitadel` and `ghcr.io/zitadel/login` image tags are `v4.11.0` or later; pin exact version in Helm values
- [x] 1.5 Verify OIDC discovery endpoint: `curl https://auth.dev.liverty-music.app/.well-known/openid-configuration` SHALL return JSON with `issuer = "https://auth.dev.liverty-music.app"`, valid `authorization_endpoint`, `token_endpoint`, `jwks_uri`, and `userinfo_endpoint`. A failure here would block every downstream OIDC flow and MUST be resolved before §13 cutover. _PASS — HTTP 200, 2364 B JSON. `issuer = "https://auth.dev.liverty-music.app"` matches; all 6 expected endpoints present (`/oauth/v2/authorize`, `/oauth/v2/token`, `/oauth/v2/keys`, `/oidc/v1/userinfo`, `/oauth/v2/introspect`, `/oidc/v1/end_session`); `response_types_supported: [code, id_token, id_token token]`._
- [x] 1.6 Verify JWKS endpoint: `curl https://auth.dev.liverty-music.app/oauth/v2/keys` SHALL return a non-empty `keys` array containing JWK objects with `kid`, `kty`, `use`, `alg`. Backend's JWT validator fetches keys from this endpoint; failure means all RPC calls fail with 401 after cutover. _PASS — HTTP 200. Two RSA keys returned: `kid=369968602230555321`, `kid=369968602347995833`, both `kty=RSA`, `use=sig`, `alg=RS256`._
- [x] 1.7 Verify the bootstrap admin machine key authenticates against the new instance: pull `zitadel-admin-sa-key` v1 from GSM, exchange the JWT-profile assertion for an access token via `POST /oauth/v2/token` (`grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer`), then call an authenticated endpoint (e.g. `GET /auth/v1/users/me` or `GET /management/v1/orgs`). **Highest-risk pre-cutover gate**: Pulumi uses this exact key path during cutover to provision Project / Application / Actions v2 resources; if it doesn't authenticate, cutover halts mid-PR. _PASS — pulled key from GSM (userId=`369968599999775417`, keyId=`369968599999840953`), built RS256 JWT bearer assertion, exchanged for access_token (`expires_in=43199`s ≈ 12h), called `/auth/v1/users/me` → 200 with `userName="pulumi-admin"`, type=machine, orgId=`369968599999251129`. Pulumi cutover authentication path is fully functional._
- [x] 1.8 Verify Login UI renders HTML, not just returns 200: `curl -sS https://auth.dev.liverty-music.app/ui/v2/login` SHALL return HTML containing the Login V2 page shell (look for the `<html>` / `<body>` tags and a Next.js script bundle reference). A 200 with empty or error HTML would indicate the Next.js SSR is broken. _PASS — HTTP 200, 30,335 B HTML, `Content-Type: text/html`. Body starts with `<!DOCTYPE html><html class="lato_..."><head>...` and references Next.js bundles at `/ui/v2/login/_next/static/chunks/`._
- [x] 1.9 Verify Zitadel database schemas exist: connect to the `zitadel` Cloud SQL DB (via kubectl debug pod or temporary psql pod with cloud-sql-proxy) and run `\dn`. SHALL return at least the schemas Zitadel creates during init: `projections`, `eventstore`, `system`, `auth`, `adminapi`, `public`. Confirms the "setup completed" log line corresponds to a fully migrated schema. _PASS — verified via temporary `zitadel-schema-check` Pod (postgres:17-alpine + cloud-sql-proxy native sidecar with `--auto-iam-authn`, deleted after run). Schemas present: `adminapi`, `auth`, `cache`, `eventstore`, `logstore`, `projections`, `public`, `queue`, `system` (9 total — exceeds the 6 expected, plus extras for cache/logstore/queue v4 features). All non-`public` schemas owned by `zitadel@liverty-music-dev.iam`. Database owner is `zitadel@liverty-music-dev.iam` (confirms §2.3 ALTER DATABASE OWNER). `eventstore.events2` has 3,042 rows — Zitadel actively populated the event store during init._

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
- [ ] 4.5 Add unit tests for the Dynamic Resource lifecycle using a mocked HTTP client _Deferred — covered in §18.9 follow-up. The cutover incident chain (#211 PATCH→POST, #212 array-of-strings) would have been caught by these tests; high-priority follow-up._
- [x] 4.6 Export classes from `src/zitadel/dynamic/index.ts`

## 5. cloud-provisioning — Rewrite src/zitadel/ for self-hosted target

_§5.1–5.4 and 5.7 were deferred to the **cutover PR** per the reshape strategy adopted in cloud-provisioning#199 (keep Cloud tenant resources live until cutover; ship `ActionsV2Component` + Dynamic Resources defined-but-unused so cutover is a single-PR provider-domain swap). All landed via cloud-provisioning#209 (cutover PR)._

- [x] 5.1 In `src/zitadel/index.ts`, change provider `domain` input from `config.domain` (cloud) to `auth.dev.liverty-music.app` _Implemented via `zitadelDomainMap[env]` indirection in `src/zitadel/constants.ts`._
- [x] 5.2 Change `jwtProfileJson` source from Pulumi config to `gcp.secretmanager.getSecretVersion({secret:"zitadel-admin-sa-key"})` _Wrapped in `pulumi.secret()` so the RSA private key never appears in preview / state in plain text._
- [x] 5.3 Remove `src/zitadel/components/token-action.ts` (v1 Action + TriggerActions) _Deleted in cutover PR._
- [x] 5.4 Remove `src/zitadel/scripts/add-email-claim.js` (v1 JS) _Deleted in cutover PR._
- [x] 5.5 Create `src/zitadel/components/actions-v2.ts` instantiating two `ZitadelTarget`s and their corresponding `ZitadelExecutionFunction` / `ZitadelExecutionRequest`
- [x] 5.6 _Dropped_ — `src/zitadel/components/frontend.ts` redirect URIs require **no change**. Redirect URIs point at the OIDC **client** (frontend SPA at `https://dev.liverty-music.app/auth/callback`), not at the IdP. Only the **issuer** hostname changes (from `dev-svijfm.us1.zitadel.cloud` to `auth.dev.liverty-music.app`); the issuer is configured by the Pulumi provider `domain` input (task 5.1), not by redirect URIs.
- [x] 5.7 Update `src/index.ts` to pass the new `domain` and `jwtProfileJson` args to the Zitadel component
- [x] 5.8 Run `make lint-ts` and fix any type errors

## 6. cloud-provisioning — Kustomize base for zitadel namespace

- [x] 6.1 Create `k8s/namespaces/zitadel/base/namespace.yaml`
- [x] 6.2 Create `k8s/namespaces/zitadel/base/serviceaccount.yaml` with Workload Identity annotation pointing at `zitadel@...iam.gserviceaccount.com`
- [x] 6.3 Create `k8s/namespaces/zitadel/base/configmap.yaml` with Zitadel YAML config (ExternalDomain, ExternalSecure, TLS mode, Database.postgres.Host/Port/User/Database, Admin.ExistingDatabase, FIRSTINSTANCE env)
- [x] 6.4 Create `k8s/namespaces/zitadel/base/external-secret.yaml` for `zitadel-masterkey` _Implements only `zitadel-masterkey` syncing to a Kubernetes Secret consumed by the Zitadel API container via `envFrom`. `zitadel-admin-sa-key` is intentionally NOT mirrored into a K8s Secret: per task §5.2, Pulumi reads the admin SA key directly from GSM via `gcp.secretmanager.getSecretVersion()`, and no in-cluster workload mounts it. Mirroring it into a K8s Secret would (a) create an orphan Secret with the placeholder value at first sync (before the bootstrap-uploader has populated GSM v1) and (b) risk a future workload accidentally mounting a stale snapshot rather than the live GSM value._
- [x] 6.5 Create `k8s/namespaces/zitadel/base/deployment-api.yaml` — main container + cloud-sql-proxy sidecar + emptyDir volume for admin-sa key
- [x] 6.6 Create `k8s/namespaces/zitadel/base/deployment-login.yaml`
- [x] 6.7 Create `k8s/namespaces/zitadel/base/service-api.yaml` and `service-login.yaml`
- [x] 6.8 Create `k8s/namespaces/zitadel/base/httproute.yaml` with path split: `/ui/v2/login/*` → zitadel-login, `/*` → zitadel
- [x] 6.9 Create `k8s/namespaces/zitadel/base/pdb.yaml` with `minAvailable: 1` for each Deployment _Base manifest retains `minAvailable: 1` for staging / prod. The `dev` overlay subsequently introduced a `pdb-patch.yaml` that relaxes both PDBs to `minAvailable: 0` per the `optimize-dev-gke-cost` change (cloud-provisioning#208 / specification#425). With the dev `replicas: 1` override (§7.3), `minAvailable: 1` would block every node drain — relaxing to 0 is the correct dev-only posture._
- [x] 6.10 _Implemented as sidecar_ — rather than a separate K8s Job coordinating with the main Zitadel container via a shared volume (which would require a PVC), the admin-sa-key upload runs as a third container (`bootstrap-uploader`) in the Zitadel API Pod. Shared `emptyDir` works natively in-pod and is idempotent on restarts. See `deployment-api.yaml`.
- [x] 6.11 Create `k8s/namespaces/zitadel/base/kustomization.yaml` referencing all of the above

## 7. cloud-provisioning — Dev overlay

- [x] 7.1 Create `k8s/namespaces/zitadel/overlays/dev/kustomization.yaml`
- [x] 7.2 Create a configmap patch setting `ZITADEL_DATABASE_POSTGRES_MAXOPENCONNS=3` and `_MAXIDLECONNS=1`
- [x] 7.3 Create a deployment patch setting `replicas: 2`, resource `requests`/`limits` sized for `e2-medium` spot, and `podAntiAffinity` on `kubernetes.io/hostname` _Initial dev overlay shipped with `replicas: 2`. The subsequent `optimize-dev-gke-cost` change (cloud-provisioning#208 / specification#425) reduced both API and Login Deployments to `replicas: 1` to fit within a 2-node spot pool budget; resource requests/limits and `podAntiAffinity` are unchanged on the base, and a sibling `pdb-patch.yaml` (§6.9) relaxes the PDB to `minAvailable: 0` so the single replica can drain. The original 2-replica intent is preserved on the base manifest for `staging` / `prod`._
- [x] 7.4 Leave readiness/liveness probe defaults from the base; confirm `/debug/ready` works through the sidecar network namespace
- [x] 7.5 Apply per-Execution `interruptOnError` policy in `actions-v2.ts`: email-claim injection Execution uses `interruptOnError: true` in every environment (email claim is a hard invariant per the identity-management spec — every access token must carry it). The auto-verify-email Execution was **removed entirely** post-cutover (cloud-provisioning#215) because Zitadel v4 `request:*` Executions REPLACE the request body with the webhook response (not merge-patch), causing `AddHumanUser` validation to fail with `invalid AddHumanUserRequest.Profile: value is required` — the previous webhook returned only `{email: {is_verified: true}}` and so stripped Profile, Phone, password, etc. See zitadel/zitadel#9748 for the analogous bug on `RetrieveIdentityProviderIntent`. The original `interruptOnError` matrix collapses to a single value (true) for the only remaining Execution.

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
- [x] 9.7 Verify external-access rejection: from outside the cluster, `curl https://api.dev.liverty-music.app/pre-access-token` (or equivalent) SHALL return HTTP 401 because the `server-route` `/*` catch-all forwards the request to `server-svc:80` where `authn.Middleware` rejects unauthenticated requests before the mux dispatches _Verified — HTTP 401 received, matching the spec Note. Security objective (external rejection of webhook surface) is met. If a 404 is preferred, tighten the HTTPRoute path matchers to enumerate only public paths in a follow-up._
- [x] 9.8 Run `make check` — linting and tests pass

## 10. backend — User Data Truncation Migration

- [x] 10.1 Generate Atlas migration: `atlas migrate diff --env local truncate_users_for_zitadel_migration` _Landed in liverty-music/backend#287._
- [x] 10.2 Edit the generated migration to `TRUNCATE` `users`, `follows`, `user_onboarding_state`, and any other `external_id`-dependent tables (use `--cascade` if needed)
- [x] 10.3 Verify the down direction is a no-op with a comment explaining the rollback is to leave the empty tables empty
- [x] 10.4 Apply locally against the dev DB: `atlas migrate apply --env local`; verify schema health via `make test-integration`

## 11. backend — Configmap & Issuer Switch

- [x] 11.1 In `cloud-provisioning/k8s/namespaces/backend/overlays/dev/server/configmap.env`, change `OIDC_ISSUER_URL` to `https://auth.dev.liverty-music.app` _Landed in cutover PR cloud-provisioning#209._
- [x] 11.2 In `k8s/namespaces/backend/overlays/dev/consumer/configmap.env`, apply the same change if the consumer reads the issuer
- [x] 11.3 Confirm backend `email_verifier` integration still targets the correct Zitadel Management API path under the new domain

## 12. frontend — OIDC Config Switch

- [x] 12.1 In the frontend repository, edit the committed `.env` file to update `VITE_ZITADEL_ISSUER`, `VITE_ZITADEL_CLIENT_ID`, and `VITE_ZITADEL_ORG_ID` to the new self-hosted instance's values (client id and org id become known after the Pulumi cutover apply succeeds; pull them from the Pulumi `dev` stack outputs). _Landed in liverty-music/frontend#342. Original wording said "GitHub Actions environment secrets" but the frontend's actual build path doesn't read GH variables for these — `.env` is committed to the repo and `Dockerfile` `COPY . .` propagates it into the Vite builder stage, where Vite inlines `import.meta.env.VITE_*` into `dist/`. A short-lived experiment to manage these via Pulumi `github.ActionsEnvironmentVariable` (cloud-provisioning#209 commit `8b22b70`) was reverted because (a) the build pipeline never consumed `vars.VITE_*` and (b) hiding the values in the GitHub UI hurts discoverability — the canonical config belongs in the repo where `git blame` and code review can see it. The `clientId` was extracted from the running Zitadel via `GET /management/v1/projects/{id}/apps/{id}` because the `@pulumiverse/zitadel` provider stores `ApplicationOidc.clientId` as a literal string `"null"` in state (provider gap) — Pulumi outputs cannot be used as the source._
- [x] 12.2 Rebuild and redeploy the dev frontend through ArgoCD Image Updater flow

## 13. Cutover Execution

_The original linear pause→apply→resume sequence (§13.1–13.8) was bypassed in practice. Cutover landed via cloud-provisioning#209 as a single Pulumi-Cloud-Deployments-driven apply on merge to `main` (no manual `pulumi up`, no ArgoCD pause). Below is the **actually executed** sequence._

- [x] 13.1 cloud-provisioning#209 (`feat(zitadel): cut dev provider over to self-hosted instance`) merged to `main` _The Pulumi state was prepared by manually running `pulumi state delete --target-dependents` against the Cloud-tenant Zitadel resources before the merge so Pulumi treated the new `auth.dev.liverty-music.app` provider as a clean apply rather than a destructive replacement._
- [x] 13.2 Pulumi auto-deploy #248 ran on merge → **failed** at 8/13 creates (Project, ApplicationOidc, LoginPolicy, MachineUser, SmtpConfig, ActionsV2 component, 2 Targets succeeded; MachineKey, OrgMember, 2 Executions, SecretVersion did not run)
- [x] 13.3 Pulumi auto-deploy #249 retry → **failed** again
- [x] 13.4 State recovery: 87 GCP infra resources had been cascade-removed by `pulumi state delete --target-dependents` (the flag's blast radius was wider than expected — it also took the GKE cluster, Postgres, secrets, IAM, service accounts that the Cloud-tenant Zitadel resources depended on). Reconstructed a merged stack JSON (current 129 + v246 missing 85 − 2 obsolete v1 actions = 214 resources) and `pulumi stack import`-ed it to v254. Then scrubbed `__pulumi_raw_state_delta` from 177 resources (provider panic on import) → v255.
- [x] 13.5 Pulumi auto-deploy #250 → **failed** with `Zitadel UpdateTarget failed (405): Method Not Allowed` for the `pre-access-token-webhook` and `auto-verify-email-webhook` Targets. Root cause: the Pulumi Dynamic Resource `update` handler used `PATCH` against `/v2/actions/targets/{id}`; Zitadel's API expects `POST` for `UpdateTarget`. Fixed in cloud-provisioning#211.
- [x] 13.6 Pulumi auto-deploy #252 → **failed** with `Zitadel SetExecution failed (400): proto: invalid value for string field targets: {`. Root cause: the Dynamic Resource sent `targets: targetIds.map(id => ({target: id}))` but Zitadel expects `targets: string[]` per the proto. Fixed in cloud-provisioning#212.
- [x] 13.7 Pulumi auto-deploy #254 → **succeeded** (8 creates, 1 delete of v1 Actions component, 22 updates including SMTP, 8 SecretVersion replaces). All Targets and Executions are now live in self-hosted Zitadel.
- [x] 13.8 frontend#342 (`cutover(zitadel): point dev frontend at self-hosted Zitadel`) merged → CI built + ArgoCD synced new image (~2 min) — confirmed via pod restart at 02:37:50.
- [x] 13.9 backend#286 (webhook handlers `feat(webhook): add Zitadel Actions v2 handlers on internal-only port`) merged → backend image rolled out at 08:08:07 with `/pre-access-token` + `/auto-verify-email` listeners on `:9090`.
- [x] 13.10 cloud-provisioning#213 (`feat(zitadel): provision login-client PAT for self-hosted Login V2 UI`) merged → `LoginClientComponent` provisions MachineUser + InstanceMember (`IAM_LOGIN_CLIENT`) + PersonalAccessToken with no `expirationDate` (dev-only choice). PAT mounted into `zitadel-login` Pod as a file at `/var/run/zitadel/login-client.pat` via `ZITADEL_SERVICE_USER_TOKEN_FILE` env var (file mode keeps the token out of `kubectl describe pod` output). _This requirement was missing from the original cutover spec — Zitadel v4 self-hosted Login V2 UI calls privileged settings + cross-org user-search APIs at SSR time and needs a service-user token; the upstream contract is documented at https://zitadel.com/docs/self-hosting/manage/login-client._
- [x] 13.11 cloud-provisioning#214 (`fix(zitadel): point Login V2 UI at public ZITADEL_API_URL`) merged → `ZITADEL_API_URL` flipped from cluster-internal Service URL to `https://auth.dev.liverty-music.app`. _Required because Zitadel v4 selects the virtual instance from the request `Host` header against the configured `InstanceDomains`; the cluster-internal hostname is not registered as an InstanceDomain so internal calls returned 404. Traffic still stays in-cluster (Gateway → HTTPRoute → API Service)._
- [x] 13.12 backend#288 (`fix(webhook): drop iss check from WebhookValidator`) merged → empirically Zitadel v4 webhook JWTs do NOT include an `iss` claim (came through empty), and the upstream community reference impl (xianyu-one/zitadel-mapping) also relies on signature + custom checks without checking `iss`.
- [x] 13.13 backend#289 (`fix(webhook): drop aud check from WebhookValidator`) merged → empirically Zitadel v4 webhook JWTs do NOT populate `aud` either (came through as empty array). Security boundary collapses to `signature (JWKS) + network isolation (:9090 ClusterIP-only) + per-handler payload-shape checks`.
- [x] 13.14 cloud-provisioning#215 (`feat(zitadel): remove auto-verify-email Action`) merged → the `auto-verify-email` Target + ExecutionRequest were removed entirely. Zitadel v4 `request:*` Executions REPLACE the request body with the webhook response (not merge-patch), and the existing handler returned only `{email: {is_verified: true}}` so it stripped Profile / Phone / etc., causing `AddHumanUser` validation to fail. The Action also empirically did not deliver the intended UX even on Cloud Zitadel (users were still prompted for OTP). See zitadel/zitadel#9748 for the analogous bug. Future option: reconstruct the FULL `AddHumanUserRequest` in the webhook response, or disable the email-verification step at LoginPolicy.
- [x] 13.15 cloud-provisioning#216 (`fix(zitadel): refresh backend-app MachineKey to align with self-hosted`) merged → state drift between Zitadel DB (`keyId 370564347228848900`, self-hosted), GSM (`keyId 365044937655378985`, Cloud-era stale), and Pulumi state (Cloud-era output preserved through merged-state import) was repaired by force-replacing `MachineKey` (changed `expirationDate` from `2519-04-01T08:45:00Z` to `2099-01-01T00:00:00Z`). Rollout: Pulumi creates new key → SecretVersion replace → ESO sync (force-annotated for immediate refresh) → Reloader-driven backend pod restart.
- [x] 13.16 SMTP config activated manually via `POST /admin/v1/smtp/{id}/_activate` → Zitadel v4 SMTP configs ship in `SMTP_CONFIG_INACTIVE` state on creation; the `@pulumiverse/zitadel` `SmtpConfig` resource provisions but does not flip activation. _Tracked as a follow-up — see §18._
- [x] 13.17 Smoke test against `https://dev.liverty-music.app`: sign-up form → `AddHumanUser` succeeds → user reaches dashboard → passkey login → `pre-access-token` webhook injects `email` claim → backend `JWTValidator` accepts. **PASSED.**

## 14. E2E Auth Regeneration

- [ ] 14.1 In `frontend`, regenerate Playwright `.auth/` storage state against the new issuer following the existing `.auth/README.md` procedure (use the test users created against the new Zitadel instance) _**Deferred.** WSL2 + WSLg cannot render the Playwright Chromium window reliably (capture-auth-state.ts hits its 5-minute polling timeout because the browser window stays at `about:blank`). The existing test user is passkey-only, which is incompatible with headless Playwright (passkey requires biometric / PIN gesture from the device). To unblock E2E, a separate password-based test user is needed; see §18 follow-ups._
- [ ] 14.2 Commit updated `.auth/` artifacts _Deferred — depends on §14.1._
- [ ] 14.3 Run `npx playwright test` locally and verify all existing E2E tests pass _Deferred — depends on §14.1._

## 15. Cooldown & Cleanup

- [x] 15.1 Leave Zitadel Cloud tenant active and unchanged for two weeks post-cutover as a rollback target _Cloud tenant `dev-svijfm.us1.zitadel.cloud` retained; Pulumi resources for it were removed from the dev stack but the tenant itself is intact in the Zitadel Cloud console._
- [ ] 15.2 Monitor `/debug/metrics` and backend JWT validation logs daily for the first week; document any anomalies _Cooldown observation in progress (post-cutover 2026-04-30); two-week window ends ~2026-05-14. One incident already observed: Zitadel API container hung on `GetAuthRequest` (30s timeouts, returned `code: internal`) after ~3.5 days uptime + heavy state-changing API traffic during the cutover incident chain. Resolved by `kubectl rollout restart deploy/zitadel`. Likely cause: in-memory projection updater stuck or Cloud SQL connection-pool exhaustion accumulated through the many `_activate` / MachineKey replace / Action delete / email change operations. DB content was not affected; restart fully cleared the issue. Tracked as follow-up §18._
- [ ] 15.3 After two weeks clean run, open a follow-up change (`archive-zitadel-cloud-tenant`) that deletes the Cloud tenant and removes rollback references

## 16. Rollback Readiness (not executed unless needed)

- [x] 16.1 Document rollback steps in `openspec/changes/self-hosted-zitadel/rollback.md` (optional, inline in design.md is sufficient) _Inline in design.md per the optional path._
- [x] 16.2 Verify Pulumi stack can be re-applied with `domain` reverted to Zitadel Cloud if rollback is triggered _The cutover PR is a single revertable git commit; reverting it restores the Cloud-tenant `domain`. Cloud tenant data is intact for the cooldown window._
- [x] 16.3 Verify ArgoCD configmap revert to old `OIDC_ISSUER_URL` is a single commit reversal

## 17. Archive Change

- [ ] 17.1 Run `/opsx:verify self-hosted-zitadel` to confirm implementation matches proposal/design/specs _Pending; spec deltas to be reconciled with the §13 incident-driven divergence (auto-verify-email removed; webhook JWT iss/aud no longer enforced; SMTP activation gap; LoginClient PAT requirement)._
- [ ] 17.2 Run `/opsx:archive self-hosted-zitadel` to move the change into the archive and fold spec deltas into `openspec/specs/`

## 18. Follow-ups Discovered During Cutover (not blocking archive)

These are gaps surfaced by the cutover that did not exist in the original proposal/design/spec but should be tracked so future migrations don't re-hit them.

### 18.1 Pulumi auto-activate `SmtpConfig`

- [ ] 18.1.1 Investigate whether `@pulumiverse/zitadel.SmtpConfig` exposes an `activate` argument (it does not in v0.2.0). If not, ship a Pulumi Dynamic Resource (`ZitadelSmtpActivation`) that calls `POST /admin/v1/smtp/{id}/_activate` after `SmtpConfig` creation, mirroring the existing `ZitadelTarget` / `ZitadelExecutionFunction` pattern in `src/zitadel/dynamic/`.
- [ ] 18.1.2 Document in `zitadel-self-hosted-deployment` spec that `SMTP_CONFIG_INACTIVE` is the default after `CreateSmtp` and a separate `_activate` call is required.
- [ ] 18.1.3 Without this, every Zitadel rebuild requires a manual API call to re-activate SMTP — and email verification silently fails on first sign-up of every new instance until the call is made.

### 18.2 Backend `ResendEmailVerification` RPC calls wrong Zitadel endpoint

- [ ] 18.2.1 Backend's `liverty_music.rpc.user.v1.UserService/ResendEmailVerification` invokes the v2 `_resend_code` endpoint (which only resends an EXISTING code; if no code was ever generated — which happens when SMTP was inactive at sign-up time — the call returns `Code is empty (EMAIL-5w5ilin4yt)` and the frontend surfaces "Failed to send verification email").
- [ ] 18.2.2 Switch to Management v1 `POST /users/{userId}/email/_resend_verification`, which generates a fresh code AND sends the email. Verified to work via direct API call during the cutover smoke test.

### 18.3 Cleanup orphaned `auto-verify-email` backend handler

- [ ] 18.3.1 Delete `internal/adapter/webhook/auto_verify_email_handler.go` + tests + DI wiring + `Service/server-webhook-svc` route registration for `/auto-verify-email`. The Zitadel-side Target + Execution were removed in cloud-provisioning#215; the backend handler is now dead code receiving no traffic.
- [ ] 18.3.2 Keep the `:9090` listener and `/pre-access-token` handler unchanged.

### 18.4 Auto-verify-email — proper implementation if/when needed

- [ ] 18.4.1 If passkey-only sign-ups should skip the email-verification screen (the original §13 §10 design intent that did not actually work), there are two options:
  - **Option A**: Disable the email-verification step at the LoginPolicy level (no Action required).
  - **Option B**: Reconstruct the FULL `AddHumanUserRequest` in the webhook response (parse the JWT body, set `email.is_verified = true`, return the entire request payload — not just the email). Requires backend handler rewrite.
- [ ] 18.4.2 Until then, sign-up users go through Zitadel's default OTP step. Acceptable for dev; revisit when the cutover extends to staging / prod.

### 18.5 Playwright E2E — password-based test user

- [ ] 18.5.1 Provision a password-only test user in the new self-hosted Zitadel (Pulumi resource `zitadel.HumanUser` + initial password) for use by Playwright. Passkey-only users are incompatible with headless / CI testing because passkey requires biometric / PIN gesture.
- [ ] 18.5.2 Update `.auth/README.md` to document the new test user credentials and the WSL2-friendly capture path (likely Playwright MCP headless rather than the existing `capture-auth-state.ts` headed-Chromium script).

### 18.6 Zitadel API in-memory state pollution after long uptime

- [ ] 18.6.1 During the cutover incident chain (multiple `_activate`, MachineKey replace, Action delete, email change API calls within ~30 minutes against a 3.5-day-old pod), the Zitadel API container hung on `GetAuthRequest` for 30+ seconds and returned `code: internal`. Resolved by `kubectl rollout restart deploy/zitadel`. Likely cause: in-memory projection updater stuck on a write lock, or Cloud SQL connection-pool exhaustion from accumulated leaked connections in async notification-worker retries.
- [ ] 18.6.2 Add a Cloud Monitoring alert on Zitadel API request `duration_p99 > 10s` for `OIDCService/*` paths so the next occurrence triggers a page rather than being discovered by a user.
- [ ] 18.6.3 Consider periodic Pod recreation (e.g., a CronJob that does `kubectl rollout restart deploy/zitadel` weekly) for dev. For prod, target the underlying issue rather than recycling.

### 18.7 K8s deploy rename: `zitadel` → `zitadel-api`, `zitadel-login` → `zitadel-web`

- [ ] 18.7.1 Rename Deployment / Service / HTTPRoute backendRefs / HealthCheckPolicy targetRefs / PDB selectors in `cloud-provisioning/k8s/namespaces/zitadel/` for naming consistency. Container names follow (`api`, `web`).
- [ ] 18.7.2 Update `ZITADEL_API_URL` default to point at the new Service name (still public URL externally; the rename is for cluster-internal clarity).
- [ ] 18.7.3 Brief downtime acceptable in dev; ArgoCD performs delete-then-create on resource rename.

### 18.8 GSM secret rename: `zitadel-machine-key` → `zitadel-backend-app-key`

- [ ] 18.8.1 Cross-repo coordinated rename. Zero-downtime split:
  - Step 1 (cloud-provisioning): create new GSM secret `zitadel-backend-app-key` populated from current `MachineKey.keyDetails`; add new ExternalSecret + K8s Secret in backend namespace; keep old in place.
  - Step 2 (backend): switch Deployment volumeMount to new K8s Secret name + update `ZITADEL_MACHINE_KEY_PATH` env if needed.
  - Step 3 (cloud-provisioning, cleanup): remove old GSM Secret + ExternalSecret + K8s Secret.

### 18.9 Pulumi state import safeguards

- [ ] 18.9.1 The cutover required a hand-crafted merged-state JSON because `pulumi state delete --target-dependents` cascade-removed 87 resources beyond the intended Cloud-Zitadel-only scope. Add a runbook entry under `/cloud-provisioning/docs/` documenting:
  - The blast radius of `--target-dependents` (it follows ALL parents/dependencies, not just same-component-tree).
  - The merged-state-import procedure used in v254.
  - The need to scrub `__pulumi_raw_state_delta` after import (provider panic prevention).
- [ ] 18.9.2 Add a Pulumi Cloud "deployment guardrail" or pre-deploy check that diff-counts `delete > 50` and requires explicit human approval (Pulumi Cloud has a similar `pulumi-deployments-config.yaml` policy hook).
