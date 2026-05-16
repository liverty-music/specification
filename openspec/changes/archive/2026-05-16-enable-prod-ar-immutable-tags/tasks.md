## 1. Pulumi: Enable `immutableTags` on prod AR repos (cloud-provisioning)

- [x] 1.1 Locate the `gcp.artifactregistry.Repository` resource construction for the `backend` and `frontend` Docker repos in `cloud-provisioning/src/gcp/`. Confirm the prod-stack code path (env conditional, stack-name check, or per-env component) is distinguishable from the dev-stack code path.
- [x] 1.2 Add `dockerConfig: { immutableTags: true }` to the prod-stack construction of both `backend` and `frontend` repos. The dev-stack construction SHALL remain unchanged (no `dockerConfig.immutableTags` field).
- [x] 1.3 Run `make lint-ts` (biome + tsc). Confirm 0 issues.
- [x] 1.4 Run `pulumi preview --stack prod` from the cloud-provisioning repo. Expected diff: exactly 2 `update` operations on `gcp:artifactregistry/repository:Repository` resources, each with `dockerConfig.immutableTags` flipping `false` (or unset) → `true`. If more deltas surface (drift on other AR fields, unrelated changes), STOP and reconcile drift before proceeding.
- [x] 1.5 Capture the preview output for inclusion in the PR description.

## 2. Kustomize: Rewrite prod overlays from SHA to semver tags (cloud-provisioning)

