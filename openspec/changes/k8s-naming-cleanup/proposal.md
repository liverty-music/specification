## Why

K8s resource naming across the platform's namespaces is inconsistent. The `self-hosted-zitadel` cutover introduced two new Deployments named `zitadel` (the API container) and `zitadel-login` (the Login V2 UI container), reflecting Zitadel's upstream Helm chart conventions. But the rest of the platform follows a `<role>-<tier>` convention (e.g., backend Deployments are `server`, the K8s Service for the public Connect-RPC port is `server-svc`, the webhook port is `server-webhook-svc`).

The mismatch shows up at every operator touchpoint:

- `kubectl get deploy -n zitadel` returns `zitadel`, `zitadel-login` — operator must know that `zitadel` here means the API tier, not the namespace.
- In-cluster Service DNS reads `zitadel.zitadel.svc.cluster.local` — the doubly-`zitadel` qualifier is confusing for anyone diagnosing routing.
- HTTPRoute `backendRefs` in `httproute.yaml` reference `zitadel` and `zitadel-login` Services; the same names appear in PDB selectors, Deployment selectors, and HealthCheckPolicy `targetRef`s — every cross-reference repeats the inconsistent naming.

Alongside the rename, the zitadel namespace currently has only a `dev` overlay; a `prod` overlay is required before the service launches. Bundling the prod overlay scaffold with the rename keeps the renamed identifiers as the single canonical naming the prod overlay learns — avoiding a "prod inherits old names, immediately gets renamed" churn.

This change standardizes the zitadel namespace on `zitadel-api` (API container) and `zitadel-web` (Login V2 UI container), matching the platform's existing `<role>-<tier>` convention. Container names follow (`api`, `web`) for log-readability. ArgoCD performs delete-then-create on renamed resources; **the service has not yet launched, so no user-facing impact and no maintenance window required**.

## What Changes

### Rename (base + dev overlay)

- **Zitadel namespace Deployments SHALL be renamed**:
  - `zitadel` → `zitadel-api`
  - `zitadel-login` → `zitadel-web`
- **Zitadel namespace Services SHALL be renamed**:
  - `zitadel` → `zitadel-api`
  - `zitadel-login` → `zitadel-web`
- **`HTTPRoute` `backendRefs`, `PodDisruptionBudget` `selector`s + `metadata.name`s, `HealthCheckPolicy` `targetRef`s + `metadata.name`s** SHALL be updated to point at the new names.
- **Container names within the Deployments SHALL be renamed**:
  - In `zitadel-api`: `zitadel` → `api`. Sidecars (`cloud-sql-proxy`, `bootstrap-uploader`) keep their existing names.
  - In `zitadel-web`: `zitadel-login` → `web`.
