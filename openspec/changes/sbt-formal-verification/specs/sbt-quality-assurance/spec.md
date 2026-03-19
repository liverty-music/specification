## ADDED Requirements

### Requirement: Aderyn static analysis in CI
Aderyn SHALL run as a CI job alongside Slither to provide a second-opinion static analysis.

#### Scenario: Aderyn runs on contract changes
- **WHEN** a push or PR modifies contract source files
- **THEN** the `aderyn` CI job MUST execute and analyze all contract source files

#### Scenario: Aderyn findings are reported
- **WHEN** Aderyn detects findings
- **THEN** results MUST be output as a markdown report and uploaded as a CI artifact

### Requirement: Mutation testing with vertigo-rs
vertigo-rs SHALL be used to measure the quality of the test suite by generating mutants and checking if tests catch them.

#### Scenario: Mutation testing runs on schedule
- **WHEN** the weekly CI schedule triggers or a manual dispatch is executed
- **THEN** vertigo-rs MUST generate mutants of TicketSBT.sol and run the test suite against each

#### Scenario: Surviving mutants are reported
- **WHEN** mutation testing completes
- **THEN** any surviving mutants (mutations not caught by tests) MUST be reported with file location and mutation type

### Requirement: Code coverage reporting
`forge coverage` SHALL generate lcov reports and make them available in CI.

#### Scenario: Coverage report generated on PR
- **WHEN** a PR modifies contract files
- **THEN** `forge coverage --report lcov` MUST execute and the lcov report MUST be uploaded as a CI artifact

#### Scenario: Coverage tracks line and branch metrics
- **WHEN** the coverage report is generated
- **THEN** it MUST include both line coverage and branch coverage for all source files in `contracts/src/`
