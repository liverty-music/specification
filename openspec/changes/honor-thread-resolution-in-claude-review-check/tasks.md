## 1. Preparation

- [x] 1.1 Archive `mechanize-claude-review-verdict` so its spec delta lands in canonical `openspec/specs/ci-optimization/spec.md`. — archived to [`archive/2026-05-28-mechanize-claude-review-verdict/`](../archive/2026-05-28-mechanize-claude-review-verdict/)
- [x] 1.2 Create tracking issue in `liverty-music/specification`. — created as [#525](https://github.com/liverty-music/specification/issues/525)
- [x] 1.3 Re-confirm the Claude bot identity by inspecting an existing resolved-thread PR via GraphQL. — Verified 2026-05-28 against frontend#367. (No longer relevant to the final design — Option B does not depend on bot identity filtering — but the verification stands as historical record.)

## 2. Investigation that drove the pivot

- [x] 2.1 Implement GraphQL `reviewThreads.isResolved` filter in the reusable workflow. — applied in [`liverty-music/.github#6`](https://github.com/liverty-music/.github/pull/6) (merged 2026-05-28T06:19:11Z)
- [x] 2.2 Attempt to add `pull_request_review_thread: [resolved, unresolved]` trigger to caller workflows. — empirically verified across 4 PRs (specification#526, backend#311, frontend#371, cloud-provisioning#310) that the trigger produces spurious push-event stub failures AND prevents the `pull_request` trigger from firing. Confirmed broken on production by checking [`akasper/plate_template/feedback-resolution-check.yml`](https://github.com/akasper/plate_template/blob/main/.github/workflows/feedback-resolution-check.yml) and [`smart-village-solutions/sva-studio/bot-comment-governance.yml`](https://github.com/smart-village-solutions/sva-studio/blob/main/.github/workflows/bot-comment-governance.yml) — all in `failure` state on every run.
- [x] 2.3 Investigate `anthropics/claude-code-action` upstream contract. — confirmed no Check Run / verdict / structured output mechanism exists. All [official examples](https://github.com/anthropics/claude-code-action/tree/main/examples) post inline comments only and do not gate.
- [x] 2.4 Decide on the pivot direction. — Option B selected: drop the Check Run and the required-status-check entirely; align with the official `pr-review-comprehensive.yml` pattern.

## 3. Implementation — Pulumi first (must precede reusable revert)

- [ ] 3.1 Open Pulumi PR in `cloud-provisioning` removing `'Claude review'` from `requiredStatusCheckContexts` on all four `GitHubRepositoryComponent` invocations (lines ~190, 200, 213, 223 of `src/index.ts`). — [cloud-provisioning#311](https://github.com/liverty-music/cloud-provisioning/pull/311) opened
- [ ] 3.2 `make lint-ts` passes locally. — verified at PR open time
- [ ] 3.3 Merge the Pulumi PR.
- [ ] 3.4 User manually runs `pulumi up -s prod`.
- [ ] 3.5 Verify required checks via `gh api repos/liverty-music/<repo>/branches/main/protection --jq '.required_status_checks.contexts'` on all four repos. Expected result: `["CI Success"]` only.

## 4. Implementation — reusable workflow revert

- [ ] 4.1 Open `.github` PR reverting the reusable workflow to the official `pr-review-comprehensive.yml` shape. Drop: `verdict_only` input, GraphQL count step, Publish Check Run step, `checks: write` permission. — [liverty-music/.github#7](https://github.com/liverty-music/.github/pull/7) opened
- [ ] 4.2 After 3.5 confirmed, merge `.github#7`.

## 5. Implementation — caller workflows (no changes needed)

- [x] 5.1 Confirm caller workflows in all four repos remain at their pre-change baseline (only `pull_request` trigger, single `review` job invoking the reusable). — verified 2026-05-28; specification's caller was reverted to baseline by `13a0e25 diag(workflows): temporarily revert caller workflow to baseline`; other three repos never had the change merged.
- [x] 5.2 Close superseded caller PRs from the initial four-iteration design ([backend#311](https://github.com/liverty-music/backend/pull/311), [frontend#371](https://github.com/liverty-music/frontend/pull/371), [cloud-provisioning#310](https://github.com/liverty-music/cloud-provisioning/pull/310)). — closed 2026-05-28
- [x] 5.3 Close superseded `.github#5` (verdict_only input version) in favor of the user-merged `.github#6` (now itself being reverted by `.github#7`). — closed 2026-05-28

## 6. Implementation — OpenSpec proposal

- [ ] 6.1 Rewrite this change's `proposal.md`, `design.md`, `specs/ci-optimization/spec.md`, and `tasks.md` to reflect Option B (this current document).
- [ ] 6.2 `openspec validate honor-thread-resolution-in-claude-review-check` passes.
- [ ] 6.3 Merge specification#526.

## 7. Validation

- [ ] 7.1 After 4.2 merged: open a small follow-up PR on any repo. Confirm: Claude review workflow runs, posts inline comments (or none), the workflow run conclusion reflects whether the action succeeded — NOT whether Claude found issues. No Check Run named `Claude review` appears on the PR.
- [ ] 7.2 Confirm via `gh pr checks <N>` that the PR's required checks are only `CI Success` plus any per-repo required checks (e.g., `buf-checks` on specification).
- [ ] 7.3 Confirm a maintainer can merge the test PR via the standard branch-protection rule (no admin override needed) once `CI Success` passes.

## 8. Documentation and archive

- [ ] 8.1 Update or remove any CLAUDE.md / docs references that specifically rely on `Claude review` being a required status check. (Search: `grep -rn "Claude review" backend/CLAUDE.md frontend/CLAUDE.md specification/CLAUDE.md cloud-provisioning/CLAUDE.md` and review each hit.)
- [ ] 8.2 (Optional, deferred) Open a tidy PR removing the now-unused `permissions: checks: write` line from all four caller workflows.
- [ ] 8.3 After 7.x confirms the new state works (one successful PR through the new flow), run `/opsx:archive` to archive this change and apply its spec delta to canonical `openspec/specs/ci-optimization/spec.md`.
