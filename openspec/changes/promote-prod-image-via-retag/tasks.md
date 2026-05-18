> **Cross-repo task layout**: Tasks 1 lives in `specification`; tasks 2 in `cloud-provisioning`; tasks 3 in `frontend`; tasks 4 is the user-gated cutover; tasks 5 is archive. The specification PR ships only the contract — implementation lands in companion PRs that reference this change's archive.

## 1. Specification

- [ ] 1.1 Open PR with this change's artifacts (proposal + design + spec deltas + tasks). Merge captures the contract.

## 2. cloud-provisioning — IAM grant + runbook

- [ ] 2.1 Add a `gcp.artifactregistry.RepositoryIamMember` resource in `cloud-provisioning/src/gcp/` that grants `roles/artifactregistry.reader` on `projects/liverty-music-dev/locations/asia-northeast2/repositories/frontend` to `github-actions@liverty-music-prod.iam.gserviceaccount.com`. Bind at the **repository resource level** (not project IAM). Resource name suggestion: `prod-ci-frontend-ar-reader`.
- [ ] 2.2 Decide which Pulumi component owns the binding: most naturally the prod project's workload-identity component (it already declares the `github-actions@prod` SA), or a new cross-project-image-promotion component. Keep dev's `frontend` AR repo handle reachable from that component (re-export from `liverty-music-dev` project component if needed).
- [ ] 2.3 Update `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md` (created by the `prod-image-tag-immutability` change) with a new section "Retag failure recovery" covering: (a) dev AR `:<sha>` missing — wait or pick a different commit; (b) accidental cross-project IAM revoke — re-`pulumi up`; (c) immutable-tag re-publish attempt — cut new semver.
- [ ] 2.4 Run `make lint-ts` and `make lint-k8s` (no K8s manifest changes expected, but the lint chain validates Pulumi typing + render).
- [ ] 2.5 Run `pulumi preview --stack dev` then `--stack prod` from the cloud-provisioning checkout. Confirm exactly one resource creation per stack (the new `RepositoryIamMember`).
- [ ] 2.6 Open PR. After review + merge, `dev` stack auto-applies via Pulumi Cloud Deployments; **operator runs `pulumi up --stack prod` manually** from the Pulumi Cloud console.
- [ ] 2.7 Verify the binding in the live IAM policy:
  - `gcloud artifacts repositories get-iam-policy frontend --project=liverty-music-dev --location=asia-northeast2 --format=json` SHOULD list `serviceAccount:github-actions@liverty-music-prod.iam.gserviceaccount.com` under `roles/artifactregistry.reader`.

## 3. frontend — workflow refactor

- [ ] 3.1 Refactor `frontend/.github/workflows/push-image.yaml` release-event branch:
  - Remove the `Set up Docker Buildx`, `Build and Push Docker Image`, and (release-conditional) `Set Image Tags (prod path)` steps from the release event.
  - Add a new step "Resolve dev AR digest for github.sha" running `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:${{ github.sha }} --format='value(image_summary.digest)'`. Retry up to 5 × 60 s if empty (race against in-flight dev push).
  - On non-empty digest output: store in `steps.<id>.outputs.digest`; otherwise fail with a clear error message pointing at the runbook section added in task 2.3.
  - Add a new step "Authenticate to Google Cloud (dev AR read + prod AR write)" — the prod environment's WIF + SA already grants prod-AR-writer; after task 2 lands, the same SA gains dev-AR-reader at the repo level.
  - Add two `gcloud artifacts docker tags add` steps:
    - `asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app@<digest>` → `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:${{ github.event.release.tag_name }}`
    - same source → `asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:${{ github.sha }}`
- [ ] 3.2 Push path (event_name == 'push') is unchanged. Verify by reading the diff that the only file under `.github/workflows/` that changed is `push-image.yaml`, and the dev path's steps are byte-identical to current main.
- [ ] 3.3 The `post-deploy-smoke` job's `needs: build-and-push` SHALL stay — the job name is unchanged even though the job's release-event behavior is now retag-only. Update the inline comment block at the top of the job to reflect the new semantics ("on release: skip; smoke fires only on push-to-main via Image Updater"). The `if:` condition (`github.event_name == 'push'`) already gates smoke off the release path; no change needed.
- [ ] 3.4 Open the workflow YAML in a parser to confirm validity: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/push-image.yaml'))"`.
- [ ] 3.5 Open PR. **Do NOT merge until task 2 completes** (`pulumi up --stack prod` applied) — without the IAM grant the digest-resolve step fails. The frontend PR description SHOULD explicitly reference the cloud-provisioning PR as a dependency.

