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
- **Auth blast radius.** The clone approach needs a credential that can write to `cloud-provisioning` stored in *both* `backend` and `frontend` secrets — and those release jobs already hold prod-AR write. One compromised release workflow would then own both prod image and prod manifest. With dispatch, the release workflow only triggers a `repository_dispatch`, and the actual `main` push is done by `cloud-provisioning`'s built-in `GITHUB_TOKEN` (the `github-actions[bot]` actor) pushing to *its own* repo. The honest boundary is **not** that the dispatch token is contents-write-less (see Cost) — it is that the token cannot push to `cloud-provisioning:main`, because `main` is branch-protected with the bypass scoped to `github-actions[bot]` only (D8/spec). So even with `contents: write`, the dispatch token's reach is bounded to non-`main` refs that ArgoCD does not track — it cannot move prod.
- **Single source of edit logic.** The yq edit + `kustomize build` validation + commit lives in one workflow file in `cloud-provisioning`, not duplicated across two release repos.
- **Branch-protection bypass narrows to one actor** (`github-actions[bot]` on `cloud-provisioning`), not a human `ci-user` identity shared across repos.

**Cost:** the dispatch still needs a token in backend/frontend to call the dispatch API (`GITHUB_TOKEN` cannot dispatch cross-repo). `POST /repos/{owner}/{repo}/dispatches` requires **`Contents: write`** for a fine-grained PAT — there is no narrower "dispatch-only" scope — so the token *can* create commits/branches on `cloud-provisioning` via the Contents API. That is acceptable **only because** branch protection on `main` (bypass = `github-actions[bot]` only) stops that token from pushing to the one ref ArgoCD tracks; its blast radius is non-`main` refs, which cannot move prod. Prefer a **GitHub App installation token** over a long-lived PAT (short-lived, auditable, revocable); if a future GitHub App permission split lets `repository_dispatch` be triggered without `Contents: write` (e.g. an Actions-scoped trigger), adopt that to shrink the grant further — tracked as an open question, not a blocker.

### D2: Validate `kustomize build` before pushing — fail closed

The bump workflow runs `kustomize build k8s/namespaces/<component>/overlays/prod` after the yq edit and **before** `git push`. A non-zero build aborts with no push. This replaces the implicit validation the manual PR got from `cloud-provisioning`'s `ci.yml` (kube-linter / kustomize). Pushing an unbuildable overlay to `main` would make ArgoCD's target state un-renderable; failing closed keeps `main` always-syncable.

Note `kustomize build` validates YAML/kustomize syntax **only** — it does not contact Artifact Registry, so it cannot tell whether the target tag's image actually exists. That gap is closed separately by D7 (provenance gate), which runs *before* the edit.

### D3: Edit via `yq`, lock-step `newTag` + version label

For `backend`: rewrite all 4 `images[].newTag` (`server`, `consumer`, `concert-discovery`, `artist-image-sync`) and the inline `# commit <sha>` trailer, plus the `labels[].pairs.app.kubernetes.io/version` (bare semver, no leading `v`). For `frontend`: the single `web-app` entry + its label. The spec already mandates these move in lock-step; the workflow encodes that so they can never drift. `yq` (mikefarah) edits YAML structurally rather than `sed` line-munging, avoiding whitespace/quote breakage.

### D4: Idempotent + rebase-retry push

- **Idempotent:** if every target `newTag` already equals `tag`, the workflow exits 0 without committing (handles dispatch redelivery / manual re-run).
- **Rebase-retry:** wrap `git push` in a fetch-rebase-retry loop (e.g. up to 5 attempts). Backend and frontend releases can dispatch within seconds; each bump touches a *different* overlay file, so a rebase is conflict-free and the retry simply re-applies on top of the other's commit. Concurrency is additionally guarded with a workflow `concurrency: { group: bump-prod-pin, cancel-in-progress: false }` to serialize bumps.

### D5: Order — dispatch only after retag success

The dispatch step is the **last** step of the release path and is gated on retag success. For backend (4-image `fail-fast: false` matrix), the dispatch must be a separate job with `needs: [build-and-push]` and an `if: needs.build-and-push.result == 'success'` so a partially-failed retag never bumps the pin to a tag whose prod image is incomplete (which would ImagePullBackOff in prod).

### D6: Optional auto-smoke after rollout

`frontend/push-image.yaml` already has a `workflow_dispatch` smoke job against a prod URL. As a follow-on, the bump workflow (or a chained job) MAY, after pushing, poll ArgoCD/`liverty-music.app` for the new bundle hash and trigger that smoke automatically. Marked optional so the core automation can ship first.

### D7: Provenance gate — the target image MUST exist before the pin moves

