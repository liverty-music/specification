## MODIFIED Requirements

### Requirement: Claude code review runs via a single org-wide reusable workflow
All four liverty-music repositories (`backend`, `frontend`, `specification`, `cloud-provisioning`) SHALL invoke Claude code review through a reusable workflow hosted at `liverty-music/.github/.github/workflows/claude-review.yml` (`workflow_call`). Each repository's own `.github/workflows/claude-code-review.yml` SHALL be a caller-only workflow that forwards `secrets: inherit`. The reusable workflow SHALL invoke `code-review@claude-code-plugins` with the `--comment` flag and `anthropics/claude-code-action@v1`, passing the slash command as a single-line `prompt:` without additional structured-prompt wrapping.

The reusable workflow's `claude_args.--allowedTools` SHALL be aligned with the `code-review` plugin's declared `allowed-tools` frontmatter — at minimum including `Bash(gh pr list:*)`, `Bash(gh pr view:*)`, `Bash(gh pr diff:*)`, `Bash(gh pr comment:*)`, `Bash(gh issue view:*)`, `Bash(gh issue list:*)`, `Bash(gh search:*)`, and `mcp__github_inline_comment__create_inline_comment`. The reusable workflow SHALL NOT accept per-repo input parameters that inject free-form text into the prompt; per-repo review focus is expressed exclusively via each repo's `CLAUDE.md`.

#### Scenario: PR is opened in any liverty-music repo
- **WHEN** a pull request is opened or updated in `backend`, `frontend`, `specification`, or `cloud-provisioning`
- **THEN** the repo's `claude-code-review.yml` SHALL call `liverty-music/.github/.github/workflows/claude-review.yml` via `uses:` rather than running Claude inline

#### Scenario: Claude review behavior needs updating
- **WHEN** the Claude review prompt, plugin version, or verdict logic needs to change
- **THEN** the change SHALL be made in `liverty-music/.github/.github/workflows/claude-review.yml` and SHALL take effect on all four repos without modifying individual repo workflows

#### Scenario: Caller workflow contains no prompt-injecting input
- **WHEN** a caller workflow at `<repo>/.github/workflows/claude-code-review.yml` is inspected
- **THEN** the `jobs.review.with:` block SHALL be absent (or empty), with no `additional_focus` or other free-form text inputs passed to the reusable workflow

### Requirement: Claude review publishes its verdict as a GitHub Check Run
The reusable workflow SHALL create a GitHub Check Run named exactly `Claude review` on the pull request's head commit. The Check Run `conclusion` SHALL be derived deterministically from the count of inline review comments that the Claude bot has posted against the pull request's head commit SHA, computed in a post-step that calls `gh api repos/<owner>/<repo>/pulls/<N>/comments` and filters by `commit_id == <head_sha>` AND `user.login == <claude bot identity>`.

The conclusion mapping SHALL be:

| Filtered comment count | `conclusion` |
|---|---|
| `0` | `success` |
| `≥ 1` | `failure` |
| `gh api` call fails or output unparseable | `neutral` |

The Check Run output `title` SHALL be `No issues found` when `conclusion == success`, `N issue(s) found` when `conclusion == failure` (where `N` is the filtered comment count), and `Verdict could not be computed` when `conclusion == neutral`. The Check Run output `summary` SHALL link to the pull request's `Files changed` view.

The verdict SHALL NOT be derived from an LLM-emitted artifact (such as a JSON file written by the Claude run). The Claude run is responsible only for posting inline review comments; the verdict is computed mechanically after the Claude run completes.

The workflow SHALL NOT submit a formal pull request review (`APPROVE` or `REQUEST_CHANGES`) for the verdict. Only the inline comments (posted by the plugin) and the Check Run are produced.

#### Scenario: Claude finds no high-signal issues
- **WHEN** the Claude run completes and `gh api repos/.../pulls/<N>/comments` returns zero comments matching `commit_id == <head_sha>` AND `user.login == <claude bot identity>`
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: success`
- **AND** the Check Run output title SHALL be `No issues found`

#### Scenario: Claude posts inline comments against the PR head
- **WHEN** the Claude run completes and `gh api repos/.../pulls/<N>/comments` returns `N ≥ 1` comments matching `commit_id == <head_sha>` AND `user.login == <claude bot identity>`
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: failure`
- **AND** the Check Run output title SHALL be `N issue(s) found`

#### Scenario: Verdict computation fails
- **WHEN** the `gh api` call to fetch PR comments exits non-zero, or its output cannot be parsed as JSON
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: neutral`
- **AND** the Check Run output title SHALL be `Verdict could not be computed`

#### Scenario: Subsequent push fixes earlier-flagged issues
- **WHEN** a PR initially has `conclusion: failure` from Claude comments on commit SHA `A`
- **AND** a new commit SHA `B` is pushed that fixes the flagged issues (such that the slash command's skip-on-repeat behavior exits the Claude run without posting new comments)
- **AND** no inline comments exist with `commit_id == B`
- **THEN** the workflow on commit `B` SHALL create a `Claude review` Check Run with `conclusion: success`
- **AND** the prior `failure` Check Run on commit `A` does not affect commit `B`'s conclusion

#### Scenario: Claude review never submits a formal PR review
- **WHEN** any Claude review run completes (success, failure, or neutral)
- **THEN** `gh pr view --json reviews` SHALL NOT show a review authored by Claude with state `APPROVED` or `CHANGES_REQUESTED`
