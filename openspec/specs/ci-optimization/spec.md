# CI Optimization

## Purpose

Defines standards for CI workflow efficiency, security permissions, and quality gates across frontend and backend repositories.

## Requirements

### Requirement: Workflows cancel superseded runs
All CI workflows (frontend and backend) SHALL use a `concurrency` group that cancels in-progress runs when a newer run for the same ref or PR is triggered. Deploy workflows SHALL use `cancel-in-progress: false` to avoid interrupting active deployments.

#### Scenario: PR receives a new push while CI is running
- **WHEN** a new commit is pushed to a pull request branch while a CI run is already in progress
- **THEN** the previous CI run is cancelled and the new run starts

#### Scenario: Deploy workflow is already running when a new push arrives
- **WHEN** a new commit is pushed to main while a deploy job is already running
- **THEN** the running deploy job is NOT cancelled (only queued runs are cancelled)

### Requirement: Workflows declare minimum required permissions
All CI workflows SHALL declare an explicit `permissions` block at the workflow or job level granting only the permissions required for the job's tasks.

#### Scenario: Lint job runs without write permissions
- **WHEN** the lint job executes
- **THEN** the job token SHALL have at most `contents: read` permission

#### Scenario: Coverage comment job writes to PR
- **WHEN** the test job posts a coverage report comment
- **THEN** the job token SHALL have `contents: read` and `pull-requests: write`

### Requirement: Frontend CI enforces code quality gates
The frontend CI workflow SHALL include jobs for: lint, test with coverage, typecheck, format check, and security audit. All jobs SHALL run on every PR and push to main.

#### Scenario: TypeScript type error is introduced
- **WHEN** a PR introduces a TypeScript type error
- **THEN** the typecheck job SHALL fail and block merge

#### Scenario: Dependency with known vulnerability is added
- **WHEN** a PR adds a dependency with a known moderate or higher severity vulnerability
- **THEN** the security audit job SHALL fail and block merge

#### Scenario: Code coverage drops below threshold
- **WHEN** test coverage for statements falls below 20%, branches below 70%, functions below 30%, or lines below 20%
- **THEN** the test job SHALL fail

### Requirement: Frontend CI reports coverage on PRs
The frontend CI workflow SHALL post a coverage summary as a PR comment using vitest-coverage-report-action.

#### Scenario: PR is opened or updated
- **WHEN** a PR is opened or a new commit is pushed to a PR
- **THEN** a coverage report comment SHALL be posted or updated on the PR

### Requirement: Backend CI enforces format correctness
The backend lint workflow SHALL include a `gofmt` check that fails if any Go source file is not formatted according to `gofmt` standards.

#### Scenario: Unformatted Go file is committed
- **WHEN** a PR contains a Go source file not formatted by `gofmt`
- **THEN** the format check job SHALL fail and block merge

### Requirement: Atlas migration lint runs without Atlas Cloud
The atlas-ci workflow SHALL run `atlas migrate lint` using only a local dev database container, without requiring an Atlas Cloud token.

#### Scenario: Migration file with destructive change is added
- **WHEN** a PR adds a migration file containing a destructive operation (e.g., DROP TABLE)
- **THEN** atlas migrate lint SHALL report the issue

#### Scenario: atlas-ci runs without ATLAS_CLOUD_TOKEN
- **WHEN** the ATLAS_CLOUD_TOKEN secret is not configured
- **THEN** atlas-ci SHALL still run and validate migrations successfully

### Requirement: Benchmark workflow uses consistent Postgres version
The benchmark workflow SHALL use the same Postgres version as the test workflow (postgres:18).

#### Scenario: Benchmark job starts
- **WHEN** the benchmark job starts its Postgres service container
- **THEN** the container SHALL use postgres:18

### Requirement: Both repos have a CI success gate job
Each repo's CI workflow SHALL include a final job that depends on all required jobs and serves as a single check for branch protection rules.

#### Scenario: All CI jobs pass
- **WHEN** all lint, test, and quality gate jobs succeed
- **THEN** the ci-success job SHALL succeed

#### Scenario: Any CI job fails
- **WHEN** any required CI job fails
- **THEN** the ci-success job SHALL fail

### Requirement: Claude code review runs via a single org-wide reusable workflow
All four liverty-music repositories (`backend`, `frontend`, `specification`, `cloud-provisioning`) SHALL invoke Claude code review through a reusable workflow hosted at `liverty-music/.github/.github/workflows/claude-review.yml` (`workflow_call`). Each repository's own `.github/workflows/claude-code-review.yml` SHALL be a caller-only workflow that forwards `secrets: inherit`. The reusable workflow SHALL invoke `code-review@claude-code-plugins` with the `--comment` flag and `anthropics/claude-code-action@v1`, passing the slash command as a single-line `prompt:` without additional structured-prompt wrapping.

