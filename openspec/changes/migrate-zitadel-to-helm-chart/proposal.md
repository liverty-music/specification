> **Supersedes:** `route-login-v2-via-internal-zitadel-api` (deployed to
> dev + prod 2026-05-19, deleted from `openspec/changes/` as part of
> this change before it could be archived — its proposed code lived
> only briefly in production and is fully replaced by the canonical
> `CUSTOM_REQUEST_HEADERS` pattern delivered via Helm chart values).

## Why

The Login V2 UI → Zitadel API in-cluster routing problem (originally
solved by the `route-login-v2-via-internal-zitadel-api` change, which
introduced a custom `ZitadelInstanceCustomDomain` Pulumi Dynamic
Resource + `SystemAPIUsers`-declared System User + private-key signing
pipeline) has a canonical upstream solution we discovered after the
fact: `ZITADEL_API_URL=http://<internal-service>:<port>` paired with
`CUSTOM_REQUEST_HEADERS="Host:<ExternalDomain>"` on the Login UI
container. This is the pattern shipped in both the official
`zitadel-charts` Helm chart and the upstream `docker-compose.yml`
reference. Our hand-rolled InstanceCustomDomain approach is therefore
~500 lines of Pulumi + 22 unit tests + 2 GSM secrets + an ESO binding
+ a manual instance-id discovery step that all become unnecessary the
moment we adopt the official Helm chart.

This change does two things at once: (1) replaces our hand-maintained
Kustomize manifests for the Zitadel API and Login UI Deployments with
the official `zitadel/zitadel-charts` Helm chart, and (2) deletes the
entire `route-login-v2-via-internal-zitadel-api` apparatus because the
chart's `extraEnv` + `customConfigmapConfig` plumbing replaces it with
two lines of values.yaml. We can do this now because Liverty Music has
not yet gone service-in — there are no real users to migrate, no
SLO/SLA risk, and the cutover window is bounded only by our own dev
testing.

## What Changes

- **MAJOR**: Migrate `k8s/namespaces/zitadel/base/` from raw Kustomize
  Deployments (`deployment-api.yaml`, `deployment-web.yaml`) to the
  official `zitadel/zitadel-charts` chart, rendered via Kustomize's
  `helmCharts:` integration (already in use for ESO and Reloader).
- **MAJOR**: Configure the chart with `ZITADEL_API_URL=http://<release>-zitadel:8080`
  and `CUSTOM_REQUEST_HEADERS=Host:<ExternalDomain>` so the Login UI's
  Connect-RPC traffic reaches the API via cluster-internal Service DNS
  while presenting the correct `Host` header (canonical upstream
  pattern; no per-instance domain registration needed).
- **BREAKING**: Delete the `ZitadelInstanceCustomDomain` Pulumi Dynamic
  Resource (`src/zitadel/dynamic/instance-custom-domain.ts`,
  `api-client.ts:buildSystemAssertion`/`systemApiCall`, tests,
  `scripts/discover-zitadel-instance-id.mjs`, `instanceIdMap`,
  `SYSTEM_API_USER_NAME`, `ZITADEL_API_INTERNAL_HOST` constants, and
  the wire-up in `src/index.ts`).
- **BREAKING**: Delete the `pulumi-system` System User infrastructure
  (`SystemApiKeyComponent` additions in `SecretsComponent`: `tls.PrivateKey`,
  `zitadel-system-api-key` GSM Secret, `zitadel-system-api-pub` GSM Secret,
  ESO IAM binding, `external-secret-system-api-pub.yaml`,
  `ZITADEL_SYSTEMAPIUSERS` env on the API container, system-api-pub
  Secret volume mount).
- **BREAKING**: Drop the `instance-id capture` step from the dev
  shutdown/restart runbook (Section B6b in `docs/runbooks/dev-shutdown-restart.md`)
  — no longer needed once `instanceIdMap` is gone.
- Resource naming: chart releases default to `zitadel`. Set
  `fullnameOverride: zitadel-api` to preserve the API resource name
  (avoiding the legacy `ZITADEL_PORT` env-var Viper collision that
  motivated the earlier `zitadel`→`zitadel-api` rename). The Login UI
  resource name is NOT user-configurable: the chart's `_helpers.tpl:38`
  hard-codes `zitadel.login.fullname` to `<zitadel.fullname>-login`,
  ignoring `login.fullnameOverride` (verified empirically against
  chart v9.34.1). The Login UI therefore lands as `zitadel-api-login`,
  and the existing HTTPRoute backendRef + HealthCheckPolicy `targetRef`
  are updated from the prior `zitadel-web` to `zitadel-api-login`
  (HealthCheckPolicy resource name `zitadel-web-policy` retained for
  ops continuity — only the `targetRef.name` field changes).
- Preserve data continuity: the masterkey, admin org id, and instance
  id all live in Postgres (Cloud SQL) and GSM. The chart deploys
  against the existing database, reuses the existing `zitadel-masterkey`
  GSM Secret via `existingMasterkeySecretName`, and reuses the existing
  `zitadel-machine-key-for-pulumi-admin` for bootstrap. No data
  migration; this is a pure manifest swap.
- Cutover: dev first (rollout, verify Login UI sign-in via Pixel-style
  end-to-end), then prod. Each environment performs the swap in a
  single ArgoCD sync — old Deployments are pruned, new Helm-rendered
  Deployments take their place, Pods restart, `bootstrap-uploader`
  sidecar idles (instance already exists), Zitadel reattaches to the
  existing database via the unchanged `zitadel-masterkey`.

