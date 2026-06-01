## ADDED Requirements

### Requirement: Prod kustomize pin-bumps SHALL be automated via repository_dispatch

After a release path successfully promotes images to prod AR, the originating workflow SHALL trigger an automated update of the prod kustomize pin in `cloud-provisioning` rather than relying on a manually-authored pull request. The backend `deploy.yml` and frontend `push-image.yaml` release paths SHALL emit a GitHub `repository_dispatch` event to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and a `client_payload` of `{ component, tag, sha }`, where `component` is `backend` or `frontend`, `tag` is the release tag (`vX.Y.Z`), and `sha` is `${GITHUB_SHA}`. The dispatch trigger SHALL be the only cross-repo action the release workflows perform. The dispatch credential is the org-owned `liverty-music-ci-bot` GitHub App, which requires `Contents: write` on `cloud-provisioning` (the documented minimum for `repository_dispatch`).

> **Boundary note (revised during implementation — see design D9).** The original design (D1) intended the release workflows to be unable to push to `cloud-provisioning:main`, with the `main` bypass scoped to `github-actions[bot]` only. That proved infeasible: a repository ruleset rejects the global `github-actions` integration as a bypass actor (`422 — must be part of the ruleset source or owner organization`, GitHub-owned), and an organization ruleset (which would accept it) requires a GitHub Team plan (`403` on Free). The `main` bypass actor is therefore the org-owned `ci-bot` App — the same credential the release workflows hold — so a compromised prod release workflow CAN push `cloud-provisioning:main`. This relaxed boundary is accepted and mitigated by: the ci-bot secrets being scoped to the `prod` environment (release events only), the provenance gate (a bump cannot pin a non-existent prod image), and the GitHub Release remaining the human gate. The strict boundary MAY be restored later by introducing a dedicated push-only App (keyed/installed only on `cloud-provisioning`) as the bypass actor.

The dispatch step SHALL run only after the prod-AR retag for that component has succeeded. For the backend's 4-image `fail-fast: false` matrix, the dispatch SHALL be a job gated on the retag job completing successfully (`needs` + `if: <retag>.result == 'success'`), so a partially-failed retag never bumps the pin to a release tag whose prod images are incomplete.

#### Scenario: Backend release dispatches a pin-bump after retag

- **WHEN** a GitHub Release `vX.Y.Z` is published in `liverty-music/backend` and all 4 retag matrix entries succeed
- **THEN** `deploy.yml` SHALL emit a `repository_dispatch` to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and `client_payload: { component: "backend", tag: "vX.Y.Z", sha: "<github.sha>" }`

#### Scenario: Frontend release dispatches a pin-bump after retag

- **WHEN** a GitHub Release `vX.Y.Z` is published in `liverty-music/frontend` and the retag succeeds
- **THEN** `push-image.yaml` SHALL emit a `repository_dispatch` to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and `client_payload: { component: "frontend", tag: "vX.Y.Z", sha: "<github.sha>" }`

#### Scenario: A partially-failed backend retag SHALL NOT dispatch

- **WHEN** a GitHub Release is published in `liverty-music/backend` and at least one of the 4 retag matrix entries fails
- **THEN** the dispatch step SHALL NOT run
- **AND** no `bump-prod-pin` event SHALL be emitted to `cloud-provisioning`

#### Scenario: Dispatch credential is the org-owned ci-bot App, prod-env scoped

- **WHEN** inspecting the secrets/permissions used by the dispatch step in `deploy.yml` and `push-image.yaml`
- **THEN** the credential SHALL be the `liverty-music-ci-bot` GitHub App (App id + private key), with `Contents: write` (the documented minimum for the dispatches API)
- **AND** those secrets SHALL be scoped to the backend/frontend `prod` GitHub Environments (release events), NOT org-wide
- **AND** because that same App is the `cloud-provisioning:main` ruleset bypass actor (design D9), a release workflow CAN push `main`; this relaxed boundary SHALL be mitigated by the prod-environment scoping, the provenance gate, and the Release-as-human-gate (it SHALL NOT rely on the token being unable to push `main`)

