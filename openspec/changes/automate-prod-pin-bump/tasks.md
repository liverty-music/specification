## 1. Cloud-provisioning: bump-prod-pin workflow

- [x] 1.1 Add `.github/workflows/bump-prod-pin.yml` triggered by `repository_dispatch` (type `bump-prod-pin`) plus a `workflow_dispatch` fallback (manual `component` + `tag` + `sha` inputs) for dropped-dispatch recovery. Gate the manual fallback with a **conditional** environment binding — `environment: ${{ github.event_name == 'workflow_dispatch' && 'prod-pin' || '' }}` (see 2.4) — so `workflow_dispatch` enters `prod-pin` (admin approval) while `repository_dispatch` resolves to empty and runs unattended. Do NOT bind the environment unconditionally (it would stall the automated path).
- [x] 1.2 Parse `client_payload.{component,tag,sha}`; validate `component ∈ {backend, frontend}` and `tag` matches `^v[0-9]+\.[0-9]+\.[0-9]+$` (fail fast on a malformed payload).
- [x] 1.2a Provenance gate (before any edit, fail-closed): for every image of the component, run `crane manifest asia-northeast2-docker.pkg.dev/liverty-music-prod/<component>/<img>:<tag>` and abort if any is not-found. Authenticate `crane` to prod AR first. This rejects bogus/stale tags and the silent-downgrade path; it applies to both the dispatch and the `workflow_dispatch` fallback.
- [x] 1.3 Implement the `yq` edit step: for `backend` rewrite all 4 `images[].newTag` + inline `# commit <sha>` trailers; for `frontend` the single `web-app` entry. Update `labels[].pairs."app.kubernetes.io/version"` to the bare semver (strip leading `v`). Edit both fields in lock-step.
- [x] 1.4 Add the idempotency guard: if every target `newTag` already equals `tag`, exit 0 without committing.
- [x] 1.5 Add the validation gate: run `kustomize build k8s/namespaces/<component>/overlays/prod` after the edit; abort (no push) on non-zero exit.
- [x] 1.6 Commit as `github-actions[bot]` and push to `main` using the workflow `GITHUB_TOKEN`; add `concurrency: { group: bump-prod-pin, cancel-in-progress: false }` and a fetch-rebase-retry loop (≤5 attempts) around the push. No PR.
- [x] 1.7 Write the commit message per the Liverty-Music convention (body explaining why + `Refs: #<issue>`); include `component`, `tag`, `sha` in the body for traceability.

## 2. GitHub settings: branch-protection bypass

- [x] 2.1 Add `github-actions[bot]` as a bypass actor on the `cloud-provisioning` `main` ruleset/branch protection (covering the PR requirement and the require-up-to-date check). Confirm no human/PAT actor is added.
- [x] 2.2 If this is Pulumi-managed (GitHubRepositoryComponent in `cloud-provisioning/src/github/`), encode the bypass actor in IaC rather than the GitHub UI; otherwise document the manual setting in the runbook.
- [x] 2.3 Provision the cross-repo dispatch credential for backend/frontend: prefer a GitHub App installation token (short-lived, auditable) over a long-lived fine-grained PAT, scoped to `cloud-provisioning`. Note `repository_dispatch` requires `Contents: write` (no narrower scope exists), so the security boundary is branch protection — verify the token CANNOT push to `cloud-provisioning:main` (only `github-actions[bot]` bypasses), confirming its reach is limited to non-`main` refs ArgoCD does not track. Store as a repo/org secret.
- [x] 2.4 Create the `prod-pin` GitHub Environment on `cloud-provisioning` with a required-reviewer protection rule (admin). The selective gating is achieved by the conditional `environment:` expression in 1.1 (the Environment itself has no trigger-type filter), so verify by test: a `workflow_dispatch` run pauses for approval, and a `repository_dispatch` run does NOT. Encode in Pulumi IaC if environments are IaC-managed, else document the manual setting in the runbook (5.1).

## 3. Backend release path: emit dispatch

- [x] 3.1 In `backend/.github/workflows/deploy.yml`, add a `dispatch-prod-pin` job with `needs: [build-and-push]` and `if: github.event_name == 'release' && needs.build-and-push.result == 'success'`.
- [x] 3.2 In that job, POST the `repository_dispatch` (`event_type: bump-prod-pin`, `client_payload: { component: "backend", tag: <release tag_name>, sha: <github.sha> }`) using the dispatch credential from 2.3.
- [x] 3.3 Verify the job does NOT fire on a partial matrix failure (manually reason through `fail-fast: false` + `result == 'success'`).

## 4. Frontend release path: emit dispatch

- [x] 4.1 In `frontend/.github/workflows/push-image.yaml`, add the same dispatch step to the release path, gated on the retag job succeeding (`component: "frontend"`).
- [ ] 4.2 (Optional, follow-on) After the bump, poll `https://liverty-music.app` for the new bundle hash and auto-trigger the existing prod smoke (`workflow_dispatch` with `smoke_url`). Gate behind a flag so the core automation can ship without it.

## 5. Specification: documentation

- [x] 5.1 Update `cloud-provisioning/docs/runbooks/prod-image-tag-pinning.md`: replace the "open a pin-bump PR" steps with the automated dispatch flow; document the `workflow_dispatch` manual-recovery path and `git revert` rollback.
- [x] 5.2 Update the explanatory comment block in both prod `kustomization.yaml` files ("Bumping on release: cut a new GH Release ... Open a PR here") to reflect that the bump is now CI-written via dispatch.

## 6. End-to-end verification (dev/staging first, then prod)

- [ ] 6.1 Dry-run the bump workflow via `workflow_dispatch` with a known-good `{component, tag, sha}` against a throwaway branch; confirm the yq edit + `kustomize build` validate + idempotency behave correctly without touching `main`.
- [ ] 6.2 Cut a real backend release and a real frontend release; confirm each dispatches, the bump lands on `cloud-provisioning:main`, and ArgoCD auto-syncs the prod overlay to the new tag.
- [ ] 6.3 Confirm the rollout in prod: new Pods carry the expected `app.kubernetes.io/version` label and pull the `:vX.Y.Z` prod-AR image; run the frontend prod smoke against `https://liverty-music.app`.
- [ ] 6.4 Confirm rollback path: `git revert` the bump commit on `cloud-provisioning:main` and verify ArgoCD rolls prod back to the prior tag.
