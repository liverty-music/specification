## Context

We currently deploy Zitadel via hand-written Kustomize manifests under
[k8s/namespaces/zitadel/](k8s/namespaces/zitadel/): two Deployments
(`zitadel-api` running `ghcr.io/zitadel/zitadel`, `zitadel-web` running
`ghcr.io/zitadel/zitadel-login`), two Services, an HTTPRoute splitting
`/ui/v2/login` vs catch-all, a `HealthCheckPolicy` pair, a PDB, a
ServiceAccount, a ConfigMap, and four ExternalSecrets (masterkey, admin
machine key, web PAT, postgres admin). On top of that, the
`route-login-v2-via-internal-zitadel-api` change (now deployed to both
envs) layered in:

- A custom `ZitadelInstanceCustomDomain` Pulumi Dynamic Resource that
  CRUDs an `InstanceCustomDomain` in Zitadel via a System User JWT,
- A `pulumi-system` System User (declared in `ZITADEL_SYSTEMAPIUSERS` env
  on the API Pod, public key in `external-secret-system-api-pub.yaml`,
  private key in GSM Secret managed by Pulumi `tls.PrivateKey`),
- A manual `scripts/discover-zitadel-instance-id.mjs` step gated behind
  `instanceIdMap[env]` + `__UNSET__` sentinel,
- A flip of `ZITADEL_API_URL` on the Login UI Pod from the public
  issuer URL to `http://zitadel-api.zitadel.svc.cluster.local`.

