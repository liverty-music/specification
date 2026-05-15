## ADDED Requirements

### Requirement: Claude code review runs via a single org-wide reusable workflow
All four liverty-music repositories (`backend`, `frontend`, `specification`, `cloud-provisioning`) SHALL invoke Claude code review through a reusable workflow hosted at `liverty-music/.github/.github/workflows/claude-review.yml` (`workflow_call`). Each repository's own `.github/workflows/claude-code-review.yml` SHALL be a caller-only workflow that forwards `secrets: inherit` and optionally provides a repo-specific `additional_focus` input. The reusable workflow SHALL invoke `code-review@claude-code-plugins` with the `--comment` flag and `anthropics/claude-code-action@v1`.

#### Scenario: PR is opened in any liverty-music repo
- **WHEN** a pull request is opened or updated in `backend`, `frontend`, `specification`, or `cloud-provisioning`
- **THEN** the repo's `claude-code-review.yml` SHALL call `liverty-music/.github/.github/workflows/claude-review.yml` via `uses:` rather than running Claude inline

#### Scenario: Claude review behavior needs updating
- **WHEN** the Claude review prompt, plugin version, or verdict logic needs to change
- **THEN** the change SHALL be made in `liverty-music/.github/.github/workflows/claude-review.yml` and SHALL take effect on all four repos without modifying individual repo workflows

### Requirement: Claude review publishes its verdict as a GitHub Check Run
The reusable workflow SHALL create a GitHub Check Run named exactly `Claude review` on the pull request's head commit. The Check Run `conclusion` SHALL be derived from a `/tmp/claude-verdict.json` file that Claude writes after posting its sticky comment.

The verdict-to-conclusion mapping SHALL be:

| Verdict JSON | `conclusion` |
|---|---|
| `{ "verdict": "pass" }` | `success` |
| `{ "verdict": "fail", "count": N, "summary": "..." }` | `failure` |
| File missing or unparseable | `neutral` |

The workflow SHALL NOT submit a formal pull request review (`APPROVE` or `REQUEST_CHANGES`) for the verdict. Only the sticky comment (posted by the plugin) and the Check Run are produced.

#### Scenario: Claude finds no high-signal issues
- **WHEN** Claude review completes and writes `{ "verdict": "pass" }` to `/tmp/claude-verdict.json`
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: success`
- **AND** the Check Run output title SHALL be `No issues found`

#### Scenario: Claude finds high-signal issues
- **WHEN** Claude review completes and writes `{ "verdict": "fail", "count": N, "summary": "<text>" }` to `/tmp/claude-verdict.json`
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: failure`
- **AND** the Check Run output title SHALL be `N issue(s) found`

#### Scenario: Claude does not produce a verdict file
- **WHEN** `/tmp/claude-verdict.json` is missing after the Claude step completes
- **THEN** the workflow SHALL create a `Claude review` Check Run with `conclusion: neutral`
- **AND** the Check Run output title SHALL be `No verdict produced`

#### Scenario: Claude review never submits a formal PR review
- **WHEN** any Claude review run completes (pass, fail, or neutral)
- **THEN** `gh pr view --json reviews` SHALL NOT show a review authored by Claude with state `APPROVED` or `CHANGES_REQUESTED`

### Requirement: `Claude review` is enforced as a Required Status Check via Pulumi
For every liverty-music repository whose `GitHubRepositoryComponent` participates in Claude review, `cloud-provisioning/src/index.ts` SHALL include `'Claude review'` in `requiredStatusCheckContexts` alongside the existing `'CI Success'`. Branch protection is applied only when the Pulumi stack environment is `prod`, so the Required Status Check is effective only after `pulumi up -s prod`.

A failing or pending `Claude review` Check Run SHALL block merging on the protected branch. Repo administrators retain the standard branch-protection admin-override capability; no other bypass actors are configured.

#### Scenario: PR has a failing Claude review Check Run
- **WHEN** a pull request is open with `Claude review` Check Run `conclusion: failure`
- **AND** all other Required Status Checks pass
- **THEN** the PR's merge button SHALL be disabled for non-admin users

#### Scenario: PR has a neutral Claude review Check Run
- **WHEN** a pull request is open with `Claude review` Check Run `conclusion: neutral`
- **AND** all other Required Status Checks pass
- **THEN** the PR's merge button SHALL be enabled (neutral does not block)

#### Scenario: Repo admin merges despite failing Claude review
- **WHEN** a repository administrator opens the merge dialog on a PR with `Claude review` `conclusion: failure`
- **THEN** the admin SHALL be able to merge via the standard branch-protection administrator-override path

### Requirement: Claude review pilots on `specification` before all-repo rollout
The first deployment of the new reusable workflow + Required Status Check SHALL enable `'Claude review'` in `requiredStatusCheckContexts` for the `specification` repository only. The other three repos (`backend`, `frontend`, `cloud-provisioning`) SHALL retain `requiredStatusCheckContexts: ['CI Success']` until the pilot has run for at least one calendar week without persistent false-positive issues.

#### Scenario: Initial deployment after pilot Pulumi PR
- **WHEN** the first Pulumi PR introducing this change has been applied to `prod`
- **THEN** only the `specification` repo's branch protection SHALL include `'Claude review'` in `requiredStatusCheckContexts`
- **AND** `backend`, `frontend`, `cloud-provisioning` SHALL still have `requiredStatusCheckContexts: ['CI Success']`

#### Scenario: Pilot graduates to full rollout
- **WHEN** the pilot has run for at least one calendar week without unmitigated false-positive issues
- **THEN** a follow-up Pulumi PR SHALL add `'Claude review'` to `requiredStatusCheckContexts` for `backend`, `frontend`, and `cloud-provisioning`
- **AND** each of those three repos SHALL have its `.github/workflows/claude-code-review.yml` replaced with a caller of the reusable workflow before that Pulumi PR is deployed to `prod`