Payload-shape validation (component enum + semver regex, D-level task 1.2) proves the request is *well-formed*, not that it is *real*. A well-formed-but-bogus tag (`v9.9.9` that was never released, a typo, a redelivered dispatch for a tag whose retag later got cleaned up) would otherwise edit `cloud-provisioning:main` to point at a non-existent prod image. `kustomize build` (D2) would still pass — it never touches AR — so the corruption would only surface later as an ArgoCD sync failure. Worse, with no provenance check the manual fallback (D8) could *silently downgrade* prod to an older real tag with no visible error at all.

So **before** the yq edit, the bump workflow SHALL verify the target image actually exists in prod AR, fail-closed exactly like D2:

```
crane manifest asia-northeast2-docker.pkg.dev/liverty-music-prod/<component>/<img>:<tag>
```

for every image of the component (4 for backend, 1 for frontend). A missing manifest aborts the run before any edit. Because the prod image only exists if the release retag actually wrote it, this single check simultaneously: (a) confirms `tag` names a genuine release, (b) confirms the retag for *this* component completed (re-establishing D5's invariant even for non-release-path triggers), and (c) removes the "silent downgrade to a bogus tag" failure mode. A GitHub Release-existence check (`gh release view`) was considered but the prod-AR manifest check is strictly stronger — it asserts the *deployable artifact* exists, not merely that a Release object was created.

### D8: The `workflow_dispatch` fallback is admin-only

The bump workflow provides a `workflow_dispatch` manual trigger for dropped-dispatch recovery (tasks 1.1). But `workflow_dispatch` is **human-reachable**: it runs as `github-actions[bot]` (the branch-protection bypass actor), so without restriction *any* contributor with `actions: write` on `cloud-provisioning` could push an arbitrary semver-shaped tag straight to `main`, defeating the "Release is the single human gate" thesis. The provenance gate (D7) already blocks bogus tags, but a contributor could still force an unreviewed *real*-tag change (e.g. a downgrade).

Mitigation: gate the bump job behind a GitHub **Environment** (e.g. `prod-pin`) with a **required-reviewer** protection rule — but apply that environment **only on the manual trigger**. GitHub Environment protection rules fire for every job that references the environment, with no built-in trigger-type filter, so an unconditional `environment: prod-pin` would also stall the automated `repository_dispatch` path on admin approval (defeating the goal). The fix is a conditional `environment:` expression:

```yaml
environment: ${{ github.event_name == 'workflow_dispatch' && 'prod-pin' || '' }}
```

`repository_dispatch` runs resolve the environment to the empty string and never enter `prod-pin`, so the required-reviewer rule is skipped and the release path stays unattended; `workflow_dispatch` runs enter `prod-pin` and pause for admin approval. (Alternatives considered: splitting into two single-trigger workflows — cleaner isolation but two files to keep in sync; or a job-level `if:` actor-allowlist guard — less auditable than an Environment gate. The conditional-environment expression is the minimal change that satisfies both requirements.) The fallback is documented as a privileged admin-only recovery operation, not a routine path.

## Risks / Trade-offs

- **A bad/bogus tag corrupts `cloud-provisioning:main`** → Mitigated by D7 (prod-AR manifest existence check, fail-closed, *before* the edit) + D2 (`kustomize build`) + D4 idempotency. A non-existent tag is rejected before any commit; a structurally-valid-but-wrong real tag is still caught by ArgoCD at sync, and the bogus-tag *silent* path is eliminated.
- **`workflow_dispatch` fallback as a human-reachable bypass** → Mitigated by D8: the workflow is bound to a `prod-pin` Environment with a required-reviewer rule, so the manual fallback needs admin approval. D7 additionally blocks any bogus-tag input regardless of caller.
- **Direct `main` push widens write access on `cloud-provisioning`** → Bypass is scoped to the single `github-actions[bot]` actor on that repo only; no human/PAT bypass added. The dispatch-trigger token in backend/frontend has `Contents: write` (the documented minimum for `repository_dispatch`), so it *can* write non-`main` refs — but branch protection denies it the `main` push, and ArgoCD tracks `main` only, so that token cannot move prod.
- **Loss of pre-merge human eyes on prod** → Accepted: solo-dev, and the Release act is the retained gate. Reversal is one `git revert` away; the bump is a normal, signed-off-by-bot commit in history.
- **backend + frontend release race** → D4 rebase-retry + `concurrency` serialization; bumps touch disjoint files so no merge conflict.
- **Dispatch lost / redelivered** → Idempotency (D4) makes redelivery a no-op; a dropped dispatch is recoverable via the admin-gated `workflow_dispatch` fallback (D8) with the same payload. Redelivery for a since-removed tag is rejected by D7.
- **Up-to-date requirement bypassed for the bot** → Intended side effect; the bot pushes straight to `main`. Human PRs still obey the rule.
