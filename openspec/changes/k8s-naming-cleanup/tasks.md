# Tasks

## 1. Repo-wide audit (find every reference)

- [ ] 1.1 `git grep -nE '\bzitadel(-login)?\b'` across the cloud-provisioning repo to list every reference to the old names. Bucket the hits:
  - K8s manifests (in-scope)
  - Pulumi source (`src/**`) — likely some `MachineUser.userName` references; check whether they should also rename
  - Comments / docs (in-scope, opportunistic clean-up)
  - Tests / fixtures
- [ ] 1.2 Confirm `backend` Go source has NO hardcoded reference to the Service hostname `zitadel.zitadel.svc.cluster.local` (it uses public URL per `self-hosted-zitadel` requirements; verify).
- [ ] 1.3 Confirm `frontend` source has NO hardcoded reference to either name.
- [ ] 1.4 Decide whether `MachineUser.userName: zitadel` (if any) is in or out of scope; default: out — Pulumi resource names are an internal artifact, the K8s rename is independent.

## 2. Base manifest renames (`k8s/namespaces/zitadel/base/`)

- [ ] 2.1 `deployment-api.yaml`:
  - [ ] 2.1.1 `metadata.name`: `zitadel` → `zitadel-api`
  - [ ] 2.1.2 `metadata.labels.app`: keep `zitadel`; `component`: keep `api` (already correct)
  - [ ] 2.1.3 `spec.selector.matchLabels` / `spec.template.metadata.labels`: keep `app: zitadel, component: api`
  - [ ] 2.1.4 Container `name`: `zitadel` → `api`
  - [ ] 2.1.5 Update header comment (the `enableServiceLinks: false` block at L30-37): change `ZITADEL_PORT` → `ZITADEL_API_PORT` in the explanatory text; note that after rename, the Viper-config conflict no longer materializes but the flag stays as defensive insurance.
  - [ ] 2.1.6 Verify the `podAntiAffinity.matchLabels` (`app: zitadel, component: api`) still references the labels (labels are unchanged, only resource name changes).

- [ ] 2.2 `deployment-login.yaml` → rename file to `deployment-web.yaml`:
  - [ ] 2.2.1 `git mv` the file.
  - [ ] 2.2.2 `metadata.name`: `zitadel-login` → `zitadel-web`
  - [ ] 2.2.3 `metadata.labels.component`: `login` → `web`
  - [ ] 2.2.4 `spec.selector.matchLabels.component` / pod template `component`: `login` → `web`
  - [ ] 2.2.5 Container `name`: `zitadel-login` → `web`
  - [ ] 2.2.6 **Remove the stale header comment block at L37-38** (`ZITADEL_API_URL points at the in-cluster API Service...`).
  - [ ] 2.2.7 Verify image path stays `ghcr.io/zitadel/zitadel-login` (image name reflects upstream artifact, NOT the container/Deployment name; this is intentional per spec rationale).
  - [ ] 2.2.8 Update `topologyKey` / `podAntiAffinity matchLabels.component`: `login` → `web`.

- [ ] 2.3 `service-api.yaml`:
  - [ ] 2.3.1 `metadata.name`: `zitadel` → `zitadel-api`
  - [ ] 2.3.2 `spec.selector.component`: keep `api` (already correct).

- [ ] 2.4 `service-login.yaml` → rename file to `service-web.yaml`:
  - [ ] 2.4.1 `git mv` the file.
  - [ ] 2.4.2 `metadata.name`: `zitadel-login` → `zitadel-web`
  - [ ] 2.4.3 `spec.selector.component`: `login` → `web`.

- [ ] 2.5 `httproute.yaml`:
  - [ ] 2.5.1 **Remove `spec.hostnames` field entirely** (moved to overlays per design decision 1).
  - [ ] 2.5.2 `backendRefs[0].name` (Login UI rule): `zitadel-login` → `zitadel-web`
  - [ ] 2.5.3 `backendRefs[1].name` (catch-all rule): `zitadel` → `zitadel-api`
  - [ ] 2.5.4 Add comment on the catch-all `/` rule explaining that `hostnames` is set per-overlay to scope this rule to the Zitadel hostname only.

- [ ] 2.6 `pdb.yaml`:
  - [ ] 2.6.1 First PDB `metadata.name`: `zitadel` → `zitadel-api`; `selector.matchLabels.component`: keep `api`.
  - [ ] 2.6.2 Second PDB `metadata.name`: `zitadel-login` → `zitadel-web`; `selector.matchLabels.component`: `login` → `web`.

- [ ] 2.7 `healthcheckpolicy.yaml`:
  - [ ] 2.7.1 First policy `metadata.name`: `zitadel-api-policy` (already correct).
  - [ ] 2.7.2 First policy `targetRef.name`: `zitadel` → `zitadel-api`.
  - [ ] 2.7.3 Second policy `metadata.name`: `zitadel-login-policy` → `zitadel-web-policy`.
  - [ ] 2.7.4 Second policy `targetRef.name`: `zitadel-login` → `zitadel-web`.
  - [ ] 2.7.5 Second policy `labels.component`: `login` → `web`.

- [ ] 2.8 `kustomization.yaml`:
  - [ ] 2.8.1 Resource list: `deployment-login.yaml` → `deployment-web.yaml`; `service-login.yaml` → `service-web.yaml`.

