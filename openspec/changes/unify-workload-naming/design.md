## Context

See proposal.md — Why. Current workloads: backend `server-app` / `consumer-app` /
`admin-console-api`, frontend `web-app` / `admin-app` / `organizer-app`. The
`admin-console-api` split + its GCP-identity isolation (dedicated GSA, Cloud SQL IAM
user, `admin-console-secrets` ExternalSecret, DATABASE_USER override, app-schema grant
migration) landed in `organizer-accounts` / `organizer-tenancy` and is the working
template for how one isolated workload's identity + DB access is wired. This change
generalizes that shape across every workload and unifies the names.

Rename precedent: `zitadel`→`zitadel-api`/`zitadel-web` (`zitadel-self-hosted-deployment`)
established the create-new → cutover → delete-old discipline and the "renamed canonical
names must be present in the rendered tree before prod ArgoCD picks them up" rule.

## Goals / Non-Goals

**Goals:** one derivable `<audience>-<tier>` name for every workload + all bound
Kubernetes, GCP-identity, image, route, and secret resources; a spec that future
workloads follow; a per-resource migration that tolerates brief interruption but keeps
external hostnames stable.

**Non-Goals:** splitting `event-consumer` per entity (future); changing any external
hostname, OIDC app, or API contract; re-architecting the workloads (this is naming +
identity only); renaming `admin-console-api` (already conforms) or building
`organizer-console-api` (that is `organizer-rpc-server` ①4/4, which will adopt the name
natively).

## Decisions

**D1 — Scheme `<audience>-<tier>`.** audience ∈ `fan`/`admin-console`/`organizer-console`
mirrors the proto RPC audience; tier ∈ `web`/`api`/`event-consumer`. Chosen over
domain-based names (`organizer-api`) because a workload serves an *audience surface*, not
one domain (the admin API serves `organizer`, and later other admin domains). Chosen over
keeping `-app` because `-app` does not distinguish web vs api vs worker.

**D2 — GCP identity keys off the workload name.** GSA account-id = stem, Cloud SQL IAM
user = `<stem>@<project>.iam`, GSM key = `zitadel-machine-key-for-<stem>`, AR repo =
`<layer>/<stem>`. This makes the identity self-describing and matches the existing
`zitadel-machine-key-for-<principal>` convention. Alternative (keep GCP identity names,
rename only K8s) was rejected by the explicit requirement to unify the identity layer.

