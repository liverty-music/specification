## Why

Prod kustomize overlays currently pin container images by 40-character commit SHA tags (e.g., `newTag: 3bc2dada3c4cd06c218235eb7fe21ad638e29bf3`), which is opaque to operators inspecting `kubectl get pod -o yaml | grep image:` or reading the manifest at a glance — they cannot tell which release version is running in prod without a registry round-trip. Switching the manifest to a semantic version tag (`newTag: v1.0.0`) restores at-a-glance readability, but raw semver tags are mutable by default in any Docker registry: anyone with AR write IAM could re-point `:v1.0.0` to a different image digest, breaking the GitOps reproducibility guarantee. GCP Artifact Registry's per-repository `dockerConfig.immutableTags: true` flag closes that gap by rejecting tag-overwrite attempts at the API level, giving the readability of semver + the immutability of digest-pinning in a single combined contract.

## What Changes

- Enable `dockerConfig.immutableTags = true` on the two prod Artifact Registry repositories in `liverty-music-prod`: `backend` (Docker) and `frontend` (Docker). Dev AR repos are NOT modified — ArgoCD Image Updater on dev needs the ability to overwrite `:latest`.
- Switch the prod kustomize overlays from commit-SHA `newTag:` to semver `newTag:`:
  - `cloud-provisioning/k8s/namespaces/backend/overlays/prod/kustomization.yaml` (4 images: server, consumer, concert-discovery, artist-image-sync)
  - `cloud-provisioning/k8s/namespaces/frontend/overlays/prod/kustomization.yaml` (1 image: web-app)
- Preserve commit SHA in an inline comment on each `newTag:` entry, for incident-response trace from manifest → exact source commit without hitting AR.
- Add `app.kubernetes.io/version: "<release-tag>"` Recommended Label patch to every prod Deployment + CronJob so the version is visible on Pod/Deployment objects for Prometheus relabeling and log enrichment.
- Document the policy in a new runbook (`cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md`) covering: which envs use immutable tags vs `:latest`, how to bump on release, and how to recover from accidental tag-overwrite attempts.

## Capabilities

### New Capabilities
- `prod-image-tag-immutability`: contracts the policy that prod AR repositories enforce tag immutability at the API level, prod kustomize overlays pin to immutable semver tags (not commit SHAs and not `:latest`), and the `app.kubernetes.io/version` Recommended Label propagates the release version onto every prod workload. Scope is intentionally narrow to prod — dev / staging are out of scope.

### Modified Capabilities
None. The companion change `prepare-prod-service-in` (active, not yet archived) already ADDS the `prod-image-pipeline` capability with broader rules ("tags SHALL be `:vX.Y.Z` or `:<sha>`, never `:latest`"). This change deliberately authors a SEPARATE capability rather than MODIFYING `prod-image-pipeline` for two reasons: (a) `prod-image-pipeline` does not yet exist in `openspec/specs/` (only in the in-flight change's delta), so MODIFIED would be unenforceable until `prepare-prod-service-in` archives; (b) tag immutability is a distinct concern from the pipeline-shape contract (registry-side policy + manifest convention vs. build/push pipeline), and conflating them would couple future evolution of both.

## Impact

- **Affected repos**: `liverty-music/cloud-provisioning` only (Pulumi src + kustomize manifests + new runbook). No proto / backend / frontend changes.
- **Affected systems**:
  - GCP Artifact Registry repos `liverty-music-prod/backend` and `liverty-music-prod/frontend` — `immutableTags` flag flips from `false` (default) to `true`.
  - ArgoCD prod cluster — Deployment / CronJob `image:` and `metadata.labels` fields change; ArgoCD will detect the diff and perform a no-op rollout (image bytes unchanged, only tag reference + label).
- **Affected workflows**:
  - GHA release builds for backend + frontend continue pushing both `:vX.Y.Z` and `:<sha>` tags — no workflow change. AR will reject any second-push attempt of an existing tag with 409 Conflict; this is the desired enforcement.
- **Affected operators**:
  - On release: bump `newTag: v1.0.0` → `newTag: v1.0.1` in prod overlays + update commit-SHA comment. Same process as today but with a more readable diff.
  - On accidental re-tag attempt: AR rejects; recovery is to cut a new patch version, not to fix the existing tag.
- **Sequencing**: independent of `prepare-prod-service-in`. Can apply after `prepare-prod-service-in` §1-§10 are complete (the v1.0.0 release artifacts must exist in prod AR before this change rewrites `newTag:` to point at them by semver name).
