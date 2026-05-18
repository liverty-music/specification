## Context

Phase 1 (`adopt-runtime-config-for-frontend`, archived 2026-05-16) eliminated build-time environment divergence. Every `vite build` invocation now produces an env-agnostic SPA bundle; per-environment values come from a `/config.json` Kubernetes ConfigMap mounted at request time. The corollary that wasn't pursued in Phase 1: with no build-time divergence, the prod release CI has nothing to build differently. It still rebuilds because that's how `prepare-prod-service-in` wrote the workflow before runtime config existed.

Today's release flow:

```
   push to main              release published (vX.Y.Z)
        │                            │
        ▼                            ▼
  docker build #1              docker build #2
  ↓ same source ↓              ↓ same source ↓
  dev AR :latest,:sha,:main    prod AR :vX.Y.Z,:sha
  (mutable)                    (immutable per
                                prod-image-tag-immutability)

  IAM: github-actions@dev      IAM: github-actions@prod
       writer on dev AR             writer on prod AR
  WIF: dev environment         WIF: prod environment
```

Both builds consume identical inputs (no env-specific build-args per the post-Phase-1 Dockerfile). Their output digests differ only due to timestamp non-determinism in dependency resolution and image layering. The prod build adds ~1–2 min to the release pipeline for zero functional benefit.

Constraints that shape this design:

- **`prod-image-tag-immutability`**: AR repos in `liverty-music-prod` have `dockerConfig.immutableTags: true`. Re-pointing an existing tag returns HTTP 409. The retag flow MUST only ever write new tags (which is exactly what each release does).
- **`prod-image-pipeline` cluster-SA prohibition**: prod cluster SAs forbid cross-project AR grants. The rule's scenarios name `gke-node@liverty-music-prod` and `backend-app@liverty-music-prod` — cluster identities — but the requirement text could be read as covering all prod SAs. CI SAs are ephemeral (active only during a Workflow run) so the cross-project blast radius is structurally different.
- **GitHub Actions Workload Identity**: each env has its own `github-actions` SA pinned to its own project. The job-level `environment:` selector already picks the prod SA for release events.
- **Backend symmetry**: same architecture, 4-image matrix. Out of scope here; tracked as a follow-up.

## Goals / Non-Goals

**Goals:**
- Eliminate the second `docker build` on the prod release path.
- Guarantee byte-identical `liverty-music-dev/frontend/web-app:<sha>` == `liverty-music-prod/frontend/web-app:<sha>` digest equality.
- Surface a clear failure mode at release time if the dev AR `:<sha>` isn't ready (no silent fallback to "build it anyway").
- Keep the IAM grant scoped: repo-level, one direction (prod CI → dev AR read), no project-wide grants.
- Preserve all current invariants: release-only trigger, prod-AR-only push, immutable semver tags, post-deploy smoke gate.

**Non-Goals:**
- **Backend retag**: same opportunity, different blast radius (4 images, 4× tag-ops); separate change.
- **Removing `cache-from: type=gha` on the dev path**: dev path keeps its current build behavior; only the release path changes.
- **Bit-reproducible builds**: not pursued. Dev produces one canonical bytes; prod just inherits them. Reproducibility tooling (`diffoscope`, SOURCE_DATE_EPOCH) is decoupled and stays out of scope.
- **Re-tagging historical prod images** (v1.0.0, v1.0.1): forward-only. Existing prod tags stay as they are.

## Decisions

### D1. Retag tool: `crane copy`

**Chosen**: `crane copy <dev-AR-FQDN>@<digest> <prod-AR-FQDN>:<tag>` — `crane` is `google/go-containerregistry`'s OCI-registry CLI, installed via `imjasonh/setup-crane@v0.4`.

**Alternatives considered**:
- `gcloud artifacts docker tags add`: initial choice; rejected after implementation. The command name is misleading — despite presenting `<source> <destination>` arguments, the API only **renames a tag within a single repository**. Cross-repository or cross-project copy returns `ERROR: Image <src-FQDN> does not match image <dst-FQDN>` because the API resolves the target image by matching the source's repo path against the destination's repo path, and they must be byte-equal. Verified live on v1.0.2 release run #26025105562. The argument shape suggested registry-to-registry copy was supported; that is not the case.
- `gcrane copy`: rejected for surprising tooling-availability reasons. `gcrane` is a GCR-specific convenience wrapper from the same `google/go-containerregistry` repo, but the standard `imjasonh/setup-crane` action installs only the generic `crane` binary, not its `gcrane` sibling. Verified live on v1.0.2 release run #26025721319 (`gcrane: command not found`). Sourcing `gcrane` separately would require a custom install step; `crane` is functionally equivalent for AR (which speaks the OCI registry protocol) so there is no payoff.
- `skopeo copy`: registry-to-registry first-class citizen. Equivalent capability to `crane copy`; rejected only because `crane` was already in scope as the canonical Google-published toolchain for AR-resident workflows. Re-evaluatable if `crane` ever lags AR feature support.
- `docker pull && docker tag && docker push`: redundant — materializes the image locally for no reason. Rejected.