The reusable workflow's `claude_args.--allowedTools` SHALL be aligned with the `code-review` plugin's declared `allowed-tools` frontmatter — at minimum including `Bash(gh pr list:*)`, `Bash(gh pr view:*)`, `Bash(gh pr diff:*)`, `Bash(gh pr comment:*)`, `Bash(gh issue view:*)`, `Bash(gh issue list:*)`, `Bash(gh search:*)`, and `mcp__github_inline_comment__create_inline_comment`. The reusable workflow SHALL NOT accept per-repo input parameters that inject free-form text into the prompt; per-repo review focus is expressed exclusively via each repo's `CLAUDE.md`.

#### Scenario: PR is opened in any liverty-music repo
- **WHEN** a pull request is opened or updated in `backend`, `frontend`, `specification`, or `cloud-provisioning`
- **THEN** the repo's `claude-code-review.yml` SHALL call `liverty-music/.github/.github/workflows/claude-review.yml` via `uses:` rather than running Claude inline

#### Scenario: Claude review behavior needs updating
- **WHEN** the Claude review prompt, plugin version, or verdict logic needs to change
- **THEN** the change SHALL be made in `liverty-music/.github/.github/workflows/claude-review.yml` and SHALL take effect on all four repos without modifying individual repo workflows

#### Scenario: Caller workflow contains no prompt-injecting input
- **WHEN** a caller workflow at `<repo>/.github/workflows/claude-code-review.yml` is inspected
- **THEN** the `jobs.review.with:` block SHALL be absent (or empty), with no `additional_focus` or other free-form text inputs passed to the reusable workflow

### Requirement: Claude review posts advisory inline comments on pull requests
The reusable workflow `liverty-music/.github/.github/workflows/claude-review.yml` SHALL invoke `anthropics/claude-code-action@v1` with the `code-review@claude-code-plugins` plugin and the `--comment` argument so that Claude posts inline review comments on each pull request. The workflow SHALL NOT create a GitHub Check Run, SHALL NOT emit a verdict file, and SHALL NOT submit a formal pull request review (`APPROVED` or `CHANGES_REQUESTED`).

The reusable workflow's `workflow_call` interface SHALL declare only the `CLAUDE_CODE_OAUTH_TOKEN` secret (no inputs). The workflow SHALL request permissions `contents: read`, `pull-requests: write`, `issues: read`, `id-token: write` — and SHALL NOT request `checks: write`.

The workflow SHALL match the shape of the official Anthropic example [`pr-review-comprehensive.yml`](https://github.com/anthropics/claude-code-action/blob/main/examples/pr-review-comprehensive.yml): a single job with a checkout step and a single `anthropics/claude-code-action@v1` step.

#### Scenario: PR is opened or updated
- **WHEN** a pull request is opened, synchronized, marked ready for review, or reopened
- **THEN** the caller workflow SHALL invoke the reusable workflow
- **AND** the reusable workflow SHALL run `anthropics/claude-code-action@v1` with the `code-review` plugin and `--comment`
- **AND** Claude SHALL post inline review comments (zero or more) on the PR's head commit
- **AND** no GitHub Check Run named `Claude review` (or any other name) SHALL be created by this workflow

#### Scenario: Claude finds no issues
- **WHEN** the Claude run completes and posts zero inline comments
- **THEN** the workflow run SHALL succeed
- **AND** Claude MAY post a top-level PR comment via `gh pr comment` per the `code-review` slash command's documented behavior

#### Scenario: Claude finds issues
- **WHEN** the Claude run completes and posts one or more inline comments
- **THEN** the workflow run SHALL succeed (the workflow does not fail on the presence of comments)
- **AND** reviewers SHALL treat the inline comments as advisory input alongside other reviewers' comments
- **AND** the PR's mergeability SHALL NOT be affected by the comments' presence or count

### Requirement: Branch protection gates merges on CI Success only
For every liverty-music repository whose `GitHubRepositoryComponent` participates in Claude review (`backend`, `frontend`, `specification`, `cloud-provisioning`), `cloud-provisioning/src/index.ts` SHALL set `requiredStatusCheckContexts` to `['CI Success']`. The string `'Claude review'` SHALL NOT appear in `requiredStatusCheckContexts` for any repo.

Branch protection is applied only when the Pulumi stack environment is `prod`; the Required Status Check is effective after `pulumi up -s prod`.

#### Scenario: PR has a failing CI Success check
- **WHEN** a pull request is open with `CI Success` Check Run `conclusion: failure`
- **THEN** the protected branch SHALL block merging
- **AND** the Claude review workflow's success or failure SHALL NOT affect mergeability

#### Scenario: PR has Claude inline comments but CI Success passes
- **WHEN** a pull request has Claude-posted inline comments (any count, any resolution state) AND `CI Success` Check Run `conclusion: success`
- **THEN** the protected branch SHALL allow merging
- **AND** no Claude-review-related Check Run SHALL be present in `gh api repos/.../branches/main/protection`'s required contexts
