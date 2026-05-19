## Why

The frontend release path was successfully migrated from rebuild-on-release to dev-AR → prod-AR retag (archived `promote-prod-image-via-retag`, validated live on `frontend@v1.0.2`). Backend's `deploy.yml` still rebuilds 4 images (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) on every release event, multiplying the redundant-build cost 4× per release and reintroducing the dev/prod image-divergence risk that retag was designed to eliminate. The pattern is now proven; backend is the missing symmetric half.

## What Changes

- Backend `liverty-music/backend/.github/workflows/deploy.yml`'s release path stops invoking `docker/build-push-action` for the 4-image matrix and instead resolves each dev AR digest for `github.sha` and runs `crane copy` to retag into prod AR under `:<release-tag>` and `:<sha>`. The dev push path is unchanged.
- Cloud-provisioning grants `github-actions@liverty-music-prod` `roles/artifactregistry.reader` on the `liverty-music-dev/backend` Artifact Registry repository (repo-scoped IAM binding declared in Pulumi, mirroring the frontend grant from `cloud-provisioning#282`).
- `prod-image-pipeline` capability tightens: the "Backend dev AR is NOT yet granted (forward-looking)" scenario flips from an *intentional gap* (informational) to a *compliance requirement* (the binding MUST now be present). The "Backend prod image build SHALL be triggered by GitHub Release tags" requirement is renamed and its body replaced with retag prose, structurally mirroring the frontend change.
- Runbook updates in `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md`'s retag failure-recovery section to cover the backend matrix dimension (4× failure surfaces per release event).

No proto / schema changes. No backend application code changes. CI workflow + Pulumi IAM only.

## Capabilities

### New Capabilities

(none — this change extends existing capabilities only)

### Modified Capabilities

- `prod-image-pipeline`:
  - **MODIFIED** "Backend prod image build SHALL be triggered by GitHub Release tags" → renamed to "Backend prod images SHALL be promoted to prod AR on GitHub Release tags"; body and scenarios replaced with retag-flow scenarios that mirror the frontend equivalent across the 4-image matrix.
  - **MODIFIED** "CI service accounts MAY hold scoped cross-project AR reader for image promotion": the "Backend dev AR is NOT yet granted (forward-looking)" scenario is **REMOVED** (because the grant now exists), and a positive scenario "Prod CI SA holds repo-scoped reader on dev backend AR" is **ADDED** to assert the binding's presence.

## Impact

- **Code**: `liverty-music/backend/.github/workflows/deploy.yml` (release-path refactor); `liverty-music/cloud-provisioning/src/gcp/index.ts` (add `prod-ci-backend-ar-reader` binding mirroring `prod-ci-frontend-ar-reader`); `liverty-music/cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md` (extend retag failure section for matrix dimension).
- **APIs**: none.
- **Dependencies**: GitHub Action `imjasonh/setup-crane@v0.4` added to backend `deploy.yml` (already used by frontend; no new tool surface).
- **Systems**: prod backend pulls switch from rebuild-produced bytes to dev-AR-byte-identical bytes. The first post-merge backend release MUST be coordinated with the cloud-provisioning prod overlay's `newTag:` bump for each of the 4 Deployments (single PR or 4× rolling bumps — to be decided in `design.md`).
- **Release-event runtime**: drops from ~6 minutes (4× ~90s sequential build-push, cache-from `type=gha`) to ~30 seconds (auth + 4× digest-resolve + 8× `crane copy`).
- **Security posture**: identical risk profile to frontend's grant — CI SA gains repo-scoped read on dev backend AR. No project-level grant, no writer, no admin, scoped to a single repo. The cluster-SA forbidden boundary is preserved.
