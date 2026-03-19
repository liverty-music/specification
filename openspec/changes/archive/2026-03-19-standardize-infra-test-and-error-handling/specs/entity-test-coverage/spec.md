## ADDED Requirements

### Requirement: Interface Possible errors completeness
Every interface in `internal/entity/` that returns `error` SHALL document `# Possible errors` in its Go doc comment, listing all `apperr` codes the implementation may return.

#### Scenario: Repository interface with CRUD operations
- **WHEN** a repository interface defines `Get`, `Create`, `Update`, `Delete` methods
- **THEN** each method's doc comment includes a `# Possible errors` section listing applicable codes (e.g., NotFound, AlreadyExists, InvalidArgument, Internal)

#### Scenario: External service adapter interface
- **WHEN** a gateway/adapter interface wraps an external API (e.g., ArtistSearcher, ConcertSearcher)
- **THEN** each method's doc comment includes a `# Possible errors` section listing business errors and infrastructure errors (e.g., NotFound, Unavailable, Internal)

### Requirement: Implementation error code consistency
Every infrastructure implementation SHALL return only the `apperr` codes documented in its interface's `# Possible errors` section.

#### Scenario: Implementation returns undocumented error code
- **WHEN** an implementation returns an `apperr` code not listed in the interface doc
- **THEN** the interface doc MUST be updated to include that code, or the implementation MUST be changed to use a documented code

#### Scenario: Implementation uses fmt.Errorf instead of apperr
- **WHEN** an infrastructure implementation returns `fmt.Errorf` wrapped errors
- **THEN** the implementation MUST be modified to use `apperr.New` or `apperr.Wrap` with an appropriate code

### Requirement: Error code semantic correctness
Infrastructure implementations SHALL use `apperr` codes according to gRPC code semantics.

#### Scenario: JSON decode failure
- **WHEN** an external API response fails JSON decoding
- **THEN** the implementation SHALL return `codes.Internal` (not `codes.DataLoss`, which means unrecoverable data loss or corruption)

#### Scenario: Input validation failure
- **WHEN** a function receives invalid input (empty ID, malformed URL, unsupported type)
- **THEN** the implementation SHALL return `codes.InvalidArgument`

#### Scenario: External service unreachable
- **WHEN** an external service is down, rate-limited, or all retries are exhausted
- **THEN** the implementation SHALL return `codes.Unavailable`

### Requirement: Error path test coverage
Every `apperr` code listed in an interface's `# Possible errors` SHALL have at least one test case verifying that the implementation returns that code.

#### Scenario: NotFound error path tested
- **WHEN** an interface documents `NotFound` as a possible error
- **THEN** at least one test case uses `assert.ErrorIs(t, err, apperr.ErrNotFound)` to verify the implementation returns NotFound for the documented condition

#### Scenario: Internal error path tested
- **WHEN** an interface documents `Internal` as a possible error
- **THEN** at least one test case verifies that infrastructure failures (DB errors, API errors) are wrapped with `codes.Internal`

### Requirement: Infrastructure test go-tester compliance
All `_test.go` files under `internal/infrastructure/` SHALL comply with go-tester skill standards.

#### Scenario: Black-box testing package
- **WHEN** a test file exists in an infrastructure package
- **THEN** the test file uses `package <name>_test` suffix (not `package <name>`)
- **AND** unexported symbols are accessed via `export_test.go` pattern if needed

#### Scenario: Table-driven test structure
- **WHEN** a test function has multiple test cases
- **THEN** cases are defined as a `[]struct` slice with `name`, `wantErr error` (not `bool` or `string`) fields
- **AND** the loop variable is named `tt`

#### Scenario: Error assertion pattern
- **WHEN** a test case checks for a specific error
- **THEN** it uses `assert.ErrorIs(t, err, expectedErr)` without a preceding redundant `require.Error(t, err)` or `assert.Error(t, err)`
