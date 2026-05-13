# Design — k8s-naming-cleanup

## Decisions

### 1. Hostname patch strategy: both overlays patch; base has no `hostnames`

`base/httproute.yaml` currently hardcodes `auth.dev.liverty-music.app` — env-specific value leaking into base. Moving the field to per-environment overlays makes the env-leak explicit and matches how `backend/base/server/httproute.yaml` and `frontend/base/web/httproute.yaml` already work (those files omit `hostnames` entirely — they don't need scoping because they don't have a `/` catch-all rule).

Zitadel's HTTPRoute is special: it has a `/` catch-all rule (`/ui/v2/login` plus everything-else → API). Without an explicit `hostnames` filter, the `/` catch-all would intercept all Gateway traffic, breaking `backend` and `frontend` routing. Hostname scoping is therefore **load-bearing** for zitadel and must be preserved per environment.

**Implementation**:

```yaml
# base/httproute.yaml — REMOVE hostnames field
spec:
  parentRefs: [...]
  # hostnames removed
  rules: [...]

# overlays/dev/httproute-patch.yaml — NEW
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: zitadel-route
spec:
  hostnames:
  - auth.dev.liverty-music.app

# overlays/prod/httproute-patch.yaml — NEW
spec:
  hostnames:
  - auth.liverty-music.app
```

Both overlay `kustomization.yaml`s add the patch entry.

Prod hostname is the bare apex `auth.liverty-music.app` — prod is treated as the canonical environment (no env subdomain). Dev gets the `*.dev.liverty-music.app` family as the alternate. Must be aligned with GCP cert map prod-IP binding (out of scope; prerequisite).

### 2. Prod replicas + node pool: `replicas: 2` + spot

| Resource | Dev | Prod (chosen) |
|---|---|---|
| `zitadel-api` replicas | 1 | **2** |
| `zitadel-web` replicas | 1 | **2** |
| Node pool | spot | **spot** (cost-driven) |
| Pod anti-affinity | base — `hostname` topology, `requiredDuringScheduling` | inherits base |
| PDB `minAvailable` | 0 (dev relaxed) | **1** (base) |

