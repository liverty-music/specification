## Context

The `dev` environment currently consumes Zitadel as a SaaS: OIDC issuer `https://dev-svijfm.us1.zitadel.cloud`, managed by the `@pulumiverse/zitadel` Pulumi provider targeting the Cloud Management API. The platform relies on Zitadel for authorization code + PKCE login, passkey-only policy, OIDC access-token-based RPC authentication, an `addEmailClaim` Action v1 that injects the user email into access tokens, and an `INTERNAL_AUTHENTICATION/PRE_CREATION` Action v1 that auto-verifies email during self-registration. The backend validates incoming JWTs via `OIDC_ISSUER_URL` and a JWKS validator refreshed every 15 minutes. The frontend (Aurelia 2 SPA) uses `oidc-client-ts` and reads issuer/client/org ids from Vite env vars. Playwright E2E tests use captured `storageState` files against this issuer.

GKE `dev` is a Standard zonal cluster, with a single Spot node pool (`e2-medium`, autoscale 1–2) chosen to eliminate cluster management and Cloud NAT costs. Cloud SQL `postgres-osaka` already runs `POSTGRES_18` as the primary Liverty Music database. GKE Gateway API (standard channel) is enabled and is the path Liverty Music uses for all ingress with Google-managed certificates. External Secrets Operator (ESO) is deployed with Workload Identity to GCP Secret Manager (GSM). ArgoCD continuously syncs `k8s/namespaces/**` into the cluster; Image Updater handles image promotion for backend/frontend.

Zitadel upstream as of April 2026 ships `v4.x` with a mandatory two-container layout (`ghcr.io/zitadel/zitadel` API on `:8080` plus `ghcr.io/zitadel/login` Login V2 UI on `:3000`, served at `/ui/v2/login/*`); PG14–PG18 are supported and PG18 requires `v4.11.0+`; CockroachDB support was removed in `v3`. The Helm chart creates separate Ingress objects per container but the same pattern is trivially adaptable to an `HTTPRoute`. The community edition is Apache 2.0 with no feature gating versus Zitadel Cloud. The upstream Terraform provider `zitadel/terraform-provider-zitadel@v2.12.5` exposes Actions v2 resources (`zitadel_action_target`, `zitadel_action_execution_function`, `_request`, `_response`, `_event`, `_target_public_key`), but `@pulumiverse/zitadel` has not been regenerated past `v0.2.0` (March 2024) and therefore still exposes only the Actions v1 `Action` + `TriggerActions` resources.

Stakeholders: the single-person development team that owns the full Liverty Music stack; no external users currently exist on the `dev` issuer, and existing `dev` user records are deliberately in scope for destruction. Downstream consumers of Zitadel identity are: the backend JWT authn middleware, the backend `email_verifier` that calls Zitadel Management APIs to re-send verification emails, and the frontend `AuthService`.

## Goals / Non-Goals

**Goals:**
- Replace the Zitadel Cloud dev tenant with an in-cluster Zitadel v4.11+ deployment reachable at `https://auth.dev.liverty-music.app` with identical functional behavior (passkey-only login, email claim in access tokens, auto-verify-email during self-registration, SMTP through Postmark) from the end-user and backend perspective.
- Eliminate the password-bearing DSN secret by connecting to Cloud SQL through the Cloud SQL Auth Proxy sidecar with `--auto-iam-authn`, using a `CLOUD_IAM_SERVICE_ACCOUNT` role pre-provisioned by Pulumi.
- Migrate Actions v1 → v2 without loss of functional parity: both the email-claim injection and the auto-verify-email behaviors are preserved via Zitadel Actions v2 Execution/Target pointing at backend-hosted webhooks.
- Keep operational cost at `dev` minimal by reusing the existing shared spot node pool and existing Cloud SQL instance, rather than introducing dedicated infrastructure.
- Establish reusable K8s manifests and Pulumi patterns so the follow-up `staging` / `prod` migrations can copy this design with only environment-specific overrides (node affinity, replica counts, Cloud SQL tier, backup cadence).
- Survive a single-pod Spot eviction without serving a 5xx storm: steady-state traffic is absorbed by the sibling replica, `/debug/ready` gates the LB, and setup/migration runs are serialized by Zitadel's internal advisory locks.

