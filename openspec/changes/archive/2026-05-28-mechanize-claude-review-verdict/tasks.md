## 1. Preparation

- [x] 1.1 Create tracking issue in `liverty-music/specification` titled `Mechanize Claude review verdict (decouple from LLM judgment)` and note its number for all subsequent commits (`Refs: #<N>`) — created as [#521](https://github.com/liverty-music/specification/issues/521)
- [x] 1.2 Identify the Claude bot's GitHub `user.login` by inspecting an existing PR's inline comments via `gh api repos/liverty-music/specification/pulls/<recent-PR>/comments | jq '.[] | {login: .user.login, type: .user.type, commit_id}'`. Record the exact login string for use in the workflow filter. — confirmed via PR #520: `user.login == "claude[bot]"`, `user.type == "Bot"`

## 2. Reusable workflow (`liverty-music/.github`)

- [x] 2.1 Create branch off `main` in the `.github` repo — `521-mechanize-claude-review-verdict`
- [x] 2.2 Edit `.github/workflows/claude-review.yml`: remove the `inputs.additional_focus` block from `on.workflow_call`
- [x] 2.3 Replace the multi-line `prompt:` value with the single-line form: `'/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }} --comment'`
- [x] 2.4 Update `claude_args.--allowedTools` to add `Bash(gh pr list:*)` and remove `Write`
- [x] 2.5 Delete the `Read verdict file` step
- [x] 2.6 Add a new `Count Claude inline comments` step that calls `gh api repos/${{ github.repository }}/pulls/${{ github.event.pull_request.number }}/comments`, filters by `commit_id == github.event.pull_request.head.sha` AND `user.login == <recorded login from 1.2>`, counts the result via `jq`, and writes the count to `$GITHUB_OUTPUT`. On `gh api` failure, write `count=-1` to signal `neutral`.
- [x] 2.7 Update the `Publish Claude review Check Run` step: replace the verdict-JSON parsing with the count → conclusion mapping from the spec (`0 → success`, `≥1 → failure`, `-1 → neutral`). Set output `title` per the spec (`No issues found` / `N issue(s) found` / `Verdict could not be computed`). Set `summary` to link to the PR's Files changed view.
- [x] 2.8 Open PR; ensure CI passes; merge — [liverty-music/.github#4](https://github.com/liverty-music/.github/pull/4) merged 2026-05-25T16:31:42Z (repo has no own CI; `Claude review` & `CI Success` not applicable)

## 3. Caller workflows (4 repos)

- [x] 3.1 `liverty-music/specification`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge — [#522](https://github.com/liverty-music/specification/pull/522) merged 2026-05-25T17:00:31Z
- [x] 3.2 `liverty-music/backend`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge — [#309](https://github.com/liverty-music/backend/pull/309) merged 2026-05-25T17:00:36Z
- [x] 3.3 `liverty-music/frontend`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge — [#370](https://github.com/liverty-music/frontend/pull/370) merged 2026-05-25T17:00:41Z
- [x] 3.4 `liverty-music/cloud-provisioning`: remove `with: additional_focus:` block from `.github/workflows/claude-code-review.yml`; open PR; merge — [#309](https://github.com/liverty-music/cloud-provisioning/pull/309) merged 2026-05-25T17:00:45Z

## 4. Validation

- [x] 4.1 Open a small test PR on `liverty-music/specification` that intentionally contains no review-worthy issues. Confirm: Claude run completes, no inline comments are posted, `Claude review` Check Run conclusion is `success`, title is `No issues found`. — validated via the 4 caller PRs themselves (#522, backend#309, frontend#370, cloud-provisioning#309): `Claude review = success` with count=0 on each, title `No issues found`
- [x] 4.2 Open a small test PR on `liverty-music/specification` that intentionally contains a CLAUDE.md violation (e.g., missing required field documentation). Confirm: Claude posts at least one inline comment, `Claude review` Check Run conclusion is `failure`, title shows the correct comment count. — validated via real PR [liverty-music/frontend#367](https://github.com/liverty-music/frontend/pull/367) (series-hierarchy migration): 18 inline comments posted on head SHA `cde65f2`, `Claude review = failure`, title `18 issue(s) found`. Content audit: 0 lint-class nits, all categorized as Bug/PLAUSIBLE/Missing-test/Schema-skew (high signal)
- [x] 4.3 Push a fix commit to the failing test PR from 4.2. Confirm: the new head SHA has zero matching inline comments, the Check Run on the new SHA is `success` (even though the slash command may skip the actual review per the documented skip-on-repeat behavior). — HEAD-SHA scoping validated indirectly via frontend#367: total Claude inline comments across 14 commits = 45, but Check Run for head SHA `cde65f2` correctly counts only 18 (the comments belonging to that SHA). If scoping were broken, count would be 45
- [x] 4.4 Verify that no formal PR review (`APPROVED` or `CHANGES_REQUESTED`) is created by Claude on any of the test PRs: `gh pr view <N> --json reviews --jq '.reviews[] | select(.author.login | test("claude"))'` returns nothing. — validated via frontend#367: 45 Claude-authored reviews exist BUT all in `COMMENTED` state (auto-created when posting inline comments). 0 reviews with `APPROVED` or `CHANGES_REQUESTED` state. Spec requirement satisfied
- [x] 4.5 Inspect a `gh api` output from one of the runs to confirm the `commit_id` and `user.login` filter matches reality. Adjust the workflow if the bot login differs from what was recorded in 1.2. — validated: `gh api repos/liverty-music/frontend/pulls/367/comments` returns objects with `user.login == "claude[bot]"` and `commit_id` matching the head SHA. Filter in workflow matches reality, no adjustment needed

## 5. Documentation and archive

- [x] 5.1 Confirm `make check` (or equivalent validation) passes on all four caller-repo PRs — verified via each PR's CI: `CI Success` passed on all 4 caller PRs before merge
- [x] 5.2 After two successful real (non-test) PRs land in any caller repo with the new mechanism, run `/opsx:archive` to archive this change and apply the spec delta to `openspec/specs/ci-optimization/spec.md` — Real PR #1 validated: [frontend#367](https://github.com/liverty-music/frontend/pull/367) (18 inline comments, all high-signal categories, mechanism works as designed). Real PR #2 validated: [backend#305](https://github.com/liverty-music/backend/pull/305) merged 2026-05-28 (51 inline comments surfaced — mostly false positives from model degradation per Layer 3 analysis; mechanism itself counted and published correctly, decision to merge via temporary branch-protection toggle documented in PR #310 follow-up)
