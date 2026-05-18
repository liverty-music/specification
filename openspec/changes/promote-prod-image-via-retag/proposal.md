## Why

The current frontend release path **rebuilds** the container image when a GitHub Release is published, producing a second image whose digest differs from the dev AR image even though the source, lockfile, and Dockerfile inputs are bit-identical. This wastes ~1–2 min of CI time per release and leaves us with two unrelated digests for the same source — defeating the "test the image you ship" attestation story that downstream tooling (SBOM signing, supply-chain provenance) will eventually require.

The rebuild model was the unconsidered default that fell out of `prepare-prod-service-in` (archived 2026-05-16); a grep for `retag` in that change's design produced zero hits. Since then, `adopt-runtime-config-for-frontend` (archived 2026-05-16) made the SPA bundle env-agnostic — there is now **no functional reason** for a separate prod build. Every meaningful per-environment value comes from `/config.json` at runtime, not from build-time injection. Two distinct digests for the same source is pure ceremony.

Retag flips the model: the dev push writes one canonical image digest into `liverty-music-dev/frontend/web-app:<sha>`. On release publish, CI re-tags that exact digest into `liverty-music-prod/frontend/web-app:vX.Y.Z` via `crane copy` (from `google/go-containerregistry`). The image deployed to prod is — byte-for-byte — the image already exercised in dev. CI time drops from ~2 min (build + push) to ~10 s (manifest re-push via AR's cross-repo blob mounting). The existing `prod-image-tag-immutability` capability already protects against accidental re-pointing of a published tag (HTTP 409 from AR), so the retag flow lands in a registry already designed for it.

The only piece of new IAM is a scoped `roles/artifactregistry.reader` on `liverty-music-dev/frontend` AR repo for `github-actions@liverty-music-prod.iam.gserviceaccount.com`. This requires an explicit carve-out in `prod-image-pipeline`'s "no cross-project AR grants" rule, which today reads as a blanket prohibition. The rule's intent (per its scenarios) is to constrain **cluster** service accounts; CI service accounts are ephemeral (active only during a Workflow run), so the cross-project blast radius is structurally different. This change tightens the rule's language to match its intent.

Scope is **frontend only**. Backend has the same 4-image-matrix rebuild structure and would benefit symmetrically, but doing both in one change multiplies the IAM-grant + workflow-refactor surface 5x and risks burying a frontend-specific issue in a larger blast radius. Backend retag is a follow-up.

## What Changes

- **BREAKING (CI workflow only — no app contract change)**: `liverty-music/frontend/.github/workflows/push-image.yaml`'s release path stops invoking `docker/build-push-action` and instead authenticates via the prod WIF, pulls the dev AR digest for the release's commit SHA, and runs `crane copy` to copy it under `:<release-tag>` and `:<sha>` in `liverty-music-prod/frontend/web-app`.
- New defensive guard: release CI fails fast with a clear error if the dev AR `:<sha>` tag does not exist yet (e.g., release cut on a non-main commit, dev push hadn't completed).
- Pulumi IAM addition: `gcp.artifactregistry.RepositoryIamMember` granting `roles/artifactregistry.reader` on `liverty-music-dev/frontend` to `github-actions@liverty-music-prod.iam.gserviceaccount.com`. Scope is **repo-level**, not project-level, to minimize blast radius.
- Spec rule update: the "no cross-project AR IAM grants" requirement is tightened from "prod cluster service accounts" (the current phrasing implies all SAs) to explicitly named cluster SAs, with a new requirement carving out CI service accounts for scoped image-promotion reads.
- Runbook update: `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md` gains a "retag failure recovery" section covering dev-AR-missing-`:sha`, accidental cross-project IAM revoke, and immutable-tag re-push rejection.
- **Bonus cleanup**: the "Image tags are explicit, never `:latest`" scenario in `prod-image-pipeline` becomes dead-code (already strictly governed by the newer `prod-image-tag-immutability` semver-only rule); fold it away.

## Capabilities

### New Capabilities
*None.*

### Modified Capabilities
- `prod-image-pipeline`: Replaces the rebuild-based frontend release requirement with a retag-based one (preserving the release-trigger gating and post-build template-presence assertion). Tightens the cluster-SA cross-project IAM prohibition to its named scope and adds a complementary CI-SA carve-out. Drops the `:<sha>`-permitting tag-form scenario now superseded by `prod-image-tag-immutability`.

## Impact

**Affected repos**:
- `frontend`: `.github/workflows/push-image.yaml` only — no app-code change. The release-event branch of the workflow restructures from "build → push" to "auth → resolve dev-AR digest → guard → tag-add → tag-add".
- `cloud-provisioning`: Pulumi component for the cross-project AR grant (one `RepositoryIamMember` resource). Runbook addition.
- `specification`: this change.

**Affected CI**:
- ~1–2 min/release saved on the prod release path. Dev path unchanged (still builds + pushes).
- New failure mode at release time: dev AR `:<sha>` not found. The guard step's error message points operators at the recovery runbook section.

**Affected IAM**:
- One new `RepositoryIamMember`: `github-actions@liverty-music-prod` ← `roles/artifactregistry.reader` on `projects/liverty-music-dev/locations/asia-northeast2/repositories/frontend`. Scope is exactly one repo in one location.

**Affected images**:
- Post-cutover: `liverty-music-prod/frontend/web-app:<release-tag>` and `:<sha>` share the digest of `liverty-music-dev/frontend/web-app:<sha>`. Pre-cutover prod images (v1.0.0, v1.0.1) are unchanged and stay in prod AR.
- AR storage usage drops slightly (the prod-side digest deduplicates against the dev-side digest going forward — they're now the same).

**User-facing impact**: None. The deployed prod artifact is byte-identical to what dev runs. Smoke E2E (post-deploy-smoke job) continues to gate the rollout.

**Coordination notes**:
- Spec PR → cloud-provisioning IAM PR (gates the workflow change — without the IAM grant, the retag step fails) → frontend workflow PR → next release tag cut tests the new flow end-to-end.
- Backend symmetric retag is a separate change; flagged in `tasks.md` for follow-up tracking.
