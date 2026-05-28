## Context

The `Claude review` Check Run was first introduced [2026-05-16](../archive/2026-05-16-claude-review-check-run/) (LLM-emitted verdict via `/tmp/claude-verdict.json`), then redesigned [2026-05-25](../mechanize-claude-review-verdict/) to derive its conclusion from a mechanical count of bot-authored inline comments scoped by `commit_id == HEAD_SHA`. The redesign correctly addressed the LLM confidence-inflation problem documented in that change's `design.md`.

Two real-world PRs immediately exposed a second-order bug that the redesign's validation (`tasks.md` §4.3) did not probe. Frontend [`#367`](https://github.com/liverty-music/frontend/pull/367) and backend [`#305`](https://github.com/liverty-music/backend/pull/305) ran the full bot review cycle (17 rounds, 100+ inline comments accumulated), then the maintainer marked every thread `isResolved = true` via the standard GitHub UI. The `Claude review` Check Run stayed at `18 issue(s) found` (frontend) and `51 issue(s) found` (backend) — both PRs were merged via admin override.

Root-cause investigation showed that GitHub's REST `/pulls/N/comments` field `commit_id` is not what the redesign assumed. It is **not** "the SHA the comment was posted against" (that field exists too, as `original_commit_id`); it is "the most recent SHA where the line being commented on is still present in the diff". GitHub re-evaluates every inline comment on every push and bumps `commit_id` forward if the line is unchanged. Therefore the filter `commit_id == HEAD_SHA` selects bot comments **still applicable to the current code** — which is a strict subset of "issues the reviewer hasn't acknowledged".

The fix is to switch the resolution signal from `commit_id` (REST) to `isResolved` (GraphQL), which honors all three reviewer acknowledgement paths (UI resolve, code-change resolve, defended-via-reply-then-resolve).

## Goals / Non-Goals

**Goals:**

- Make `Claude review` Check Run honor GitHub-native thread resolution (the "Resolve conversation" button).
- Continue to honor code-change resolution (covered by `isOutdated`).
- Re-fire the Check Run on resolve/unresolve clicks so feedback is immediate, without forcing a no-op commit.
- Avoid burning Anthropic API tokens (and re-posting nits) when the workflow is re-triggered by a resolve event.
- Preserve every preserved property of `mechanize-claude-review-verdict`: Check Run name, conclusion vocabulary, branch-protection contract, caller-workflow surface area, no Pulumi changes.

**Non-Goals:**