### Requirement: A cloud-provisioning workflow SHALL apply the prod pin-bump on dispatch

`cloud-provisioning` SHALL contain a workflow (`bump-prod-pin.yml`) triggered by `repository_dispatch` of type `bump-prod-pin`. On receipt, for the `component` named in the payload it SHALL rewrite, in `k8s/namespaces/<component>/overlays/prod/kustomization.yaml`, every `images[].newTag` (all 4 entries for `backend`, the single `web-app` entry for `frontend`) and the `labels[].pairs."app.kubernetes.io/version"` value, in lock-step, to the release version. The `newTag` SHALL be the `vX.Y.Z` form; the version label SHALL be the bare semver (no leading `v`). The inline source-commit trailer comment after each `newTag` SHALL be updated to the payload `sha`.

Before editing, the workflow SHALL validate the payload: `component` SHALL be one of `backend | frontend` and `tag` SHALL match `^v[0-9]+\.[0-9]+\.[0-9]+$`. Shape validation alone is insufficient — the workflow SHALL ALSO verify **image provenance** before any edit: for every image of the component (the 4 backend images, or the single `web-app` image) it SHALL confirm the prod-AR image at the target tag exists via `crane manifest asia-northeast2-docker.pkg.dev/liverty-music-prod/<component>/<img>:<tag>`. A missing manifest for any image SHALL abort the run before any file is edited (fail-closed). Because a prod-AR image at `:<tag>` exists only if the release retag wrote it, this provenance gate confirms the tag names a genuine release whose retag completed, and prevents a well-formed-but-bogus or stale tag from corrupting `main` (including the silent-downgrade-to-bogus-tag case).

The workflow SHALL then validate the edited overlay with `kustomize build k8s/namespaces/<component>/overlays/prod` BEFORE committing; a non-zero build SHALL abort the run without pushing. On success it SHALL commit and push directly to `cloud-provisioning:main` using a `liverty-music-ci-bot` GitHub App installation token (the App is the `main` ruleset bypass actor — see design D9; the built-in `GITHUB_TOKEN` / `github-actions[bot]` cannot be a repo-ruleset bypass actor). ArgoCD's existing auto-sync rolls the change out — the workflow SHALL NOT open a pull request.

#### Scenario: Dispatch updates newTag and version label in lock-step

- **WHEN** `bump-prod-pin.yml` receives `{ component: "backend", tag: "v1.4.0", sha: "abc123..." }`
- **THEN** all 4 `images[].newTag` in `k8s/namespaces/backend/overlays/prod/kustomization.yaml` SHALL be set to `v1.4.0`
- **AND** the `app.kubernetes.io/version` label SHALL be set to `1.4.0`
- **AND** each `newTag`'s inline `# commit <sha>` trailer SHALL be updated to `abc123...`

#### Scenario: Missing prod-AR image aborts before any edit

- **WHEN** `bump-prod-pin.yml` receives a well-formed payload whose `tag` has no corresponding prod-AR image (`crane manifest asia-northeast2-docker.pkg.dev/liverty-music-prod/<component>/<img>:<tag>` returns not-found for any image of the component)
- **THEN** the workflow SHALL fail at the provenance step
- **AND** SHALL NOT edit `kustomization.yaml`, commit, or push
- **AND** the failure SHALL occur regardless of which trigger (`repository_dispatch` or the `workflow_dispatch` fallback) delivered the payload

#### Scenario: kustomize build failure aborts before push

- **WHEN** the post-edit `kustomize build k8s/namespaces/<component>/overlays/prod` exits non-zero
- **THEN** the workflow SHALL fail
- **AND** SHALL NOT commit or push any change to `main`

#### Scenario: Successful bump pushes directly to main, no PR

- **WHEN** the edit validates and differs from the current pin
- **THEN** the workflow SHALL commit and push to `cloud-provisioning:main` as the `liverty-music-ci-bot` App
- **AND** SHALL NOT open a pull request
- **AND** ArgoCD SHALL subsequently auto-sync the prod overlay to the new tag

#### Scenario: Bump is idempotent