The motivating bug (Login UI's Connect-RPC hanging for 30s through the
public LB hairpin) is solved by *that* change. But after digging into
the Zitadel source ([cmd/defaults.yaml](https://github.com/zitadel/zitadel/blob/main/cmd/defaults.yaml),
[apps/login/src/lib/custom-headers.ts](https://github.com/zitadel/zitadel/blob/main/apps/login/src/lib/custom-headers.ts),
[apps/login/src/lib/zitadel.ts](https://github.com/zitadel/zitadel/blob/main/apps/login/src/lib/zitadel.ts))
and the official chart values
([zitadel-charts/charts/zitadel/values.yaml](https://github.com/zitadel/zitadel-charts/blob/main/charts/zitadel/values.yaml)),
the canonical pattern is simply:

```yaml
# Login UI container env
ZITADEL_API_URL: "http://<release>-zitadel:8080"          # cluster-internal Service
CUSTOM_REQUEST_HEADERS: "Host:auth.liverty-music.app"      # presented to API
```

Zitadel's `apps/login/src/lib/custom-headers.ts` parses
`CUSTOM_REQUEST_HEADERS` and merges those headers into every outbound
Connect-RPC call. The API's `instance_interceptor.go` then resolves the
instance by the `Host` header (matching configured `InstanceDomains`),
not by the cluster-internal Service hostname. No InstanceCustomDomain
registration is required.

The Helm chart bakes both env vars in by default and exposes
`zitadel.configmapConfig` / `zitadel.customConfigmapConfig` /
`zitadel.dbConfig` / `login.customConfigmapConfig` for the rest. Since
we are still pre-service-in, the opportunity cost of "keep the
hand-rolled manifests" is higher than the cutover cost of swapping to
the chart while also deleting the over-engineered Phase 1/2 code.

Stakeholders: solo developer (user). No external SLO commitments yet.
Cutover window: any time outside of an active development session.

## Goals / Non-Goals

**Goals:**
- Replace `k8s/namespaces/zitadel/base/deployment-api.yaml` and
  `deployment-web.yaml` with a single `helmCharts:` entry rendering
  `zitadel/zitadel-charts` (chart version pinned alongside ESO's pin
  pattern). Both API and Login UI Deployments come from the chart.
- Eliminate all infrastructure introduced by
  `route-login-v2-via-internal-zitadel-api` (Dynamic Resource, System
  User, GSM Secrets for system-api keys, ESO ExternalSecret, env, mount,
  discover script, instanceIdMap). Replace with two lines of values.yaml.
- Preserve resource names (`zitadel-api`, `zitadel-web`) so the HTTPRoute,
  HealthCheckPolicy, ServiceMonitor, and any kubectl-based ops keep working
  without modification.
- Preserve database state, masterkey, admin org id, instance id by
  reusing the existing `zitadel-masterkey` and
  `zitadel-machine-key-for-pulumi-admin` GSM Secrets and pointing the
  chart's database config at the same Cloud SQL instance.
- Cut over dev first; verify Login UI end-to-end (`/ui/v2/login/login`
  loads, `/ui/v2/login/register` form submits); then cut over prod.

**Non-Goals:**
- No Zitadel version bump as part of this change. The chart pins
  `image.tag` to the same `v4.14.0` we already run.
- No database migration. Zitadel runs against the existing Cloud SQL
  database with the existing masterkey.
- No change to the HTTPRoute, HealthCheckPolicy, Gateway certificate,
  domain hierarchy, or any DNS records.
- No change to the backend's MachineKey infrastructure
  (`ZitadelPermanentPassword` keeps its own admin client; only the
  System User pieces are deleted).
- No re-organization of the ESC environment hierarchy or stack file
  structure.

## Decisions

### D1: Use the official `zitadel/zitadel-charts` chart via Kustomize `helmCharts:` integration

**Choice**: Render the chart at `kustomize build` time, same pattern we
already use for `external-secrets`, `reloader`, `nats`, `keda`,
`atlas-operator`.

**Why over alternatives**:

- *Option A — keep raw Kustomize, just add `CUSTOM_REQUEST_HEADERS` env
  and delete Phase 1/2 code.* Solves the over-engineering but doesn't
  eliminate the maintenance surface of two hand-tuned Deployment
  manifests. We diverge from upstream defaults every time the chart
  updates pod security context, probes, resource hints, etc. Rejected
  because the user explicitly requested simplification ("できる限り
  構成をシンプルにしたい").
- *Option B — install the chart via a separate ArgoCD `Application`
  with `spec.source.helm`.* Inconsistent with the existing
  `helmCharts:` pattern in our manifest tree; would require splitting
  the zitadel namespace into two ArgoCD apps (one for HTTPRoute /
  HealthCheckPolicy / ExternalSecrets, one for the chart). Rejected
  because it adds an ArgoCD App to maintain without a corresponding
  benefit.
- *Option C (chosen) — `helmCharts:` in
  `k8s/namespaces/zitadel/base/kustomization.yaml`.* Single ArgoCD
  App, single values.yaml, chart version pinned, render is reproducible
  in CI via `kubectl kustomize --enable-helm`. Matches existing pattern.

### D2: Resource naming via `fullnameOverride` (with chart constraint discovered during prototyping)

**Choice**: Set `fullnameOverride: zitadel-api` for the API side. The
Login UI side is NOT user-renameable — the chart's
`_helpers.tpl:38` hard-codes `zitadel.login.fullname` to
`<zitadel.fullname>-login`, ignoring `login.fullnameOverride`
(verified against [zitadel-charts@9.34.1](https://github.com/zitadel/zitadel-charts/blob/zitadel-9.34.1/charts/zitadel/templates/_helpers.tpl)
during prototyping). The Login UI therefore lands as `zitadel-api-login`.

Resulting names:
- API Deployment / Service / ConfigMap: `zitadel-api` (via `fullnameOverride`).
- Login UI Deployment / Service: `zitadel-api-login` (chart-forced suffix).

The shared ServiceAccount `zitadel` is reused via `serviceAccount.create: false` +
`serviceAccount.name: zitadel` (both at top-level and under `login:`).

**Why this naming**: `fullnameOverride: zitadel-api` (not the
chart-default `zitadel`) avoids re-introducing the legacy
`ZITADEL_PORT` env-var Viper collision that motivated the earlier
`zitadel`→`zitadel-api` rename (K8s service-discovery env var
`ZITADEL_PORT=tcp://<ip>:80` would otherwise be parsed by Viper as
the binary's `Port` config field and startup would fail).

**Downstream consequences of the Login UI name**: HTTPRoute
backendRefs and HealthCheckPolicy targetRef are updated from the
prior `zitadel-web` to `zitadel-api-login` to match the chart-natural
name. The `HealthCheckPolicy` resource name `zitadel-web-policy` is
retained for ops continuity — only its `targetRef.name` field is
updated.

### D3: Reuse existing masterkey and admin MachineKey GSM Secrets

**Choice**: Configure chart values to mount the existing
`zitadel-masterkey` GSM Secret (via the existing ESO ExternalSecret
syncing it into the K8s Secret `zitadel-masterkey`) using
`zitadel.masterkeySecretName: zitadel-masterkey`. Keep the
`bootstrap-uploader` sidecar wired through `extraContainers` so the
prod bootstrap pattern (chicken-and-egg admin key upload) stays
intact. The chart's first boot detects the existing instance via the
database state and skips re-bootstrapping.

**Why over alternatives**:

- *Option A — let the chart manage its own masterkey via a freshly-generated
  Secret.* Catastrophic: the chart would generate a new masterkey,
  Zitadel would fail to decrypt the database rows encrypted under the
  old key. Rejected outright.
- *Option B (chosen) — point the chart at our existing Pulumi-managed
  masterkey.* The chart provides `zitadel.masterkeySecretName` (or
  equivalent — chart version-dependent) precisely for this case.

### D4: `cloud-sql-proxy` + `bootstrap-uploader` as K8s native sidecars (`initContainers` with `restartPolicy: Always`)

**Choice**: Inject both sidecars via `zitadel.initContainers` with
`restartPolicy: Always` (Kubernetes 1.29+ native sidecar pattern), NOT
via `zitadel.extraContainers`.

**Why over alternatives**:

- *Option A — `zitadel.extraContainers` (the naive choice).* Discovered
  bug during local rendering: the chart auto-injects `zitadel.extraContainers`
  into the main API Deployment AND the init/setup Jobs (`job_init.yaml` +
  `job_setup.yaml` templates concatenate `zitadel.extraContainers` into
  `containers:` before the primary container). Classic sidecars are
  never-exits (`cloud-sql-proxy` is a long-running proxy;
  `bootstrap-uploader` does `tail -f /dev/null` after upload), so the
  init/setup Job Pods never reach Succeeded — every chart deploy hits
  `activeDeadlineSeconds: 300` and Job fails. Rejected.
- *Option B — disable the chart's init/setup Jobs (`initJob.enabled: false`,
  `setupJob.enabled: false`).* Loses automatic schema migration on
  chart version bumps. Bad long-term.
- *Option C (chosen) — `zitadel.initContainers` with `restartPolicy:
  Always`.* K8s native sidecar containers (KEP-753, stable in 1.29).
  They run alongside the main container exactly like classic sidecars
  for Deployments, BUT in a Job context they receive SIGTERM and exit
  cleanly when the main container completes — Job reaches Succeeded.
  The chart's templates render `zitadel.initContainers` verbatim via
  `toYaml`, so `restartPolicy: Always` carries through. GKE Autopilot
  runs 1.30+, satisfying the version requirement.

The sidecars get injected into init/setup Job Pods too. For
`cloud-sql-proxy` that's actually required (the `zitadel init` and
`zitadel setup` commands need DB access via the proxy). For
`bootstrap-uploader` it's harmless — the `/var/zitadel/bootstrap/admin-sa.json`
file never appears in those Pods, the watch loop spins on `sleep 2`,
and SIGTERM at Job-end exits it cleanly.

### D5: Shared `base/values.yaml` + per-overlay `additionalValuesFiles` via `LoadRestrictionsNone`

**Choice**: `base/values.yaml` holds the shared chart values; each
overlay's `values.yaml` carries only env-specific diffs (ExternalDomain,
Cloud SQL IAM usernames, full `zitadel.initContainers` list with the
env-specific connection name). Overlays' `helmCharts:` entries layer
them via `valuesFile: ../../base/values.yaml` +
`additionalValuesFiles: [values.yaml]`.

**Why over alternatives**:

- *Option A — self-contained per-overlay `values.yaml` (no base sharing).*
  ~80% duplication between dev and prod values files; every chart
  version bump or structural change requires lockstep edits in two
  files. Initially adopted because Kustomize's default
  `LoadRestrictionsRootOnly` blocks the cross-directory `valuesFile`
  ref. Rejected after research: the restriction IS configurable.
- *Option B (chosen) — shared base + `LoadRestrictionsNone`.* Kustomize
  documents the `--load-restrictor=LoadRestrictionsNone` flag explicitly
  (`man kubectl-kustomize`, Argo CD `kustomize.buildOptions` docs). The
  documented trade-off is loss of "kustomization relocatability" — no
  concern here because no overlay is designed to be moved/copied. Two
  places need the flag:
  1. `Makefile:lint-k8s` (the `kustomize build --enable-helm` invocation)
  2. ArgoCD's `argocd-cm.kustomize.buildOptions` (so production rendering
     gets the same treatment as CI lint)
  After this flag is applied repo-wide, all overlay→base value refs
  work, not just the zitadel ones.

The `zitadel.initContainers` list still cannot live in `base/values.yaml`
alone because Helm values-list semantics REPLACE rather than MERGE on
layering. The env-specific `cloud-sql-proxy` connection name forces the
full list (including the identical `bootstrap-uploader`) into the
overlay. ~25 lines of duplication for `bootstrap-uploader`, vs ~150
lines avoided by sharing the rest.

### D6: Chart auto-generates `CUSTOM_REQUEST_HEADERS`; only override `NEXT_PUBLIC_BASE_PATH`

**Choice**: Let the chart auto-generate `CUSTOM_REQUEST_HEADERS` and
`ZITADEL_API_URL` via its `login-config-dotenv` ConfigMap. Override
only `NEXT_PUBLIC_BASE_PATH=/ui/v2` via `login.env` to collapse the
`/ui/v2/login/login` redundancy.

The chart at v9.34.1 emits the following on the Login UI Pod
(confirmed via local `kustomize build --enable-helm` render):

```
ZITADEL_API_URL=http://zitadel-api:80
CUSTOM_REQUEST_HEADERS=Host:<ExternalDomain>,X-Zitadel-Public-Host:<ExternalDomain>
```

`ZITADEL_API_URL` is the cluster-internal Service URL derived from
the chart's `fullnameOverride: zitadel-api` + `service.port: 80`.
`CUSTOM_REQUEST_HEADERS` carries both `Host` and the canonical
`X-Zitadel-Public-Host` header (the latter is what Zitadel's
`PublicHostHeaders` default reads from in `cmd/defaults.yaml` for
instance discovery from cluster-internal callers).

DO NOT override `CUSTOM_REQUEST_HEADERS` inline in `login.env` — that
would silently drop the auto-generated `X-Zitadel-Public-Host` half
of the header pair, breaking instance discovery on the cluster-internal
hop.

**Why over alternatives**:

- *Option A — InstanceCustomDomain registration (the
  `route-login-v2-via-internal-zitadel-api` approach).* Rejected per
  proposal: this is the over-engineered path being superseded.
- *Option B (chosen) — let the chart's `login-config-dotenv` ConfigMap
  drive both env vars, override only what we need to differ from chart
  defaults (`NEXT_PUBLIC_BASE_PATH`).* Canonical upstream pattern,
  no Pulumi state, no GSM secrets, the X-Zitadel-Public-Host header
  is included automatically.

### D7: Pulumi state cleanup for `protect: true` resources

**Choice**: The deletion sequence:

1. Push a PR that removes the resource declarations from `secrets.ts`
   and `src/index.ts` (System User PrivateKey + 2 GSM Secrets + 2
   SecretVersions + IAM binding + InstanceCustomDomain).
2. **Before merge**, manually run `pulumi state unprotect <urn>` for
   each of the 5 `protect: true` resources in each stack (dev + prod).
3. Merge → Pulumi auto-up on dev runs `delete` for the now-unprotected
   resources. Prod requires manual `pulumi up`.

**Why**: `protect: true` blocks deletion. Removing the declaration
without first un-protecting causes Pulumi to error rather than delete.
Documented in tasks.md step list.

### D8: Cutover order — dev first, then prod, both single-sync

**Choice**:

1. Open one PR that contains: spec delta + chart manifests + values.yaml
   + all Pulumi deletions + runbook update.
2. Merge → dev Pulumi auto-up runs first (deletes Phase 1/2 resources
   in dev).
3. After dev Pulumi up settles, ArgoCD syncs the new manifests in dev →
   Pods restart against the existing dev database → verify Login UI
   sign-up flow via Pixel.
4. Manually trigger prod Pulumi up.
5. After prod Pulumi up settles, ArgoCD syncs prod → Pods restart →
   verify prod Login UI.

**Why**: One PR keeps the diff atomic and reviewable. The dev →
verify → prod sequence is gated on observable dev success, not a clock.

## Risks / Trade-offs

- **[Risk] Chart `fullnameOverride` keys diverge from our guess** → Verify
  the actual values.yaml keys at the pinned chart version *before*
  writing the final values.yaml. If `fullnameOverride` doesn't exist
  for the Login UI portion, fall back to chart `nameOverride` +
  `releaseName` combo, or rename our HTTPRoute backendRefs (rejected
  — too noisy). Mitigation: prototype values.yaml + `kubectl kustomize
  --enable-helm` rendering locally before opening the PR.
- **[Risk] Pod restart causes Login UI 503 during ArgoCD sync** →
  Acceptable (pre-service-in, no users). PodDisruptionBudget +
  rollingUpdate.maxUnavailable: 0 limits the window. Mitigation:
  perform cutover outside of active dev sessions.
- **[Risk] Chart adds a resource we didn't expect (e.g., default
  NetworkPolicy that breaks the cloud-sql-proxy sidecar)** → Render
  locally with `kubectl kustomize --enable-helm k8s/namespaces/zitadel/base`
  before commit; review all generated resources; disable defaults via
  values.yaml (`networkPolicy.enabled: false` etc) if they conflict.
- **[Risk] Cloud SQL IAM user name `zitadel@liverty-music-dev.iam`
  doesn't survive a chart values that defaults DSN to a password-bearing
  form** → Force the chart's database config to IAM auth via
  `zitadel.dbConfig.user.password: ""` and `username: zitadel@...`. If
  the chart can't express "no password, IAM auth", fall back to
  injecting raw env (`ZITADEL_DATABASE_POSTGRES_USER_USERNAME` etc).
- **[Risk] `protect: true` removal in two steps (unprotect → merge)
  introduces a window where the resources exist without protection** →
  Acceptable; window is minutes, only the user has admin access.
  Alternatively, move the `protect: true` resources to a separate
  Pulumi destroy commit that lands first. Decided against extra
  commits for solo-developer simplicity.
- **[Risk] Forgetting to keep the bootstrap-uploader sidecar disables
  the chicken-and-egg path for a future restore-from-scratch** →
  Required acceptance criterion in tasks.md is "chart-rendered API
  Pod has bootstrap-uploader sidecar visible in `kubectl describe pod`".
- **[Trade-off] Chart pinning vs. easy upstream updates** → Pin the
  chart version explicitly in `kustomization.yaml` (just like ESO at
  `0.12.1`). Upgrade via PR + dev verify + prod cutover. Same cadence
  as today's image-tag bumps.
- **[Trade-off] Helm rendering at `kustomize build` time means we lose
  Helm's release-history concept** → Already a non-feature in our
  workflow (ArgoCD is the source of truth for "what's deployed"; rollback
  is `git revert`, not `helm rollback`). No loss.

## Migration Plan

See tasks.md for the step-by-step. Summary:

1. Local prototype: write `values.yaml` + updated `kustomization.yaml`,
   render via `kubectl kustomize --enable-helm`, diff against current
   rendered base.
2. Pulumi: delete code declarations, but first run `pulumi state
   unprotect` for the 5 `protect: true` resources in both stacks.
3. Open one PR covering spec delta + manifests + Pulumi changes +
   runbook update.
4. Merge → dev auto-up → dev ArgoCD sync → verify Login UI.
5. Prod manual `pulumi up` → prod ArgoCD sync → verify Login UI.
6. Archive the OpenSpec change (`/opsx:archive migrate-zitadel-to-helm-chart`)
   after isComplete=true.

**Rollback**: `git revert` the PR. Re-protect resources is not
necessary — Pulumi will re-create them on the reverted state with
`protect: true` reasserted. The previous-generation Deployments come
back through the same ArgoCD sync. Database is untouched; Zitadel
attaches with the same masterkey. RTO ≈ time for one Pulumi up + one
ArgoCD sync (~10 min).
