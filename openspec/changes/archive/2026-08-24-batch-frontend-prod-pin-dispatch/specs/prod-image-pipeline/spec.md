## MODIFIED Requirements

### Requirement: Prod kustomize pin-bumps SHALL be automated via repository_dispatch

After a release path successfully promotes images to prod AR, the originating workflow SHALL trigger an automated update of the prod kustomize pin in `cloud-provisioning` rather than relying on a manually-authored pull request. The backend `deploy.yml` and frontend `push-image.yaml` release paths SHALL emit a GitHub `repository_dispatch` event to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and a `client_payload` of `{ component, tag, sha }`, where `component` is `backend` or `frontend`, `tag` is the release tag (`vX.Y.Z`), and `sha` is `${GITHUB_SHA}`. The dispatch trigger SHALL be the only cross-repo action the release workflows perform. The dispatch credential is the org-owned `liverty-music-ci-bot` GitHub App, which requires `Contents: write` on `cloud-provisioning` (the documented minimum for `repository_dispatch`).

A release SHALL emit exactly **one** `bump-prod-pin` dispatch per originating repository, naming a single `component`. `backend` covers all four backend images in that one dispatch; `frontend` covers all frontend prod bundles — `fan-web`, `admin-console-web`, and `organizer-console-web` — in that one dispatch. A release path SHALL NOT fan out into multiple per-bundle dispatches (no `frontend-admin` / `frontend-organizer` component values): all bundles of one release are pinned as a single atomic unit. This keeps the dispatch count independent of how many bundles a repository ships, so the cross-repo pin update is one operation whose bundles either all land together or not at all.

> **Boundary note (revised during implementation — see design D9).** The original design (D1) intended the release workflows to be unable to push to `cloud-provisioning:main`, with the `main` bypass scoped to `github-actions[bot]` only. That proved infeasible: a repository ruleset rejects the global `github-actions` integration as a bypass actor (`422 — must be part of the ruleset source or owner organization`, GitHub-owned), and an organization ruleset (which would accept it) requires a GitHub Team plan (`403` on Free). The `main` bypass actor is therefore the org-owned `ci-bot` App — the same credential the release workflows hold — so a compromised prod release workflow CAN push `cloud-provisioning:main`. This relaxed boundary is accepted and mitigated by: the ci-bot secrets being scoped to the `prod` environment (release events only), the provenance gate (a bump cannot pin a non-existent prod image), and the GitHub Release remaining the human gate. The strict boundary MAY be restored later by introducing a dedicated push-only App (keyed/installed only on `cloud-provisioning`) as the bypass actor.

The dispatch step SHALL run only after the prod-AR retag for that component has succeeded. For the backend's 4-image `fail-fast: false` matrix, the dispatch SHALL be a job gated on the retag job completing successfully (`needs` + `if: <retag>.result == 'success'`), so a partially-failed retag never bumps the pin to a release tag whose prod images are incomplete. For the frontend's three independent bundle build jobs (`fan-web`, `admin-console-web`, `organizer-console-web`), the single dispatch SHALL likewise be all-or-nothing: it SHALL be emitted only when **all three** bundle retags succeed, so the frontend release is never pinned with an incomplete set of prod images.

#### Scenario: Backend release dispatches a pin-bump after retag

- **WHEN** a GitHub Release `vX.Y.Z` is published in `liverty-music/backend` and all 4 retag matrix entries succeed
- **THEN** `deploy.yml` SHALL emit a `repository_dispatch` to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and `client_payload: { component: "backend", tag: "vX.Y.Z", sha: "<github.sha>" }`

#### Scenario: Frontend release dispatches a pin-bump after retag

- **WHEN** a GitHub Release `vX.Y.Z` is published in `liverty-music/frontend` and the `fan-web`, `admin-console-web`, and `organizer-console-web` retags all succeed
- **THEN** `push-image.yaml` SHALL emit exactly **one** `repository_dispatch` to `liverty-music/cloud-provisioning` with `event_type: bump-prod-pin` and `client_payload: { component: "frontend", tag: "vX.Y.Z", sha: "<github.sha>" }`
- **AND** it SHALL NOT emit any `frontend-admin` or `frontend-organizer` component dispatch

#### Scenario: A partially-failed backend retag SHALL NOT dispatch

- **WHEN** a GitHub Release is published in `liverty-music/backend` and at least one of the 4 retag matrix entries fails
- **THEN** the dispatch step SHALL NOT run
- **AND** no `bump-prod-pin` event SHALL be emitted to `cloud-provisioning`

#### Scenario: A partially-failed frontend retag SHALL NOT dispatch

- **WHEN** a GitHub Release is published in `liverty-music/frontend` and at least one of the `fan-web` / `admin-console-web` / `organizer-console-web` retags fails
- **THEN** the dispatch step SHALL NOT run
- **AND** no `bump-prod-pin` event SHALL be emitted to `cloud-provisioning` (no bundle is pinned rather than pinning a partial set)

