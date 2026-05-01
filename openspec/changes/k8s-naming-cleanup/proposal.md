## Why

K8s resource naming across the platform's namespaces is inconsistent. The `self-hosted-zitadel` cutover introduced two new Deployments named `zitadel` (the API container) and `zitadel-login` (the Login V2 UI container), reflecting Zitadel's upstream Helm chart conventions. But the rest of the platform follows a `<role>-<tier>` convention (e.g., backend Deployments are `server`, the K8s Service for the public Connect-RPC port is `server-svc`, the webhook port is `server-webhook-svc`).

The mismatch shows up at every operator touchpoint:

- `kubectl get deploy -n zitadel` returns `zitadel`, `zitadel-login` — operator must know that `zitadel` here means the API tier, not the namespace.
- `ZITADEL_API_URL` in `deployment-login.yaml` points at `https://auth.dev.liverty-music.app`, but for in-cluster shortcut diagnostics the Service name is `zitadel.zitadel.svc.cluster.local` — the doubly-`zitadel` qualifier is confusing.
- HTTPRoute `backendRefs` in `httproute.yaml` reference `zitadel` and `zitadel-login` Services; renaming Services means coordinated updates across the route, the Deployment selector, the PDB selector, and the HealthCheckPolicy targetRef.

This change standardizes the zitadel namespace on `zitadel-api` (API container) and `zitadel-web` (Login V2 UI container), matching the platform's existing `<role>-<tier>` convention. Container names follow (`api`, `web`) for log-readability. The rename window is brief but does require ArgoCD to perform delete-then-create on the renamed Deployment / Service / PDB resources, so it is scheduled as a deliberate change rather than ridden along an unrelated PR.

## What Changes

- **Zitadel namespace Deployments SHALL be renamed**:
  - `zitadel` → `zitadel-api`
  - `zitadel-login` → `zitadel-web`
- **Zitadel namespace Services SHALL be renamed**:
  - `zitadel` → `zitadel-api`
  - `zitadel-login` → `zitadel-web`
- **`HTTPRoute` `backendRefs`, `PodDisruptionBudget` `selector`s, `HealthCheckPolicy` `targetRef`s** SHALL be updated to point at the new names.
- **Container names within the Deployments SHALL be renamed**:
  - In `zitadel-api`: `zitadel` → `api`. Sidecars (`cloud-sql-proxy`, `bootstrap-uploader`) keep their existing names.
  - In `zitadel-web`: `zitadel-login` → `web`.
- **The `ZITADEL_API_URL` env var on `zitadel-web`** SHALL continue to point at the public URL (`https://auth.dev.liverty-music.app`) per the existing `self-hosted-zitadel` requirement; the rename is for cluster-internal naming clarity only.
- **Brief downtime** during ArgoCD's delete-then-create on renamed resources is acceptable in `dev`. PDB `minAvailable: 0` (already in place per `optimize-dev-gke-cost`) cleanly permits the eviction.
- **No other namespaces are touched in this change** — out-of-scope but tracked: `backend/server/atlas/external-secrets/reloader/argocd/cloudflared` already follow `<role>-<tier>`; the `concert-data-store` namespace MAY have similar drift but is deferred to a follow-up.

## Capabilities

### Modified Capabilities

- `zitadel-self-hosted-deployment`: Three requirements that name resources (`zitadel-api Deployment`, `zitadel-web Deployment`, in-cluster Service URL) SHALL be updated to use the new names. The semantics of each requirement (two-container layout, public Gateway URL, Cloud SQL proxy sidecar pattern) do not change.

### New Capabilities

None.

### Removed Capabilities

None.

## Impact

**Affected files**

- `cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml` — file rename + `metadata.name` change + container `name`.
- `cloud-provisioning/k8s/namespaces/zitadel/base/deployment-login.yaml` → `deployment-web.yaml` — file rename + `metadata.name` change + container `name`.
- `cloud-provisioning/k8s/namespaces/zitadel/base/service-api.yaml` — `metadata.name` + selector.
- `cloud-provisioning/k8s/namespaces/zitadel/base/service-login.yaml` → `service-web.yaml` — file rename + `metadata.name` + selector.
- `cloud-provisioning/k8s/namespaces/zitadel/base/httproute.yaml` — `backendRefs[].name`.
- `cloud-provisioning/k8s/namespaces/zitadel/base/pdb.yaml` — selector for both PDBs.
- `cloud-provisioning/k8s/namespaces/zitadel/base/kustomization.yaml` — file list.
- `cloud-provisioning/k8s/namespaces/zitadel/overlays/dev/{deployment-patch,deployment-login-patch,pdb-patch}.yaml` — patch targets renamed.

**Affected systems**

- Cluster-internal callers of the Zitadel API service: only the `zitadel-web` Login UI container, via `ZITADEL_API_URL`. Since `ZITADEL_API_URL` is the public URL (per the cutover spec), no Service-name update is needed there. If any future consumer adopts the in-cluster shortcut (`zitadel-api.zitadel.svc.cluster.local`), it picks up the new name natively.

**Reversibility**

- Single revert of the merge commit recreates the old names. ArgoCD performs the inverse delete-then-create rollback. PDB `minAvailable: 0` makes the eviction window symmetric.

**Downtime**

- ArgoCD performs delete-then-create on renamed Deployments / Services. With `replicas: 1` (dev) and `minAvailable: 0`, expect ~30–60 s of `auth.dev.liverty-music.app` unavailability per Deployment rename. Schedule outside business hours; coordinate with whoever is running E2E.

**Dependencies**

- Requires `self-hosted-zitadel` archived. Independent of the other three follow-ups but coordination-friendly with `rename-zitadel-machine-key-secret` if both are scheduled in the same maintenance window.
