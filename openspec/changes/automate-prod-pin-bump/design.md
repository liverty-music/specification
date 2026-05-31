## Context

Prod rollout today (per the `prod-image-pipeline` spec) is two-gate:

1. **Release publish** → `backend/deploy.yml` and `frontend/push-image.yaml` retag the dev AR digest into prod AR under `:vX.Y.Z` + `:<sha>` (no rebuild, `crane copy`). Nothing in the cluster changes yet.
2. **Manual pin-bump PR** in `cloud-provisioning` → a human edits `k8s/namespaces/{backend,frontend}/overlays/prod/kustomization.yaml` (`images[].newTag` + the `app.kubernetes.io/version` label), opens a PR, waits for the up-to-date rebase + checks, merges. ArgoCD auto-sync then rolls it out.

Prod uses **explicit semver pinning** (`newTag`), not ArgoCD Image Updater (dev's mechanism) — that is intentional and stays (`prod-image-tag-immutability`). What we are changing is only *who* edits the pin and *how* it lands: from a human PR to an automated dispatch-driven push.

The project is solo-developer; gate #2's human review adds no value because the deliberate "ship to prod" decision is already encoded in gate #1 (cutting the Release). The PR is pure toil, amplified by the "require branches up to date" rule that forces a rebase on every pending PR.

## Goals / Non-Goals

**Goals:**
- Remove the manual pin-bump PR from the critical path; a published Release rolls out to prod with no further human action.
- Preserve a *machine* validation gate (`kustomize build` of the prod overlay) so a malformed edit never reaches ArgoCD.
- Introduce **no** long-lived cross-repo write credential (no `ci-user` PAT in backend/frontend secrets).
- Keep the bump auditable (a real commit in `cloud-provisioning` history) and trivially reversible (`git revert`).
- Tolerate backend and frontend releases landing close together without losing a bump.

**Non-Goals:**
- Changing dev's ArgoCD Image Updater flow (untouched).
- Changing the retag mechanism (`crane copy` dev→prod) — unchanged.
- Changing prod's semver-pin / AR immutability policy — unchanged; we automate the *value* written to `newTag`, not the strategy.
- Adding a merge queue or reworking branch protection beyond a single bypass-actor entry.
- Auto-rollback on smoke failure (out of scope; rollback stays manual `git revert`).

## Decisions

### D1: `repository_dispatch` over clone-and-push-from-release-job

**Chosen:** the release workflow emits a `repository_dispatch` event (`POST /repos/liverty-music/cloud-provisioning/dispatches`) with `event_type: bump-prod-pin` and `client_payload: { component, tag, sha }`. A workflow *inside* `cloud-provisioning` receives it and pushes to its own `main`.

**Why over the alternative** (release job clones `cloud-provisioning`, edits, pushes):
- **Auth blast radius.** The clone approach needs a credential that can write to `cloud-provisioning` stored in *both* `backend` and `frontend` secrets — and those release jobs already hold prod-AR write. One compromised release workflow would then own both prod image and prod manifest. With dispatch, the release workflow only needs permission to *trigger* a dispatch (a fine-grained token scoped to `contents:write` or a `repository_dispatch` PAT with no manifest-write power on its own), and the actual `main` push is done by `cloud-provisioning`'s built-in `GITHUB_TOKEN` (the `github-actions[bot]` actor) pushing to *its own* repo.
- **Single source of edit logic.** The yq edit + `kustomize build` validation + commit lives in one workflow file in `cloud-provisioning`, not duplicated across two release repos.
- **Branch-protection bypass narrows to one actor** (`github-actions[bot]` on `cloud-provisioning`), not a human `ci-user` identity shared across repos.

**Cost:** the dispatch still needs a token in backend/frontend to call the dispatch API (`GITHUB_TOKEN` cannot dispatch cross-repo). Use a fine-grained PAT or GitHub App installation token scoped to `cloud-provisioning` with the minimum needed to POST a dispatch. This token cannot, by itself, write manifests — it only triggers the in-repo workflow.

### D2: Validate `kustomize build` before pushing — fail closed

The bump workflow runs `kustomize build k8s/namespaces/<component>/overlays/prod` after the yq edit and **before** `git push`. A non-zero build aborts with no push. This replaces the implicit validation the manual PR got from `cloud-provisioning`'s `ci.yml` (kube-linter / kustomize). Pushing an unbuildable overlay to `main` would make ArgoCD's target state un-renderable; failing closed keeps `main` always-syncable.

### D3: Edit via `yq`, lock-step `newTag` + version label

For `backend`: rewrite all 4 `images[].newTag` (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) and the inline `# commit <sha>` trailer, plus the `labels[].pairs.app.kubernetes.io/version` (bare semver, no leading `v`). For `frontend`: the single `web-app` entry + its label. The spec already mandates these move in lock-step; the workflow encodes that so they can never drift. `yq` (mikefarah) edits YAML structurally rather than `sed` line-munging, avoiding whitespace/quote breakage.

### D4: Idempotent + rebase-retry push

- **Idempotent:** if every target `newTag` already equals `tag`, the workflow exits 0 without committing (handles dispatch redelivery / manual re-run).
- **Rebase-retry:** wrap `git push` in a fetch-rebase-retry loop (e.g. up to 5 attempts). Backend and frontend releases can dispatch within seconds; each bump touches a *different* overlay file, so a rebase is conflict-free and the retry simply re-applies on top of the other's commit. Concurrency is additionally guarded with a workflow `concurrency: { group: bump-prod-pin, cancel-in-progress: false }` to serialize bumps.

### D5: Order — dispatch only after retag success

The dispatch step is the **last** step of the release path and is gated on retag success. For backend (4-image `fail-fast: false` matrix), the dispatch must be a separate job with `needs: [build-and-push]` and an `if: needs.build-and-push.result == 'success'` so a partially-failed retag never bumps the pin to a tag whose prod image is incomplete (which would ImagePullBackOff in prod).

### D6: Optional auto-smoke after rollout

`frontend/push-image.yaml` already has a `workflow_dispatch` smoke job against a prod URL. As a follow-on, the bump workflow (or a chained job) MAY, after pushing, poll ArgoCD/`liverty-music.app` for the new bundle hash and trigger that smoke automatically. Marked optional so the core automation can ship first.

## Risks / Trade-offs

- **A bad manifest edit reaches prod** → Mitigated by D2 (`kustomize build` fail-closed) + D4 idempotency. ArgoCD self-heal/prune is unchanged, so a structurally-valid-but-wrong tag is still caught by the immutable-tag pull (missing prod image ⇒ visible sync failure, not silent).
- **Direct `main` push widens write access on `cloud-provisioning`** → Bypass is scoped to the single `github-actions[bot]` actor on that repo only; no human/PAT bypass added. The dispatch-trigger token in backend/frontend cannot write manifests on its own.
- **Loss of pre-merge human eyes on prod** → Accepted: solo-dev, and the Release act is the retained gate. Reversal is one `git revert` away; the bump is a normal, signed-off-by-bot commit in history.
- **backend + frontend release race** → D4 rebase-retry + `concurrency` serialization; bumps touch disjoint files so no merge conflict.
- **Dispatch lost / redelivered** → Idempotency (D4) makes redelivery a no-op; a dropped dispatch is recoverable by re-running the bump workflow manually with the same payload (a `workflow_dispatch` fallback input SHOULD be provided).
- **Up-to-date requirement bypassed for the bot** → Intended side effect; the bot pushes straight to `main`. Human PRs still obey the rule.