**D3 — Create-new → cutover → delete-old per resource.** In-place renames of state-tracked
(Pulumi GSA/secret/SQL user) or route-bound (HTTPRoute) resources trigger replace
cascades or routing gaps. Additive migration (stand up the new-named resource, repoint,
then delete the old) is safe and matches the `admin-console-api` template. Pulumi URN
renames on lifecycle-sensitive resources use `aliases` where an in-place adopt is
preferable to a destroy/create (per the platform's URN-rename practice).

**D4 — `event-consumer` stays single.** One cross-domain worker now; the name reserves
the `-event-consumer` tier so a future per-entity split (`concert-event-consumer`, …) is
additive. KEDA durables are already behavior-named and are NOT renamed by the workload
rename (renaming durables would churn JetStream consumers — explicitly avoided).

**D5 — Hostnames are frozen.** `api.liverty-music.app`, `admin.liverty-music.app`,
`organizer.{base}`, `api.admin.liverty-music.app` etc. stay put; only the internal
resource names change, so external clients and OIDC redirect URIs are untouched.

**D6 — Spec reconciliation scope.** Only `zitadel-self-hosted-deployment` pins a renamed
identifier as a normative requirement (the GSM key) → a MODIFIED delta. Other specs'
name mentions are incidental prose reconciled by a tasks sweep against the new convention
spec; they carry no behavioral change (hostnames/APIs unchanged).

## Risks / Trade-offs (per-resource)

| Resource class | Blast radius | Risk → Mitigation |
|---|---|---|
| **GSA `backend-app`→`fan-api`** | WI binding, per-secret IAM, Cloud SQL IAM user, GSM key, all role grants | Widest. New GSA lacks all bindings until re-granted → **create GSA + replicate every role/binding (cloudsql.client+instanceUser, secret accessors, WI) first, verify, then cutover KSA annotation, then delete old** (the `admin-console-api` incident showed a missing `cloudsql.client`/DB-user/grant crashloops the pod — replicate the *full* set). |
| **Zitadel MachineKey / GSM `…-for-backend-app`→`…-for-fan-api`** | backend→Zitadel JWT auth | keyId drift breaks bearer auth (§13.15 class) → **re-issue MachineKey under fan-api, write new GSM, cutover fan-api env + ESO ref, confirm `keyId` matches Zitadel AuthNKey, then delete old key/secret.** |
| **Cloud SQL IAM DB user `backend-app@…`→`fan-api@…`** | fan-api DB access | new user has no app-schema grants → **create CLOUD_IAM_SERVICE_ACCOUNT user + run the grant-loop migration (as in `organizer-accounts` #390) before flipping DATABASE_USER.** |
| **Backend Deployment/Service/HTTPRoute `server-app`/`server-route`→`fan-api*`** | `api.liverty-music.app` routing | routing gap on repoint → **create fan-api Deployment/Service/route, attach route to the Gateway (hostname unchanged), verify 200, then detach/delete server-route + server-app.** |
| **AR image repos `backend/server`,`frontend/web-app`,…→`…/fan-api`,`…/fan-web`,…** | CI push, prod pin, immutable-tag retag, bump-prod-pin dispatch list | prod pin/retag reference old repo → **create new repos, update CI push targets + `bump-prod-pin` image list + release retag map, cut a release to populate new repos, then repoint overlays' `images:` block.** |
| **Frontend Deployments `*-app`→`*-web` + bundle-isolation** | admin/organizer/web bundles | isolation script allowlists old workload/bundle names → **update `verify-bundle-isolation` allowlist in lockstep; create-new deploys, repoint frontend HTTPRoutes, delete old.** |
| **ExternalSecret `admin-console-secrets`→`admin-console-api-secrets` (+ per-workload)** | ESO sync + mount | mount ref mismatch → **create new ExternalSecret (new target Secret), update deployment mount, Reloader restarts, delete old.** |
| **`consumer-app`→`event-consumer` + KEDA ScaledObject** | JetStream durables | renaming durables wedges consumers → **rename only the Deployment/Service/ScaledObject/image; keep durable names; verify HPA currentMetrics not `<unknown>`.** |
| **Monitoring `app.kubernetes.io/name` labels + PodMonitoring/AlertPolicy** | dashboards, alerts, PromQL | queries keyed on old workload name go blind → **update PromQL/dashboards/AlertPolicies referencing old names in the same change; verify metrics still resolve post-cutover.** |
| **Pulumi logical URNs** | state | logical-name change → destroy/create → **use `aliases` for adopt-in-place where safe; accept destroy/create only for the additively-recreated identities above.** |

## Migration Plan

**D7 — Prod-direct cutover (no dev-first).** The dev environment is intentionally
stopped for cost, so the "dev first, then prod" rehearsal is not available. Instead the
migration runs **directly in prod**, made safe by the additive create-new → cutover →
delete-old discipline itself: the new-named resources stand up **alongside** the live
old ones and carry no traffic/identity until the explicit cutover step, and every step
before delete-old is reversible by repointing back to the old resources. This trades the
dev rehearsal for a strictly additive prod rollout with a per-resource rollback at each
gate. The delete-old step is deferred until the new workload is verified healthy in prod.

Per audience, additively and one workload at a time (prod-direct), so a failure is
contained to one surface:

1. **cloud-provisioning (identity + infra)**: add new GSA/DB-user/GSM-key/AR-repo/WI +
   all bindings for the target name (old kept live). `pulumi up` (prod).
2. **backend/frontend (images)**: point CI at new AR repos, cut a release to populate
   them (dual-published), run the Cloud SQL grant migration for the new DB user.
3. **k8s (create-new)**: add new-named Deployment/Service/SA/HTTPRoute/HealthCheckPolicy/
   ExternalSecret/configmap/ScaledObject/PodMonitoring alongside the old; ArgoCD sync.
   The new workload is running and self-verifiable (health probe, DB connect, auth) while
   still detached from the external hostname.
4. **cutover**: repoint each HTTPRoute (hostname unchanged) + DATABASE_USER + secret refs
   + monitoring labels to the new workload; verify health (200 on the live hostname + DB
   connect + auth). This is the only step with a brief interruption window.
5. **delete-old**: only after the new workload is confirmed healthy in prod, remove old
   Deployments/Services/routes/secrets/GSA/DB-user/GSM-key/AR-repo; `pulumi up`; confirm
   no dangling references.
6. **spec sweep**: reconcile incidental old-name references in the other specs against the
   `workload-naming-convention` spec.
- **Rollback**: until step 5, the old-named resources are still live — repoint routes/
  env back to them; the new resources are additive and removable. Because there is no dev
  rehearsal, the new workload's self-verification in step 3 (before cutover) is the
  primary safety gate: do not proceed to cutover until it passes detached.

## Open Questions

- Whether to fold `cloud-sql-proxy` into the convention (it is a shared 3rd-party proxy,
  not an audience workload) — leaning keep-as-is; resolve during cloud-provisioning tasks
  without changing the spec.
