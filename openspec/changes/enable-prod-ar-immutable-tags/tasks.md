## 1. Pulumi: Enable `immutableTags` on prod AR repos (cloud-provisioning)

- [x] 1.1 Locate the `gcp.artifactregistry.Repository` resource construction for the `backend` and `frontend` Docker repos in `cloud-provisioning/src/gcp/`. Confirm the prod-stack code path (env conditional, stack-name check, or per-env component) is distinguishable from the dev-stack code path.
- [x] 1.2 Add `dockerConfig: { immutableTags: true }` to the prod-stack construction of both `backend` and `frontend` repos. The dev-stack construction SHALL remain unchanged (no `dockerConfig.immutableTags` field).
- [x] 1.3 Run `make lint-ts` (biome + tsc). Confirm 0 issues.
- [x] 1.4 Run `pulumi preview --stack prod` from the cloud-provisioning repo. Expected diff: exactly 2 `update` operations on `gcp:artifactregistry/repository:Repository` resources, each with `dockerConfig.immutableTags` flipping `false` (or unset) → `true`. If more deltas surface (drift on other AR fields, unrelated changes), STOP and reconcile drift before proceeding.
- [x] 1.5 Capture the preview output for inclusion in the PR description.

## 2. Kustomize: Rewrite prod overlays from SHA to semver tags (cloud-provisioning)

- [x] 2.1 Read the current backend prod overlay `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml`. Identify the 4 `images:` entries with `newTag: <40-char-sha>` (server, consumer, concert-discovery, artist-image-sync). Note the current SHA value for each.
- [x] 2.2 For each of the 4 backend entries, rewrite `newTag:` to `v1.0.0` and append an inline comment recording the current commit SHA: `newTag: v1.0.0  # commit <40-char-sha>`. The comment SHALL be on the same line as the `newTag:` field.
- [x] 2.3 Read the current frontend prod overlay `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`. Identify the 1 `images:` entry for `web-app` with `newTag: <40-char-sha>`. Note the current SHA value.
- [x] 2.4 Rewrite the frontend `newTag:` to `v1.0.0` with the same inline SHA comment pattern.
- [x] 2.5 In the existing overlay block comment that explains the pin strategy, update the rationale: replace the paragraph about commit-SHA tags with a paragraph about semver + AR Immutable Tags policy, and reference `docs/runbooks/prod-image-tag-pinning.md` (to be added in §4).

## 3. Kustomize: Add `app.kubernetes.io/version` Recommended Label (cloud-provisioning)

- [x] 3.1 In `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml`, add a `labels:` block (or a `commonLabels:`-equivalent transformer) that sets `app.kubernetes.io/version: "1.0.0"` on every Deployment + CronJob rendered by this overlay. Per design D5, the value SHALL be bare semver without the leading `v`.
- [x] 3.2 Verify the label is applied via `includeSelectors: false` (or by using a `metadata`-only patch) so it does NOT modify pod / service selectors — modifying selectors would break running Deployments. Recommended approach: kustomize `labels:` block with `includeSelectors: false`. Alternative: an explicit JSON 6902 patch adding `metadata.labels.app.kubernetes.io/version` to each Deployment and CronJob.
- [x] 3.3 Verify the label also propagates to `spec.template.metadata.labels` so Pods carry it (so Prometheus scraping picks it up). Per kustomize semantics, `labels:` with `includeTemplates: true` (Kustomize v4.5+) covers this; alternatively, add the label to `spec.template.metadata.labels` via the same patch.
- [x] 3.4 Repeat §3.1–§3.3 for the frontend prod overlay `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`.

## 4. Runbook: Document the prod image tag pinning policy

- [x] 4.1 Create `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md` with the following sections:
  - **Policy summary**: prod uses immutable semver tags backed by AR `immutableTags: true`; dev uses mutable `:latest`/`:main` for Image Updater.
  - **Why immutable tags + semver instead of digest pinning**: link to design.md D1 rationale.
  - **Operator workflow for cutting a release**: cut GH Release `vX.Y.Z` → GHA push → bump `newTag:` in prod overlay PR → merge → ArgoCD rolls.
  - **AR rejection behavior**: what 409 Conflict means, when it fires, expected vs unexpected cases.
  - **Recovery procedures**:
    - Release re-run after partial GHA failure: idempotent if same bytes; cut `vX.Y.Z+1` if bytes diverged.
    - Accidental manual `gcloud artifacts docker tags add` rejected: do not work around; cut a new patch version.
    - Rollback to prior version: flip `newTag:` in overlay PR; previous tag remains immutable and resolvable.
    - Genuine emergency requiring tag re-point (e.g., compromised supply chain force-replace): temporary `dockerConfig.immutableTags = false` via Pulumi (operator-attended, requires PR + apply), re-tag, re-enable. This is the only legitimate escape hatch and SHALL be paired with a documented post-incident review.
