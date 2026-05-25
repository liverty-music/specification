## 1. Preparation

- [x] 1.1 Create tracking issue in `liverty-music/specification` titled `Mechanize Claude review verdict (decouple from LLM judgment)` and note its number for all subsequent commits (`Refs: #<N>`) — created as [#521](https://github.com/liverty-music/specification/issues/521)
- [x] 1.2 Identify the Claude bot's GitHub `user.login` by inspecting an existing PR's inline comments via `gh api repos/liverty-music/specification/pulls/<recent-PR>/comments | jq '.[] | {login: .user.login, type: .user.type, commit_id}'`. Record the exact login string for use in the workflow filter. — confirmed via PR #520: `user.login == "claude[bot]"`, `user.type == "Bot"`

## 2. Reusable workflow (`liverty-music/.github`)

- [ ] 2.1 Create branch off `main` in the `.github` repo
- [x] 2.2 Edit `.github/workflows/claude-review.yml`: remove the `inputs.additional_focus` block from `on.workflow_call`
- [x] 2.3 Replace the multi-line `prompt:` value with the single-line form: `'/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }} --comment'`
- [x] 2.4 Update `claude_args.--allowedTools` to add `Bash(gh pr list:*)` and remove `Write`
- [x] 2.5 Delete the `Read verdict file` step
- [x] 2.6 Add a new `Count Claude inline comments` step that calls `gh api repos/${{ github.repository }}/pulls/${{ github.event.pull_request.number }}/comments`, filters by `commit_id == github.event.pull_request.head.sha` AND `user.login == <recorded login from 1.2>`, counts the result via `jq`, and writes the count to `$GITHUB_OUTPUT`. On `gh api` failure, write `count=-1` to signal `neutral`.
- [x] 2.7 Update the `Publish Claude review Check Run` step: replace the verdict-JSON parsing with the count → conclusion mapping from the spec (`0 → success`, `≥1 → failure`, `-1 → neutral`). Set output `title` per the spec (`No issues found` / `N issue(s) found` / `Verdict could not be computed`). Set `summary` to link to the PR's Files changed view.
- [ ] 2.8 Open PR; ensure CI passes; merge

## 3. Caller workflows (4 repos)

- [ ] 3.1 `liverty-music/specification`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge
- [ ] 3.2 `liverty-music/backend`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge
- [ ] 3.3 `liverty-music/frontend`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge
- [ ] 3.4 `liverty-music/cloud-provisioning`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge

## 4. Validation

- [ ] 4.1 Open a small test PR on `liverty-music/specification` that intentionally contains no review-worthy issues. Confirm: Claude run completes, no inline comments are posted, `Claude review` Check Run conclusion is `success`, title is `No issues found`.
- [ ] 4.2 Open a small test PR on `liverty-music/specification` that intentionally contains a CLAUDE.md violation (e.g., missing required field documentation). Confirm: Claude posts at least one inline comment, `Claude review` Check Run conclusion is `failure`, title shows the correct comment count.
- [ ] 4.3 Push a fix commit to the failing test PR from 4.2. Confirm: the new head SHA has zero matching inline comments, the Check Run on the new SHA is `success` (even though the slash command may skip the actual review per the documented skip-on-repeat behavior).
- [ ] 4.4 Verify that no formal PR review (`APPROVED` or `CHANGES_REQUESTED`) is created by Claude on any of the test PRs: `gh pr view <N> --json reviews --jq '.reviews[] | select(.author.login | test("claude"))'` returns nothing.
- [ ] 4.5 Inspect a `gh api` output from one of the runs to confirm the `commit_id` and `user.login` filter matches reality. Adjust the workflow if the bot login differs from what was recorded in 1.2.

## 5. Documentation and archive

- [ ] 5.1 Confirm `make check` (or equivalent validation) passes on all four caller-repo PRs
- [ ] 5.2 After two successful real (non-test) PRs land on `specification` with the new mechanism, run `/opsx:archive` to archive this change and apply the spec delta to `openspec/specs/ci-optimization/spec.md`
