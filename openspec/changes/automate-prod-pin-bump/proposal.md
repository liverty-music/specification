## Why

Promoting a release to prod today is a two-gate process: cutting the GitHub Release retags the dev image into prod AR, but the image only rolls out after a human opens and merges a "pin-bump" PR in `cloud-provisioning` that updates `newTag` + the `app.kubernetes.io/version` label. For a solo-developer project this PR adds no review value — the deliberate decision already happened when the Release was cut — yet it costs manual toil on every release and, under the "require branches up to date" rule, a rebase dance. We want to keep a *machine* gate (manifest validation) while removing the *human* gate, so a published Release flows straight through to a prod rollout.

## What Changes

- The backend (`deploy.yml`) and frontend (`push-image.yaml`) release paths SHALL, **after** the prod-AR retag succeeds, emit a GitHub `repository_dispatch` event to `liverty-music/cloud-provisioning` carrying `{ component, tag, sha }` (component ∈ `backend | frontend`).
- A **new** `cloud-provisioning` workflow (`bump-prod-pin.yml`) SHALL receive that dispatch and, for the named component, rewrite the prod overlay's `images[].newTag` (all 4 entries for backend, the single `web-app` entry for frontend) and the `app.kubernetes.io/version` label to the new release version, in lock-step.
- The bump workflow SHALL **validate** `kustomize build` of the affected prod overlay before committing; a build failure aborts the push (replacing the CI gate the manual PR used to provide).
- The bump workflow SHALL commit and push **directly to `cloud-provisioning:main`** using its own `GITHUB_TOKEN` (the `github-actions[bot]` actor), bypassing the manual-PR step. ArgoCD's existing auto-sync then rolls the change out.
- The bump SHALL be **idempotent** (no-op if `newTag` already equals the target) and SHALL **rebase-retry** on push rejection to tolerate a backend+frontend release landing close together.
- The manual pin-bump PR ceases to be the rollout gate. The Release act becomes the single human gate; the dispatch → validate → push chain is fully automated.
- Cross-repo auth uses `repository_dispatch` specifically so the release workflows hold **no** write credential to `cloud-provisioning` — the bump workflow pushes to *its own* repo with the built-in token. No long-lived PAT is introduced.

## Capabilities

### New Capabilities
<!-- none — this extends the existing prod image pipeline rather than introducing a new capability surface -->

### Modified Capabilities
- `prod-image-pipeline`: Add a requirement that prod kustomize pin-bumps are automated via `repository_dispatch` from the release workflows to a `cloud-provisioning` bump workflow (validate-then-push-to-main), replacing the manual pin-bump PR as the rollout gate. The existing "Prod kustomize overlays SHALL pin image URIs to prod-AR paths" and the release-retag requirements are unchanged; this adds the *bump mechanism* on top of them.

## Impact

- **`liverty-music/backend`** — `deploy.yml`: append a `repository_dispatch`-emitting step to the release path, gated on all 4 retag matrix entries succeeding.
- **`liverty-music/frontend`** — `push-image.yaml`: append the same dispatch step to the release path; optionally chain the existing prod smoke (`workflow_dispatch` → automatic) after rollout.
- **`liverty-music/cloud-provisioning`** — new `.github/workflows/bump-prod-pin.yml`; the prod overlays under `k8s/namespaces/{backend,frontend}/overlays/prod/kustomization.yaml` become CI-written for the `newTag` + version-label fields.
- **GitHub settings** — `cloud-provisioning` branch protection / ruleset MUST add `github-actions[bot]` as a bypass actor for direct `main` push (and thereby the up-to-date requirement). No new secrets.
- **Operational** — prod rollout latency drops from "manual PR + rebase + merge" to "dispatch + kustomize validate + push" (seconds). Rollback remains `git revert` of the bump commit. ArgoCD auto-sync behavior is unchanged.
- **Risk surface** — a buggy edit could push a broken manifest to prod; mitigated by the mandatory `kustomize build` validation gate and idempotency. ArgoCD still self-heals/prunes as before.
