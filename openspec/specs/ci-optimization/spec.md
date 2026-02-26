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
