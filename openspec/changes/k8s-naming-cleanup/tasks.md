# Tasks

## 1. Repo-wide audit (find every reference)

- [x] 1.1 `git grep -nE '\bzitadel(-login)?\b'` across the cloud-provisioning repo. Buckets:
  - **In-scope** K8s manifests: `k8s/namespaces/zitadel/base/*`, `k8s/namespaces/zitadel/overlays/dev/*`
  - **In-scope** K8s Secret rename (consumer-encoded name): `zitadel-login-pat` → `zitadel-web-pat` (ExternalSecret resource + target K8s Secret + file). GSM-side key name stays per Pulumi ownership.
  - **Marginal touch-up** comments referring to the renamed Deployment by name:
    - `k8s/namespaces/otel-collector/base/deployment.yaml:11` — "Pairs with the same annotation on the `zitadel` Deployment" → `zitadel-api`
    - `src/gcp/components/zitadel-monitoring.ts:160` and `:255` — runbook hints (`kubectl rollout restart deployment/zitadel`)
  - **Out-of-scope** (different naming axis or upstream-derived):
    - Pulumi `src/zitadel/components/**` — Zitadel-side concepts (Provider/Org/Project), upstream SDK package, MachineUser names. None of these are K8s resource names.
    - `src/gcp/components/{network,postgres,kubernetes}.ts` — `zitadelApp = 'zitadel'` Pulumi resource ids, namespace name, cert map name, SA name. Unchanged.
    - `k8s/argocd-apps/dev/zitadel.yaml` — Application name is top-level (one per namespace), not tied to renamed Deployments.
    - `k8s/cluster/base/cluster-secret-store.yaml:12 - zitadel` — namespace allowlist entry; namespace name unchanged.
    - `k8s/namespaces/backend/{server,consumer}/**` — `zitadel-machine-key-*` references use the `zitadel-machine-key-for-<principal>` GSM convention (separate rename axis, archived in `rename-zitadel-machine-keys`).
    - Image path `ghcr.io/zitadel/zitadel-login` — upstream artifact name, NOT the K8s container/Deployment name.
    - Container `zitadel-config` ConfigMap, `zitadel-secrets` Secret, `zitadel-db-grant` Job, `zitadel-restart` CronJob — orthogonal names not tied to API/Login tiers.
    - `external-secret.yaml: name: zitadel-secrets` — namespace-scoped secrets name. Unchanged.
    - K8s ServiceAccount name `zitadel` — namespace-shared SA; renaming cascades to GCP IAM SA and Workload Identity binding. Out of scope.
- [x] 1.2 Backend `git grep -nE 'zitadel(-login)?\.zitadel\.svc'` returned 0 matches. Confirmed: no cluster-internal hostname references in backend Go source.
- [x] 1.3 Frontend `git grep` returned only `urn:zitadel:iam:...` URN (Zitadel-protocol identifier, unrelated to K8s) and `/zitadel\.cloud/` OTel ignore regex (legacy hostname, separate concern). No K8s resource references.
- [x] 1.4 Decision: Pulumi `MachineUser.userName` and other Pulumi resource ids are out of scope. K8s rename is independent.

## 2. Base manifest renames (`k8s/namespaces/zitadel/base/`)

- [x] 2.1 `deployment-api.yaml`:
  - [x] 2.1.1 `metadata.name`: `zitadel` → `zitadel-api`
  - [x] 2.1.2 `metadata.labels.app`: keep `zitadel`; `component`: keep `api` (already correct, verified)
  - [x] 2.1.3 `spec.selector.matchLabels` / `spec.template.metadata.labels`: keep `app: zitadel, component: api` (verified, no change)
  - [x] 2.1.4 Container `name`: `zitadel` → `api`
  - [x] 2.1.5 Service-link comment rewritten to explain: post-rename the injected env var becomes `ZITADEL_API_PORT` (no matching uint16 config field) so the specific Viper conflict no longer materializes; flag stays as defensive insurance for any future Service. DNS-based discovery (`zitadel-api.zitadel.svc.cluster.local`) works regardless.
  - [x] 2.1.6 `podAntiAffinity.matchLabels` (`app: zitadel, component: api`) intact (labels unchanged).
  - **EXTRA (drift fix)**: Added explicit `spec.replicas: 2` to base. The spec.md asserted "base replicaCount: 2" but the file had no `replicas:` field, which would default to 1. Now base declares HA intent; dev overlay explicitly relaxes to 1; prod overlay inherits 2 naturally.