#### Scenario: Dispatch credential is the org-owned ci-bot App, prod-env scoped

- **WHEN** inspecting the secrets/permissions used by the dispatch step in `deploy.yml` and `push-image.yaml`
- **THEN** the credential SHALL be the `liverty-music-ci-bot` GitHub App (App id + private key), with `Contents: write` (the documented minimum for the dispatches API)
- **AND** those secrets SHALL be scoped to the backend/frontend `prod` GitHub Environments (release events), NOT org-wide
- **AND** because that same App is the `cloud-provisioning:main` ruleset bypass actor (design D9), a release workflow CAN push `main`; this relaxed boundary SHALL be mitigated by the prod-environment scoping, the provenance gate, and the Release-as-human-gate (it SHALL NOT rely on the token being unable to push `main`)

### Requirement: A cloud-provisioning workflow SHALL apply the prod pin-bump on dispatch

`cloud-provisioning` SHALL contain a workflow (`bump-prod-pin.yml`) triggered by `repository_dispatch` of type `bump-prod-pin`. On receipt, for the `component` named in the payload it SHALL rewrite, in `k8s/namespaces/<component>/overlays/prod/kustomization.yaml`, every `images[].newTag` (all 4 entries for `backend`; the three frontend bundle entries — `fan-web`, `admin-console-web`, `organizer-console-web` — for `frontend`) and the `labels[].pairs."app.kubernetes.io/version"` value, in lock-step, to the release version. The `newTag` SHALL be the `vX.Y.Z` form; the version label SHALL be the bare semver (no leading `v`). The inline source-commit trailer comment after each `newTag` SHALL be updated to the payload `sha`. All of a component's image entries SHALL be rewritten and committed as a **single commit** (one edit pass, one `kustomize build`, one push), so a component's bundles never land in prod as separate commits or a transient mixed-version state.

Before editing, the workflow SHALL validate the payload: `component` SHALL be one of `backend | frontend` and `tag` SHALL match `^v[0-9]+\.[0-9]+\.[0-9]+$`. Shape validation alone is insufficient — the workflow SHALL ALSO verify **image provenance** before any edit: for every image of the component (the 4 backend images, or the three frontend bundle images) it SHALL confirm the prod-AR image at the target tag exists via `crane manifest asia-northeast2-docker.pkg.dev/liverty-music-prod/<component>/<img>:<tag>`. A missing manifest for any image SHALL abort the run before any file is edited (fail-closed). Because a prod-AR image at `:<tag>` exists only if the release retag wrote it, this provenance gate confirms the tag names a genuine release whose retag completed, and prevents a well-formed-but-bogus or stale tag from corrupting `main` (including the silent-downgrade-to-bogus-tag case).

The workflow SHALL then validate the edited overlay with `kustomize build k8s/namespaces/<component>/overlays/prod` BEFORE committing; a non-zero build SHALL abort the run without pushing. On success it SHALL commit and push directly to `cloud-provisioning:main` using a `liverty-music-ci-bot` GitHub App installation token (the App is the `main` ruleset bypass actor — see design D9; the built-in `GITHUB_TOKEN` / `github-actions[bot]` cannot be a repo-ruleset bypass actor). ArgoCD's existing auto-sync rolls the change out — the workflow SHALL NOT open a pull request.

#### Scenario: Dispatch updates newTag and version label in lock-step

- **WHEN** `bump-prod-pin.yml` receives `{ component: "backend", tag: "v1.4.0", sha: "abc123..." }`
- **THEN** all 4 `images[].newTag` in `k8s/namespaces/backend/overlays/prod/kustomization.yaml` SHALL be set to `v1.4.0`
- **AND** the `app.kubernetes.io/version` label SHALL be set to `1.4.0`
- **AND** each `newTag`'s inline `# commit <sha>` trailer SHALL be updated to `abc123...`

#### Scenario: A frontend dispatch pins all bundles atomically in one commit

- **WHEN** `bump-prod-pin.yml` receives `{ component: "frontend", tag: "v1.58.1", sha: "6139459..." }`
- **THEN** the `fan-web`, `admin-console-web`, and `organizer-console-web` `images[].newTag` in `k8s/namespaces/frontend/overlays/prod/kustomization.yaml` SHALL ALL be set to `v1.58.1`
- **AND** the `app.kubernetes.io/version` label SHALL be set to `1.58.1`
- **AND** all three rewrites SHALL be committed and pushed as a single commit (no per-bundle commits and no transient state where only some bundles are on `v1.58.1`)

#### Scenario: Provenance gate rejects a frontend tag whose bundles are not all in prod AR

- **WHEN** `bump-prod-pin.yml` receives a `frontend` dispatch for a `tag` for which at least one of the three frontend bundle images does not exist in prod AR
- **THEN** the workflow SHALL abort at the provenance check before editing any file
- **AND** it SHALL NOT commit or push a partial or bogus pin

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
