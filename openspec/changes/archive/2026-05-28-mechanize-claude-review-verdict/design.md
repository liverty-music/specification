## Context

The `Claude review` Check Run was introduced 2026-05-15 ([archive/2026-05-16-claude-review-check-run](../archive/2026-05-16-claude-review-check-run/)) to surface code-review verdicts in the PR list view and gate merges via Required Status Checks. The implementation asked the wrapping LLM agent — orchestrated by `anthropics/claude-code-action@v1` — to invoke the `/code-review:code-review` slash command, then write `/tmp/claude-verdict.json` containing a binary pass/fail verdict that a subsequent `actions/github-script` step mapped to a Check Run `conclusion`.

Investigation conducted 2026-05-25 found that this design deviates from official `anthropics/claude-code-action` and `code-review` plugin patterns in six places (`additional_focus` free-text injection, factually-wrong "sticky comment" prompt wording, Step 1 / Step 2 wrapping, user-invented verdict-file mechanism, `--allowedTools` mismatch with the slash command's frontmatter, and unhandled skip-on-repeat behavior). Each deviation is independently documented in `anthropics/claude-code-action` issues (notably [#1087](https://github.com/anthropics/claude-code-action/issues/1087), [#590](https://github.com/anthropics/claude-code-action/issues/590), [anthropics/claude-code#19618](https://github.com/anthropics/claude-code/issues/19618)) and in academic literature on LLM confidence inflation under binary classification pressure ([arxiv 2602.17170](https://arxiv.org/pdf/2602.17170), [arxiv 2604.01457](https://arxiv.org/pdf/2604.01457)).

The Anthropic model-serving incidents of 2026-05-18 to 2026-05-22 (multiple `Opus 4.7`, `Sonnet 4.6`, `Haiku 4.5` elevated-error events per [status.claude.com](https://status.claude.com/)) amplified the consequences of these deviations into user-visible symptoms: nit-level comment overload, "HIGH SIGNAL only" filter being ignored, and self-contradicting verdicts within a single PR's review loop. Plugin source confirms the `code-review` slash command itself has not changed since 2026-04-10, and `anthropics/claude-code-action` v1.0.133 (2026-05-23) only bumped the underlying SDK without behavior changes — so the regression locus is the user-side wrapper, with model wobble as the amplifier.

## Goals / Non-Goals

**Goals:**

- Eliminate binary pass/fail verdict pressure on the LLM (replace with deterministic post-step counting).
- Restore alignment with official `anthropics/claude-code-action` invocation patterns (single-line `prompt:`, slash command standalone).
- Preserve the `Claude review` Check Run name, the Required Status Check gating policy, and the pilot-then-rollout deployment posture (no Pulumi changes).
- Reduce the prompt-injection surface (remove `additional_focus` free-text input).
- Make the workflow's `--allowedTools` agree with the slash command's declared frontmatter, removing silent subagent failures.

**Non-Goals:**

- Fix the upstream skip-on-repeat behavior ([anthropics/claude-code#19618](https://github.com/anthropics/claude-code/issues/19618)). Mitigated by HEAD-SHA-scoped counting, not resolved.
- Improve plugin output quality during Anthropic-side incidents (out of our control).
- Migrate to the cloud-hosted "Code Review" product (`REVIEW.md`-based) on `claude.com`. Mentioned as a future option, not adopted here.
- Change the Pulumi branch-protection contract or Required Status Check name.
- Change per-repo `CLAUDE.md` files (the "Go conventions / pgx" content previously injected via `additional_focus` is already documented there).

## Decisions

### Decision 1: Mechanical comment counting replaces LLM-emitted verdict file

The Check Run `conclusion` is derived in a bash post-step that calls `gh api repos/<owner>/<repo>/pulls/<N>/comments`, filters to comments whose `commit_id` equals the PR head SHA AND whose `user.login` indicates the Claude bot (e.g., `claude[bot]`), and counts the result. Zero comments → `success`. One or more → `failure`. Any error fetching → `neutral`.

**Why:**

- LLM-emitted binary verdicts are documented to suffer confidence inflation under fail-justifying prompts ([arxiv 2602.17170](https://arxiv.org/pdf/2602.17170)). Removing the LLM from the verdict path removes the inflation pressure entirely.
- The post-step observes the same artifact a human reviewer sees on the PR (the inline comments). There is no second source of truth.
- HEAD-SHA scoping prevents stale comments from prior pushes inflating the count — partially mitigating the skip-on-repeat scenario where the slash command exits early on subsequent pushes.

**Alternative considered:** Use the action's `outputs.structured_output` with a `--json-schema`. Rejected because the `code-review` plugin emits a natural-language summary, not structured output, and changing the plugin is out of scope.

**Alternative considered:** Use `track_progress: true` from the official examples. Rejected for the same reason — `track_progress` surfaces UI progress, not a machine-readable verdict.

### Decision 2: Remove `additional_focus` input entirely

The reusable workflow's `additional_focus` input is removed. Caller workflows drop their `with: additional_focus:` blocks. Per-repo review focus is expressed in each repo's `CLAUDE.md`.

**Why:**

- The `/code-review` slash command's only documented argument is `--comment`. `additional_focus` was injected as free-form text between Step 1 and Step 2 of the wrapper prompt — semantically identical to a prompt-injection pattern (per [OWASP guidance](https://owasp.org/www-community/attacks/PromptInjection)).
- Under degraded models, the additional-focus text reads as "also flag X" rather than "ALSO use this as filter context", which directly opposes the plugin's "HIGH SIGNAL only" instruction and causes nit volume to spike.
- The content previously injected ("Go conventions, error handling, table-driven tests, pgx usage" for backend; equivalents for other repos) is already in each repo's `CLAUDE.md`, which the slash command's CLAUDE.md-audit agents already read. There is no information loss.

**Alternative considered:** Move `additional_focus` content into a per-repo `REVIEW.md`. Rejected because the open-source `code-review` plugin (which we use) reads `CLAUDE.md`, not `REVIEW.md` — `REVIEW.md` is a feature of the separate cloud-hosted Code Review product on `claude.com`.

### Decision 3: Restore single-line `prompt:` and align `--allowedTools` with slash-command frontmatter

The reusable workflow's `prompt:` becomes one line: `'/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }} --comment'`. The "Step 1 / Step 2" wrapping is removed. `claude_args.--allowedTools` adds `Bash(gh pr list:*)` to match the slash command's declared `allowed-tools` frontmatter; `Write` is removed (no verdict file to write).

**Why:**

- All 10 official examples in `anthropics/claude-code-action/examples/` and 8 use cases in `docs/solutions.md` invoke slash commands standalone, not wrapped in numbered steps.
- The slash command has its own internal step-1-through-9 structure (`code-review.md`). Nesting an outer "Step 1 / Step 2" forces the wrapper agent to choose between solving outer steps and delegating to inner steps — a state of instruction conflict that fails first under model degradation.
- `--allowedTools` per [anthropics/claude-code#37683](https://github.com/anthropics/claude-code/issues/37683) does not block tools; it only removes approval prompts. On CI runners with no human to approve, a missing tool from the allowlist causes subagent hang/timeout.

### Decision 4: Check Run name, Required Status Check, and pilot/rollout posture unchanged

The Check Run is still named `Claude review`. The Pulumi `requiredStatusCheckContexts` configuration in `cloud-provisioning/src/index.ts` is untouched. The conclusion vocabulary (`success` / `failure` / `neutral`) is unchanged.

**Why:**

- Branch-protection settings are environment-gated (`prod` only) and stable. Touching them widens blast radius and forces a Pulumi PR. The mechanical-counting change is workflow-only.
- The conclusion semantics from the consumer's perspective (GitHub branch protection) are identical: `failure` blocks merge, `success` allows, `neutral` allows. Only the derivation mechanism inside the workflow changes.

### Decision 5: Tracking issue created in `liverty-music/specification` before implementation

A new tracking issue is created in `liverty-music/specification` ahead of any workflow PR, mirroring the prior `#474` precedent. The issue number is referenced in all PR commits per the liverty-music commit convention (`Refs: #<issue-number>`).

**Why:**

- The change spans four caller-repo PRs plus one `.github` repo PR. Without a single tracking issue, the audit trail fragments.

## Risks / Trade-offs

- **[Skip-on-repeat: second push gets no fresh review]** → Mitigation: HEAD-SHA scoping ensures `failure` doesn't persist from stale prior-push comments. If the second push fixes the issues from the first push, the count returns to zero and the Check Run flips to `success`. Trade-off: a second push that introduces NEW bugs won't be caught — accepted because this matches the plugin's documented behavior and is upstream-only fixable.
- **[Bot-author detection brittleness]** → The post-step filters by `user.login` matching the Claude bot identity. If Anthropic changes the bot's GitHub identity (rename, app re-installation), the filter silently breaks → `success` despite issues posted. Mitigation: assert at least one of the filtered comments has the expected `user.type == "Bot"` or `user.login` pattern; fail to `neutral` rather than `success` if zero comments match BUT inline comments exist on the head SHA from any bot.
- **[Comments from non-Claude bots on same PR]** → A different bot (Dependabot, Renovate) posting inline comments on the same PR head SHA could inflate the count. Mitigation: the `user.login` filter is exact-match to Claude's bot identity, not a generic "is a bot" check.
- **[`gh api` rate limits or network errors]** → The post-step uses the workflow's `GITHUB_TOKEN`, which has generous limits, but transient errors are possible. Mitigation: on `gh api` non-zero exit, publish Check Run with `conclusion: neutral` and a summary indicating "verdict computation failed".
- **[Loss of the "fail with summary text" UX]** → Previously the Check Run's `output.title` showed `N issue(s) found` derived from the LLM's verdict JSON. Mechanical counting still gives `N`, but the LLM-authored one-line `summary` field is gone. Mitigation: include the count in the title (`N issue(s) found`) and link to the PR inline-comments view in the `summary`. Acceptable degradation — the summary was rarely informative.

## Migration Plan

1. Create tracking issue in `liverty-music/specification` ("Mechanize Claude review verdict (decouple from LLM judgment)").
2. Land the `.github` repo change first (reusable workflow at `liverty-music/.github/.github/workflows/claude-review.yml`). Because all four caller workflows reference `@main`, they will pick up the new reusable workflow on the next PR push.
3. Land the four caller-repo changes (drop `with: additional_focus:`) in any order. Each is a single-file, single-block deletion.
4. Validate on the `specification` repo (the original pilot target) by opening a small test PR. Confirm: single-line prompt is sent, slash command runs to completion, inline comments are posted (if applicable), Check Run conclusion matches comment count.
5. After two successful PRs on `specification`, declare migration complete. Archive this change.

**Rollback:** revert the merge commits in `liverty-music/.github` and the four caller repos. Branch protection is unchanged, so rollback restores the previous (broken-but-tolerated) state without any Pulumi action.

## Open Questions

- Should the `gh api` filter also exclude comments authored before the head SHA was pushed (in case `commit_id` ever lags)? Probably not — `commit_id` on the API response is authoritative — but to be confirmed during implementation by inspecting a real run's API output.
- Is there value in publishing a sticky comment summarizing the verdict (for PR readers who don't expand the Check Run)? Defer; can be added later as a non-breaking enhancement.