- [x] 2.1 Read the current backend prod overlay `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml`. Identify the 4 `images:` entries with `newTag: <40-char-sha>` (server, consumer, concert-discovery, artist-image-sync). Note the current SHA value for each.
- [x] 2.1a **Pre-flight gate**: confirm `:v1.0.0` exists in prod AR for all 5 images (4 backend + 1 frontend) BEFORE rewriting any overlay. If any image's `:v1.0.0` is missing, STOP — `prepare-prod-service-in` §1-§10 have not completed for that image; do not proceed (otherwise ArgoCD would reconcile to a non-existent tag and prod Pods would enter `ImagePullBackOff`).
  ```bash
  for IMG in server consumer concert-discovery artist-image-sync; do
    OUT=$(gcloud artifacts docker images list \
      asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/$IMG \
      --filter='tags:v1.0.0' --format='value(tags)' --project=liverty-music-prod 2>&1)
    if [ -z "$OUT" ]; then echo "FAIL: $IMG :v1.0.0 missing"; exit 1; else echo "OK: $IMG"; fi
  done
  OUT=$(gcloud artifacts docker images list \
    asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app \
    --filter='tags:v1.0.0' --format='value(tags)' --project=liverty-music-prod 2>&1)
  if [ -z "$OUT" ]; then echo "FAIL: web-app :v1.0.0 missing"; exit 1; else echo "OK: web-app"; fi
  ```
  All 5 SHALL print `OK:`.
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
- [x] 5.3 Confirm rendered output contains `app.kubernetes.io/version: "1.0.0"` at all required paths per the spec requirement: (a) Deployment / CronJob `metadata.labels` (top-level), (b) Deployment `spec.template.metadata.labels` (Pod template), (c) CronJob `spec.jobTemplate.metadata.labels` (Job template), (d) CronJob `spec.jobTemplate.spec.template.metadata.labels` (Pod template inside the Job template — the path Prometheus / OTel actually scrape, since CronJobs have NO `spec.template`). **Also**: grep-assert the label value has NO leading `v` (bare semver per K8s Recommended Labels convention); a `v` prefix slip (e.g., `"v1.0.0"` instead of `"1.0.0"`) renders the label valid YAML but violates the K8s convention and breaks downstream tools that key off the bare semver. Command: `kubectl kustomize k8s/namespaces/backend/overlays/prod | grep -E 'app\.kubernetes\.io/version:' | grep -vE 'app\.kubernetes\.io/version: "?[0-9]'` SHALL return empty (i.e., every match has a digit immediately after `version:`, no `v` prefix). Same for frontend.
- [x] 5.4 Confirm no `selector.matchLabels.app.kubernetes.io/version` is added (selector modifications would break running Deployments — the label SHALL be metadata-only).
- [x] 5.5a Locally-runnable validation: `kubectl kustomize k8s/namespaces/backend/overlays/prod` and `... frontend/overlays/prod` exit 0 with sensible YAML; `scripts/check-spot-nodeselector.sh` passes on both rendered prod overlays; `git diff k8s/namespaces/*/overlays/dev/` is empty (no accidental dev mutation).
- [x] 5.5b CI-gated full `make lint-k8s` (requires Helm for argocd / external-secrets / reloader chart renders; not available in the local dev environment, so this gate is enforced by the cloud-provisioning PR's `Lint` workflow on GitHub Actions). Confirmed green on cloud-provisioning PR #274 commits 47b7396 + d7be28b (both `Lint pass` per `gh pr checks 274`).
- [x] 5.6 Confirm no dev overlay was accidentally modified: `git diff cloud-provisioning/k8s/namespaces/*/overlays/dev/` SHALL be empty.

## 6. PR submission (cloud-provisioning)

- [x] 6.1 Open a single cloud-provisioning PR bundling: §1 (Pulumi src), §2–§3 (kustomize overlays), §4 (runbook). PR title: `feat(infra): enable immutable tags on prod AR + pin overlays to semver`. → liverty-music/cloud-provisioning#274.
- [x] 6.2 In the PR description, include: the `pulumi preview --stack prod` diff from §1.5, the rendered-image grep output from §5.1–§5.3, a link to this OpenSpec change, and a link to the design.md.
- [x] 6.3 Address CI + review feedback; merge when green. → spec PR liverty-music/specification#484 merged 2026-05-16 06:06:07Z (admin bypass — see archive PR description); cp PR #274 merged 06:06:31Z (clean, Claude review pass on Round 2).

## 7. Operator-attended apply (Pulumi prod)

- [x] 7.1 After merge, trigger `pulumi up --stack prod` via Pulumi Cloud console (per cloud-provisioning AGENTS rule that prod up is manual). → Pulumi Deployments v167, succeeded 2026-05-16 06:09Z, git.head 1277a7e8.
- [x] 7.2 Confirm the apply shows exactly the 2 `update` operations from §1.4. → +0-0~3: 2 AR Repository updates + 1 unrelated dashboard drift reconcile (acknowledged in PR description as pre-existing).
- [x] 7.3 Verify post-apply via `gcloud artifacts repositories describe backend --project=liverty-music-prod --location=asia-northeast2 --format='value(dockerConfig.immutableTags)'` returns `True`. → verified via `gcloud beta` (the GA `gcloud artifacts` omits `dockerConfig` from format output; `beta` shows it correctly). Result: `True`, updateTime 2026-05-16T06:09:14.491103Z.
- [x] 7.4 Verify the same for the `frontend` repo. → `True`, updateTime 2026-05-16T06:09:15.589077Z.
- [x] 7.5 Verify dev AR repos remain mutable. → both dev `backend` and `frontend` returned empty (= not set / mutable), last updateTime 2026-05-15 (untouched by today's apply).

## 8. Post-merge: ArgoCD reconciliation (prod cluster)

- [x] 8.1 Watch ArgoCD detect the cloud-provisioning main-branch change and sync the `backend` + `frontend` Applications on prod. → initial reconcile (06:06Z) missed the merge commit (06:06:31Z) by 30 seconds; hard refresh via `kubectl annotate application <app> argocd.argoproj.io/refresh=hard --overwrite` triggered pickup of revision `1277a7e8` at 06:11:33Z (backend) and 06:11:29Z (frontend). Operationally noted: post-Pulumi-up + post-merge sequence should always include hard refresh when timing-sensitive.
- [x] 8.2 Verify post-sync Deployment + CronJob spec on prod — every image ends with `:v1.0.0`. → 4 backend images (server, consumer, concert-discovery, artist-image-sync) all `:v1.0.0` under `liverty-music-prod/backend/`. cloud-sql-proxy continues `gcr.io/cloud-sql-connectors/cloud-sql-proxy:2` (upstream, out of scope).
- [x] 8.3 Same check for frontend namespace. → `web-app` image is `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:v1.0.0`.
- [x] 8.4 Verify `app.kubernetes.io/version` label is present on every Deployment + CronJob in prod backend + frontend namespaces. → all 4 backend workloads (server, consumer, both CronJobs) + cloud-sql-proxy + frontend web-app carry `app.kubernetes.io/version: 1.0.0` at top-level metadata.
- [x] 8.5 Verify the label propagates to the Pod template path that Prometheus / OTel actually scrape. → CronJob `spec.jobTemplate.spec.template.metadata.labels.app.kubernetes.io/version` populated for both `artist-image-sync-app` and `concert-discovery-app` (`1.0.0`); Deployment `spec.template.metadata.labels.app.kubernetes.io/version` populated for all Deployments (verified via kustomize render + live `kubectl get deploy`).
- [x] 8.6 Spot-check: no `ImagePullBackOff` / `ErrImagePull` post-rollout. → all prod Pods Running; image bytes unchanged (same digest under new tag).

## 9. Smoke: confirm no regression in apex / api / auth serving

- [x] 9.1 `curl -I https://liverty-music.app/` — 200 ✓.
- [x] 9.2 `curl -I https://api.liverty-music.app/healthz` — 401 ✓ (auth gate reachable).
- [x] 9.3 `curl -sI https://auth.liverty-music.app/.well-known/openid-configuration` — 200 ✓ (Zitadel OIDC discovery responds).

## 10. Operational validation: immutable tag enforcement (DEFERRED to first post-merge release)

This section validates the AR enforcement empirically. **Deferred to the first post-merge release cut** (whenever that organically happens, e.g., the first frontend/backend `v1.0.1` triggered for any other reason). Reasoning:
- The pre-flight assumption is that AR Immutable Tags works correctly per GCP's documented behavior. The infra itself is in place (`dockerConfig.immutableTags: True` verified on both prod AR repos at §7.3-§7.4) — the only thing not exercised is the 409 rejection path.
- Cutting a release purely to validate AR's enforcement adds release noise without proportional risk reduction (the worst case is "AR doesn't reject" which would be caught the moment a real release tries to re-push, and the recovery path is documented in the runbook).
- Per /opsx:verify report at archive time (W1 + S2): these tasks remain `[ ]` intentionally; the change archives without them.

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
- [ ] 10.5 Bump prod overlay `newTag: v1.0.0` → `newTag: v1.0.1` (and `app.kubernetes.io/version: "1.0.1"`) in a new cloud-provisioning PR. Merge. Confirm ArgoCD rolls cleanly. NOTE: the pre-enablement carve-out (whether AR accepts re-tag on the original `:v1.0.0`) is NOT empirically validated — GCP's documentation is sufficient. Mutating a prod tag to "document" GCP-documented behavior would put production at risk if the recovery re-tag failed mid-way. See spec.md "Forward-only carve-out" prose note under Requirement 1.

## 11. Archive

- [x] 11.1 Mark all preceding tasks `[x]` (§10 intentionally left `[ ]` per the section header — deferred to first post-merge release cut, documented in /opsx:verify report W1 + S2 and in the archive PR description).
- [x] 11.2 Run `openspec validate enable-prod-ar-immutable-tags --strict`. → passes.
- [x] 11.3 Run `/opsx:archive enable-prod-ar-immutable-tags`. → this archive PR bundles tasks-tick + delta-sync (creating `openspec/specs/prod-image-tag-immutability/spec.md` in main) + git mv.
