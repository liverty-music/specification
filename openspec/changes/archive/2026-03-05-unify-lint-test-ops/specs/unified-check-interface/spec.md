## ADDED Requirements

### Requirement: Makefile with standard targets in every repo

Each repo (backend, frontend, specification, cloud-provisioning) SHALL have a `Makefile` at the repository root with the following targets: `lint`, `fix`, `test`, `test-integration`, `check`. Not all targets are required in every repo — only those relevant to the repo's toolchain.

#### Scenario: Backend make lint

- **WHEN** `make lint` is run in the backend repo
- **THEN** `gofmt -l .` MUST execute and fail if any files are unformatted
- **THEN** `golangci-lint run --timeout=3m --build-tags=integration ./...` MUST execute

#### Scenario: Backend make fix

- **WHEN** `make fix` is run in the backend repo
- **THEN** `gofmt -w .` MUST execute to auto-fix formatting

#### Scenario: Backend make test

- **WHEN** `make test` is run in the backend repo
- **THEN** PostgreSQL MUST be started via `docker compose up -d postgres --wait`
- **THEN** Atlas migrations MUST be applied via `atlas migrate apply --env local`
- **THEN** `go test ./...` MUST execute (unit tests only, no integration tag)

#### Scenario: Backend make test-integration

- **WHEN** `make test-integration` is run (CI environment, DB already available)
- **THEN** `go test -tags=integration -race -timeout=5m ./...` MUST execute

#### Scenario: Backend make check

- **WHEN** `make check` is run in the backend repo
- **THEN** `make lint` MUST execute first
- **THEN** `make test` MUST execute after lint passes

#### Scenario: Frontend make lint

- **WHEN** `make lint` is run in the frontend repo
- **THEN** `npx biome lint src test` MUST execute
- **THEN** `npx biome format src test` MUST execute (check-only, no write)
- **THEN** `npm run lint:css` MUST execute
- **THEN** `npx tsc --noEmit` MUST execute

#### Scenario: Frontend make fix

- **WHEN** `make fix` is run in the frontend repo
- **THEN** `npx biome check --write src test` MUST execute

#### Scenario: Frontend make test

- **WHEN** `make test` is run in the frontend repo
- **THEN** `npx vitest run --coverage` MUST execute

#### Scenario: Frontend make check

- **WHEN** `make check` is run in the frontend repo
- **THEN** `make lint` MUST execute first
- **THEN** `make test` MUST execute after lint passes

#### Scenario: Specification make lint

- **WHEN** `make lint` is run in the specification repo
- **THEN** `buf lint` MUST execute
- **THEN** `buf format -d --exit-code` MUST execute
- **THEN** `buf breaking --against '.git#branch=origin/main'` MUST execute (uses `origin/main` for CI compatibility — CI checkout creates a detached HEAD with no local `main` branch)

#### Scenario: Specification make fix

- **WHEN** `make fix` is run in the specification repo
- **THEN** `buf format -w` MUST execute

#### Scenario: Specification make check

- **WHEN** `make check` is run in the specification repo
- **THEN** `make lint` MUST execute

#### Scenario: Cloud-provisioning make lint

- **WHEN** `make lint` is run in the cloud-provisioning repo
- **THEN** `make lint-ts` MUST execute (biome check + tsc)
- **THEN** `make lint-k8s` MUST execute (kustomize render + kube-linter + spot nodeSelector check)

#### Scenario: Cloud-provisioning make lint-ts

- **WHEN** `make lint-ts` is run in the cloud-provisioning repo
- **THEN** `npx biome check src` MUST execute
- **THEN** `npx tsc --noEmit` MUST execute

#### Scenario: Cloud-provisioning make fix

- **WHEN** `make fix` is run in the cloud-provisioning repo
- **THEN** `npx biome check --write src` MUST execute

#### Scenario: Cloud-provisioning make check

- **WHEN** `make check` is run in the cloud-provisioning repo
- **THEN** `make lint-ts` MUST execute (lint-k8s excluded — requires kustomize/kube-linter/helm)

### Requirement: CI workflows use Makefile targets

CI workflows SHALL call `make lint` and `make test-integration` (or `make test`) instead of inline commands. CI-specific setup (service containers, tool installation, codecov upload) remains in the workflow YAML.

#### Scenario: Backend CI lint job

- **WHEN** the backend lint CI workflow runs
- **THEN** it MUST call `make lint` instead of inline gofmt and golangci-lint commands

#### Scenario: Backend CI test job

- **WHEN** the backend test CI workflow runs
- **THEN** CI MUST set up the PostgreSQL service container and run atlas migrations
- **THEN** it MUST call `make test-integration` for the actual test execution

#### Scenario: Frontend CI lint job

- **WHEN** the frontend lint CI workflow runs
- **THEN** it MUST call `make lint` instead of separate biome/tsc/stylelint commands

#### Scenario: Frontend CI test job

- **WHEN** the frontend test CI workflow runs
- **THEN** it MUST call `make test` (no separate DB needed)

#### Scenario: Specification CI checks

- **WHEN** the specification CI workflow runs on a PR
- **THEN** it MUST call `make lint`

#### Scenario: Cloud-provisioning CI lint-ts job

- **WHEN** the cloud-provisioning CI workflow runs
- **THEN** it MUST call `make lint-ts` instead of separate biome/tsc commands

#### Scenario: Cloud-provisioning CI lint-k8s job

- **WHEN** the cloud-provisioning K8s lint workflow runs
- **THEN** it MUST call `make lint-k8s` instead of inline kustomize/kube-linter/spot-check commands