**Rationale for spot in prod**:
- Service has not yet launched — cost matters more than rock-solid uptime
- Base already has `podAntiAffinity` requiring different hosts per replica ([deployment-api.yaml:40-47](cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml#L40-L47)) — this is exactly the spot-tolerance safeguard. Comment at L38-39: "Keep both replicas on different nodes so a single Spot preemption cannot take the entire API plane down."
- PDB `minAvailable: 1` (base) + replicas 2 → at most one pod can be voluntarily evicted at a time
- Spot preemption guarantees ≤30s graceful drain notice; with 2 replicas on different hosts, the surviving replica continues serving while the evicted one rescheduled

**Acknowledged risks**:
- Simultaneous preemption of both spot nodes is rare but possible. If it happens, ≤30s window where both pods rescheduling concurrently. Acceptable pre-launch.
- Eviction during a deploy can compound: rolling update + spot preemption could briefly land at 0 ready. `maxSurge: 1, maxUnavailable: 0` (base) keeps the deploy from going below 1 voluntarily, but spot can take 1 below 1 involuntarily.

Revisit `non-spot` once traffic exists / SLO matters more than dev/prod parity.

### 3. ArgoCD prod Application: created in this change

Add `argocd-apps/prod/zitadel.yaml` mirroring `argocd-apps/dev/zitadel.yaml` but pointing at `k8s/namespaces/zitadel/overlays/prod`.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: zitadel
  namespace: argocd
  finalizers:
  - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/liverty-music/cloud-provisioning.git
    targetRevision: main
    path: k8s/namespaces/zitadel/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: zitadel
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    - ServerSideApply=true
```

**Open prerequisite** (out of scope, must precede prod sync):
- Prod ArgoCD instance bootstrapped (currently only dev ArgoCD exists; `argocd-apps/dev/` is the only argocd-apps directory)
- Prod Cloud SQL DB + Postgres admin secret (`zitadel-postgres-admin-password` in GSM prod)
- Prod GSM secrets backing the ExternalSecrets (`zitadel-machine-key-for-backend-app-prod`, etc.)
- Prod ESC environment values (`liverty-music/prod`)
- Prod GCP cert map binding `auth.{prod-hostname}` → prod Gateway static IP

Because these prereqs are absent at the moment, ArgoCD will report `OutOfSync` / `Healthy: Missing` until they exist. The Application file lands in source, and sync becomes useful once prereqs are provisioned in a follow-up. **No syncPolicy adjustment** — we want ArgoCD to start syncing immediately once prereqs land, not require a separate flip.

### 4. Container short-naming

Confirmed from proposal: `zitadel` → `api` (in `zitadel-api` Deployment), `zitadel-login` → `web` (in `zitadel-web` Deployment). Log readability:

```
Before: kubectl logs -n zitadel deploy/zitadel -c zitadel
After:  kubectl logs -n zitadel deploy/zitadel-api -c api
```

Sidecars (`cloud-sql-proxy`, `bootstrap-uploader`) keep their existing names — they're shared patterns elsewhere in the platform.

### 5. Service-link env-var comment update

[deployment-api.yaml:30-36](cloud-provisioning/k8s/namespaces/zitadel/base/deployment-api.yaml#L30-L36) explains why `enableServiceLinks: false` is needed:

> Without this, the `zitadel` Service in this namespace injects `ZITADEL_PORT=tcp://<ip>:80` into every pod, which Viper then parses as the top-level Zitadel config field `Port` (expected uint16) — causing startup to fail.

After rename, the conflicting env var name becomes `ZITADEL_API_PORT` (Service `zitadel-api` → service-link env vars are `ZITADEL_API_*`). Viper would map this to `Api.Port` — Zitadel has no such config field, so the conflict actually *goes away*. But `enableServiceLinks: false` stays defensively (other Services could be added; the flag is cheap insurance).

**Action**: update the comment to reflect the new Service name and clarify that the original conflict no longer applies after rename but the flag stays defensively.

### 6. Stale comment cleanup

[deployment-login.yaml:37-38](cloud-provisioning/k8s/namespaces/zitadel/base/deployment-login.yaml#L37-L38):

```
# ZITADEL_API_URL points at the in-cluster API Service so the login UI
# can call the API without egressing the cluster.
```

This contradicts the actual value (`https://auth.dev.liverty-music.app`) and the detailed rationale a few lines below (L59-71). Leftover from before [cloud-provisioning#214](https://github.com/liverty-music/cloud-provisioning/pull/214). Removed as part of this change (the file is being renamed anyway).

## Trade-offs explored and rejected

### Hostname strategy B: keep base = dev hostname, prod patches only
Rejected because base would continue to embed env-specific data. The dev overlay would have no httproute artifact while prod would — asymmetric.

### Hostname strategy C: Kustomize replacements + ConfigMap variable
Rejected as over-engineering. No other namespace uses Kustomize `replacements` for hostnames; introducing the pattern for one value across two overlays is not worth the cognitive overhead.

### Replicas: 3 + non-spot
Rejected for cost during pre-launch. Pod anti-affinity already gives 2-replicas-on-different-nodes guarantee; 3rd replica adds cost without proportional safety on spot.

### ArgoCD Application deferred to separate change
Rejected by explicit user decision: bundle Application in this change so the source tree captures the complete prod topology at once. The Application's `OutOfSync` state until prereqs land is an acceptable interim signal.

## Out-of-scope cleanups noted

- `concert-data-store` namespace MAY have similar naming drift; deferred to a follow-up change.
- Backend / frontend HTTPRoutes have inconsistencies vs zitadel (no `hostnames`, no path-prefix rules) — that's a Gateway-level routing topology question, separately worth designing. Out of scope here.
- Prod ESC / Pulumi / GCP cert map / prod ArgoCD bootstrap — flagged as prerequisites, tracked via the natural OutOfSync signal on the new Application.