- [x] 4.2 Cross-reference from the prod overlays: in both backend and frontend prod `kustomization.yaml` block comments, add a line `# Policy: see docs/runbooks/prod-image-tag-pinning.md`.

## 5. Validation (cloud-provisioning, pre-PR)

- [x] 5.1 Run `kubectl kustomize cloud-provisioning/k8s/namespaces/backend/overlays/prod` and grep rendered Deployment + CronJob `image:` fields. Confirm every image URI ends with `:v1.0.0` and starts with `asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/`.
- [x] 5.2 Run `kubectl kustomize cloud-provisioning/k8s/namespaces/frontend/overlays/prod` and confirm the `web-app` Deployment image URI ends with `:v1.0.0` and starts with `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/`.
- [x] 5.3 Confirm rendered output contains `app.kubernetes.io/version: "1.0.0"` at all required paths per the spec requirement: (a) Deployment / CronJob `metadata.labels` (top-level), (b) Deployment `spec.template.metadata.labels` (Pod template), (c) CronJob `spec.jobTemplate.metadata.labels` (Job template), (d) CronJob `spec.jobTemplate.spec.template.metadata.labels` (Pod template inside the Job template — the path Prometheus / OTel actually scrape, since CronJobs have NO `spec.template`).
- [x] 5.4 Confirm no `selector.matchLabels.app.kubernetes.io/version` is added (selector modifications would break running Deployments — the label SHALL be metadata-only).
- [x] 5.5 Run `make lint-k8s` from cloud-provisioning. Confirm the spot-nodeselector / kube-linter passes still hold. (NOTE: local `make lint-k8s` fails on argocd Helm chart prerequisite — `helm` not installed locally; backend + frontend prod overlays render cleanly via `kubectl kustomize` and `scripts/check-spot-nodeselector.sh` passes. CI has Helm.)
- [x] 5.6 Confirm no dev overlay was accidentally modified: `git diff cloud-provisioning/k8s/namespaces/*/overlays/dev/` SHALL be empty.

## 6. PR submission (cloud-provisioning)

- [ ] 6.1 Open a single cloud-provisioning PR bundling: §1 (Pulumi src), §2–§3 (kustomize overlays), §4 (runbook). PR title: `feat(infra): enable immutable tags on prod AR + pin overlays to semver`.
- [ ] 6.2 In the PR description, include: the `pulumi preview --stack prod` diff from §1.5, the rendered-image grep output from §5.1–§5.3, a link to this OpenSpec change, and a link to the design.md.
- [ ] 6.3 Address CI + review feedback; merge when green.

## 7. Operator-attended apply (Pulumi prod)

- [ ] 7.1 After merge, trigger `pulumi up --stack prod` via Pulumi Cloud console (per cloud-provisioning AGENTS rule that prod up is manual).
- [ ] 7.2 Confirm the apply shows exactly the 2 `update` operations from §1.4.
- [ ] 7.3 Verify post-apply via `gcloud artifacts repositories describe backend --project=liverty-music-prod --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'` returns `True`.
- [ ] 7.4 Verify the same for the `frontend` repo.
- [ ] 7.5 Verify dev AR repos remain mutable: `gcloud artifacts repositories describe backend --project=liverty-music-dev --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'` returns empty or `False`.

## 8. Post-merge: ArgoCD reconciliation (prod cluster)