- [x] 2.2 `deployment-login.yaml` → renamed to `deployment-web.yaml`:
  - [x] 2.2.1 `git mv` executed.
  - [x] 2.2.2 `metadata.name`: `zitadel-login` → `zitadel-web`
  - [x] 2.2.3 `metadata.labels.component`: `login` → `web`
  - [x] 2.2.4 `spec.selector.matchLabels.component` + pod template `component`: `login` → `web`
  - [x] 2.2.5 Container `name`: `zitadel-login` → `web`
  - [x] 2.2.6 **Removed** the stale header comment block (`ZITADEL_API_URL points at the in-cluster API Service...`).
  - [x] 2.2.7 Image path stays `ghcr.io/zitadel/zitadel-login` (upstream artifact name, separate from K8s rename).
  - [x] 2.2.8 `podAntiAffinity matchLabels.component`: `login` → `web`.
  - **EXTRA**: Updated internal hostname reference in rationale comment (`zitadel.zitadel.svc.cluster.local` → `zitadel-api.zitadel.svc.cluster.local`); updated catch-all rule comment (`zitadel` Service → `zitadel-api` Service); updated cross-file comment reference (`external-secret-login-pat.yaml` → `external-secret-web-pat.yaml`); updated `secretName: zitadel-login-pat` → `zitadel-web-pat` (mount); added explicit `spec.replicas: 2` (same drift fix as 2.1).

- [x] 2.3 `service-api.yaml`:
  - [x] 2.3.1 `metadata.name`: `zitadel` → `zitadel-api`
  - [x] 2.3.2 `spec.selector.component`: keep `api`.

- [x] 2.4 `service-login.yaml` → renamed to `service-web.yaml`:
  - [x] 2.4.1 `git mv` executed.
  - [x] 2.4.2 `metadata.name`: `zitadel-login` → `zitadel-web`
  - [x] 2.4.3 `spec.selector.component` + `metadata.labels.component`: `login` → `web`.

- [x] 2.5 `httproute.yaml`:
  - [x] 2.5.1 `spec.hostnames` field **removed** (moved to overlays).
  - [x] 2.5.2 `backendRefs[0].name` (Login UI rule): `zitadel-login` → `zitadel-web`
  - [x] 2.5.3 `backendRefs[1].name` (catch-all rule): `zitadel` → `zitadel-api`
  - [x] 2.5.4 Comment added explaining the per-overlay `hostnames` discipline and why it is load-bearing (the `/` catch-all would otherwise intercept all Gateway traffic).

- [x] 2.6 `pdb.yaml`:
  - [x] 2.6.1 First PDB `metadata.name`: `zitadel` → `zitadel-api`.
  - [x] 2.6.2 Second PDB `metadata.name`: `zitadel-login` → `zitadel-web`; `selector.matchLabels.component`: `login` → `web`.

- [x] 2.7 `healthcheckpolicy.yaml`:
  - [x] 2.7.1 First policy `metadata.name`: `zitadel-api-policy` (verified, unchanged).
  - [x] 2.7.2 First policy `targetRef.name`: `zitadel` → `zitadel-api`.
  - [x] 2.7.3 Second policy `metadata.name`: `zitadel-login-policy` → `zitadel-web-policy`.
  - [x] 2.7.4 Second policy `targetRef.name`: `zitadel-login` → `zitadel-web`.
  - [x] 2.7.5 Second policy `labels.component`: `login` → `web`.

- [x] 2.8 `kustomization.yaml`:
  - [x] 2.8.1 Resource list: `deployment-login.yaml` → `deployment-web.yaml`; `service-login.yaml` → `service-web.yaml`; `external-secret-login-pat.yaml` → `external-secret-web-pat.yaml`.

