## Why

Platform workloads are named on three inconsistent axes — `server-app` / `web-app` /
`admin-app` / `organizer-app` (`-app`), `admin-console-api` (`-api`), `consumer-app`
(worker) — so the same logical application has different names in the app layer
(proto `rpc.admin.organizer.v1`, backend `organizer`) and the infra layer
(`admin-console-api` backend vs `admin-app` frontend). The mismatch obscures which
frontend, backend, GCP identity, image, route, and secret belong together, and every
new workload re-litigates the naming. This change establishes one convention and
migrates every existing resource to it so a reader can derive all related resource
names from the audience alone.

## What Changes

- Introduce a platform **workload naming convention**: `<audience-console>-<tier>`,
  where audience ∈ `fan` / `admin-console` / `organizer-console` and tier ∈ `web`
  (browser bundle), `api` (Connect-RPC server), `event-consumer` (JetStream worker).
  Derived resource suffixes stay uniform: Service `-svc`, HealthCheckPolicy
  `-policy`, HTTPRoute `-route`, ExternalSecret `-secrets`, and the GCP identity /
  GSM-key naming (`zitadel-machine-key-for-<principal>`) keys off the same principal.
- **BREAKING (resource identity)** rename every existing workload + its derived
  resources to the convention (service interruption during cutover is accepted):
  - `web-app` → `fan-web`, `server-app` → `fan-api`, `consumer-app` → `event-consumer`
  - `admin-app` → `admin-console-web` (backend `admin-console-api` already conforms)
  - `organizer-app` → `organizer-console-web` (the organizer backend API is built as
    `organizer-console-api` from the start by `organizer-rpc-server` ①4/4)
- **BREAKING (GCP identity)** rename the GCP layer to match the principal: GSA
  `backend-app` → `fan-api` (and the admin GSA already `admin-console-api`), the
  Cloud SQL `CLOUD_IAM_SERVICE_ACCOUNT` users, the per-secret IAM bindings, the
  Workload Identity bindings, and the GSM key `zitadel-machine-key-for-backend-app`
  → `zitadel-machine-key-for-fan-api` (re-issued Zitadel `backend-app` MachineKey).
- Rename the derived resources coherently in the same cutover: Deployments,
  Services, ServiceAccounts, HTTPRoutes (`server-route` → `fan-api-route`, etc.),
  HealthCheckPolicies, ExternalSecrets (incl. `admin-console-secrets` →
  `admin-console-api-secrets`), configmaps, Artifact Registry image repositories,
  prod image pins, `app.kubernetes.io/name` labels + PodMonitoring, KEDA
  ScaledObject, and the frontend bundle-isolation script's workload allowlist.
- Adopt a **create-new → cutover → delete-old** migration per resource (mirroring
  the `zitadel`→`zitadel-api`/`zitadel-web` rename precedent) so state-tracked and
  route-bound resources move without a stuck/replace cascade.
- `event-consumer` stays a single worker in this change; future per-entity split
  (e.g. `concert-event-consumer`) is out of scope but the name anticipates it.

## Capabilities

### New Capabilities
- `workload-naming-convention`: the canonical `<audience-console>-<tier>` scheme, the
  derived-resource suffix rules, the GCP identity / GSM-key naming, the full canonical
  name mapping table, and the migration ordering rule (create-new → cutover →
  delete-old). Future workloads SHALL derive their names from this spec.

### Modified Capabilities
- `zitadel-self-hosted-deployment`: the GSM key requirement changes from
  `zitadel-machine-key-for-backend-app` to `zitadel-machine-key-for-fan-api` (the
  `backend-app` Zitadel principal is renamed `fan-api`). This is the one existing
  spec that pins a renamed identifier as a normative requirement.

<!-- Other specs (`identity-management`, `deployment-infrastructure`,
     `prod-image-pipeline`, `k8s-resource-right-sizing`, `prod-image-tag-immutability`,
     `argocd-image-automation`, `frontend-hosting`, `apex-frontend-serving`,
     `prod-environment-bootstrap`, `zitadel-action-webhook`, `secret-management`,
     `dev-db-access`, `atlas-operator`, `argocd-*`) mention old workload names only
     incidentally (prose/examples), not as behavioral contracts — external behavior
     (hostnames, APIs) is unchanged by a rename. Their references are reconciled as an
     implementation task sweep against the new convention spec, not as behavioral
     deltas here. -->
- (documentation reconciliation of incidental name references → tasks.md, not a delta)

## Impact

- **cloud-provisioning**: the bulk — Pulumi (`kubernetes.ts` GSAs + IAM, `postgres.ts`
  Cloud SQL users, GSM secret names in `identity`/`project`), all `k8s/namespaces/{backend,frontend}`
  base + overlays (Deployments/Services/SAs/HTTPRoutes/HealthCheckPolicies/ExternalSecrets/
  configmaps/ScaledObject/PodMonitoring), prod image pins, and the bump-prod-pin workflow's
  image list.
- **backend**: Dockerfile/CI image repo targets (`backend/server`→`backend/fan-api`), the
  Cloud SQL `DATABASE_USER` for fan-api, Atlas grant migration for the renamed IAM DB user,
  any workload-name references in config/docs.
- **frontend**: CI image repo targets (`frontend/web-app`→`frontend/fan-web`, `admin-app`→
  `admin-console-web`, `organizer-app`→`organizer-console-web`), the bundle-isolation script
  allowlist, release/retag + repository_dispatch pin-bump image names.
- **specification**: this new capability spec + the modified deltas above; a sweep to
  reconcile incidental name references in other specs (`k8s-resource-right-sizing`,
  `prod-image-tag-immutability`, `argocd-image-automation`, `frontend-hosting`,
  `apex-frontend-serving`, `prod-environment-bootstrap`, `zitadel-action-webhook`,
  `secret-management`, `dev-db-access`, `atlas-operator`, `argocd-*`).
- **Zitadel**: re-issue the `backend-app` MachineKey under the `fan-api` principal +
  its GSM secret; the login/OIDC apps are unaffected (audience hostnames unchanged).
- Cutover accepts brief per-service interruption; hostnames (`api.liverty-music.app`,
  `admin.liverty-music.app`, etc.) are unchanged so external URLs are stable.
