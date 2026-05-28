## Why

The predecessor change [`mechanize-claude-review-verdict`](../archive/2026-05-28-mechanize-claude-review-verdict/) tried to gate PR merges on `Claude review` Check Run output by mechanically counting inline comments. Two production PRs ([`liverty-music/backend#305`](https://github.com/liverty-music/backend/pull/305), [`liverty-music/frontend#367`](https://github.com/liverty-music/frontend/pull/367)) exposed that the chosen `commit_id == HEAD_SHA` REST filter detects only code-overwrite resolution, missing UI-resolve and "still-applicable-after-push" cases.

This change initially proposed a layered fix: GraphQL `reviewThreads.isResolved` filtering + `pull_request_review_thread` re-trigger + split-job caller pattern + `verdict_only` reusable-workflow input. Investigation while implementing the fix revealed a deeper problem: **the entire pattern of using `Claude review` as a required status check is not supported by `anthropics/claude-code-action` upstream**, and every layer of the harness adds workarounds for upstream behavior it was never designed to provide.

Concretely:

- `anthropics/claude-code-action` exposes no Check Run / verdict / pass-fail output mechanism. Its [official examples](https://github.com/anthropics/claude-code-action/tree/main/examples) (`pr-review-comprehensive.yml`, `pr-review-filtered-authors.yml`, `pr-review-filtered-paths.yml`) all post inline comments only — none create a Check Run or gate the workflow.
- The `code-review` slash command itself ([`anthropics/claude-code` plugins](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md)) does not emit a verdict file or any structured pass/fail signal.
- `pull_request_review_thread` is documented as a webhook event but **does not function as a GitHub Actions workflow trigger**. Empirical test (this change, 2026-05-28): adding `on: pull_request_review_thread:` to a caller workflow produces spurious push-event stub failures AND prevents the `pull_request` trigger from firing at all. Confirmed against 11+ third-party workflows on GitHub that use this trigger — all in `failure` state.

The accumulated user-side harness reached four iterations, each fixing the prior layer's bug while introducing new complexity (LLM verdict file → REST `commit_id` filter → GraphQL `isResolved` filter → split-job + `verdict_only` + broken trigger). Per the operating instruction "可能な限り構成をシンプルに / 場当たり的なハックは禁止", reset to the upstream pattern: `Claude review` becomes advisory-only.

## What Changes

- **BREAKING (workflow)**: Revert the reusable workflow `liverty-music/.github/.github/workflows/claude-review.yml` to the official [`pr-review-comprehensive.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-comprehensive.yml) shape — a single job invoking `anthropics/claude-code-action@v1` with the `code-review` plugin and `--comment`. Remove the `Count unresolved Claude review threads` step, the `Publish Claude review Check Run` step, the `verdict_only` input, the `checks: write` permission, and all pagination / GraphQL / jq filtering logic.
- **BREAKING (branch protection)**: Drop `'Claude review'` from `requiredStatusCheckContexts` on all four liverty-music repos (`backend`, `frontend`, `specification`, `cloud-provisioning`) in [`cloud-provisioning/src/index.ts`](https://github.com/liverty-music/cloud-provisioning/blob/main/src/index.ts). `'CI Success'` remains as the sole required check.
- **PRESERVED (caller workflows)**: All four caller workflows at `<repo>/.github/workflows/claude-code-review.yml` keep their existing `on: pull_request: types: [opened, synchronize, ready_for_review, reopened]` trigger and single-job structure invoking the reusable workflow. No `pull_request_review_thread`, no split-jobs, no `verdict_only` plumbing. (The `permissions: checks: write` line on each caller becomes unused after the reusable stops creating Check Runs; treated as harmless and deferred for cleanup.)
- **PRESERVED (review behavior)**: `Claude review` workflow still runs on every PR push, the bot still posts inline review comments. What changes is solely the gate: reviewers (human or otherwise) read the comments and decide what to act on; merge is no longer blocked by an automated comment count.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `ci-optimization`: Remove the requirement that `Claude review` publishes a Check Run derived from comment counting. Remove the requirement that `Claude review` is enforced as a Required Status Check via Pulumi. Replace with an advisory-only requirement: Claude review posts inline comments; no Check Run is published; merge gating uses other deterministic checks.

## Impact

- **Affected repo: `liverty-music/.github`** — reusable workflow at `.github/workflows/claude-review.yml` is reverted to the minimal upstream shape ([#7](https://github.com/liverty-music/.github/pull/7)).
- **Affected repo: `liverty-music/cloud-provisioning`** — Pulumi component invocations in `src/index.ts` drop `'Claude review'` from `requiredStatusCheckContexts` on all four `GitHubRepositoryComponent` entries ([#311](https://github.com/liverty-music/cloud-provisioning/pull/311)).
- **No change required in caller workflows** (`backend`, `frontend`, `specification`, `cloud-provisioning` `.github/workflows/claude-code-review.yml`) — they already use the official `pull_request` trigger pattern.
- **Tracking issue**: [`liverty-music/specification#525`](https://github.com/liverty-music/specification/issues/525).
- **Predecessor archive**: `mechanize-claude-review-verdict` archived at [`archive/2026-05-28-mechanize-claude-review-verdict`](../archive/2026-05-28-mechanize-claude-review-verdict/). Its spec delta is in the current canonical `openspec/specs/ci-optimization/spec.md` and is being further modified by this change.
- **Superseded PRs** (closed without merge): [`liverty-music/.github#5`](https://github.com/liverty-music/.github/pull/5) (verdict_only input version), [`liverty-music/backend#311`](https://github.com/liverty-music/backend/pull/311), [`liverty-music/frontend#371`](https://github.com/liverty-music/frontend/pull/371), [`liverty-music/cloud-provisioning#310`](https://github.com/liverty-music/cloud-provisioning/pull/310).
- **Already merged (but being walked back by this change)**: [`liverty-music/.github#6`](https://github.com/liverty-music/.github/pull/6) merged the GraphQL-`isResolved` Check Run logic to `main`. This change's [.github#7](https://github.com/liverty-music/.github/pull/7) reverts it.

## Deployment ordering

1. Merge [cloud-provisioning#311](https://github.com/liverty-music/cloud-provisioning/pull/311) (Pulumi drops required check).
2. User manually runs `pulumi up -s prod`. Verify via `gh api repos/liverty-music/<repo>/branches/main/protection --jq '.required_status_checks.contexts'` that `Claude review` is gone from all four repos.
3. Only AFTER step 2 confirmed, merge [.github#7](https://github.com/liverty-music/.github/pull/7) (reusable workflow stops creating Check Run).
4. Merge this specification PR ([#526](https://github.com/liverty-music/specification/pull/526)) — the OpenSpec proposal/design/spec/tasks for the change.
5. Archive `honor-thread-resolution-in-claude-review-check` after the next normal PR proves the new state works (inline comments posted, no Check Run created, merge succeeds via `CI Success` only).