- [x] 2.9 `external-secret-login-pat.yaml` → renamed to `external-secret-web-pat.yaml`:
  - [x] 2.9.1 K8s-side rename applied: ExternalSecret `metadata.name`, `spec.target.name` both `zitadel-login-pat` → `zitadel-web-pat`. GSM `remoteRef.key` keeps `zitadel-login-pat` (Pulumi-owned). Mount in `deployment-web.yaml` updated. Header comment expanded to explain the K8s-vs-GSM naming split.
  - [x] 2.9.2 Reloader-driven Pod restart on Secret rename is acceptable pre-launch (no service users).

**EXTRA (marginal touch-ups, audit-identified):**
- [x] Updated `k8s/namespaces/otel-collector/base/deployment.yaml:11` comment to reference `zitadel-api` Deployment.
- [x] Updated `src/gcp/components/zitadel-monitoring.ts:160` runbook hint to reference `deployment/zitadel-api`.

## 3. Dev overlay updates (`k8s/namespaces/zitadel/overlays/dev/`)

- [x] 3.1 `kustomization.yaml`:
  - [x] 3.1.1 Patch `target.name` entries: `zitadel` → `zitadel-api`; `zitadel-login` → `zitadel-web`.
  - [x] 3.1.2 Referenced `deployment-web-patch.yaml` instead of `deployment-login-patch.yaml`.
  - [x] 3.1.3 Added new patch entry for `httproute-patch.yaml`.

- [x] 3.2 `deployment-patch.yaml`:
  - [x] 3.2.1 `metadata.name`: `zitadel` → `zitadel-api`.

- [x] 3.3 `deployment-login-patch.yaml` → renamed to `deployment-web-patch.yaml`:
  - [x] 3.3.1 `git mv` executed.
  - [x] 3.3.2 `metadata.name`: `zitadel-login` → `zitadel-web`. Header comment refreshed.

- [x] 3.4 NEW: `httproute-patch.yaml` — created with `metadata.name: zitadel-route`, `spec.hostnames: [auth.dev.liverty-music.app]`, explanatory comment.

- [x] 3.5 `pdb-patch.yaml`: both PDB `metadata.name`s renamed. Header comment refreshed to reference `deployment-web-patch.yaml`.

- [x] 3.6 **CORRECTED — `cronjob-restart-zitadel.yaml` DID need updates** (original task incorrectly marked as "no changes"). Updates applied:
  - Header comment: `kubectl rollout restart deploy/zitadel` → `deploy/zitadel-api`.
  - RBAC `resourceNames: ["zitadel"]` → `["zitadel-api"]` (the pinned-resource grant must follow the rename).
  - CronJob args: `deployment/zitadel` → `deployment/zitadel-api`.
  - `configmap-patch.env` unaffected (confirmed).

## 4. Prod overlay creation (NEW: `k8s/namespaces/zitadel/overlays/prod/`)

- [x] 4.1 Directory `overlays/prod/` created.

- [x] 4.2 NEW: `kustomization.yaml`:
  - [x] 4.2.1 `namespace: zitadel`.
  - [x] 4.2.2 `resources: [../../base]`; `cronjob-restart-zitadel.yaml` explicitly NOT imported (verified via render: prod has no `zitadel-restart` resources).
  - [x] 4.2.3 `patches`: references `deployment-api-patch.yaml`, `deployment-web-patch.yaml`, `httproute-patch.yaml`.
  - [x] 4.2.4 No `configMapGenerator` merge for prod (deferred to prod-provisioning change).

- [x] 4.3 NEW: `deployment-api-patch.yaml`:
  - [x] 4.3.1 `metadata.name: zitadel-api`.
  - [x] 4.3.2 **REVISED** — `replicas` field NOT set in patch (inherits base `replicas: 2` after the section-2 drift fix). Explicit patch was originally planned but is redundant with the base value.
  - [x] 4.3.3 Spot-pool nodeSelector applied.

- [x] 4.4 NEW: `deployment-web-patch.yaml`:
  - [x] 4.4.1 `metadata.name: zitadel-web`.
  - [x] 4.4.2 Same as 4.3.2: replicas inherits base, no patch needed.
  - [x] 4.4.3 Spot-pool nodeSelector applied.

- [x] 4.5 NEW: `httproute-patch.yaml`:
  - [x] 4.5.1 `metadata.name: zitadel-route`.
  - [x] 4.5.2 `spec.hostnames: [auth.liverty-music.app]`.

