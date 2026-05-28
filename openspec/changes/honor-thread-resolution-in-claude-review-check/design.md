## Context

The `Claude review` Check Run was introduced 2026-05-15 ([archive/2026-05-16-claude-review-check-run](../archive/2026-05-16-claude-review-check-run/)) on the theory that the bot's review output should gate merges via Required Status Checks. Two subsequent changes ([mechanize](../archive/2026-05-28-mechanize-claude-review-verdict/), and the initial revisions of this change) tried to fix progressively-discovered bugs in the gating mechanism:

| Iteration | Mechanism | Discovered failure mode | Outcome |
|---|---|---|---|
| 1 (2026-05-16) | LLM emits `/tmp/claude-verdict.json` | Binary-classification confidence inflation under degraded models ([arxiv 2602.17170](https://arxiv.org/pdf/2602.17170)) | Replaced by mechanize |
| 2 (mechanize, 2026-05-25) | REST `commit_id == HEAD_SHA AND user.login == "claude[bot]"` filter | `commit_id` is auto-bumped forward on every push for still-applicable comments — does NOT mean "posted against this SHA"; misses UI Resolve and empty-commit pushes | Replaced by [.github#6](https://github.com/liverty-music/.github/pull/6) (merged) |
| 3 (.github#6, 2026-05-28) | GraphQL `reviewThreads.isResolved == false AND comments.commit.oid == HEAD_SHA AND author.bot == claude` | Better, but no auto-recompute on UI Resolve clicks; this PR set out to add the recompute trigger | Being reverted by [.github#7](https://github.com/liverty-music/.github/pull/7) |
| 4 (this change's initial design) | Split-job caller + `verdict_only` input + `pull_request_review_thread: [resolved, unresolved]` trigger | The `pull_request_review_thread` trigger is documented as a webhook event but silently disables ALL GitHub Actions triggers on the workflow (spurious push-event stub failures; no `pull_request` runs fire). Verified empirically against this PR's caller workflow changes, and confirmed by 11+ third-party production workflows on GitHub that use the same trigger and are all in `failure` state | Abandoned; this change pivots to Option B |

Investigation through iteration 4 surfaced a deeper question: is the gate even viable upstream? The answer is no:

- [`anthropics/claude-code-action`](https://github.com/anthropics/claude-code-action) (action v1) exposes no verdict, pass/fail, or Check Run output. The README and `docs/custom-automations.md` are silent on the topic.
- All official examples ([`examples/`](https://github.com/anthropics/claude-code-action/tree/main/examples)) — including the three PR-review examples (`pr-review-comprehensive.yml`, `pr-review-filtered-authors.yml`, `pr-review-filtered-paths.yml`) — invoke the action and stop. None create a Check Run, none set workflow conclusion, none gate the merge.
- The [`code-review`](https://github.com/anthropics/claude-code/blob/main/plugins/code-review/commands/code-review.md) slash command itself posts inline comments and a terminal summary — no verdict file, no structured output.

The four-iteration accumulation is therefore not a series of bugs in a supported pattern; it is a series of user-side wrappers for a pattern upstream does not offer. Per the operating instruction "可能な限り構成をシンプルに / 場当たり的なハックは禁止", this change abandons the gate entirely and aligns with the upstream pattern.

## Goals / Non-Goals

**Goals:**

- Align the `Claude review` workflow with the official `anthropics/claude-code-action` pattern (`pr-review-comprehensive.yml`).
- Remove the `Claude review` Check Run, its Pulumi-managed required-status-check enforcement, and all user-side counting / GraphQL / pagination / `verdict_only` logic.
- Preserve `Claude review`'s ability to post inline review comments on PRs (advisory only).
- Eliminate the operating-protocol conflict where the current broken gate forces admin-override merges to bypass branch protection.

**Non-Goals:**

- Replace the gate with a different gating mechanism (e.g., CODEOWNERS-enforced thread-resolution, GitHub App webhook bridge, scheduled recompute). Considered and rejected — see Decision 3.
- Add or migrate to alternative review automation products (Anthropic's hosted Code Review at `claude.com`, third-party bots). Out of scope.
- Change `CI Success` or any other existing required check.
- Reorganize permissions on caller workflows (`checks: write` on each caller becomes unused after this change; harmless and deferred for future cleanup).

## Decisions

### Decision 1: Revert the reusable workflow to the official `pr-review-comprehensive.yml` shape

`liverty-music/.github/.github/workflows/claude-review.yml` becomes a single-job, single-step workflow:

```yaml
name: Reusable Claude Review

on:
  workflow_call:
    secrets:
      CLAUDE_CODE_OAUTH_TOKEN:
        required: true

permissions:
  contents: read
  pull-requests: write
  issues: read
  id-token: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 1
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          plugin_marketplaces: https://github.com/anthropics/claude-code.git
          plugins: code-review@claude-code-plugins
          prompt: '/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }} --comment'
          claude_args: '--allowedTools "Bash(gh pr comment:*),Bash(gh pr diff:*),Bash(gh pr view:*),Bash(gh pr list:*),Bash(gh issue view:*),Bash(gh issue list:*),Bash(gh search:*),mcp__github_inline_comment__create_inline_comment"'
```

Removed: the `verdict_only` input on `workflow_call`; the `Count unresolved Claude review threads` step; the `Publish Claude review Check Run` step; the `checks: write` permission; all pagination loop / GraphQL / jq logic.

**Why:**

- This is the exact shape of [`pr-review-comprehensive.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-comprehensive.yml) with only two delta: (1) the `prompt` invokes the `code-review` slash command instead of inlining review instructions, matching how mechanize structured it; (2) `secrets.CLAUDE_CODE_OAUTH_TOKEN` is used rather than `secrets.ANTHROPIC_API_KEY` because liverty-music authenticates via Claude OAuth.
- No custom code = no custom bugs. Future upstream improvements (e.g., if Anthropic adds a verdict mechanism) are picked up by bumping the action pin.

**Alternative considered:** Keep the GraphQL-`isResolved` post-step but remove the Check Run creation, just for telemetry. Rejected — telemetry without a gate is unused information and still drags in pagination / filter logic that has to be maintained.

### Decision 2: Drop `'Claude review'` from `requiredStatusCheckContexts` in Pulumi

`cloud-provisioning/src/index.ts` updates all four `GitHubRepositoryComponent` invocations to `requiredStatusCheckContexts: ['CI Success']`. The Pilot-graduation comment on the `specification` entry is removed.

**Why:**

- If Decision 1 ships and the required check stays, every PR is permanently blocked — the `Claude review` Check Run is no longer created, so it can never turn green. Pulumi must lead Decision 1's deploy.
- `'CI Success'` remains as the deterministic gate (lint, test, build, etc.). This is the same set of checks that gated PRs before the mechanize / honor-thread-resolution arc.

### Decision 3: No replacement gating mechanism

Considered and rejected:

- **GitHub App webhook bridge**: A small App listening for `pull_request_review_thread` webhooks and triggering `repository_dispatch` events. Solves the auto-recompute problem but adds an external service to operate, a secret to manage, and rate-limit considerations. Disproportionate complexity for the value.
- **`workflow_dispatch` manual recompute**: Add a manual "Recompute verdict" button to the Actions UI. Half-measure — the Check Run still exists, still needs the count logic, still has all the maintenance burden, in exchange for an affordance that humans rarely click. Worse total cost than just deleting the gate.
- **CODEOWNERS-gated `isResolved` filter**: Only count threads resolved by a non-author CODEOWNER as truly resolved. Adds code complexity, governance subtleties, and doesn't solve the resolve-without-push problem.
- **Periodic cron recompute**: A scheduled workflow that walks open PRs and updates Check Runs. Adds a cron, walks a quota, and produces stale-by-design results.

The principled choice is: **bot review is advisory by nature; treat it as such.** Reviewers (human + automation) see comments and act on them; merge is gated on objective, deterministic checks.

### Decision 4: Caller workflows on all four repos remain unchanged

`.github/workflows/claude-code-review.yml` on `backend`, `frontend`, `specification`, `cloud-provisioning` keeps:

```yaml
on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
permissions:
  contents: read
  pull-requests: write
  issues: read
  id-token: write
  checks: write   # unused after Decision 1; harmless, deferred for cleanup
jobs:
  review:
    uses: liverty-music/.github/.github/workflows/claude-review.yml@main
    secrets: inherit
```

**Why:**

- The reusable workflow's `workflow_call` interface no longer accepts `verdict_only`. Caller workflows that don't pass that input continue to work — no breaking change for callers.
- The shape matches the official `pr-review-comprehensive.yml` `on:` block exactly.
- No need to add `pull_request_review_thread`, `workflow_dispatch`, or any other re-trigger affordance — there's no Check Run to recompute.
- The `checks: write` permission becomes unused but is harmless. Cleaning it up across four repos is deferred to a follow-up tidy PR.

### Decision 5: Document the historical arc in the spec delta but keep the canonical spec lean

The spec delta in this change rewrites the `Claude review publishes its verdict as a GitHub Check Run` requirement to a simpler "Claude review posts advisory inline comments" requirement, and removes the `Claude review is enforced as a Required Status Check via Pulumi` requirement and the pilot-rollout requirement.

The why-trail (LLM verdict → REST `commit_id` → GraphQL `isResolved` → broken trigger → revert) is captured in this design.md and in the [issue #525](https://github.com/liverty-music/specification/issues/525) thread. It is NOT reproduced in the canonical spec — the spec describes the current state of the system, not the historical journey.

**Why:**

- Canonical specs that document failed approaches become "if-not, why-not" mazes that obscure the current contract.
- The archive of `mechanize-claude-review-verdict` and this change's design.md jointly preserve the chronological record for anyone investigating the operating-protocol clash referenced in CLAUDE.md.

## Risks / Trade-offs

- **[Loss of forced response to bot findings]** → Reviewers can now merge a PR with un-addressed Claude review comments. Mitigation: human reviewers should treat the bot's output as an input to their review, same as any other reviewer. The bot is advisory by nature ([upstream pattern](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-comprehensive.yml)) and treating it otherwise — as we found over four iterations — fights the tool.

- **[Bot still spends Anthropic API budget on every PR push]** → No change from current state. If cost becomes a concern, separate work to add path/author filters (per [`pr-review-filtered-authors.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-filtered-authors.yml) and [`pr-review-filtered-paths.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-filtered-paths.yml)).

- **[CLAUDE.md "NEVER skip hooks unless explicitly requested" guard becomes vacuous for Claude review]** → The guard applied because admin-override was the only way past the stuck Check Run. After this change there is no Check Run to override; the guard is unaffected for other checks (lint, test, signing). Update CLAUDE.md if the guard's existing wording specifically references Claude review (none observed at the time of writing).

- **[`permissions: checks: write` on each caller becomes unused]** → No functional impact. Defer cleanup to a tidy PR.

- **[Pulumi deploy ordering risk]** → If `.github#7` merges before `pulumi up -s prod` is applied, every open PR becomes permanently un-mergeable. Deployment ordering documented in `proposal.md` "Deployment ordering" section and in the Pulumi PR description.

## Migration Plan

See `proposal.md` "Deployment ordering". Summary:

1. Merge [`cloud-provisioning#311`](https://github.com/liverty-music/cloud-provisioning/pull/311).
2. Run `pulumi up -s prod`. Verify required checks via `gh api ...` on all four repos.
3. Merge [`.github#7`](https://github.com/liverty-music/.github/pull/7).
4. Merge this PR ([`specification#526`](https://github.com/liverty-music/specification/pull/526)).
5. Open a normal follow-up PR on any repo to confirm: Claude review posts inline comments (if any), no `Claude review` Check Run is created, merge gating is `CI Success` only.
6. Archive this change.

**Rollback (order is the inverse of the forward migration):** Restore the `.github` reusable workflow to its pre-#7 state **first** — so the `Claude review` Check Run resumes being created — then re-apply `'Claude review'` to `requiredStatusCheckContexts` via Pulumi (`pulumi up -s prod`). Reversing this order (Pulumi-first) re-creates the same un-mergeable window the forward plan avoided: Pulumi would require a check the workflow no longer produces. The Check Run resumes with the GraphQL-`isResolved` logic from `.github#6`. Rollback restores the bug behavior (stuck failures from non-code-resolved threads) but is operationally safe.

## Open Questions

- Should we add path filters per [`pr-review-filtered-paths.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-filtered-paths.yml) to skip review on cosmetic-only PRs (e.g., openspec doc changes)? Deferred — separate work, not blocking this change.
- Should `permissions: checks: write` be removed from all four caller workflows? Deferred — harmless, tidy-PR.
- If a future need arises to revisit gating, the principled path is to wait for an upstream feature (Anthropic-side Check Run support in `claude-code-action`) rather than to rebuild the wrapper. Open as a research watch.
