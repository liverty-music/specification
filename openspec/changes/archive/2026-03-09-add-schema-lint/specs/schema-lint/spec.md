## MODIFIED Requirements

### Requirement: Database migration workflow includes schema lint
The `make check` target SHALL include `lint-schema` in addition to `lint` and `test`.

#### Scenario: make check target composition
- **WHEN** a developer runs `make check`
- **THEN** `lint`, `lint-schema`, and `test` SHALL all execute
