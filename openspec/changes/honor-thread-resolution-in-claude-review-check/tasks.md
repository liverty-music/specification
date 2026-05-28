## 1. Preparation

- [x] 1.1 Archive `mechanize-claude-review-verdict` (after confirming `tasks.md` §5.2 acknowledges that the resolution-signal gap is being addressed in this follow-up change) so that its spec delta lands in canonical `openspec/specs/ci-optimization/spec.md`. Without this, the MODIFIED requirement in §2 of this change targets outdated canonical text. — archived to `archive/2026-05-28-mechanize-claude-review-verdict/`; canonical now contains the `commit_id == HEAD_SHA` text that this change MODIFIES
- [ ] 1.2 Create tracking issue in `liverty-music/specification` titled `Honor thread resolution in Claude review Check Run` and note its number for all subsequent commits (`Refs: #<N>`).
- [x] 1.3 Re-confirm the Claude bot identity by inspecting an existing resolved-thread PR via GraphQL. — Verified 2026-05-28 against frontend#367: bot login in GraphQL is `"claude"` (NOT `"claude[bot]"` as in REST), `__typename == "Bot"`. Design and spec updated to reflect actual values and use both fields for defensive matching.

## 2. Reusable workflow (`liverty-music/.github`)

- [ ] 2.1 Create branch off `main` in the `.github` repo (e.g., `<N>-honor-thread-resolution`).
- [ ] 2.2 Edit `.github/workflows/claude-review.yml`: add `if: github.event_name == 'pull_request'` to the `Run Claude review` step.
- [ ] 2.3 Replace the `Count Claude inline comments` step body: drop the REST `gh api repos/<owner>/<repo>/pulls/<N>/comments` call and the `commit_id == HEAD_SHA` filter; add a `gh api graphql` call with the `reviewThreads` query from `design.md` Decision 1.
- [ ] 2.4 In the new count step, after the GraphQL call succeeds, check `pageInfo.hasNextPage`. If `true`, write `count=-1` to `$GITHUB_OUTPUT` and exit 0 (publish step will emit `neutral`).
- [ ] 2.5 In the new count step, apply the jq filter `[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false and .isOutdated == false and .comments.nodes[0].author.__typename == "Bot" and .comments.nodes[0].author.login == "claude")] | length` and write the result to `$GITHUB_OUTPUT`.
- [ ] 2.6 Verify the existing `Publish Claude review Check Run` step still maps `count → conclusion` correctly: `0 → success`, `≥1 → failure`, `-1 → neutral`. Update the `neutral` title to optionally append `(>100 threads)` when `count == -1` and the GraphQL call succeeded (vs. when it failed entirely). Both paths still map to `count == -1` from the bash step's perspective; the title differentiation MAY be deferred.
- [ ] 2.7 Open PR in `liverty-music/.github`; merge after CI passes.

## 3. Caller workflows (4 repos)

- [ ] 3.1 `liverty-music/specification`: edit `.github/workflows/claude-code-review.yml` `on:` block — add `pull_request_review_thread: { types: [resolved, unresolved] }` alongside the existing `pull_request:` trigger. Open PR; merge.
- [ ] 3.2 `liverty-music/backend`: same edit. Open PR; merge.
- [ ] 3.3 `liverty-music/frontend`: same edit. Open PR; merge.
- [ ] 3.4 `liverty-music/cloud-provisioning`: same edit. Open PR; merge.

## 4. Validation

- [ ] 4.1 Open a small test PR on `liverty-music/specification` containing a deliberate CLAUDE.md violation. Confirm `Claude review` runs to completion, posts at least one inline comment, and the Check Run is `failure` with the correct count.
- [ ] 4.2 In that PR, click "Resolve conversation" on one of the bot threads (without pushing any commit). Confirm: (a) GitHub fires `pull_request_review_thread.resolved`, (b) the caller workflow re-invokes the reusable workflow, (c) the `Run Claude review` step is **skipped** (verified via the Actions UI showing the step as "Skipped"), (d) the count step runs and produces `count = N-1`, (e) the Check Run is republished with the new count.
- [ ] 4.3 Click "Unresolve conversation" on the same thread. Confirm the workflow re-fires on `pull_request_review_thread.unresolved` and the Check Run flips back to the original count.
- [ ] 4.4 Resolve every remaining bot thread. Confirm the Check Run flips to `conclusion: success`, title `No issues found`, **without any code change being pushed**.
- [ ] 4.5 Push a commit that would normally re-trigger Claude. Confirm the `Run Claude review` step **does** execute (the `if` guard is satisfied on `pull_request.synchronize`).
- [ ] 4.6 Re-verify on a real second PR (any backend or frontend PR with bot findings) that the resolve-to-clear workflow works in non-pilot repos.

## 5. Documentation and archive

- [ ] 5.1 Confirm `make check` (or equivalent validation) passes on all four caller-repo PRs before merge.
- [ ] 5.2 (Optional) Add a one-line note to each repo's `CLAUDE.md` (or the workspace-level `CLAUDE.md`) explaining that maintainers can clear `Claude review` failures by clicking "Resolve conversation" on bot threads, and that the Check Run recomputes within seconds.
- [ ] 5.3 After two successful real PRs land using the new mechanism (one with resolve-to-clear actually exercised), run `/opsx:archive` to archive this change and apply the spec delta to `openspec/specs/ci-optimization/spec.md`.
