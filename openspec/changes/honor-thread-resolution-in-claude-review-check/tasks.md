## 1. Preparation

- [x] 1.1 Archive `mechanize-claude-review-verdict` (after confirming `tasks.md` §5.2 acknowledges that the resolution-signal gap is being addressed in this follow-up change) so that its spec delta lands in canonical `openspec/specs/ci-optimization/spec.md`. Without this, the MODIFIED requirement in §2 of this change targets outdated canonical text. — archived to `archive/2026-05-28-mechanize-claude-review-verdict/`; canonical now contains the `commit_id == HEAD_SHA` text that this change MODIFIES
- [x] 1.2 Create tracking issue in `liverty-music/specification` titled `Honor thread resolution in Claude review Check Run` and note its number for all subsequent commits (`Refs: #<N>`). — created as [#525](https://github.com/liverty-music/specification/issues/525)
- [x] 1.3 Re-confirm the Claude bot identity by inspecting an existing resolved-thread PR via GraphQL. — Verified 2026-05-28 against frontend#367: bot login in GraphQL is `"claude"` (NOT `"claude[bot]"` as in REST), `__typename == "Bot"`. Design and spec updated to reflect actual values and use both fields for defensive matching.

## 2. Reusable workflow (`liverty-music/.github`)

- [x] 2.1 Create branch off `main` in the `.github` repo. — branch `525-honor-thread-resolution`
- [x] 2.2 Edit `.github/workflows/claude-review.yml`: add `if: github.event_name == 'pull_request'` to the `Run Claude review` step. — applied in liverty-music/.github#5
- [x] 2.3 Replace the `Count Claude inline comments` step body. — applied in liverty-music/.github#5
- [x] 2.4 GraphQL pageInfo.hasNextPage handling. — applied in liverty-music/.github#5
- [x] 2.5 jq filter applied. — applied in liverty-music/.github#5 (uses __typename + login)
- [x] 2.6 Publish step verified to still map count → conclusion correctly. — unchanged from mechanize; differentiated `(>100 threads)` title deferred
- [x] 2.7 Open PR in `liverty-music/.github`. — [liverty-music/.github#5](https://github.com/liverty-music/.github/pull/5); merge pending CI

## 3. Caller workflows (4 repos)

- [x] 3.1 `liverty-music/specification` caller workflow updated. — [#526](https://github.com/liverty-music/specification/pull/526); merge pending CI
- [x] 3.2 `liverty-music/backend` caller workflow updated. — [#311](https://github.com/liverty-music/backend/pull/311); merge pending CI
- [x] 3.3 `liverty-music/frontend` caller workflow updated. — [#371](https://github.com/liverty-music/frontend/pull/371); merge pending CI
- [x] 3.4 `liverty-music/cloud-provisioning` caller workflow updated. — [#310](https://github.com/liverty-music/cloud-provisioning/pull/310); merge pending CI

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