- **WHEN** `bump-prod-pin.yml` receives a payload whose `tag` already matches every target `newTag` for that component
- **THEN** the workflow SHALL exit successfully without creating a commit or pushing

#### Scenario: Concurrent backend and frontend bumps both land

- **WHEN** a `backend` bump and a `frontend` bump are dispatched within seconds of each other
- **THEN** the workflow SHALL serialize the runs (`concurrency` group) and/or rebase-retry the push so that both the backend overlay and the frontend overlay end up bumped on `main`
- **AND** neither bump SHALL be lost to a push rejection

### Requirement: cloud-provisioning main ruleset SHALL allow the ci-bot App to bypass for the pin-bump push

To permit `bump-prod-pin.yml` to push directly to `cloud-provisioning:main`, the repository's `main` ruleset SHALL list the org-owned `liverty-music-ci-bot` GitHub App as a bypass actor (`actorType: Integration`, covering both the pull-request requirement and the "require branches up to date" requirement). The bypass actor SHALL NOT be the built-in `github-actions[bot]` — a repository ruleset rejects the global `github-actions` integration ("must be part of the ruleset source or owner organization"), and an org ruleset (which would accept it) requires a GitHub Team plan; an org-owned App is the available mechanism. No human identity and no long-lived personal access token SHALL be added as a bypass actor.

#### Scenario: ci-bot push to main is accepted

- **WHEN** `bump-prod-pin.yml` pushes a validated pin-bump commit to `cloud-provisioning:main` authenticated as a `liverty-music-ci-bot` installation token
- **THEN** the ruleset SHALL accept the push without requiring a pull request or an up-to-date branch

#### Scenario: Human pushes still obey the ruleset

- **WHEN** a human (or any non-ci-bot actor, including `github-actions[bot]`) attempts to push directly to `cloud-provisioning:main`
- **THEN** the ruleset SHALL continue to require a pull request and the up-to-date check (the bypass SHALL be scoped to the `liverty-music-ci-bot` App only)

### Requirement: The manual pin-bump fallback SHALL be admin-gated

`bump-prod-pin.yml` SHALL provide a `workflow_dispatch` fallback (manual `component` + `tag` + `sha` inputs) for dropped-dispatch recovery. Because a `workflow_dispatch` run mints a ci-bot token and pushes to `main` as the `liverty-music-ci-bot` App — the ruleset bypass actor — and is reachable by any contributor with `actions: write`, the bump job SHALL require admin approval via a GitHub Environment (e.g. `prod-pin`) with a required-reviewer rule **on the manual trigger only**. Since Environment protection rules have no trigger-type filter (they apply to every job referencing the environment), the workflow SHALL bind the environment conditionally — `environment: ${{ github.event_name == 'workflow_dispatch' && 'prod-pin' || '' }}` (or an equivalent two-workflow split) — so that `repository_dispatch` runs do NOT enter `prod-pin` and proceed unattended, while `workflow_dispatch` runs enter `prod-pin` and pause for approval. This fallback SHALL be documented as a privileged admin-only recovery operation, not a routine path. The provenance gate (see "A cloud-provisioning workflow SHALL apply the prod pin-bump on dispatch") applies to the fallback identically, so even an approved manual run cannot pin a tag whose prod image does not exist.

#### Scenario: Manual fallback requires admin approval

- **WHEN** a contributor triggers `bump-prod-pin.yml` via `workflow_dispatch`
- **THEN** the bump job's `environment:` SHALL resolve to `prod-pin` (because `github.event_name == 'workflow_dispatch'`)
- **AND** the run SHALL pause for the `prod-pin` Environment's required-reviewer approval before the bump job executes
- **AND** an unapproved run SHALL NOT edit or push any change to `main`

#### Scenario: Release path is not gated by the reviewer rule

- **WHEN** the workflow is triggered by a `repository_dispatch` of type `bump-prod-pin` from the release path
- **THEN** the bump job's `environment:` SHALL resolve to empty (not `prod-pin`), so no required-reviewer rule applies
- **AND** the bump SHALL proceed unattended (no manual approval), subject to the payload-validation and provenance gates
