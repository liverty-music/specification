## Why

The predecessor change [`mechanize-claude-review-verdict`](../mechanize-claude-review-verdict/) correctly removed LLM-emitted verdict pressure by deriving the `Claude review` Check Run conclusion from a mechanical count of inline review comments. It chose `commit_id == HEAD_SHA AND user.login == "claude[bot]"` (REST `/pulls/N/comments`) as the resolution signal. That signal turned out to detect only **one** of the three resolution paths a reviewer can take, producing a permanent FAILURE state in real use.

Specifically, `commit_id` on a review comment is **not** the SHA where the comment was originally posted — it is the most recent SHA where the comment is still applicable to the code. GitHub auto-updates it forward on every push as long as the commented line is unchanged. Therefore the predecessor filter is semantically `still-applicable-bot-comments-on-HEAD`, which excludes only the "code was rewritten over the line" case. It does not exclude:

- A maintainer clicking **Resolve conversation** in the GitHub UI (`isResolved = true` does not change `commit_id`).
- A defendable inline reply where the maintainer pushes back and resolves (same as above).
- An empty / unrelated commit being pushed (every still-live comment's `commit_id` is bumped to the new HEAD — count is unchanged).

This was observed on two production PRs that completed full 17-round bot review cycles:

| PR | Threads resolved (UI) | Final Check Run | Final title |
|---|---|---|---|
| [`liverty-music/backend#305`](https://github.com/liverty-music/backend/pull/305) | 66 / 66 | `failure` | `51 issue(s) found` |
| [`liverty-music/frontend#367`](https://github.com/liverty-music/frontend/pull/367) | 45 / 45 | `failure` | `18 issue(s) found` |

Both PRs required **admin override** to merge, which directly conflicts with the `NEVER skip hooks unless explicitly requested` guard documented in CLAUDE.md. Left unfixed, this forces a choice between removing `Claude review` from `requiredStatusCheckContexts` (defeating the gate) or routinely bypassing branch protection (defeating the operating-protocol guard).

The fix is to switch the resolution signal from REST-comment-`commit_id` to GraphQL **`reviewThreads.isResolved`** (plus `isOutdated` to retain the "code-change-resolved" path), and to re-trigger the workflow on `pull_request_review_thread` events so resolve clicks take effect without a manual re-push.

## What Changes

- **BREAKING (workflow logic)**: In `liverty-music/.github/.github/workflows/claude-review.yml`, replace the REST `/pulls/N/comments` + `commit_id == HEAD_SHA` filter with a GraphQL `reviewThreads(first: 100)` query filtering `isResolved == false AND isOutdated == false AND comments.nodes[0].author.login == "claude[bot]"`. Count remains the conclusion signal.
- **ADD**: All four caller workflows (`backend`, `frontend`, `specification`, `cloud-provisioning`) MUST add `pull_request_review_thread` (types `resolved`, `unresolved`) to their `on:` triggers so resolve clicks recompute the Check Run.
- **ADD**: Guard the expensive `anthropics/claude-code-action@v1` step in the reusable workflow with `if: github.event_name == 'pull_request'` so resolve-click re-triggers run only the cheap count + publish steps. Without this guard each resolve click would burn Anthropic API tokens and likely re-post nits.
- **ADD**: On GraphQL `pageInfo.hasNextPage == true` (>100 threads), publish `conclusion: neutral`. A PR with that many threads is unhealthy regardless and should not be auto-gated either way.
- **PRESERVED**: Check Run name (`Claude review`), conclusion vocabulary (`success` / `failure` / `neutral`), Required Status Check policy, no Pulumi changes, no `CLAUDE.md` content changes.
- **PRESERVED**: All five decisions of `mechanize-claude-review-verdict` — verdict decoupled from LLM, `additional_focus` removed, single-line slash command, `--allowedTools` aligned, tracking-issue convention. This change supersedes only the implementation detail of how comments are counted; the thesis stands.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `ci-optimization`: Replace the `commit_id == HEAD_SHA`-driven comment-count requirement with an unresolved-`reviewThread`-count requirement; require caller workflows to fire on `pull_request_review_thread`; require the reusable workflow to skip the Claude run step on non-`pull_request` events.

## Impact

- **Affected repo**: `liverty-music/.github` (reusable workflow at `.github/workflows/claude-review.yml` — count step + step guard change).
- **Affected caller workflows** (4 repos, ~3-line addition each): `backend/.github/workflows/claude-code-review.yml`, `frontend/.github/workflows/claude-code-review.yml`, `specification/.github/workflows/claude-code-review.yml`, `cloud-provisioning/.github/workflows/claude-code-review.yml`.
- **No Pulumi change**: Branch protection is unchanged.
- **CLAUDE.md update (optional, documentation-only)**: Add a one-line note in each repo's `CLAUDE.md` (or the workspace CLAUDE.md) clarifying that maintainers can clear `Claude review` failures by clicking "Resolve conversation" on the relevant threads, and that resolving a thread automatically recomputes the Check Run.
- **Tracking issue**: To be created in `liverty-music/specification` (next-available number) before implementation. Per the liverty-music commit convention every commit footer is `Refs: #<issue-number>`.
- **Predecessor dependency**: `mechanize-claude-review-verdict` MUST be archived before this change is applied (so its spec delta lands in canonical `openspec/specs/ci-optimization/spec.md` and this change's MODIFIED requirement targets the post-mechanize text). See [`design.md`](./design.md) §"Migration Plan" for the ordering.
- **Known residual issue (unchanged from predecessor)**: The `code-review` plugin's skip-on-repeat behavior ([anthropics/claude-code#19618](https://github.com/anthropics/claude-code/issues/19618)) remains out of scope. Mitigation is unchanged — `isOutdated` excludes code-resolved threads, `isResolved` excludes UI-resolved threads, so a stale cache cannot inflate the count.