**Non-Goals:**
- Migrating existing `dev` users, organizations, projects, grants, metadata, or audit logs from Zitadel Cloud. The Backend's user-scoped tables are truncated as part of cutover.
- Building a regional or HA Zitadel topology. `dev` runs zonal on Spot; HA shaping is deferred to the `staging` / `prod` follow-up change.
- Replacing or upgrading the Cloud SQL instance itself — this change only adds a database and an IAM user to the existing instance.
- Self-hosting the Login V2 UI on a different hostname. Login UI and API share `auth.dev.liverty-music.app` with path routing.
- Replacing `@pulumiverse/zitadel` or PRing a regenerated provider upstream. The narrow gap (Actions v2 resources only) is closed with a local Dynamic Resource; a full provider modernization is out of scope.
- Deleting the Zitadel Cloud tenant immediately. It is retained for a defined cooldown period as a rollback target.

## Decisions

### D1. TLS mode `external`, Gateway terminates TLS, cluster traffic is HTTP/h2c

Zitadel exposes three TLS modes (`disabled`, `external`, `enabled`). `external` is the canonical reverse-proxy posture: Zitadel serves plain HTTP internally but advertises `https://...` on `ExternalDomain`/`ExternalPort` so OIDC discovery, redirect URIs, and issuer claim all use HTTPS. GKE Gateway terminates TLS using a Google-managed certificate, identical to the existing backend API. The cluster-internal hop is h2c, preserving HTTP/2 multiplexing for streaming and gRPC endpoints. `enabled` (end-to-end TLS) is rejected because it duplicates certificate management in two places and delivers no additional value inside a Workload Identity–secured cluster with no mTLS requirement. `disabled` is rejected because it would force Zitadel to emit non-HTTPS OIDC discovery URLs, breaking client verification.

### D2. Two Services + one HTTPRoute with path split on `/ui/v2/login/*`

