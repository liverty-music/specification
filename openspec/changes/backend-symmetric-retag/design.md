## Context

The frontend retag flow (archived `2026-05-18-promote-prod-image-via-retag`) is live on `frontend@v1.0.2`, with byte-identical digest verified across dev and prod AR. This change applies the same pattern to backend, which still rebuilds 4 images (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) on every release event via a strategy-matrix in `liverty-music/backend/.github/workflows/deploy.yml`. The matrix structure is intentionally preserved; only each matrix entry's release-path behavior changes.

Two prior traps from the frontend rollout that this design treats as established constraints:

1. `gcloud artifacts docker tags add` cannot cross-project copy (rejected outright; not re-evaluated).
2. `imjasonh/setup-crane@v0.4` installs the `crane` binary, not `gcrane`; `crane` reads auth from `~/.docker/config.json` populated by `gcloud auth configure-docker` (must be in BOTH event paths, not gated to push-only).

Backend constraints unique to this change:

- 4 separate AR sub-repositories under `liverty-music-{dev,prod}/backend/` — each image is a distinct OCI artifact at `liverty-music-{dev,prod}/backend/<image-name>`.
- The matrix runs 4 parallel jobs (one per image). Each job independently authenticates, configures Docker, and copies one image's pair of tags. No cross-job state.
- The first post-merge backend release MUST be paired with a cloud-provisioning kustomization bump on 4 prod overlays (one per Deployment) — but only when the operator actually wants to roll prod forward. The retag itself doesn't deploy.
- `prod-image-tag-immutability` already covers backend (it's `environment !== 'dev'` keyed). No tag-write contract change.

## Goals / Non-Goals

**Goals:**

- Cut backend release-event runtime from ~6 min (4× sequential `docker/build-push-action`) to ~30 s (per-matrix-entry digest-resolve + 2× `crane copy`).
- Byte-identical bytes from dev to prod for each of the 4 backend images.
- Invert the `prod-image-pipeline` "Backend dev AR is NOT yet granted (forward-looking)" scenario from documentation-of-gap to compliance-of-presence — the canonical spec accurately reflects the new IAM topology.
- Single Pulumi binding declares the new grant; no Workload Identity Federation or service-account-key changes.

**Non-Goals:**

- No backend Dockerfile changes, no entity/RPC schema changes, no backend Go code changes.
- No new image in the matrix.
- No retag of historical backend prod images (e.g., `:v0.x.y` already published) — the retag flow starts at the first release published after this change merges and the prod AR has the required source digests from the dev push corresponding to that release's commit SHA.
- No "Frontend prod image SHALL be env-agnostic at the bundle level"-equivalent backend invariant — backend images are server-side; they don't carry env-divergent build args today (`deploy.yml` passes no `--build-arg` already), so there's nothing to assert.
- No automated digest-equality CI assertion (tracked as separate optional future change per §6.2 of the frontend retag's tasks.md).

## Decisions

### D1. Tool: `crane copy`

**Chosen**: `crane copy` (from `google/go-containerregistry`, installed via `imjasonh/setup-crane@v0.4`).

**Alternatives considered**:

- `gcloud artifacts docker tags add`: rejected; same-repo-only as proven during the frontend rollout's first failure.
- `gcrane copy`: rejected; the `imjasonh/setup-crane` action does NOT install the `gcrane` wrapper binary (only `crane`), as discovered during the frontend rollout's second failure. `crane` is functionally equivalent against AR.
- `skopeo copy`: alternative go-containerregistry-equivalent. Not chosen because `crane` is already wired into the workspace's CI (frontend), so reusing it eliminates per-CI tool drift.

### D2. Matrix structure: preserve, retag per matrix entry

**Chosen**: keep the existing 4-image strategy matrix in `deploy.yml`. The release path adds steps inside the matrix loop: install crane, resolve dev AR digest for `<matrix.image.name>:${GITHUB_SHA}`, run `crane copy` twice (`:<release-tag>` and `:${GITHUB_SHA}`). All 4 matrix jobs run in parallel; total wall-clock time is bounded by the slowest single retag (typically <30 s).

**Alternatives considered**:

- Collapse the matrix into a single job that loops over 4 images sequentially. Rejected because losing parallelism slows wall-clock by ~4× without freeing any other resource — the matrix runners are already pre-allocated, and per-job auth setup is amortized across the steps inside that job.
- Split into separate `build-and-push` (dev) and `promote-and-push` (release) jobs that share a common matrix. Rejected because the existing `build-and-push` job's pre-auth, WIF, and SDK setup are identical for both paths; only the terminal step diverges (build-push vs digest-resolve+crane-copy). A single matrix with conditional steps keeps the workflow's mental model uniform with frontend.

### D3. IAM grant: single repo-scoped binding on dev backend AR

**Chosen**: add one `RepositoryIamMember` in `cloud-provisioning/src/gcp/index.ts`, mirroring `prod-ci-frontend-ar-reader` but targeted at the dev `backend` AR repo. The same `if (environment === 'dev') { … }` gate is used (the resource lives in the dev project's AR; the prod CI SA is the member). Member: `serviceAccount:github-actions@${brandId}-prod.iam.gserviceaccount.com`. Role: `roles/artifactregistry.reader`. Resource: dev backend AR repo. `protect: true` to prevent accidental teardown.

**Alternatives considered**:

- Grant project-level reader on `liverty-music-dev`. Rejected — violates the "scoped cross-project AR reader" requirement which explicitly requires repository-level binding, and would expand the blast radius from one repo to every AR repo in the dev project.
- Combine frontend + backend grants into a single binding with multiple resources. Rejected — Pulumi's `RepositoryIamMember` is one-resource-per-binding. Two separate declarations are clearer in code review and Pulumi state.

### D4. First-cutover coordination: separate per-namespace overlay bump

**Chosen**: the first backend release after this change lands triggers retag of all 4 images into prod AR. The actual prod cutover is a separate cloud-provisioning PR that bumps `k8s/namespaces/backend/overlays/prod/kustomization.yaml`'s `newTag:` from the prior tag to the new one for ALL 4 Deployments simultaneously (single PR, single ArgoCD sync wave). Per-Deployment staggered bumps are rejected because the 4 backend services share a release SemVer — versioning them independently introduces drift the project doesn't want.

**Alternatives considered**:

- Auto-bump via ArgoCD Image Updater on `:vX.Y.Z` regex (similar to dev's `:latest` write-back). Rejected — prod overlays intentionally use static `newTag:` pins for human-gated rollouts. This is consistent with the frontend equivalent and with the `prod-image-tag-immutability` spec's runbook semantics.

### D5. Partial-success failure handling

**Risk**: the matrix may produce partial success — e.g., 3/4 retags succeed and 1 fails (transient AR error, IAM propagation delay, etc.). The 3 successful retags wrote prod AR tags that are now immutable per `prod-image-tag-immutability`.

**Chosen response**: documented in the runbook update (`docs/runbooks/prod-image-tag-pinning.md` extension to the "Retag failure recovery" section). The operator SHALL NOT attempt to re-trigger the failed retag in isolation — instead, the recovery path is:

1. Investigate the per-matrix-entry failure log.
2. If the cause is transient and the partial state is safe (3 prod AR tags exist, 1 missing), re-run the failed matrix entry via `gh run rerun --job <job-id>`. The successful matrix entries' AR writes are idempotent against re-runs because the digest is identical (same source) and `crane copy` to an existing immutable tag with the same digest is a no-op (verified during the frontend rollout — `prod-image-tag-immutability` returns 200 OK, not 409, when the destination digest matches the existing digest).
3. If the cause is permanent (e.g., release was cut on a non-main commit and the digest-resolve fails for all 4), the entire release SHALL be re-cut on the correct commit. Per the immutable-tags rule, the existing 3/4 prod AR tags remain in place; the new release uses a new SemVer.

The "re-run failed job is safe" claim relies on `crane copy` to an immutable tag at the same digest being a no-op. This was empirically validated during the frontend rollout: PR #361's failed v1.0.2 run wrote no prod-AR tags, PR #362's subsequent run completed cleanly, and the final PR #363 run's `crane copy` against an AR repo with `immutableTags: true` returned 200 OK (not 409 Conflict) when the destination digest matched. That evidence carries over to backend (same registry, same tool, same auth path). No additional regression test is added in this change's tasks — re-litigating an established premise inflates the task list without changing the outcome. If a future change introduces a parallel write path that COULD violate the same-digest no-op property, that change is the right place to gate it with an explicit assertion.

## Risks / Trade-offs

- **[Risk] IAM propagation delay** → first release after Pulumi apply may fail digest-resolve with PERMISSION_DENIED. Mitigation: Pulumi up runs ahead of any release event (gated by cloud-provisioning's main-merge automation); the IAM grant typically propagates within seconds. Same risk profile as the frontend rollout, where no propagation delay was observed in practice.

- **[Risk] Partial-matrix failure leaves prod in mixed-version state** → the kustomize bump PR pins all 4 newTag values to the same release SemVer; ArgoCD applies them as one Application sync. So a successful Pulumi apply followed by a successful 4/4 retag and then a successful single cloud-provisioning bump means the 4 backend Deployments roll in lock-step. The risk is only if (a) one of the 4 retags fails AND (b) the operator merges the cloud-provisioning bump anyway. The ArgoCD sync would then fail at the Deployment whose image tag is missing in prod AR. Mitigation: the cloud-provisioning bump PR MUST be gated on all 4 retag jobs completing successfully (operator checklist, not enforced by CI in this iteration).

- **[Risk] Backend dev AR storage growth** → the retag flow inherently retains every dev `:<sha>` AR tag the prod CI SA might need to resolve, in perpetuity. Same risk as frontend (where the retention exposure is identical). Mitigation: deferred to a future capability — AR lifecycle policies — that would prune `:<sha>` tags older than N days while preserving any tag that has a corresponding prod retag. Not in scope for this change.

- **[Trade-off] No automated digest-equality CI step** → `crane copy` to AR uses cross-repo blob mounting; the destination digest IS the source digest by construction of the protocol. A separate CI assertion would be a redundant tautology. Manual verification at the first cutover (tasks §4.x) is sufficient.

## Migration Plan

1. **specification PR** (this change): merge.
2. **cloud-provisioning PR**: add `prod-ci-backend-ar-reader` binding in `src/gcp/index.ts`, mirroring the frontend one. Runbook update for backend matrix dimension. Merge → dev Pulumi auto-applies via Pulumi Cloud Deployments. Verify the binding live with `gcloud artifacts repositories get-iam-policy backend --project=liverty-music-dev --location=asia-northeast2`.
3. **backend PR**: refactor `deploy.yml` release path. Open the PR only after step 2's Pulumi apply completes (or the first release will fail digest-resolve). Merge → dev push event re-builds the 4 images normally (validates the unchanged dev path).
4. **First post-merge backend release** (e.g., `vN+1`): cut via the standard GitHub Release flow. The release event triggers the new retag path across the 4-image matrix. Watch the workflow run; confirm all 4 matrix entries land both `:vN+1` and `:<sha>` in prod AR.
5. **Backend prod cutover**: separate cloud-provisioning PR bumping the 4 Deployments' `newTag:` from prior to `vN+1`. ArgoCD syncs prod backend in lock-step.

**Rollback strategy**: per the immutable-tags rule, rollback is "cut a new patch release on the prior good commit" — not "re-tag prod AR". Same as frontend.

## Open Questions

(none — all decisions resolved; this change inherits validated patterns from the frontend retag rollout)