- **The `ZITADEL_API_URL` env var on `zitadel-web`** SHALL continue to point at the public URL (`https://auth.dev.liverty-music.app`) per the existing `self-hosted-zitadel` requirement; the rename is for cluster-internal naming clarity only. The stale header comment in `deployment-login.yaml` (lines 37–38, "ZITADEL_API_URL points at the in-cluster API Service…") is leftover from before the public-URL cutover (cloud-provisioning#214) and SHALL be removed at the same time.

### Prod overlay scaffold (new)

- **`overlays/prod/` SHALL be created**, mirroring the structural pattern of `overlays/dev/` but with prod-appropriate values. Exact parameter choices (replica count, node pool, image policy, hostname patch strategy) are deferred to `design.md`. The minimum scaffold:
  - `overlays/prod/kustomization.yaml` — references `../../base`; **does not include `cronjob-restart-zitadel.yaml`** (that resource is an explicit dev-only band-aid for `self-hosted-zitadel` §18.6 hang, scoped to dev by design — see the dev kustomization comment).
  - Patches for the renamed Deployments (`zitadel-api`, `zitadel-web`) with prod replica + nodeSelector posture.
  - HTTPRoute hostname patch — base currently hardcodes `auth.dev.liverty-music.app`; prod requires its own hostname. Resolution strategy (move hostname out of base into per-env patches vs override via a JSON patch in prod) is a `design.md` decision.
- **Open prod-overlay design questions** captured in `design.md`:
  - Hostname strategy (where does `auth.<env>.liverty-music.app` live?)
  - Replica count and PDB inheritance (`minAvailable: 1` from base, vs higher floor for prod)
  - Node pool / spot vs non-spot (current dev uses `cloud.google.com/gke-spot: "true"`)
  - Resource requests/limits for prod load profile

### Out of scope

- Other namespaces: `backend/server/atlas/external-secrets/reloader/argocd/cloudflared` already follow `<role>-<tier>`; `concert-data-store` MAY have similar drift but is deferred to a follow-up change.
- Prod ESC/Pulumi resources backing the new `prod` overlay (Cloud SQL DB, IAM, Secret Manager entries for prod Zitadel). The scaffold uses placeholder values that prod-resource provisioning will replace; tracked separately.

## Capabilities

### Modified Capabilities

- `zitadel-self-hosted-deployment`: Three requirements that name resources (`zitadel-api Deployment`, `zitadel-web Deployment`, in-cluster Service URL) SHALL be updated to use the new names. The semantics of each requirement (two-container layout, public Gateway URL, Cloud SQL proxy sidecar pattern) do not change. A new requirement SHALL describe the per-environment overlay pattern (dev = current cost-optimized posture; prod = scaffold per this change with design-determined parameters).

### New Capabilities

None.

### Removed Capabilities

None.

## Impact

**Affected files (rename)**

- `cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml` — `metadata.name` change + container `name`.
- `cloud-provisioning/k8s/namespaces/zitadel/base/deployment-login.yaml` → renamed to `deployment-web.yaml` — `metadata.name` change + container `name` + remove stale header comment.
- `cloud-provisioning/k8s/namespaces/zitadel/base/service-api.yaml` — `metadata.name` + selector.
- `cloud-provisioning/k8s/namespaces/zitadel/base/service-login.yaml` → renamed to `service-web.yaml` — `metadata.name` + selector.
- `cloud-provisioning/k8s/namespaces/zitadel/base/httproute.yaml` — `backendRefs[].name` (2 rules).
- `cloud-provisioning/k8s/namespaces/zitadel/base/pdb.yaml` — `metadata.name` + selector for both PDBs.
- `cloud-provisioning/k8s/namespaces/zitadel/base/healthcheckpolicy.yaml` — `metadata.name` + `targetRef.name` for both HealthCheckPolicies.
- `cloud-provisioning/k8s/namespaces/zitadel/base/kustomization.yaml` — resource file list (renamed entries).
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/kustomization.yaml` — patch `target.name`s.
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/deployment-patch.yaml` — `metadata.name`.
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/deployment-login-patch.yaml` → renamed to `deployment-web-patch.yaml` — `metadata.name`.
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/pdb-patch.yaml` — `metadata.name`s for both PDBs.

**Affected files (prod overlay scaffold)**

- `cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/kustomization.yaml` — new file; mirrors dev structure minus the dev-only CronJob.
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/deployment-api-patch.yaml` — new file; prod replica + nodeSelector posture.
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/prod/deployment-web-patch.yaml` — new file; prod replica + nodeSelector posture.
- Additional files (hostname patch, PDB patch if needed) determined in `design.md`.

**Affected systems**

- Cluster-internal callers of the Zitadel API service: only the `zitadel-web` Login UI container, via `ZITADEL_API_URL`. Since `ZITADEL_API_URL` is the public URL (per the cutover spec), no Service-name update is needed there. If any future consumer adopts the in-cluster shortcut (`zitadel-api.zitadel.svc.cluster.local`), it picks up the new name natively.
- ArgoCD `dev` Application: performs delete-then-create on renamed Deployments / Services / PDBs / HealthCheckPolicies. With the service not yet launched, this is a clean rebuild — no eviction concerns.
- ArgoCD `prod` Application: needs to be created/wired to point at the new `overlays/prod/` directory. Whether this is in scope of this change or done as part of prod-resource provisioning is a `design.md` decision.

**Reversibility**

- Single revert of the merge commit recreates the old names. ArgoCD performs the inverse delete-then-create rollback. The prod overlay scaffold is removed by the revert as well; no orphan resources because prod hasn't synced yet (or has synced placeholders only).

**Dependencies**

- Requires `self-hosted-zitadel` archived ✓ (archived 2026-05-11).
- Independent of `rename-zitadel-machine-keys` ✓ (archived 2026-05-13); the two are now decoupled.
- Prod-resource provisioning (Cloud SQL, IAM, GSM) is **NOT** required for this change to merge; the prod overlay scaffold may render to manifests that reference yet-to-exist secrets/DBs, but ArgoCD only syncs prod once the prod Application is created and resources exist. The scaffold lands in source first.
