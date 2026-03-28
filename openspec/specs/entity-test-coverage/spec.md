## ADDED Requirements

### Requirement: isHypeMatched exhaustive coverage
`isHypeMatched(hype, lane)` SHALL be tested for all 12 combinations of HypeLevel x LaneType using table-driven tests.

#### Scenario: Full matrix via it.each
- **WHEN** every (hype, lane) pair is evaluated
- **THEN** results match the rule `HYPE_ORDER[hype] >= LANE_ORDER[lane]`

### Requirement: hasFollow boundary cases
`hasFollow()` SHALL be tested for multi-element lists and duplicate artist IDs.

#### Scenario: Artist found among multiple follows
- **WHEN** follows contains 3 entries and the target is the last one
- **THEN** returns true

#### Scenario: Duplicate artist IDs in list
- **WHEN** follows contains two entries with the same artist ID
- **THEN** returns true

### Requirement: normalizeStep full legacy mapping
`normalizeStep()` SHALL be tested for every key in the legacy numeric migration table plus gap values.

#### Scenario: All mapped numeric values
- **WHEN** input is `'0'`, `'1'`, `'3'`, `'4'`, `'5'`, or `'7'`
- **THEN** returns the corresponding OnboardingStepValue

#### Scenario: Unmapped numeric gap values
- **WHEN** input is `'2'` or `'6'`
- **THEN** returns `'lp'` (fallback)

### Requirement: translationKey coverage
`translationKey()` SHALL have dedicated tests covering known codes and unknown codes.

#### Scenario: Known prefecture code
- **WHEN** code is `'JP-13'`
- **THEN** returns `'tokyo'`

#### Scenario: Unknown code fallback
- **WHEN** code is `'XX-99'`
- **THEN** returns `'XX-99'`

### Requirement: codeToHome boundary cases
`codeToHome()` SHALL be tested for short input strings.

#### Scenario: Code shorter than 3 characters
- **WHEN** code is `'JP'` (no hyphen or subdivision)
- **THEN** returns `{ countryCode: 'JP', level1: 'JP' }` without throwing

### Requirement: bytesToHex zero-padding
`bytesToHex()` SHALL verify that single-digit hex values are zero-padded.

#### Scenario: Leading zero byte
- **WHEN** input is `[0x00]`
- **THEN** returns `'00'`

### Requirement: bytesToDecimal multi-byte
`bytesToDecimal()` SHALL be tested with 3+ byte inputs.

#### Scenario: Three-byte input
- **WHEN** input is `[0x01, 0x00, 0x00]`
- **THEN** returns `'65536'`

### Requirement: uuidToFieldElement robustness
`uuidToFieldElement()` SHALL handle already-stripped and non-standard inputs.

#### Scenario: UUID without hyphens
- **WHEN** input is `'550e8400e29b41d4a716446655440000'`
- **THEN** returns the same decimal as the hyphenated form

### Requirement: artistHue empty string
`artistHue()` SHALL handle empty string input without throwing.

#### Scenario: Empty string input
- **WHEN** name is `''`
- **THEN** returns a number in 0-359 range

### Requirement: artistHueFromColorProfile dominantHue zero
`artistHueFromColorProfile()` SHALL treat `dominantHue === 0` as valid chromatic, not as falsy fallback.

#### Scenario: Chromatic profile with hue 0 (red)
- **WHEN** profile is `{ isChromatic: true, dominantHue: 0, dominantLightness: 50 }`
- **THEN** returns `0` (not the name-hash fallback)

### Requirement: HYPE_TIERS completeness
`HYPE_TIERS` SHALL have an entry for every value of the `Hype` union type.

#### Scenario: All hype values present
- **WHEN** checking keys of `HYPE_TIERS`
- **THEN** keys include `'watch'`, `'home'`, `'nearby'`, `'away'`

#### Scenario: Each entry has labelKey and icon
- **WHEN** iterating all entries
- **THEN** every entry has non-empty `labelKey` and non-empty `icon`

### Requirement: HYPE_ORDER and LANE_ORDER completeness
Exported order constants SHALL cover every value of their respective union types.

#### Scenario: HYPE_ORDER keys match HypeLevel
- **WHEN** checking keys of `HYPE_ORDER`
- **THEN** keys are exactly `['watch', 'home', 'nearby', 'away']`

#### Scenario: LANE_ORDER keys match LaneType
- **WHEN** checking keys of `LANE_ORDER`
- **THEN** keys are exactly `['home', 'nearby', 'away']`

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

### Requirement: SafePredictor interface in entity layer

The entity layer SHALL define a `SafePredictor` interface to decouple the adapter layer from infrastructure blockchain imports.

#### Scenario: TicketHandler uses SafePredictor interface

- **WHEN** TicketHandler needs to compute a Safe address
- **THEN** it SHALL depend on `entity.SafePredictor` interface
- **AND** SHALL NOT import `internal/infrastructure/blockchain/safe` directly

#### Scenario: SafePredictor implementation satisfies interface

- **WHEN** `safe.Predictor` is used as the concrete implementation
- **THEN** it SHALL satisfy the `entity.SafePredictor` interface via compile-time check