- [ ] 2.9 `external-secret-login-pat.yaml` (verify):
  - [ ] 2.9.1 Check if this ExternalSecret targets a K8s Secret consumed by `zitadel-web` (was `zitadel-login`). If the secret name encodes the consumer, decide whether to rename the secret too (likely IN scope: `zitadel-login-pat` → `zitadel-web-pat`). If yes, follow through in the mount in `deployment-web.yaml` and the ExternalSecret resource itself.
  - [ ] 2.9.2 If renaming the K8s Secret triggers a Reloader-driven Pod restart, that's fine pre-launch.

## 3. Dev overlay updates (`k8s/namespaces/zitadel/overlays/dev/`)

- [ ] 3.1 `kustomization.yaml`:
  - [ ] 3.1.1 Patch `target.name` entries: `zitadel` → `zitadel-api`; `zitadel-login` → `zitadel-web`.
  - [ ] 3.1.2 Reference `deployment-web-patch.yaml` instead of `deployment-login-patch.yaml`.
  - [ ] 3.1.3 Add a new patch entry pointing at `httproute-patch.yaml` (new file, see 3.4).

- [ ] 3.2 `deployment-patch.yaml`:
  - [ ] 3.2.1 `metadata.name`: `zitadel` → `zitadel-api`.

- [ ] 3.3 `deployment-login-patch.yaml` → rename file to `deployment-web-patch.yaml`:
  - [ ] 3.3.1 `git mv`.
  - [ ] 3.3.2 `metadata.name`: `zitadel-login` → `zitadel-web`.

- [ ] 3.4 NEW: `httproute-patch.yaml`:
  - [ ] 3.4.1 Create with `metadata.name: zitadel-route`, `spec.hostnames: [auth.dev.liverty-music.app]`.

- [ ] 3.5 `pdb-patch.yaml`:
  - [ ] 3.5.1 Both PDB `metadata.name`s renamed (`zitadel` → `zitadel-api`; `zitadel-login` → `zitadel-web`).

- [ ] 3.6 (no changes) `configmap-patch.env`, `cronjob-restart-zitadel.yaml` — unaffected by rename, dev-only.

## 4. Prod overlay creation (NEW: `k8s/namespaces/zitadel/overlays/prod/`)

- [ ] 4.1 Create directory `overlays/prod/`.

- [ ] 4.2 NEW: `kustomization.yaml`:
  - [ ] 4.2.1 `namespace: zitadel`.
  - [ ] 4.2.2 `resources: [../../base]` — **does NOT include `cronjob-restart-zitadel.yaml`** (dev-only band-aid).
  - [ ] 4.2.3 `patches`: reference `deployment-api-patch.yaml`, `deployment-web-patch.yaml`, `httproute-patch.yaml`.
  - [ ] 4.2.4 (Decision: no `configMapGenerator` merge for prod yet — prod-specific config values are out of scope of this change; that's part of prod provisioning prep.)

- [ ] 4.3 NEW: `deployment-api-patch.yaml`:
  - [ ] 4.3.1 `metadata.name: zitadel-api`.
  - [ ] 4.3.2 `spec.replicas: 2` (matches base; explicit for symmetry with dev patch shape and clarity for future tuning).
  - [ ] 4.3.3 `spec.template.spec.nodeSelector.cloud.google.com/gke-spot: "true"`.

- [ ] 4.4 NEW: `deployment-web-patch.yaml`:
  - [ ] 4.4.1 `metadata.name: zitadel-web`.
  - [ ] 4.4.2 `spec.replicas: 2`.
  - [ ] 4.4.3 `spec.template.spec.nodeSelector.cloud.google.com/gke-spot: "true"`.

- [ ] 4.5 NEW: `httproute-patch.yaml`:
  - [ ] 4.5.1 `metadata.name: zitadel-route`.
  - [ ] 4.5.2 `spec.hostnames: [auth.liverty-music.app]`.

- [ ] 4.6 (Decision: no `pdb-patch.yaml` in prod — base `minAvailable: 1` is the desired value.)

## 5. ArgoCD prod Application

- [ ] 5.1 NEW: `k8s/argocd-apps/prod/zitadel.yaml`:
  - [ ] 5.1.1 Mirror `k8s/argocd-apps/dev/zitadel.yaml` exactly except `spec.source.path: k8s/namespaces/zitadel/overlays/prod`.
  - [ ] 5.1.2 `syncPolicy.automated.prune: true`, `selfHeal: true`, `syncOptions: [CreateNamespace=true, ServerSideApply=true]`.
- [ ] 5.2 If `k8s/argocd-apps/prod/` does not exist yet, create the directory (this change introduces it).

## 6. Verification (local)

- [ ] 6.1 `kubectl kustomize k8s/namespaces/zitadel/base` — must render without `hostnames` on HTTPRoute and with the renamed Deployments/Services/PDBs/HealthCheckPolicies.
- [ ] 6.2 `kubectl kustomize k8s/namespaces/zitadel/overlays/dev` — must render with `hostnames: [auth.dev.liverty-music.app]`, `replicas: 1` patches, the `cronjob-restart-zitadel` CronJob, and the new resource names.
- [ ] 6.3 `kubectl kustomize k8s/namespaces/zitadel/overlays/prod` — must render with `hostnames: [auth.liverty-music.app]`, `replicas: 2`, spot nodeSelector, the new resource names, and NO `restart-zitadel` CronJob.
- [ ] 6.4 `make lint-k8s` — passes.
- [ ] 6.5 `make lint-ts` — passes (sanity check; Pulumi side untouched by this change).
- [ ] 6.6 `make check` — full pre-commit suite passes.

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
