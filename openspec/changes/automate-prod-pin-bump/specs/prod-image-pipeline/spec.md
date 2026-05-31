## ADDED Requirements

### Requirement: Prod kustomize pin-bumps SHALL be automated via repository_dispatch

After a release path successfully promotes images to prod AR, the originating workflow SHALL trigger an automated update of the prod kustomize pin in `cloud-provisioning` rather than relying on a manually-authored pull request. The backend `deploy.yml` and frontend `push-image.yaml` release paths SHALL emit a GitHub `repository_dispatch` event to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and a `client_payload` of `{ component, tag, sha }`, where `component` is `backend` or `frontend`, `tag` is the release tag (`vX.Y.Z`), and `sha` is `${GITHUB_SHA}`. The release workflows SHALL NOT hold any credential that can write to `cloud-provisioning`'s contents directly — the dispatch trigger is the only cross-repo action they perform.

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

#### Scenario: Release workflows hold no cloud-provisioning write credential

- **WHEN** inspecting the secrets/permissions used by the dispatch step in `deploy.yml` and `push-image.yaml`
- **THEN** the credential SHALL be limited to triggering the `repository_dispatch` (it SHALL NOT grant direct write to `cloud-provisioning`'s `contents` such that the release job itself could push manifests)

### Requirement: A cloud-provisioning workflow SHALL apply the prod pin-bump on dispatch

`cloud-provisioning` SHALL contain a workflow (`bump-prod-pin.yml`) triggered by `repository_dispatch` of type `bump-prod-pin`. On receipt, for the `component` named in the payload it SHALL rewrite, in `k8s/namespaces/<component>/overlays/prod/kustomization.yaml`, every `images[].newTag` (all 4 entries for `backend`, the single `web-app` entry for `frontend`) and the `labels[].pairs."app.kubernetes.io/version"` value, in lock-step, to the release version. The `newTag` SHALL be the `vX.Y.Z` form; the version label SHALL be the bare semver (no leading `v`). The inline source-commit trailer comment after each `newTag` SHALL be updated to the payload `sha`.

The workflow SHALL validate the edited overlay with `kustomize build k8s/namespaces/<component>/overlays/prod` BEFORE committing; a non-zero build SHALL abort the run without pushing. On success it SHALL commit and push directly to `cloud-provisioning:main` using the workflow's own `GITHUB_TOKEN` (the `github-actions[bot]` actor). ArgoCD's existing auto-sync rolls the change out — the workflow SHALL NOT open a pull request.

#### Scenario: Dispatch updates newTag and version label in lock-step

- **WHEN** `bump-prod-pin.yml` receives `{ component: "backend", tag: "v1.4.0", sha: "abc123..." }`
- **THEN** all 4 `images[].newTag` in `k8s/namespaces/backend/overlays/prod/kustomization.yaml` SHALL be set to `v1.4.0`
- **AND** the `app.kubernetes.io/version` label SHALL be set to `1.4.0`
- **AND** each `newTag`'s inline `# commit <sha>` trailer SHALL be updated to `abc123...`

#### Scenario: kustomize build failure aborts before push

- **WHEN** the post-edit `kustomize build k8s/namespaces/<component>/overlays/prod` exits non-zero
- **THEN** the workflow SHALL fail
- **AND** SHALL NOT commit or push any change to `main`

#### Scenario: Successful bump pushes directly to main, no PR

- **WHEN** the edit validates and differs from the current pin
- **THEN** the workflow SHALL commit and push to `cloud-provisioning:main` as `github-actions[bot]`
- **AND** SHALL NOT open a pull request
- **AND** ArgoCD SHALL subsequently auto-sync the prod overlay to the new tag

#### Scenario: Bump is idempotent

- **WHEN** `bump-prod-pin.yml` receives a payload whose `tag` already matches every target `newTag` for that component
- **THEN** the workflow SHALL exit successfully without creating a commit or pushing

#### Scenario: Concurrent backend and frontend bumps both land

- **WHEN** a `backend` bump and a `frontend` bump are dispatched within seconds of each other
- **THEN** the workflow SHALL serialize the runs (`concurrency` group) and/or rebase-retry the push so that both the backend overlay and the frontend overlay end up bumped on `main`
- **AND** neither bump SHALL be lost to a push rejection

### Requirement: cloud-provisioning branch protection SHALL allow the bot to bypass for the pin-bump push

To permit `bump-prod-pin.yml` to push directly to `cloud-provisioning:main`, the repository's branch protection / ruleset SHALL list `github-actions[bot]` as a bypass actor for the `main` branch (covering both the pull-request requirement and the "require branches up to date" requirement). No human identity and no long-lived personal access token SHALL be added as a bypass actor for this purpose.

#### Scenario: Bot push to main is accepted

- **WHEN** `bump-prod-pin.yml` pushes a validated pin-bump commit to `cloud-provisioning:main` as `github-actions[bot]`
- **THEN** branch protection SHALL accept the push without requiring a pull request or an up-to-date branch

#### Scenario: Human pushes still obey branch protection

- **WHEN** a human (non-bot) attempts to push directly to `cloud-provisioning:main`
- **THEN** branch protection SHALL continue to require a pull request and the up-to-date check (the bypass SHALL be scoped to `github-actions[bot]` only)