`crane copy` reads its auth from `~/.docker/config.json` credential helpers, NOT from `GOOGLE_APPLICATION_CREDENTIALS` directly. The release path therefore runs `gcloud auth configure-docker <region>-docker.pkg.dev` (already on the dev push path; now shared with the release path) so the gcloud credential helper is registered. Without it `crane` falls back to anonymous and the prod-AR write returns HTTP 403.

The retag invocation is two calls (one per tag — `:vX.Y.Z` and `:<sha>`). Within the same AR region `crane copy` uses cross-repo blob mounting (a server-side OCI primitive): the destination registry references the source's existing blobs by digest rather than re-uploading them, so only manifest objects (a few KB each) actually transfer. Total wall-clock ~10s for both calls.

**Historical note** — the original D1 chose `gcloud artifacts docker tags add` on the (incorrect) premise that gcloud's API supported cross-repository copy. That assumption was inherited from the command's misleading name and not validated against a live cross-project test before the proposal merged. The corrective sequence is preserved as PRs #361 (gcloud-tags-add, failed), #362 (gcrane, failed), #363 (crane, succeeded). Future spec changes touching registry primitives SHOULD include a smoke step against a non-trivial source/destination pair before merging the contract.

### D2. IAM model: scoped reader on dev AR for prod CI SA

**Chosen**: Add `gcp.artifactregistry.RepositoryIamMember` granting `roles/artifactregistry.reader` to `github-actions@liverty-music-prod.iam.gserviceaccount.com` on `projects/liverty-music-dev/locations/asia-northeast2/repositories/frontend`. Repo-level, one direction.

**Alternatives considered**:
- **Two-step WIF auth in CI**: authenticate first to dev WIF, pull the manifest, then re-authenticate to prod WIF and push. No IAM change required. Rejected — needlessly complex workflow (two `google-github-actions/auth@v2` invocations, careful credential scoping between steps), and `gcloud auth configure-docker` doesn't have great ergonomics for switching identities mid-job.
- **Project-level reader grant**: `roles/artifactregistry.reader` on `liverty-music-dev` project. Rejected — overscoped. Repo-level binding limits blast radius to the one repo the CI actually needs.
- **Granting prod SA writer on dev AR (so it could "promote in place" if we ever wanted that)**: rejected. No use case; expanded blast radius for zero benefit.

The cluster-SA prohibition in `prod-image-pipeline` is the closest precedent against cross-project grants. Its scenarios name cluster SAs explicitly. We resolve the tension by tightening that rule's language (named cluster SAs, not all prod SAs) and adding a complementary CI-SA carve-out spec requirement. The carve-out's rationale: CI SAs hold no persistent runtime privilege, can't be exfiltrated from a running cluster, and the WIF binding limits impersonation to a specific GitHub repo's Actions context.

### D3. Release-time guard: dev AR digest must exist

**Chosen**: Before the retag step, resolve the dev AR digest for `github.sha` via:

```bash
DIGEST=$(gcloud artifacts docker images describe \
  asia-northeast2-docker.pkg.dev/liverty-music-dev/frontend/web-app:${GITHUB_SHA} \
  --format='value(image_summary.digest)')
```

If `DIGEST` is empty (tag doesn't exist), the step fails with an explicit error referencing the runbook section that explains the recovery procedure.

**Why the guard is necessary**: a release can be cut on any commit (`gh release create v1.0.2 --target <sha>`). If the operator picks a commit whose dev build hasn't run or failed, retag would silently produce no prod image (or an error from `gcloud` whose meaning isn't obvious to the on-call). The guard turns that into a clear "this commit isn't in dev AR; either wait for the dev build or pick a different commit".

The existing `Verify release commit is on main` step (added in `prepare-prod-service-in`) already constrains release targets to main-reachable commits. The new digest-exists guard is complementary, not redundant: a commit can be on main but its dev build can still have failed (e.g., transient docker hub outage during the dev push), and the digest guard catches that.

### D4. Tag-set on the prod path

**Chosen**: Each release retags TWO tags:
- `:<release-tag>` (e.g., `:v1.0.2`) — the human-readable semver pin used by Kustomize overlays.
- `:<sha>` — the immutable digest-pointer used for incident-response trace.

Both point to the same digest. This matches the current rebuild path's tag-set (`prod-image-pipeline` "Image tags are explicit, never `:latest`" scenario) so Kustomize overlays don't need to know whether the image was built or retagged.

**Alternative considered**: retag only `:<release-tag>`. Rejected — the `:<sha>` tag is useful when an incident requires referencing the prod image by source SHA without parsing the kustomize comment block. Two tag-add calls cost ~10s total; not worth the saving.

### D5. Rollback strategy

If the new retag flow breaks (e.g., AR API quirk we didn't anticipate, IAM grant lag), rollback is **reverting the frontend workflow PR**. The cloud-provisioning IAM grant can stay in place — an unused `RepositoryIamMember` has no operational impact. The previous rebuild flow returns and the next release uses it.

Forward-only after that: if the cause is identified, re-roll the workflow PR with the fix. The IAM grant doesn't need to be re-applied (it's idempotent across the revert window).

