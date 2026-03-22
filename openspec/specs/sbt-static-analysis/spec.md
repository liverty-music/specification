## ADDED Requirements

### Requirement: Slither static analysis in CI
The CI pipeline SHALL run Slither static analysis on every push/PR that modifies contract files. Analysis results MUST be reviewed and false positives explicitly excluded.

#### Scenario: Slither runs on contract changes
- **WHEN** a push or PR modifies files matching `contracts/src/**`, `contracts/test/**`, or `contracts/foundry.toml`
- **THEN** the `slither` CI job MUST execute and analyze all contract source files

#### Scenario: Slither blocks merge on findings
- **WHEN** Slither detects a vulnerability that is not in the exclusion list
- **THEN** the CI job MUST fail and block the PR from merging

#### Scenario: False positives are explicitly excluded
- **WHEN** a Slither finding is triaged as a false positive
- **THEN** it MUST be excluded via `.slither.config.json` with a comment explaining why

### Requirement: Gas regression detection
The CI pipeline SHALL track gas usage via `forge snapshot` and detect regressions.

#### Scenario: Gas snapshot baseline exists in git
- **WHEN** the contracts are built
- **THEN** a `.gas-snapshot` file MUST exist in the `contracts/` directory and be tracked in git

#### Scenario: Gas regression fails CI
- **WHEN** a code change causes gas usage to increase beyond the baseline
- **THEN** `forge snapshot --check` MUST fail the CI job

### Requirement: Increased fuzz depth in CI
The CI pipeline SHALL run fuzz tests with a higher iteration count than local development defaults.

#### Scenario: CI runs fuzz tests with 10000 iterations
- **WHEN** the `forge-test` CI job executes
- **THEN** it MUST use `--fuzz-runs 10000` (not the default 256)
