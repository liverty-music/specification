# Capability: Concert Search Internals

## Purpose

Defines internal quality requirements for the concert search usecase implementation. These requirements enforce Clean Architecture boundaries, testability, and code structure. They do not affect any external behavior -- all existing concert search functionality remains identical.

## ADDED Requirements

### Requirement: Usecase layer SHALL NOT import infrastructure packages

The concert search usecase (`internal/usecase/`) SHALL NOT directly import any package from `internal/infrastructure/`. All infrastructure dependencies SHALL be accessed through interfaces defined in the usecase or entity layer.

#### Scenario: No infrastructure/geo import

- **WHEN** the concert usecase resolves centroid coordinates for proximity search
- **THEN** it SHALL call a `CentroidResolver` interface injected via dependency injection
- **AND** the usecase package SHALL NOT contain any import of `internal/infrastructure/geo`

#### Scenario: No direct infrastructure imports in usecase package

- **WHEN** reviewing the import declarations of files in `internal/usecase/`
- **THEN** no file SHALL import any path matching `internal/infrastructure/*`

### Requirement: Search status marking SHALL use defer pattern

The `executeSearch` method SHALL mark the search as failed or completed using a single `defer` block on the named error return value. There SHALL NOT be multiple scattered calls to `markSearchFailed` or `markSearchCompleted` within the method body.

#### Scenario: Search fails at any step

- **WHEN** `executeSearch` returns a non-nil error at any point in its execution
- **THEN** the defer block SHALL call `markSearchFailed` exactly once
- **AND** no other code path in `executeSearch` SHALL call `markSearchFailed`

#### Scenario: Search completes successfully

- **WHEN** `executeSearch` returns a nil error
- **THEN** the defer block SHALL call `markSearchCompleted` exactly once
- **AND** no other code path in `executeSearch` SHALL call `markSearchCompleted`

### Requirement: Time-dependent tests SHALL use testing/synctest

Tests for time-dependent concert search logic (search log freshness, pending timeout) SHALL use `testing/synctest` (Go 1.25+ standard library) for deterministic time control. Production code SHALL continue to call `time.Now()` / `time.Since()` directly — no custom Clock interface SHALL be introduced.

#### Scenario: Search log freshness test

- **WHEN** a test verifies that a recently completed search is skipped
- **THEN** the test SHALL use `synctest.Test(t, func(t *testing.T){...})` to control the fake clock
- **AND** the production code SHALL call `time.Since()` without any Clock abstraction

#### Scenario: Pending search timeout test

- **WHEN** a test verifies that a stale pending search is retried
- **THEN** the test SHALL advance synthetic time past `pendingTimeout` using `time.Sleep` inside the synctest bubble
- **AND** the test result SHALL be deterministic regardless of wall-clock time

### Requirement: resolveUserID SHALL NOT be duplicated

The `resolveUserID` function SHALL exist in exactly one location within `internal/usecase/`. All usecases that need to resolve a user ID from context claims SHALL call the shared function.

#### Scenario: Concert usecase resolves user ID

- **WHEN** the concert usecase needs to resolve the authenticated user's ID
- **THEN** it SHALL call the shared `resolveUserID` function
- **AND** SHALL NOT contain its own copy of the resolution logic

#### Scenario: Follow usecase resolves user ID

- **WHEN** the follow usecase needs to resolve the authenticated user's ID
- **THEN** it SHALL call the same shared `resolveUserID` function
- **AND** SHALL NOT contain its own copy of the resolution logic

### Requirement: Entity construction SHALL use domain methods

The `executeSearch` method SHALL NOT construct `entity.Concert` objects inline. Concert entity construction from scraped data SHALL use `ScrapedConcert.ToConcert()` (provided by the `extract-entity-domain-logic` change).

#### Scenario: Converting scraped concerts to entities

- **WHEN** `executeSearch` processes results from the external search API
- **THEN** it SHALL call `ScrapedConcert.ToConcert()` to construct each `entity.Concert`
- **AND** SHALL NOT manually assign entity fields from scraped data inline
