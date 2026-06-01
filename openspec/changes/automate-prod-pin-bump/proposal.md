## Why

Promoting a release to prod today is a two-gate process: cutting the GitHub Release retags the dev image into prod AR, but the image only rolls out after a human opens and merges a "pin-bump" PR in `cloud-provisioning` that updates `newTag` + the `app.kubernetes.io/version` label. For a solo-developer project this PR adds no review value — the deliberate decision already happened when the Release was cut — yet it costs manual toil on every release and, under the "require branches up to date" rule, a rebase dance. We want to keep a *machine* gate (manifest validation) while removing the *human* gate, so a published Release flows straight through to a prod rollout.

## What Changes

- The backend (`deploy.yml`) and frontend (`push-image.yaml`) release paths SHALL, **after** the prod-AR retag succeeds, emit a GitHub `repository_dispatch` event to `liverty-music/cloud-provisioning` carrying `{ component, tag, sha }` (component ∈ `backend | frontend`).
- A **new** `cloud-provisioning` workflow (`bump-prod-pin.yml`) SHALL receive that dispatch and, for the named component, rewrite the prod overlay's `images[].newTag` (all 4 entries for backend, the single `web-app` entry for frontend) and the `app.kubernetes.io/version` label to the new release version, in lock-step.
- The bump workflow SHALL **validate** `kustomize build` of the affected prod overlay before committing; a build failure aborts the push (replacing the CI gate the manual PR used to provide).
- The bump workflow SHALL commit and push **directly to `cloud-provisioning:main`** as the org-owned `liverty-music-ci-bot` App (minting an installation token), bypassing the manual-PR step. ArgoCD's existing auto-sync then rolls the change out. (The built-in `GITHUB_TOKEN` / `github-actions[bot]` cannot be a repo-ruleset bypass actor — see design D9.)
- The bump SHALL be **idempotent** (no-op if `newTag` already equals the target) and SHALL **rebase-retry** on push rejection to tolerate a backend+frontend release landing close together.
- The manual pin-bump PR ceases to be the rollout gate. The Release act becomes the single human gate; the dispatch → validate → push chain is fully automated.
- Cross-repo auth uses a short-lived `liverty-music-ci-bot` GitHub App installation token (no long-lived PAT). The same App is the `main` ruleset bypass actor, so — unlike the original intent (design D1) — the release-held credential CAN push `cloud-provisioning:main`; this relaxed boundary is mitigated by prod-environment secret scoping, the provenance gate, and Release-as-gate (design D9).

## Capabilities

### New Capabilities
<!-- none — this extends the existing prod image pipeline rather than introducing a new capability surface -->

### Modified Capabilities
- `prod-image-pipeline`: Add a requirement that prod kustomize pin-bumps are automated via `repository_dispatch` from the release workflows to a `cloud-provisioning` bump workflow (validate-then-push-to-main), replacing the manual pin-bump PR as the rollout gate. The existing "Prod kustomize overlays SHALL pin image URIs to prod-AR paths" and the release-retag requirements are unchanged; this adds the *bump mechanism* on top of them.

## Impact

- **`liverty-music/backend`** — `deploy.yml`: append a `repository_dispatch`-emitting step to the release path, gated on all 4 retag matrix entries succeeding.
- **`liverty-music/frontend`** — `push-image.yaml`: append the same dispatch step to the release path; optionally chain the existing prod smoke (`workflow_dispatch` → automatic) after rollout.
- **`liverty-music/cloud-provisioning`** — new `.github/workflows/bump-prod-pin.yml`; the prod overlays under `k8s/namespaces/{backend,frontend}/overlays/prod/kustomization.yaml` become CI-written for the `newTag` + version-label fields.
- **GitHub settings** — `cloud-provisioning:main` is governed by a repository ruleset whose sole bypass actor is the `liverty-music-ci-bot` App (covering the PR + up-to-date requirements). The ci-bot App credential is provisioned as backend/frontend `prod` environment secrets (dispatch) and cloud-provisioning repository secrets (push).
- **Operational** — prod rollout latency drops from "manual PR + rebase + merge" to "dispatch + kustomize validate + push" (seconds). Rollback remains `git revert` of the bump commit. ArgoCD auto-sync behavior is unchanged.
- **Risk surface** — a buggy edit could push a broken manifest to prod; mitigated by the mandatory `kustomize build` validation gate and idempotency. ArgoCD still self-heals/prunes as before.
