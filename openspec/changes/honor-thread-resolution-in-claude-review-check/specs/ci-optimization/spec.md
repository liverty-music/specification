## MODIFIED Requirements

### Requirement: Claude review publishes its verdict as a GitHub Check Run
The reusable workflow SHALL create a GitHub Check Run named exactly `Claude review` on the pull request's head commit. The Check Run `conclusion` SHALL be derived deterministically from the count of **unresolved review threads opened by the Claude bot**, computed in a post-step that calls `gh api graphql` against the pull request's `reviewThreads(first: 100)` field and filters by `isResolved == false` AND `isOutdated == false` AND (`comments.nodes[0].author.__typename == "Bot"` AND `comments.nodes[0].author.login == "claude"`).

The Check Run conclusion mapping SHALL be:

| Filtered thread count | `conclusion` |
|---|---|
| `0` | `success` |
| `≥ 1` | `failure` |
| GraphQL call fails, response is unparseable, or `pageInfo.hasNextPage == true` (>100 threads) | `neutral` |

The Check Run output `title` SHALL be `No issues found` when `conclusion == success`, `N issue(s) found` when `conclusion == failure` (where `N` is the filtered thread count), and `Verdict could not be computed` when `conclusion == neutral` (the title MAY append `(>100 threads)` when the pagination-overflow branch is taken). The Check Run output `summary` SHALL link to the pull request's `Files changed` view.

The verdict SHALL NOT be derived from an LLM-emitted artifact (such as a JSON file written by the Claude run), and SHALL NOT be derived from a REST-comments-`commit_id` filter. The Claude run is responsible only for posting inline review comments; the verdict is computed mechanically against live thread state after the count step completes.

The workflow SHALL NOT submit a formal pull request review (`APPROVE` or `REQUEST_CHANGES`) for the verdict. Only the inline comments (posted by the plugin) and the Check Run are produced.

#### Scenario: Claude finds no high-signal issues
- **WHEN** the Claude run completes and zero `reviewThreads` match `isResolved == false AND isOutdated == false AND comments.nodes[0].author.__typename == "Bot" AND comments.nodes[0].author.login == "claude"`
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: success`
- **AND** the Check Run output title SHALL be `No issues found`

#### Scenario: Claude has open unresolved bot threads
- **WHEN** the count step finds `N ≥ 1` `reviewThreads` matching the filter
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: failure`
- **AND** the Check Run output title SHALL be `N issue(s) found`

#### Scenario: Verdict computation fails
- **WHEN** the `gh api graphql` call exits non-zero, OR its output cannot be parsed, OR `pageInfo.hasNextPage == true`
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: neutral`
- **AND** the Check Run output title SHALL be `Verdict could not be computed`

#### Scenario: Maintainer resolves a bot thread via the GitHub UI
- **WHEN** a maintainer clicks "Resolve conversation" on a bot-opened thread
- **THEN** GitHub SHALL fire a `pull_request_review_thread` event with `action: resolved`
- **AND** the caller workflow SHALL re-invoke the reusable workflow
- **AND** the count step SHALL recompute against live thread state
- **AND** the Check Run on the head SHA SHALL be republished with the new count

#### Scenario: Maintainer un-resolves a previously-resolved bot thread
- **WHEN** a maintainer clicks "Unresolve conversation" on a previously-resolved bot thread
- **THEN** the caller workflow SHALL re-invoke the reusable workflow on the `pull_request_review_thread.unresolved` event
- **AND** the count step SHALL include that thread again
- **AND** the Check Run SHALL reflect the higher count

#### Scenario: Subsequent push fixes earlier-flagged issues by changing the lines
- **WHEN** a PR initially has `conclusion: failure` from bot threads on commit SHA `A`
- **AND** a new commit SHA `B` is pushed that edits or removes the flagged lines (such that GitHub marks the corresponding threads `isOutdated: true`)
- **THEN** the workflow on commit `B` SHALL exclude those threads from the count
- **AND** if no other unresolved bot threads remain, the Check Run SHALL be `conclusion: success`

#### Scenario: Empty or unrelated commit is pushed without resolving any threads
- **WHEN** a commit is pushed that does not touch any line referenced by an open bot thread, AND no threads are marked resolved
- **THEN** every open bot thread remains `isResolved: false AND isOutdated: false`
- **AND** the Check Run conclusion SHALL remain `failure` with the same count as before the push
- **AND** the count SHALL NOT be inflated by the new HEAD SHA (the count is independent of `commit_id`)

#### Scenario: Claude review never submits a formal PR review
- **WHEN** any Claude review run completes (success, failure, or neutral)
- **THEN** `gh pr view --json reviews` SHALL NOT show a review authored by Claude with state `APPROVED` or `CHANGES_REQUESTED`

### Requirement: Claude review caller workflows fire on PR events AND thread resolve events
Each caller workflow at `<repo>/.github/workflows/claude-code-review.yml` SHALL register `on:` triggers for both `pull_request` (types `opened`, `synchronize`, `reopened`) AND `pull_request_review_thread` (types `resolved`, `unresolved`). The caller workflow MAY also register `workflow_dispatch` for manual recompute.

The reusable workflow at `liverty-music/.github/.github/workflows/claude-review.yml` SHALL guard its `Run Claude review` step with `if: github.event_name == 'pull_request'` so that re-triggers from thread-resolve events do not consume Anthropic API tokens or re-post inline comments. The count step and publish step SHALL run on every trigger.

#### Scenario: PR is opened or updated
- **WHEN** a pull request is opened, synchronized, or reopened
- **THEN** the caller workflow SHALL invoke the reusable workflow
- **AND** the reusable workflow's `Run Claude review` step SHALL execute (the `if` guard is satisfied)
- **AND** the count step SHALL execute after the Claude run completes
- **AND** the publish step SHALL create or update the Check Run

#### Scenario: Maintainer toggles thread resolution
- **WHEN** a `pull_request_review_thread` event fires with `action: resolved` or `action: unresolved`
- **THEN** the caller workflow SHALL invoke the reusable workflow
- **AND** the reusable workflow's `Run Claude review` step SHALL be skipped (the `if` guard fails)
- **AND** the count step SHALL still execute
- **AND** the publish step SHALL create or update the Check Run

#### Scenario: Caller workflow is inspected
- **WHEN** a caller workflow at `<repo>/.github/workflows/claude-code-review.yml` is read
- **THEN** the `on:` block SHALL contain both `pull_request` and `pull_request_review_thread`
- **AND** the `pull_request_review_thread.types` value SHALL include both `resolved` and `unresolved`