## 4. Cutover and verification

- [ ] 4.1 After spec PR + cloud-provisioning PR (incl. `pulumi up --stack prod`) + frontend PR all merge, cut the next release tag (e.g., `v1.0.2` or higher — increment from the current `v1.0.1`).
- [ ] 4.2 Watch the `Deploy Frontend` workflow's release-event run. Expected: `Resolve dev AR digest` succeeds; two `gcloud artifacts docker tags add` calls succeed; total release-event runtime drops from ~90 s (prior build-push) to ~30 s (auth + resolve + 2× tag-add).
- [ ] 4.3 Verify byte-identity: `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app:v1.0.2 --format='value(image_summary.digest)'` matches `gcloud artifacts docker images describe asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:<sha-of-v1.0.2-commit> --format='value(image_summary.digest)'`.
- [ ] 4.4 Cloud-provisioning prod overlay bump: in `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml`, update `app.kubernetes.io/version` label + `images[*].newTag` + inline commit SHA comment to the new release. Open + merge a small bump PR.
- [ ] 4.5 ArgoCD syncs prod to v1.0.2. Verify `curl https://liverty-music.app/` returns `200` and `curl https://liverty-music.app/config.json` returns `environment=prod`.
- [ ] 4.6 Run the post-deploy smoke manually against prod: `gh workflow run "Deploy Frontend" --repo liverty-music/frontend -f smoke_url=https://liverty-music.app` (the standalone workflow_dispatch path added in PR #359). Confirm `2 passed`.

## 5. Archive

- [ ] 5.1 After tasks 1–4 verified, prepare an archive PR per the repo's openspec-sync-specs pattern: move `openspec/changes/promote-prod-image-via-retag/` to `openspec/changes/archive/<date>-promote-prod-image-via-retag/`.
- [ ] 5.2 Merge spec deltas into canonical `openspec/specs/prod-image-pipeline/spec.md`:
  - **MODIFIED**: "Prod cluster service accounts SHALL NOT hold cross-project Artifact Registry IAM grants" — tightened scope text + scenario renames (`No prod SA in dev project IAM policy` → `No prod cluster SA in dev project IAM policy`).
  - **MODIFIED**: "Frontend prod image build SHALL be triggered by GitHub Release tags" — replaced rebuild body with the retag flow; added 3 new scenarios (`GitHub Release publish promotes the dev AR digest`, `Prod and dev images share the same digest after promotion`, `Release CI SHALL refuse if dev AR :<sha> is missing`); preserved + renamed the post-build template-presence scenario (`Post-build template-presence assertion gates both paths` → `Post-build template-presence assertion gates the dev path` to reflect that prod no longer runs a build).
  - **ADDED**: "CI service accounts MAY hold scoped cross-project AR reader for image promotion" with all four scenarios.
  - **REMOVED** (1): The "Image tags are explicit, never `:latest`" scenario under "Prod kustomize overlays SHALL pin image URIs to prod-AR paths" — superseded by `prod-image-tag-immutability`'s semver-only rule.
  - **REMOVED** (2): The "Prod and dev builds use identical Dockerfile inputs" scenario under "Frontend prod image build SHALL be triggered by GitHub Release tags" — its precondition (`comparing the docker build invocations of the dev push path and the release prod path`) is no longer satisfiable because the release path no longer runs `docker build`. The env-agnostic guarantee is preserved by the dev-path template-presence assertion + the new "Prod and dev images share the same digest after promotion" scenario.
- [ ] 5.3 Run `openspec validate --specs` against the merged canonical specs to confirm no orphan references remain (e.g., `docker/build-push-action.*release` patterns in `prod-image-pipeline`).

## 6. Follow-ups (NOT in this change)

- [ ] 6.1 **Backend symmetric retag**: file a new OpenSpec change to apply the same dev-AR → prod-AR retag flow to backend's 4-image matrix (`server`, `consumer`, `concert-discovery`, `artist-image-sync`). The pattern this change validates carries over directly, but the matrix multiplies the IAM grant + workflow refactor surface and is best owned by a separate change. Reference this archived change in the new change's design.md as the established pattern.
- [ ] 6.2 **Digest-equality CI assertion (future)**: post-cutover, optionally add a CI step that asserts `digest(prod:vX.Y.Z) == digest(dev:<sha>)` to catch any future regression where someone reintroduces a prod-side build. Out of scope for the initial cutover; track as a separate small change if the assertion proves valuable.