## Risks / Trade-offs

- **[Risk] AR API quirk we haven't seen** → Mitigation: D3 guard fails fast on the first release using this flow. Rollback is reverting the workflow PR. The IAM grant is a no-op when unused.
- **[Risk] Cross-project IAM grant drifts to "writer" via human edit or scope creep** → Mitigation: the grant is declared in Pulumi (typed, reviewed in PR), and the spec's CI-SA carve-out requirement explicitly bounds the grant to "reader" + "scoped to one repo". Drift surfaces in PR review.
- **[Risk] An operator cuts a release on a commit whose dev build failed** → Mitigation: D3 guard. Error message references the runbook recovery section.
- **[Risk] `prod-image-tag-immutability` blocks a legitimate rerun (e.g., release tag deleted + re-created at a new commit)** → Mitigation: Already documented in the existing runbook; this change adds a section explaining that the retag flow inherits the same constraint and recovery is "cut a new release tag with a higher semver".
- **[Trade-off] One new cross-project IAM grant** → Spec-level mitigation: the CI-SA carve-out is added as an explicit requirement with a scenario, so future auditors find the rationale instead of treating the grant as a mistake.
- **[Trade-off] Backend doesn't get this benefit yet** → Scope decision (Non-Goals). Tracked as a follow-up.
- **[Trade-off] AR storage saving is small** → ~10–20 MB per release de-duplicated against the dev digest. Not a budget driver; mentioned only for completeness.

## Migration Plan

1. **Specification PR (this change)**: proposal + design + spec delta to `prod-image-pipeline` + tasks. Merge before any infra change to capture the contract.

2. **Cloud-provisioning PR**: Pulumi addition (`RepositoryIamMember`) + runbook section. Open against `cloud-provisioning/main`. Merge triggers automatic `pulumi up --stack dev` via Pulumi Cloud Deployments. **Prod stack is not auto-applied** — operator runs `pulumi up --stack prod` from the Pulumi Cloud console after the PR merges. Verify the new IAM member shows up in `gcloud artifacts repositories get-iam-policy frontend --project=liverty-music-dev --location=asia-northeast2` afterwards.

3. **Frontend PR**: workflow refactor (the release path branch of `push-image.yaml`). Open against `frontend/main`. **Do not merge until step 2's prod `pulumi up` has completed** — otherwise the next release event would fail at the retag step (no AR reader IAM yet).

4. **Cutover test**: cut a release tag (`v1.0.2` or similar — pick the next semver). Watch the `Deploy Frontend` workflow's release-event run. Expected: ~10s for the digest-resolve + tag-add steps, vs ~90s for the prior build-push. Post-deploy-smoke job continues to gate.

5. **Verify in prod AR**: `gcloud artifacts docker images list asia-northeast2-docker.pkg.dev/liverty-music-prod/frontend/web-app --include-tags` shows the new `:v1.0.2` tag pointing at the same digest as the dev AR `:<sha>` for that commit.

6. **Archive this change**: after a clean release-tag run + smoke pass.

## Open Questions

1. **Should the digest-resolve step retry if the dev AR push is in-flight?** A release can theoretically be cut seconds after the merge-to-main, while the dev build is still pushing. The dev push is a few minutes; a simple "wait up to 5 min for the dev :<sha> tag to appear" retry loop would handle the race. → Recommended: yes, retry with bounded wait (5 attempts × 60s). Captured in tasks.md and made a `SHALL` requirement in the spec delta.

2. **Should we add a release-time check that the dev AR digest matches `dist/` we'd build locally?** Would catch the case where the dev image was tampered post-build (extremely unlikely with Workload Identity + AR ACLs, but it's the kind of attestation step a future SBOM-signing change might want). → Out of scope. Listed as a future enhancement in tasks.md §6.2.

3. **Backend retag scope**: do we capture a tracking issue/proposal stub at the same time we ship this, or wait until frontend retag has soaked? → Recommended: wait. Validate the pattern on frontend (one image, simpler workflow) before applying to backend's 4-image matrix.

## Resolved

- **`prod-image-pipeline`'s removed "`:<sha>` permitted" scenario — tombstone or silent drop?** → Tombstone, in round-1 review. The spec delta now has an explicit REMOVED entry with reason + migration. The second REMOVED entry similarly tombstones the orphaned "Prod and dev builds use identical Dockerfile inputs" scenario that the MODIFIED retag flow no longer supports.

- **Dev-path tag set: `:latest,:<sha>` (canonical spec) vs `:latest,:main,:<sha>` (this delta)?** → Verified against `frontend/.github/workflows/push-image.yaml` line 113: the dev push path actually writes `:latest,:<sha>,:main`. The canonical spec was incomplete; this delta's MODIFIED requirement body incidentally corrects the gap. No behavior change to the workflow.