Starting in v4, Zitadel ships the Login V2 UI as a separate container image (`ghcr.io/zitadel/login`) that serves the `/ui/v2/login/*` path tree on port `3000`; all remaining paths (OIDC, `/v2/*`, `/zitadel.*.v2.*`, `/debug/ready`, legacy `/oauth/v2`, `/oidc/v1`, `/ui/console`) must continue to route to the API container on port `8080`. The HTTPRoute expresses this as two `backendRefs` with `matches.path.prefix` rules; the login prefix is matched first (more specific wins per Gateway API semantics with equal weight, but the chart documents a `/ui/v2/login` prefix as sufficient). Deploying both as discrete `Deployment`s with `replicaCount: 2` mirrors the chart defaults and keeps eviction blast radius to a single role at a time. Alternatives considered: a single Deployment with both containers (rejected — separate lifecycles, different resource profiles, the chart does not support this); fronting each container with its own hostname (rejected — doubles DNS/certificate surface and conflicts with Zitadel's expectation that the issuer and login share a host).

### D3. Cloud SQL Auth Proxy sidecar + `--auto-iam-authn` instead of password-based DSN

A `cloud-sql-proxy` sidecar container running `gcr.io/cloud-sql-connectors/cloud-sql-proxy` with `--auto-iam-authn --private-ip --instance liverty-music-dev:asia-northeast2:postgres-osaka` bridges `127.0.0.1:5432` to Cloud SQL, using Workload Identity to impersonate `zitadel@liverty-music-dev.iam` and letting Cloud SQL validate the IAM-authenticated connection server-side. Zitadel's PostgreSQL config consumes split fields (`Database.postgres.Host=localhost`, `Port=5432`, `Database=zitadel`, `User.Username=zitadel@liverty-music-dev.iam`) and omits password entirely. `SSL.Mode=disable` is correct at this layer because the sidecar proxies over Google's mTLS channel. Rejected alternatives: password-based DSN (rejected — forces a secret, rotation pain, duplicates auth model vs. backend); static Cloud SQL public IP + IAM token injection in Zitadel directly (rejected — Zitadel does not ship Google IAM DB auth natively, which would require patching the binary).

The one cost of IAM auth is that IAM users cannot `CREATE ROLE` or `CREATE DATABASE`. Zitadel's default init path attempts both. The config option `Database.postgres.Admin.ExistingDatabase: true` is the officially sanctioned escape hatch: it instructs Zitadel to skip superuser-only queries and proceed directly to schema migrations, which IAM users can run against a pre-created `zitadel` database whose ownership has been granted to them. Pulumi pre-creates both the database and the IAM user and grants ownership.

### D4. Connection pool tuned for dev Cloud SQL connection budget

The existing `db-f1-micro` Cloud SQL instance caps the project-wide connection total at 25, with backend server and consumer workloads each configured to take up to 5. With two Zitadel replicas, applying the production-recommended `MaxOpenConns: 10` would consume 20 connections by itself and exhaust the budget. Instead, `dev` runs with `MaxOpenConns: 3` / `MaxIdleConns: 1`, giving a worst-case Zitadel footprint of 6 active connections. This is sufficient for the single-person dev traffic profile (sub-1 rps steady state) and projection rebuilds (rare, bounded). The values are environment-specific and carried in the dev Kustomize overlay, not the base manifests. `staging` / `prod` will inherit the production-recommended defaults when those environments migrate.

### D5. Actions v1 → v2 via backend webhook with `PAYLOAD_TYPE_JWT` authentication

The Zitadel Actions v2 model replaces inline JavaScript with external HTTP targets. Two flows must migrate:

- **Email claim injection** (v1: `addEmailClaim` JS on `FLOW_TYPE_CUSTOMISE_TOKEN`/`TRIGGER_TYPE_PRE_ACCESS_TOKEN_CREATION`): becomes an `ExecutionFunction` with `name: "preaccesstoken"` targeting a `REST_CALL` endpoint at `http://server-webhook-svc.backend.svc.cluster.local/pre-access-token`. The handler receives a JWT-wrapped payload, validates it against Zitadel's own JWKS (same keys the backend already caches for user access tokens — the webhook JWTs are self-issued), extracts `user.human.email`, and returns `{"append_claims":[{"key":"email","value":"…"}]}`.
- **Auto-verify email** (v1: `INTERNAL_AUTHENTICATION/PRE_CREATION` JS calling `api.setEmailVerified(true)`): becomes an `ExecutionRequest` targeting the Zitadel internal request method that creates a human user (specifically intercepting the user-creation gRPC path) at `http://server-webhook-svc.backend.svc.cluster.local/auto-verify-email`. The target webhook mutates the request to set `email.is_verified = true` before it reaches the Zitadel core. This path is less elegant than v1 but is the officially documented migration and avoids the OTP step during self-registration.

The endpoint hostnames are `server-webhook-svc.backend.svc.cluster.local` — a **new**, internal-only `Service` on a **separate port** (`9090`) from the public `server-svc` on port `80`. The existing GKE Gateway only fronts `server-svc`, so the webhook paths are unreachable from outside the cluster regardless of URL guess-work. Cluster-internal traffic is plain HTTP per D1; TLS would require a pod-level certificate that nothing in this change provisions.

`PAYLOAD_TYPE_JWT` is chosen over `PAYLOAD_TYPE_JSON` because the backend already trusts Zitadel's JWKS; reusing the validator (`JWTValidator` from `internal/infrastructure/auth`) yields stronger authentication than an HMAC shared secret and one fewer secret to rotate. `PAYLOAD_TYPE_JWE` is deferred — it adds encryption at rest for the webhook payload but the payload never leaves the cluster.

Each webhook Target pins a distinct `aud` (audience) claim:

- `/pre-access-token` → `urn:liverty-music:webhook:pre-access-token`
- `/auto-verify-email` → `urn:liverty-music:webhook:auto-verify-email`

Pinning a webhook-specific audience defends against **replay of end-user access tokens**. Because end-user access tokens and webhook JWTs are signed by the same JWKS, signature + issuer + expiry checks alone cannot distinguish them. The `aud` check is what keeps a captured user token from being POSTed to the webhook endpoint as if it were a legitimate Zitadel-issued webhook request. Both Targets and Executions live in the `liverty-music` org scope.

### D6. Custom Pulumi Dynamic Resource for Actions v2 because the provider is stale

`@pulumiverse/zitadel@0.2.0` predates the Zitadel Actions v2 API. Regenerating the pulumiverse provider against `terraform-provider-zitadel@v2.12.5` is out of scope (cross-repo, schema regeneration, release cadence). Instead, two `pulumi.dynamic.Resource` classes (`ZitadelTarget`, `ZitadelExecutionFunction`) are implemented in `cloud-provisioning/src/zitadel/dynamic/` with a small `ZitadelApiClient` helper that:
1. Uses the admin machine key JWT profile to obtain a short-lived access token via the OIDC `client_credentials` grant on the new `auth.dev.liverty-music.app` issuer,
2. POSTs to `/v2/actions/targets` and `/v2/actions/executions` using that token.

Create, read, update, delete are implemented against the documented REST surface; the `signingKey` returned at Target create time is captured as a Pulumi output but never used for verification because `PAYLOAD_TYPE_JWT` supersedes it. All v1-era resources (Project, ApplicationOidc, LoginPolicy, SmtpConfig, MachineUser, MachineKey, OrgMember) continue to use `@pulumiverse/zitadel` unchanged — only the domain input switches from `dev-svijfm.us1.zitadel.cloud` to `auth.dev.liverty-music.app`.

Alternatives considered: ArgoCD `PostSync` Job with bash/curl (rejected — loses Pulumi's drift detection and typed outputs); calling the Zitadel gRPC via `grpcurl` from a `pulumi.local.Command` (rejected — same drift problem plus no typed inputs); forking pulumiverse locally (rejected — long-term maintenance burden for a single-person team, gains minimal over a ~100-line dynamic resource).

### D7. Bootstrap admin machine key via `ZITADEL_FIRSTINSTANCE_*` and an ESO-piped K8s Job

The first time Zitadel starts on an empty database, `start-from-init` reads `ZITADEL_FIRSTINSTANCE_*` env vars to create the initial instance. Setting `ZITADEL_FIRSTINSTANCE_MACHINEKEYPATH=/var/zitadel/admin-sa.json`, `ZITADEL_FIRSTINSTANCE_ORG_MACHINE_MACHINE_USERNAME=pulumi-admin`, `ZITADEL_FIRSTINSTANCE_ORG_MACHINE_MACHINEKEY_TYPE=1` (JSON key) causes the init container to write a JWT-profile JSON to an `emptyDir` volume shared with a sidecar Job. The Job uses Workload Identity to upload the JSON to GSM secret `zitadel-admin-sa-key`, then exits. On the next Pulumi stack apply, `@pulumiverse/zitadel`'s Provider reads the `jwtProfileJson` from GSM (via ESO-populated Kubernetes secret or directly via GCP client SDK within the Pulumi program) and proceeds to configure Project/App/LoginPolicy/SMTP/Actions v2 against the running instance.

Because `ZITADEL_FIRSTINSTANCE_*` only applies at instance creation, the env vars are left in place permanently (they're ignored on subsequent boots) rather than removed. A 32-byte masterkey is generated once by Pulumi (`RandomString` with `special: false`), stored in GSM secret `zitadel-masterkey`, mounted into the Zitadel container, and never rotated — Zitadel documents this as irreversibly tied to all event-store encryption.

### D8. Schedule onto the existing spot node pool with PDB and podAntiAffinity

The single-person `dev` cluster cost posture explicitly accepts short auth outages; promoting Zitadel to an on-demand pool would nearly double the dev compute bill for protection against a scenario that already occurs (node eviction) for the existing backend. Two defenses compensate:
- `PodDisruptionBudget minAvailable: 1` protects against K8s-initiated voluntary disruption (autoscaler drain, node upgrades) — not GCP Spot preemption, but meaningful during routine cluster maintenance.
- `podAntiAffinity.requiredDuringSchedulingIgnoredDuringExecution` on `kubernetes.io/hostname` forces the two replicas onto different nodes so a single preemption cannot take both down.
- `readinessProbe: /debug/ready` removes a pod from the Gateway backend pool during startup or migration; `rollingUpdate.maxUnavailable: 0` prevents the deploy-time gap.

The trade-off is that a simultaneous two-node preemption does cause a ~30–90s total auth outage in `dev` during the rare case that both spot VMs are reclaimed. `staging` / `prod` will use an on-demand pool with regional distribution in the follow-up change.

### D9. Wipe user-scoped backend tables instead of running a user migration

The existing `dev` issuer's user IDs (`sub` claims) do not survive the switch to the self-hosted instance, so any existing `users` / `follows` / `onboarding_state` rows become orphaned with dangling `external_id`s pointing to a defunct issuer. Rather than attempt to rewrite identifiers, a reversible Atlas migration truncates user-scoped tables at cutover. The migration is reversible only in the trivial sense that the down direction is a no-op (an empty table cannot have rows restored). No user data migration path is offered because `dev` has no users outside the team and test fixtures.

### D10. Retain the Zitadel Cloud tenant during a cooldown window

To cap the blast radius of a bad cutover, the Cloud tenant is not deleted on the day of the switch. Instead, `dev` DNS can be reverted and the backend `OIDC_ISSUER_URL` flipped back if stabilization fails. The Cloud tenant is deleted in a follow-up change once the self-hosted instance has served `dev` for two weeks without incident. The backend's existing `JWT_ACCEPTED_ISSUERS` config (originally added for a separate migration path) is left unconfigured — simultaneous dual-issuer acceptance in dev is not needed because no third-party clients consume dev tokens.

## Risks / Trade-offs

- **[Spot double-eviction during Zitadel setup phase]** → Zitadel's setup phase runs under a PostgreSQL advisory lock, so even if a replica dies mid-migration another can resume. The acceptable failure mode is that dev auth is unavailable during re-setup (~1 minute). Mitigation: run the initial `start-from-init` on purpose during a known-quiet period; subsequent upgrades use `start-from-setup` which is idempotent.
- **[Cloud SQL connection exhaustion at peak]** → The total budget is 25; projected worst case is Zitadel(6) + backend-server(5) + backend-consumer(5) + Atlas(2) = 18, with 7 headroom. Mitigation: observe `pg_stat_activity` after cutover; if projection rebuilds during upgrades push the total higher, temporarily scale the Zitadel replica count down to 1 during the upgrade. Long-term mitigation is the staging/prod migration upgrading the Cloud SQL tier.
- **[Dynamic Resource drift if Zitadel REST API changes]** → Zitadel has historically held v2 API compatibility across minor versions but has broken between major versions. Mitigation: pin a minimum Zitadel version (`v4.11.0`) in the Helm values and gate upgrades on CHANGELOG review. The Dynamic Resource is a thin shim; rewriting for a future v5 is a bounded cost.
- **[Actions v2 auto-verify webhook fails → users stuck behind OTP]** → Unlike the v1 JS Action that ran in-process, a v2 webhook is a network hop that can timeout or 500. Mitigation: set `interruptOnError: false` on the auto-verify target in `dev` so a failure falls back to the OTP step rather than blocking registration; set `true` in `prod` (follow-up change). The backend webhook handler is pinned to the same pod pool as the API so network topology is short and monitored.
- **[`PAYLOAD_TYPE_JWT` requires clock skew tolerance between Zitadel and backend]** → Clock drift could cause `nbf`/`exp` rejection. Mitigation: the backend JWT validator already applies a small skew allowance; no change needed. In-cluster pods share the GCP host clock, so drift is sub-second in practice.
- **[Masterkey loss is catastrophic]** → A lost masterkey cannot be replaced; all event-store-encrypted secrets become unrecoverable. Mitigation: the masterkey is stored in GSM with versioning and IAM-restricted access; a manual local copy is taken by the team owner and stored in a personal password manager as off-platform backup.
- **[Cooldown period DNS/env revert racing with ArgoCD sync]** → If a rollback is needed, flipping DNS must precede ArgoCD reverting backend configmaps. Mitigation: the rollback runbook (in tasks.md) serializes DNS, ArgoCD, and Pulumi actions with explicit checkpoints.

## Migration Plan

**Cutover is a single-session operation** run by the team owner, with ArgoCD paused on the `backend` and `frontend` namespaces during the window. High-level order (detailed steps live in tasks.md):

1. **Pre-flight**: confirm Cloud SQL PG version is `POSTGRES_18` (already confirmed); confirm the Zitadel Helm chart's `v4.11+` tag is available; snapshot Cloud SQL.
2. **Pulumi stack #1 (infra)**: apply Cloud SQL `zitadel` database + `zitadel@...iam` user + ownership grant; create GSM secrets (masterkey, placeholder admin-sa-key); create DNS A record + managed cert for `auth.dev.liverty-music.app`.
3. **K8s manifests**: ArgoCD syncs `k8s/namespaces/zitadel/overlays/dev` — this brings up the Deployments. The init container runs `start-from-init` with `FIRSTINSTANCE_*` env vars, writes the admin SA key to an `emptyDir`, and a sidecar Job uploads it to GSM. ArgoCD sync-waves guarantee the Job completes before any dependent workload is considered ready.
4. **Pulumi stack #2 (Zitadel config)**: re-apply Pulumi, which now reads the admin-sa-key from GSM and provisions Project / ApplicationOidc / LoginPolicy / SmtpConfig / MachineUser / MachineKey / OrgMember on the new instance, plus the v2 `ZitadelTarget` + `ZitadelExecutionFunction` Dynamic Resources.
5. **Backend**: apply Atlas migration to truncate `users`, `follows`, and related user-scoped tables; update `OIDC_ISSUER_URL` configmap to `https://auth.dev.liverty-music.app`; ArgoCD rollouts backend with the new issuer.
6. **Frontend**: update Vite env secrets (`VITE_ZITADEL_ISSUER`, `_CLIENT_ID`, `_ORG_ID`) in the frontend GitHub Environment, trigger a rebuild; ArgoCD deploys the new frontend.
7. **Playwright**: regenerate `.auth/` storage state against the new issuer and commit.
8. **Verification**: smoke test the landing-page Login flow and Tutorial Step-6 Sign-Up flow end-to-end; inspect backend logs for successful JWT validation against the new issuer; inspect Zitadel `/debug/metrics` for baseline request rate.
9. **Cooldown**: leave the Cloud tenant in place for two weeks, then delete in a separate follow-up change.

**Rollback** (triggered within the cooldown window if instability): revert DNS + frontend env secrets + backend `OIDC_ISSUER_URL` configmap to the Cloud tenant; redeploy backend and frontend; leave the self-hosted Zitadel running untouched for post-mortem analysis. User-scoped data truncation is not reversed — rollback restores the pre-migration backend code but users re-register against the reverted Cloud tenant (same tenant they had before, so their Zitadel accounts still exist).

## Open Questions

All questions identified during the `/opsx:explore` phase are resolved:
- Action v2 webhook authentication: decided (`PAYLOAD_TYPE_JWT`, JWKS-verified).
- Pulumi provider gap: decided (local Dynamic Resource for v2 only).
- `zitadel-db-dsn` secret necessity: decided (no secret, IAM auth + ConfigMap).
- PG version constraint: confirmed (`POSTGRES_18`, requires Zitadel `v4.11.0+`).

Deliberately deferred to follow-up work (not blocking this change):
- HA topology for `staging` / `prod` (separate change).
- Cloud SQL instance tier upgrade for `staging` / `prod` connection budget.
- Potential PR upstream to `pulumiverse/pulumi-zitadel` to regenerate from `terraform-provider-zitadel@v2.12.x`.