- [ ] 8.1 Watch ArgoCD detect the cloud-provisioning main-branch change and sync the `backend` + `frontend` Applications on prod.
- [ ] 8.2 Verify post-sync Deployment + CronJob spec on prod via `kubectl --context=gke_liverty-music-prod_asia-northeast2_autopilot-cluster-osaka -n backend get deploy,cronjob -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.template.spec.containers[*].image}{"\t"}{.spec.jobTemplate.spec.template.spec.containers[*].image}{"\n"}{end}'` — every image SHALL end with `:v1.0.0`.
- [ ] 8.3 Same check for frontend namespace.
- [ ] 8.4 Verify `app.kubernetes.io/version` label is present on every Deployment + CronJob in prod backend + frontend namespaces (top-level: `kubectl get deploy,cronjob -A -o jsonpath='{range .items[*]}{.metadata.labels.app\.kubernetes\.io/version}{"\n"}{end}'`).
- [ ] 8.5 Verify the label propagates to the Pod template path that Prometheus / OTel actually scrape. For Deployments: `kubectl get deploy -A -o jsonpath='{range .items[*]}{.spec.template.metadata.labels.app\.kubernetes\.io/version}{"\n"}{end}'`. For CronJobs: `kubectl get cronjob -A -o jsonpath='{range .items[*]}{.spec.jobTemplate.spec.template.metadata.labels.app\.kubernetes\.io/version}{"\n"}{end}'` (CronJobs have NO `spec.template`; the Pod template lives under `spec.jobTemplate.spec.template`). Also verify on a live Pod: `kubectl get pod -n backend --show-labels | grep app.kubernetes.io/version` returns non-empty.
- [ ] 8.6 Spot-check: ensure Pods did not enter `ImagePullBackOff` or `ErrImagePull` — the image bytes are unchanged (same digest, different tag), so the rollout SHALL succeed within standard rolling-update time.

## 9. Smoke: confirm no regression in apex / api / auth serving

- [ ] 9.1 `curl -I https://liverty-music.app/` — confirm 200 (frontend SPA still serves).
- [ ] 9.2 `curl -I https://api.liverty-music.app/healthz` — confirm 401 (backend reachable, auth gate active).
- [ ] 9.3 `curl -sI https://auth.liverty-music.app/.well-known/openid-configuration` — confirm 200 (Zitadel OIDC discovery still responds).

## 10. Operational validation: immutable tag enforcement (optional, post-archive)

This section validates the AR enforcement empirically. Optional because it requires cutting a real (or no-op) release; defer if not convenient at archive time.

- [ ] 10.1 Cut a no-op patch release on either `liverty-music/backend` or `liverty-music/frontend` (e.g., `v1.0.1` with a docs-only commit). This produces the **first post-enablement tag** — the only kind that exercises the AR immutability enforcement (pre-enablement `:v1.0.0` was written before `immutableTags: true` was applied and remains technically mutable per GCP's forward-only semantics).
- [ ] 10.2 Watch the GHA workflow push `:v1.0.1` + `:<new-sha>` to prod AR. Confirm both pushes succeed (AR accepts new tags).
- [ ] 10.3 Attempt a re-push: re-trigger the same workflow run from GitHub Actions UI. Two possible outcomes:
  - (a) `docker/build-push-action` re-builds with deterministic identical bytes → AR accepts the no-op push of the same digest under `:v1.0.1` (no 409 fires because nothing is being re-pointed).
  - (b) Build produces non-identical bytes (timestamp / dependency drift in image layers) → AR rejects the second `:v1.0.1` push with HTTP 409 Conflict. **This is the intended enforcement.**
  Verify which case occurs and update the spec scenario annotation if (a) turns out to be universally true.
- [ ] 10.4 Attempt a manual re-tag of the post-enablement tag (NOT `:v1.0.0` which is pre-enablement and may behave inconsistently):
  ```
  gcloud artifacts docker tags add \
    asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/server@sha256:<some-other-existing-digest> \
    asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/server:v1.0.1
  ```
  - Confirm the command fails with a 409 / "immutable tags" / "tag already exists" error.
- [ ] 10.5 (Optional) Document the pre-enablement carve-out empirically: attempt the same re-tag against the pre-enablement `:v1.0.0`. Per GCP docs the API may accept it; record actual observed behavior in the runbook to set operator expectations correctly. (This task is documentary — do NOT actually let the re-tag stand; if AR accepts, immediately re-tag back to the original digest.)
- [ ] 10.6 Bump prod overlay `newTag: v1.0.0` → `newTag: v1.0.1` (and `app.kubernetes.io/version: "1.0.1"`) in a new cloud-provisioning PR. Merge. Confirm ArgoCD rolls cleanly.

## 11. Archive

- [ ] 11.1 Mark all preceding tasks `[x]`.
- [ ] 11.2 Run `openspec validate enable-prod-ar-immutable-tags --strict`. Confirm pass.
- [ ] 11.3 Run `/opsx:archive enable-prod-ar-immutable-tags`. This bundles tasks-tick + delta-sync (creating `openspec/specs/prod-image-tag-immutability/spec.md` in main) + git mv into the archive PR.
