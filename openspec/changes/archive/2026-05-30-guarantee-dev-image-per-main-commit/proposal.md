## Why

The prod release pipeline rests on an invariant that is silently false: **"any commit on `main` is releasable."** The release path promotes a pre-built dev image by resolving `dev-AR/<image>:<github.sha>` and `crane copy`-ing it to prod — it never rebuilds. But the dev build is gated by a `paths:` filter (`**.go`, `go.mod`, `Dockerfile`, …), so a commit that touches only non-matching files (CI config, docs) produces **no dev `:<sha>` image**. Cutting a release on such a `main` HEAD fails at digest-resolve after a wasted ~5-minute retry budget — which is exactly what happened promoting backend `v1.2.0` (HEAD `efd340a` was a CI-only commit with no image; we had to re-target the last built commit).

Worse, the pipeline's own guidance is self-contradictory: the `Verify release commit is on main` guard prints **"Cut releases on main HEAD only"**, yet following that advice is what triggers the failure — the recovery (re-target an earlier built commit) directly contradicts it.

Rather than patch the symptom (better error messages, fast-fail detection), this change **makes the invariant true**: every `main` commit gets a resolvable dev `:<sha>` image, so "release any main commit" actually holds and the entire failure class — plus the disambiguation and contradictory-guidance problems — disappears.

## What Changes

- **Every commit on `main` SHALL have a resolvable dev-AR `:<sha>` image.** When a push to `main` is filtered out of the build (no source/Dockerfile change), the pipeline inherits the parent commit's dev-AR digest by `crane copy`-ing it onto the new commit's `:<sha>` tag — no rebuild. This is semantically exact: a commit that changed no build-relevant file produces byte-identical bytes to its parent, so the parent's digest *is* this commit's image.
- **The release path's digest-resolve guard is simplified.** With the invariant guaranteed, a missing `:<sha>` on a `main` commit can no longer mean "filtered-out / never coming" — it can only mean a genuine in-flight race or a build failure. The retry semantics and error classification are restated against the new, narrower cause set.
- **The contradictory guidance is removed.** The `Verify release commit is on main` and digest-resolve messages are aligned with the (now-true) invariant: releasing on `main` HEAD is always valid.
- Applied **symmetrically** to backend (`deploy.yml`, 4-image matrix) and frontend (`push-image.yaml`, single `web-app` image), since both carry `paths:` filters and the same gap.
- The retag-failure recovery **runbook** (cloud-provisioning) is updated to reflect that the path-filtered cause is now eliminated at the source.

This is a behavioral change to the CI/CD pipeline only. No proto, API, or runtime-service change.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `prod-image-pipeline`: ADD a requirement that every `main` commit has a resolvable dev-AR `:<sha>` image (parent-digest inheritance on filtered pushes), for both backend and frontend. MODIFY the existing "Release CI SHALL refuse a matrix entry if its dev AR `:<sha>` is missing" requirements (backend + frontend) so the cause set and retry rationale reflect the guaranteed invariant, and align the on-main verification guidance.

## Impact

- **Specs**: `openspec/specs/prod-image-pipeline/spec.md` (modified + added requirements).
- **Backend**: `backend/.github/workflows/deploy.yml` — drop the `push` `paths:` gate as a *trigger*, replace with an in-workflow build-vs-inherit decision; add a parent-digest inherit path across the 4-image matrix.
- **Frontend**: `frontend/.github/workflows/push-image.yaml` — same build-vs-inherit treatment for `web-app`.
- **cloud-provisioning**: `docs/runbooks/prod-image-tag-pinning.md` — revise the "dev AR `:<sha>` does not exist" failure mode. No new IAM (the existing `prod-ci-<repo>-ar-reader` repo-scoped readers and dev-AR write credentials already cover digest read + tag write within dev AR).
- **No change** to ArgoCD apps, kustomize overlays, prod AR immutability, or any service runtime.
- **Risk**: every `main` push now spins a CI runner even for doc-only commits (previously skipped). The inherit path adds no Docker build (~10s crane retag), so the marginal cost is runner startup, not build time — consistent with the `ci-optimization` capability's intent (avoid redundant *builds*, not avoid all runs).
