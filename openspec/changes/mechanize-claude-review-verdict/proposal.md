## Why

The current `Claude review` Check Run pipeline (introduced in [archive/2026-05-16-claude-review-check-run](../archive/2026-05-16-claude-review-check-run/)) asks the wrapping LLM agent to commit to a binary pass/fail verdict via `/tmp/claude-verdict.json`. Combined with an `additional_focus` free-text injection, a "Step 1 / Step 2" wrapper around the slash command, and a `--allowedTools` list that omits `Bash(gh pr list:*)`, this design has 6 documented deviations from `anthropics/claude-code-action` and `code-review` plugin official patterns. Under the Anthropic model-serving incidents of 2026-05-18 to 2026-05-22 (Opus 4.7 / Sonnet 4.6 / Haiku 4.5 elevated errors), these deviations produced nit-level comment overload, ignored "HIGH SIGNAL only" filter instructions, and self-contradicting verdicts inside a single review loop — symptoms that block PRs on noise rather than real issues.

The fix is to decouple the verdict from LLM judgment: let Claude do only the review (post inline comments), and let a deterministic post-step count the comments Claude posted against the PR head SHA to derive the Check Run conclusion. This eliminates the confidence-inflation pressure that binary verdict prompts are known to induce, removes the prompt-injection surface that `additional_focus` opens, and restores the workflow to single-line slash-command invocation per the official examples.

## What Changes

- **BREAKING (spec-only)**: Remove the `Claude writes /tmp/claude-verdict.json` contract from `ci-optimization`. The Check Run `conclusion` is now derived from counting inline review comments authored by the Claude bot against the PR head SHA, computed in a post-step bash + `gh api` + `jq` pipeline.
- **BREAKING (workflow API)**: Remove the `additional_focus` input from the reusable workflow `liverty-music/.github/.github/workflows/claude-review.yml`. Repo-specific review focus is expressed exclusively in each repo's `CLAUDE.md`.
- Simplify the reusable workflow's `prompt:` from a multi-step structured prompt to the single-line slash-command invocation used pre-2026-05-15.
- Correct the slash command's `--allowedTools` to match the `code-review` plugin's declared frontmatter (add `Bash(gh pr list:*)`), and remove tools no longer needed (`Write` for the verdict file).
- Caller workflows in `backend`, `frontend`, `specification`, `cloud-provisioning` drop their `with: additional_focus:` blocks.
- Branch-protection policy (Required Status Check on `Claude review`) is unchanged. The Check Run still publishes `success` / `failure` / `neutral` conclusions; only the derivation mechanism changes.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `ci-optimization`: Replace the verdict-file-driven Check Run requirement with a comment-count-driven requirement, and remove `additional_focus` from the reusable-workflow requirement.

## Impact

- **Affected repo**: `liverty-music/.github` (reusable workflow at `.github/workflows/claude-review.yml` — prompt, post-steps, and inputs all change).
- **Affected caller workflows** (4 repos, ~1-line change each): `backend/.github/workflows/claude-code-review.yml`, `frontend/.github/workflows/claude-code-review.yml`, `specification/.github/workflows/claude-code-review.yml`, `cloud-provisioning/.github/workflows/claude-code-review.yml`.
- **No Pulumi change**: `cloud-provisioning/src/index.ts` already adds `'Claude review'` to `requiredStatusCheckContexts`; the Check Run name and Required-Status-Check semantics are unchanged.
- **No CLAUDE.md change required**: the "Go conventions / error handling / table-driven tests / pgx usage" content currently injected via `additional_focus` is already documented in `backend/CLAUDE.md` and the equivalent files in other repos.
- **Tracking issue**: to be created in `liverty-music/specification` (next-available number) before implementation begins, per the liverty-music commit convention (`Refs: #<issue-number>`).
- **Known residual issue**: the `code-review` plugin's skip-on-repeat behavior ([anthropics/claude-code#19618](https://github.com/anthropics/claude-code/issues/19618)) is out of scope; mitigated partially by HEAD-SHA-scoped counting (stale comments from prior pushes do not inflate the count).