## Capabilities

### New Capabilities
<!-- None. This change modifies and shrinks an existing capability. -->

### Modified Capabilities
- `zitadel-self-hosted-deployment`: Replaces the Kustomize-rendered
  Deployment manifests with a Helm-chart-rendered topology, removes
  the three requirements introduced by the
  `route-login-v2-via-internal-zitadel-api` change
  (Cluster-Internal URL via direct routing; InstanceCustomDomain
  registration; SystemAPIUsers-declared System User), and replaces
  them with a single requirement that captures the
  `ZITADEL_API_URL` + `CUSTOM_REQUEST_HEADERS` pattern delivered
  through chart values. Also updates the "Two-Container Deployment"
  requirement to permit chart-rendered Deployments (resource names
  unchanged via `fullnameOverride`).

## Impact

**Code (cloud-provisioning)**:
- Delete: `src/zitadel/dynamic/instance-custom-domain.ts`,
  `src/zitadel/dynamic/__tests__/instance-custom-domain.test.ts`.
- Delete from `src/zitadel/dynamic/api-client.ts`: `buildSystemAssertion()`,
  `systemApiCall()`, and `SystemUserProfile` (keep the admin-MachineKey-based
  client used by `ZitadelPermanentPassword`).
- Delete: `scripts/discover-zitadel-instance-id.mjs`.
- Delete from `src/zitadel/constants.ts`: `instanceIdMap`,
  `SYSTEM_API_USER_NAME`, `ZITADEL_API_INTERNAL_HOST`.
- Delete from `src/index.ts`: the `ZitadelInstanceCustomDomain`
  instantiation block + its `protect`/`dependsOn` wiring.
- Delete from `src/zitadel/components/secrets.ts`: System User
  `tls.PrivateKey`, `zitadel-system-api-key` Secret, `zitadel-system-api-pub`
  Secret, related ESO IAM binding (`Secret.IAMMember`), and their
  `protect: true` resources.

**Code (Kubernetes manifests)**:
- Replace: `k8s/namespaces/zitadel/base/deployment-api.yaml` and
  `deployment-web.yaml` → single `helmCharts:` entry in
  `k8s/namespaces/zitadel/base/kustomization.yaml` plus a
  `values.yaml`.
- Delete: `k8s/namespaces/zitadel/base/external-secret-system-api-pub.yaml`
  (no more System User public key sync).
- Delete: `k8s/namespaces/zitadel/overlays/prod/deployment-web-patch.yaml`
  (Phase 2 made it a no-op; the values.yaml is env-agnostic).
- Preserve: `httproute.yaml`, `healthcheckpolicy-*.yaml`, `namespace.yaml`,
  `service-*.yaml` (or absorbed into chart-provided Services if naming
  aligns), the `zitadel-masterkey`/`zitadel-machine-key-for-pulumi-admin`
  ExternalSecrets, the `cloud-sql-proxy` sidecar wiring (injected via
  chart `extraContainers`).

**State / data (zero migration)**:
- Cloud SQL database, Zitadel system tables, masterkey-encrypted rows
  — all untouched. The chart connects to the same database with the
  same masterkey.
- GSM Secrets `zitadel-masterkey` and
  `zitadel-machine-key-for-pulumi-admin` — names preserved; chart
  reads via `existingMasterkeySecretName` and the existing
  bootstrap-uploader sidecar pattern.
- Pulumi state cleanup: `protect: true` resources (5 on dev, 6 on prod
  including the `zitadel-api-internal` Dynamic Resource) MUST be
  unprotected via `pulumi -s <env> state unprotect <urn>` BEFORE the
  PR merge. `pulumi state unprotect` only writes the state flag — it
  does NOT touch the live resources. Once unprotected, the regular
  `pulumi up` triggered by the merge deletes the cloud objects normally
  (the code declarations are gone, so Pulumi computes the diff as a
  deletion). See design.md D7 + tasks.md §4 for the procedure. Do NOT
  use `pulumi state delete` here — that removes the entry from state
  without destroying the cloud object, leaving GSM Secrets and IAM
  bindings as orphaned infrastructure.

**Runbooks / docs**:
- `docs/runbooks/dev-shutdown-restart.md`: remove Section B6b
  (instance-id capture step is obsolete; no `instanceIdMap` to commit).
- A new section documenting the Helm values surface and how to bump
  the chart version.

**Dependencies**:
- New: `zitadel/zitadel-charts` (Helm chart, version pinned in
  `kustomization.yaml`).
- Removed: nothing at npm/Go level; the `tls`, `@connectrpc/connect-node`,
  and `node:crypto` imports used only by the Dynamic Resource and its
  helpers go away with the files.

**Risk / blast radius**:
- This is a full Deployment replacement. The cutover is a single
  ArgoCD sync per environment: old `zitadel-api` / `zitadel-web`
  Deployments are deleted, chart-rendered Deployments take their
  place, Pods restart against the same database. ~30-60s of unavailability
  expected per env during Pod restart.
- Acceptable because: not service-in yet, Login UI sign-in is the only
  blocking flow, dev cutover validates the recipe before prod.
- Rollback: `git revert` the manifest + Pulumi changes, `argocd app sync`.
  Database state is intact, so the rollback path is symmetric.
