## 1. Cloud-provisioning IAM grant

- [ ] 1.1 Add `prod-ci-backend-ar-reader` `RepositoryIamMember` in `cloud-provisioning/src/gcp/index.ts`, mirroring the existing `prod-ci-frontend-ar-reader` but with `repository: backendArtifactRegistry.name` (or the equivalent local symbol). Same `if (environment === 'dev')` gate, same `member: serviceAccount:github-actions@${brandId}-prod.iam.gserviceaccount.com`, same `role: 'roles/artifactregistry.reader'`, same `protect: true`. The two grants are declared side-by-side for code-review clarity.
- [ ] 1.2 Update the `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md` "Retag failure recovery" section to describe the backend matrix dimension: 4 parallel jobs, `strategy.fail-fast: false`, partial-success recovery via `gh run rerun --job <job-id>`, and the no-op-on-immutable-tag-with-same-digest behavior of `crane copy` that makes re-runs safe.
- [ ] 1.3 Open the cloud-provisioning PR. Body links this OpenSpec change. Merge it; verify dev Pulumi Cloud Deployment auto-applies (check the `dev` stack's most recent update for "+ gcp:artifactregistry/repositoryIamMember:RepositoryIamMember prod-ci-backend-ar-reader").
- [ ] 1.4 Verify the binding live: `gcloud artifacts repositories get-iam-policy backend --project=liverty-music-dev --location=asia-northeast2 --flatten='bindings[].members' --filter='bindings.members~github-actions@liverty-music-prod'`. Expected: one binding for `roles/artifactregistry.reader` at repo resource level; nothing for `writer`/`admin`/`repoAdmin`; nothing at project-level (`gcloud projects get-iam-policy liverty-music-dev …` returns empty).

## 2. Backend workflow refactor

- [ ] 2.1 In `liverty-music/backend/.github/workflows/deploy.yml`, set `strategy.fail-fast: false` on the `build-and-push` job so a single matrix entry's failure does not cancel the other 3.
- [ ] 2.2 Add the `Install crane` step (gated to `if: github.event_name == 'release'`) using `imjasonh/setup-crane@v0.4`. Inline comment block: explicitly note that the action installs `crane` (NOT `gcrane`), and that `crane` reads auth from `~/.docker/config.json` populated by the existing `Configure Docker` step which already runs on both paths (no change needed there for backend, unlike the frontend rollout which had to drop a `push`-only gate).
- [ ] 2.3 Replace the release-path `Build and Push Docker Image` step with two new release-only steps per matrix entry:
  - `Resolve dev AR digest for <matrix.image.name>:${GITHUB_SHA}` — runs the 6-attempt × 60s-wait loop documented in the frontend equivalent. Source image FQDN: `${REGION}-docker.pkg.dev/liverty-music-dev/${REPOSITORY}/${matrix.image.name}:${GITHUB_SHA}`.
  - `Promote dev AR digest to prod AR (semver + sha tags)` — runs `crane copy <src>@<digest> <dst>:<release-tag>` and `crane copy <src>@<digest> <dst>:${GITHUB_SHA}`. Destination FQDN: `${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${matrix.image.name}` (where `PROJECT_ID` resolves to `liverty-music-prod` via the `prod` GH environment binding).
- [ ] 2.4 Gate the existing `Set up Docker Buildx` step and the `docker/build-push-action` step to `if: github.event_name == 'push'` so neither runs on the release path. Keep the `Set Image URI`, `Set Image Tags (dev path)` steps as-is on the conditions they already have.
- [ ] 2.5 Remove the now-dead `Set Image Tags (prod path)` step from `deploy.yml`. The release path no longer consumes `IMAGE_TAGS` because `crane copy` takes destination tags directly. Leaving the step would mislead future readers about whether prod-path tag-set still wires anything.
- [ ] 2.6 Update the inline comment block at the top of `deploy.yml` to document the dual-trigger semantics: `push → dev rebuild`, `release → 4× crane copy`. Reference this archived OpenSpec change once archived.
- [ ] 2.7 Open the backend PR after step 1's IAM grant is live. Body links this OpenSpec change. Merge after CI + review.

## 3. Workflow runtime validation (dev path unchanged)

- [ ] 3.1 The merge-to-main of the backend workflow PR triggers a `push` event, which exercises the dev path. Watch the run. Expected: all 4 matrix entries succeed (build + push to `liverty-music-dev/backend/{server,consumer,concert-discovery,artist-image-sync}:latest,:main,:<sha>`), with no behavior change from the prior workflow. Total runtime should be within ±10% of the prior dev-path baseline.
- [ ] 3.2 Confirm the dev AR has the 4 `:<sha>` tags for the merge commit: `for img in server consumer concert-discovery artist-image-sync; do gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-dev/backend/$img:<sha> --format='value(image_summary.digest)'; done`. Capture the 4 digests; they are the byte-identity reference for the first retag run.

## 4. First retag end-to-end validation

- [ ] 4.1 Cut a backend GitHub Release on the same merge commit from §3.1 (e.g., `vN+1`). Confirm the Release `target_commitish` is the merge commit's SHA.
- [ ] 4.2 Watch the `Deploy Backend` workflow's release-event run. Expected: 4 matrix entries run in parallel; each `Resolve dev AR digest` succeeds; each runs 2× `crane copy` successfully; total release-event runtime is ≤ ~60 s (well under the ~6 min the prior 4× build-push took). Capture the run ID.
- [ ] 4.3 Verify byte-identity for each of the 4 images: `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-prod/backend/<img>:vN+1` SHALL match the dev digest captured in §3.2 for the same `<img>` + `<sha>`. All 4 SHALL match.
- [ ] 4.4 Cloud-provisioning prod overlay bump: in `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml`, bump the 4 `images[*].newTag` entries (and the `app.kubernetes.io/version` label) to `vN+1`. Open + merge a small bump PR. Single PR covers all 4 Deployments so ArgoCD applies them in lock-step.
- [ ] 4.5 ArgoCD syncs prod to vN+1. Verify via `kubectl --context=<prod-cluster> -n backend get deploy -o jsonpath` that all 4 backend Deployments now reference `:vN+1` and the `app.kubernetes.io/version: <vN+1>` label is present.
- [ ] 4.6 Verify prod backend RPC health: `curl https://api.liverty-music.app/grpc.health.v1.Health/Check` (auth-exempt endpoint per the dev/prod conventions) SHALL return `SERVING`. Optionally run an authenticated smoke against `api.liverty-music.app` using the stored test-user JWT.

## 5. Archive

- [ ] 5.1 After tasks 1–4 verified, prepare an archive PR per the repo's openspec-sync-specs pattern: move `openspec/changes/backend-symmetric-retag/` to `openspec/changes/archive/<date>-backend-symmetric-retag/`.
- [ ] 5.2 Merge spec deltas into canonical `openspec/specs/prod-image-pipeline/spec.md`:
  - **MODIFIED**: "Backend prod image build SHALL be triggered by GitHub Release tags" → renamed to "Backend prod images SHALL be promoted to prod AR on GitHub Release tags"; replace requirement body with retag prose; replace scenarios per the delta.
  - **MODIFIED**: "CI service accounts MAY hold scoped cross-project AR reader for image promotion" — remove the "Backend dev AR is NOT yet granted (forward-looking)" scenario; replace with "Prod CI SA holds repo-scoped reader on dev backend AR"; merge the no-writer/admin scenario into one that iterates both repos via `<repo>` placeholder.
- [ ] 5.3 Run `openspec validate --specs` against the merged canonical specs to confirm no orphan references remain (e.g., `docker/build-push-action.*release` patterns in `prod-image-pipeline` for backend).

## 6. Follow-ups (NOT in this change)

- [ ] 6.1 **AR `:<sha>` retention policy**: file a follow-up to add Artifact Registry lifecycle / cleanup policies that prune dev `:<sha>` tags older than N days while preserving any tag that has a corresponding prod retag. The retag flow's correctness does not require pruning (resolution is by `:<sha>` not by recency), but storage cost grows unbounded otherwise. Out of scope for the retag cutover itself.
- [ ] 6.2 **Digest-equality CI assertion**: optionally add a CI step that asserts `digest(prod:vX.Y.Z) == digest(dev:<sha>)` per image after each retag. Redundant by construction of `crane copy`, but a useful integrity tripwire if a future change reintroduces a parallel rebuild path. Tracked carrying over from the frontend retag's §6.2 — still optional.
