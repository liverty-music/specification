## Why

The Claude code-review GitHub Action currently runs in all four repos (`backend`, `frontend`, `specification`, `cloud-provisioning`) but only posts a sticky PR comment. The verdict is invisible from the PR list view and cannot gate merges, so reviewers must open every PR to discover whether Claude flagged issues. The workflow YAML is also duplicated four times, so any change to the review behavior requires four PRs.

Investigation found that `anthropics/claude-code-action@v1` exposes no native input for submitting a formal PR review (`APPROVE` / `REQUEST_CHANGES`), and the `code-review@claude-code-plugins` plugin is designed for comment-only operation. The community-aligned alternative — used by GitHub Copilot Code Review, CodeRabbit, Qodo, and Sentry Seer — is to emit a GitHub **Check Run** with `success` / `failure` / `neutral` conclusion. Check Runs give green/red visibility, can be made a Required Status Check to block merges, and do not interfere with the human approval flow (avoiding the required-reviewer bypass concern that motivates Copilot to refuse formal reviews).

## What Changes

- Add a new reusable workflow (`workflow_call`) that runs `code-review@claude-code-plugins --comment` and then publishes a `Claude review` GitHub Check Run whose `conclusion` reflects the verdict (`success` when zero high-signal issues, `failure` when any issue, `neutral` if the verdict cannot be produced).
- Host the reusable workflow in a new `liverty-music/.github` org-wide repo so all four repos call into the same source of truth.
- Each repo's `claude-code-review.yml` becomes a ~12-line caller that forwards a repo-specific `additional_focus` input and inherits org secrets.
- Add `Claude review` to `requiredStatusCheckContexts` in branch protection so failing Check Runs block merges. Pilot in `specification` first, then roll out to the other three repos.
- Bypass policy: admin override only (no `Allow specified actors to bypass` entries).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `ci-optimization`: Add requirements describing the Claude review reusable workflow, the Check Run verdict contract, and the branch-protection requirement that gates merges on the `Claude review` check.

## Impact

- **New repo**: `liverty-music/.github` (created via Pulumi in `cloud-provisioning/src/github/components/organization.ts`; `RepositoryName` enum extended).
- **cloud-provisioning/src/index.ts**: Add `'Claude review'` to `specification` repo's `requiredStatusCheckContexts` (pilot). After validation, also add to `backend`, `frontend`, and `cloud-provisioning`.
- **liverty-music/.github/.github/workflows/claude-review.yml**: New reusable workflow.
- **{backend,frontend,specification,cloud-provisioning}/.github/workflows/claude-code-review.yml**: Replaced with a ~12-line caller. Spec repo first (pilot); others after.
- **Deployment**: Requires `pulumi up -s prod` because both `GitHubOrganizationComponent` (new repo) and `BranchProtection` (Required Status Check) are gated by `environment === 'prod'`.
- **Tracking issue**: [liverty-music/specification#474](https://github.com/liverty-music/specification/issues/474).
- **Related prior change**: archive `2026-03-27-enforce-required-ci-checks` (established the `'CI Success'` Required Status Check pattern).