- [x] 4.6 No `pdb-patch.yaml` in prod (verified: base `minAvailable: 1` flows through; render confirms).

## 5. ArgoCD prod Application

- [x] 5.1 NEW: `k8s/argocd-apps/prod/zitadel.yaml` created.
  - [x] 5.1.1 Mirror of `k8s/argocd-apps/dev/zitadel.yaml`, with `spec.source.path: k8s/namespaces/zitadel/overlays/prod`.
  - [x] 5.1.2 `syncPolicy.automated.prune: true`, `selfHeal: true`, `syncOptions: [CreateNamespace=true, ServerSideApply=true]`.
- [x] 5.2 New directory `k8s/argocd-apps/prod/` introduced by this change.

## 6. Verification (local)

- [x] 6.1 `kubectl kustomize k8s/namespaces/zitadel/base` — renders cleanly. HTTPRoute has no `hostnames`; Deployments/Services/PDBs/HCPs use new names; ExternalSecret `zitadel-web-pat` mirrors GSM `zitadel-login-pat`.
- [x] 6.2 `kubectl kustomize k8s/namespaces/zitadel/overlays/dev` — renders with `hostnames: [auth.dev.liverty-music.app]`, `replicas: 1`, `cronjob-restart-zitadel` resources (SA/Role/RoleBinding/CronJob), new resource names.
- [x] 6.3 `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` — renders with `hostnames: [auth.liverty-music.app]`, `replicas: 2`, spot nodeSelector, new resource names, no `restart-zitadel` CronJob.
- [~] 6.4 **Partial** — `make lint-k8s` fails on the unrelated `argocd` dev overlay due to a local `helm` CLI compatibility issue (`helm version -c --short`: unknown flag). Zitadel-only verification passed: `kube-linter lint /tmp/rendered-zitadel --config .kube-linter.yaml` → "No lint errors found!"; `./scripts/check-spot-nodeselector.sh /tmp/rendered-zitadel` → "OK: All workloads have Spot VM nodeSelector." Full `make lint-k8s` should be retried in CI where helm is wired up.
- [x] 6.5 `make lint-ts` — clean (biome + tsc on 44 files).
- [x] 6.6 `make check` — clean (lint-ts + 40 tests pass).

## 7. Cutover (dev only — prod waits on prereqs)

- [ ] 7.1 Merge PR. ArgoCD dev Application picks up the change.
- [ ] 7.2 Observe ArgoCD UI: `zitadel` Application transitions through `OutOfSync` while old resources prune and new ones materialize. ArgoCD `prune: true` removes the old `zitadel` / `zitadel-login` Deployments/Services/etc.
- [ ] 7.3 Verify dev pods come up cleanly:
  - `kubectl get -n zitadel deploy` → `zitadel-api`, `zitadel-web`.
  - `kubectl get -n zitadel svc` → `zitadel-api`, `zitadel-web`.
  - `kubectl get -n zitadel pdb` → both renamed.
  - `kubectl get -n zitadel httproute` → hostname is `auth.dev.liverty-music.app`.
  - `kubectl logs -n zitadel deploy/zitadel-api -c api` returns Zitadel startup logs.
- [ ] 7.4 Smoke test the auth endpoint: `curl -s https://auth.dev.liverty-music.app/.well-known/openid-configuration | jq .issuer` returns `https://auth.dev.liverty-music.app`.
- [ ] 7.5 Confirm `zitadel` ArgoCD prod Application appears with `OutOfSync` / `Missing` status — this is the expected interim state until prod prereqs (Cloud SQL DB, GSM secrets, ESC env, GCP cert map binding) are provisioned. Document the known-OutOfSync state in the PR description.

## 8. Follow-ups to track (not in this change)

- [ ] 8.1 Prod prereqs change: Pulumi-side Cloud SQL DB / IAM user / GSM secrets / ESC env for prod Zitadel. Once landed, prod ArgoCD Application transitions to `Healthy`.
- [ ] 8.2 `concert-data-store` namespace naming audit (deferred from this change).
- [ ] 8.3 Backend/frontend HTTPRoute consistency review (no `hostnames`, no `/` catch-all rule) — separate Gateway-routing design discussion.