- Fix the upstream `code-review` skip-on-repeat behavior ([anthropics/claude-code#19618](https://github.com/anthropics/claude-code/issues/19618)). Still mitigated, not resolved.
- Add CODEOWNERS-based governance for who can resolve threads. The default GitHub trust model (anyone with write access) is consistent with branch-protection trust.
- Add a `claude-review-acknowledged` label override. The `isResolved` mechanism already provides a per-thread acknowledgement affordance with the same authority surface; a label override would be redundant and would defeat the per-thread granularity.
- Migrate to the cloud-hosted "Code Review" product on `claude.com`.

## Decisions

### Decision 1: GraphQL `reviewThreads` with `isResolved` and `isOutdated` filters replaces REST `commit_id` filter

The reusable workflow's count step calls `gh api graphql` against:

```graphql
query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      reviewThreads(first: 100) {
        pageInfo { hasNextPage }
        nodes {
          isResolved
          isOutdated
          comments(first: 1) {
            nodes { author { __typename login } }
          }
        }
      }
    }
  }
}
```

The filter is:

```jq
[
  .data.repository.pullRequest.reviewThreads.nodes[]
  | select(.isResolved == false
           and .isOutdated == false
           and .comments.nodes[0].author.__typename == "Bot"
           and .comments.nodes[0].author.login == "claude")
] | length
```

**Bot identity note (verified 2026-05-28 against frontend#367):** GitHub's GraphQL Author interface returns bot login *without* the `[bot]` suffix (e.g., `"claude"`), unlike the REST API which returns `"claude[bot]"`. The `__typename == "Bot"` guard ensures we cannot be spoofed by a human GitHub user named "claude".

**Why:**

- `isResolved` reflects the standard GitHub UI affordance (the "Resolve conversation" button). Using it as the resolution signal aligns the Check Run with the reviewer's own mental model.
- `isOutdated` is GitHub's authoritative judgment of "is this comment still applicable to the diff" — strictly broader and more accurate than the REST `commit_id` heuristic, since it also covers cases where the line was moved or its surrounding context changed.
- `comments.nodes[0]` is the thread opener. GraphQL's default ordering for `comments` is chronological, so the first node is reliably the bot. (In our workflow Claude always opens threads; maintainer replies are never thread openers.)
- `first: 100` keeps the query under GitHub's hard cap of 100 nodes per page and avoids cursor pagination complexity. Healthy PRs are far below this limit; see Decision 4.

**Alternative considered:** Use the REST `/pulls/N/comments` endpoint and filter by `in_reply_to_id` and a separate "is thread resolved" lookup. Rejected because the REST API does not expose thread-resolved state — `isResolved` is a GraphQL-only concept on the `PullRequestReviewThread` object.

**Alternative considered:** Use `original_commit_id` + a side-channel "issues acknowledged" registry. Rejected because GitHub already provides the registry as `reviewThreads.isResolved`.

### Decision 2: Add `pull_request_review_thread` to caller-workflow `on:` triggers

Each caller workflow at `<repo>/.github/workflows/claude-code-review.yml` adds:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
  pull_request_review_thread:
    types: [resolved, unresolved]
```

**Why:**

- Without this, clicking "Resolve conversation" does nothing observable to the Check Run — the failure persists until something else (manual re-run, no-op push) re-fires the workflow. That breaks the reviewer's expectation of immediate feedback.
- GitHub fires `pull_request_review_thread` events with full `pull_request` context in the payload, so the reusable workflow's `github.event.pull_request.number` and `.head.sha` continue to work without changes.
- `unresolved` is included so that re-opening a thread also recomputes the Check Run, restoring `failure` symmetrically.

**Trigger documentation note (verified 2026-05-28):** The official GitHub Actions ["Events that trigger workflows" reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) does NOT list `pull_request_review_thread` as a workflow trigger. The webhook event IS documented at the [webhook reference](https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request_review_thread) with activity types `resolved` and `unresolved`. The Actions runtime supports this trigger even though the Actions docs are silent on it — verified by 11+ production workflows on GitHub using `on: pull_request_review_thread: types: [resolved, unresolved]` (e.g., [`akasper/plate_template/feedback-resolution-check.yml`](https://github.com/akasper/plate_template/blob/main/.github/workflows/feedback-resolution-check.yml), [`smart-village-solutions/sva-studio/bot-comment-governance.yml`](https://github.com/smart-village-solutions/sva-studio/blob/main/.github/workflows/bot-comment-governance.yml)). YAML schema validators (vscode-github-actions extension included) may flag this as an unknown property — false positive due to outdated schema.

**Alternative considered:** Add only `pull_request_review_thread.types: [resolved]`. Rejected for asymmetry — unresolving must also reflect immediately, otherwise an accidentally-resolved-then-unresolved thread leaves the Check Run stuck on `success`.

**Alternative considered:** Use `pull_request_review.types: [submitted]`. Rejected because it fires on every review submission (formal review or comment batch), not on resolve, and the count step is decoupled from review submissions.

### Decision 3: Guard the `Run Claude review` step with `if: github.event_name == 'pull_request'`

Inside the reusable workflow, the `anthropics/claude-code-action@v1` step is gated:

```yaml
- name: Run Claude review
  id: claude
  if: github.event_name == 'pull_request'
  uses: anthropics/claude-code-action@v1
  with: ...
```

The count step and publish step remain ungated (`if: always()` for the count, no conditional for publish).

**Why:**

- Resolve clicks should recompute the verdict cheaply. Re-running Claude on every resolve click would (a) burn Anthropic API tokens for no signal change, (b) likely re-post the same nits the maintainer just resolved, creating a cycle.
- The count step's input (the set of review threads) is independent of whether Claude just ran — it queries the live PR state — so skipping Claude on thread events still produces a correct count.

**Alternative considered:** Run Claude on every trigger and rely on the skip-on-repeat upstream behavior to be cheap. Rejected because skip-on-repeat is not free (the action still spins up, reads the diff, and decides to skip), and skip-on-repeat is itself a known-unreliable behavior under model degradation.

### Decision 4: Fail-neutral on >100 threads (pagination overflow)

If the GraphQL response's `pageInfo.hasNextPage == true`, the count step writes `count=-1` and the publish step emits `conclusion: neutral` with title `Verdict could not be computed (>100 threads)`.

**Why:**

- A PR with >100 review threads is unhealthy regardless of who authored them. Neither auto-passing nor auto-failing is meaningful; surface ambiguity and let humans investigate.
- The highest observed count in production is 66 threads (backend#305), so 100 is a comfortable ceiling for healthy PRs.
- Implementing cursor pagination would add ~15 lines of bash and a second `gh api` call; on a runaway PR it would just produce a high but uninformative count.

### Decision 5: Bot-author detection unchanged (`user.login == "claude[bot]"`)

The bot identity check is the same exact-match used in `mechanize-claude-review-verdict` task 1.2.

**Why:**

- Risk surface is unchanged from the predecessor change.
- If Anthropic ever renames the bot identity, this filter silently produces `count=0` (success). Same risk as the predecessor; mitigated by the same logic — if zero threads match the filter but the GraphQL response had any bot threads from any author, that would warrant escalation. (Not implemented as code; documented as a known-unmonitored risk.)

## Risks / Trade-offs

- **[Stale `failure` until a re-trigger fires]** → After this change, clicking "Resolve conversation" re-fires the workflow, so the lag is bounded by GitHub's event delivery (<10s in practice). Before either workflow_dispatch or a commit could clear it. This is a strict improvement.

- **[Resolve-as-mute by PR author]** → The default GitHub trust model lets the PR author resolve their own threads, which silences the bot's gate. This is consistent with the existing branch-protection trust (PR authors with write access can also approve merges via admin override). Documented as expected behavior in the migration plan; not a CODEOWNERS-enforced restriction. If this becomes a problem, a follow-up change can introduce a CODEOWNERS check.

- **[Replay attack: maintainer resolves all threads, then bot re-reviews on next push and re-flags them]** → Acceptable. The bot is the source of truth on whether an issue still exists. If it re-flags, the maintainer can defend and re-resolve, or fix the code. The Check Run reflects the latest state.

- **[`pull_request_review_thread` event delivery delay]** → GitHub does not document a delivery SLA. If the event is delayed or dropped, the Check Run stays stale until the next `pull_request` synchronize. Mitigation: nothing — the predecessor failure mode was worse (stuck permanently), so a brief stuck state on event drops is an acceptable degradation.

- **[GraphQL rate limits]** → The default `GITHUB_TOKEN` has a 5,000-point/hour rate budget for GraphQL. This query is single-shot and ~2 points. Even pathological re-trigger volume (one resolve click per second) is well within budget.

- **[>100 threads collapses to neutral, blocking the gate from concluding]** → The `requiredStatusCheckContexts` rule treats `neutral` as a pass (per GitHub's documented behavior). A PR that overflows would be merge-eligible despite an unreviewed state. Acceptable: this is a degenerate PR that needs human attention regardless.

- **[Caller-workflow `on:` block change is required in 4 repos]** → Cannot be done purely in the reusable workflow because `on:` is owned by the caller. This makes the rollout a 5-PR fan-out instead of 1. Documented in the migration plan.

## Migration Plan

1. **Archive `mechanize-claude-review-verdict`** so its spec delta lands in canonical `openspec/specs/ci-optimization/spec.md`. The current canonical still describes the verdict-file mechanism — without archiving first, this change's MODIFIED requirement would target outdated text and create a delta-against-delta state.
2. Create tracking issue in `liverty-music/specification` ("Honor thread resolution in Claude review Check Run").
3. Land the `.github` repo change first (reusable workflow): GraphQL count step + Claude-run step guard. All four caller workflows reference `@main`, so they pick up the new logic on the next push.
4. Land the four caller-repo changes (add `pull_request_review_thread` to `on:`). Order does not matter.
5. **Validate** on a real PR by deliberately reproducing the bug-and-fix cycle:
   - Open a PR that intentionally contains a CLAUDE.md violation.
   - Confirm `Claude review` = `failure` with a non-zero count.
   - Click "Resolve conversation" on each bot thread via the GitHub UI (no commit push).
   - Confirm the workflow re-runs on `pull_request_review_thread.resolved`, and the Check Run flips to `success` within ~30s.
   - Click "Unresolve" on one thread.
   - Confirm the workflow re-runs and Check Run flips back to `failure` with count 1.
6. (Optional) Land a documentation update in each repo's `CLAUDE.md` describing the resolve-to-clear flow.
7. Archive this change.

**Rollback:** Revert the merge commits in `liverty-music/.github` and the four caller repos. The Check Run returns to the (broken-but-tolerated) `commit_id == HEAD_SHA` behavior — but production has been operating in that broken state for the entire mechanize window, so rollback is safe.

## Open Questions

- Should the `Claude review` Check Run's summary link to the unresolved threads filter (`?reviewer=claude%5Bbot%5D` style) in addition to the Files-changed view? Defer; can be a non-breaking enhancement after the core fix lands.
- Should the workflow also include `pull_request_review_thread.types: [outdated]`? GitHub does not currently document `outdated` as a `pull_request_review_thread` event subtype, so likely no. To be verified during implementation by inspecting webhook delivery on a real outdated event.
- Should the `Run Claude review` step also be skipped on `workflow_dispatch` (manual recompute), or is keeping it gated to `pull_request` enough? Likely yes — `workflow_dispatch` is the natural "I want to force a recount without re-reviewing" trigger. To be confirmed once the workflow is functioning.
