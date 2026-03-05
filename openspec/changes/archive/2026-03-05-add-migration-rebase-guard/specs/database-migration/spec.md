## MODIFIED Requirements

### Requirement: The CI pipeline MUST validate migration file ordering

The atlas-ci workflow SHALL verify that all new migration files have timestamps greater than the latest migration version on the base branch. PRs with out-of-order migrations SHALL fail CI.

#### Scenario: PR with out-of-order migration file

- **WHEN** a PR adds a migration file with a timestamp earlier than the latest on `main`
- **THEN** the atlas-ci job SHALL fail with a descriptive error message
- **AND** the error message SHALL suggest running `scripts/check-migration-drift.sh --fix`

#### Scenario: PR with correctly ordered migration file

- **WHEN** a PR adds a migration file with a timestamp later than the latest on `main`
- **THEN** the atlas-ci job SHALL pass the ordering check
