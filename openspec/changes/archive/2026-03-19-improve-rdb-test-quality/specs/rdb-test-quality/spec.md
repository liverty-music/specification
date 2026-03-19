## ADDED Requirements

### Requirement: Every repository method has error-path coverage
Each method defined in an `entity.*Repository` interface that documents possible errors SHALL have at least one integration test case per documented error code in the corresponding `rdb` test file.

#### Scenario: Documented NotFound error is tested
- **WHEN** a repository method documents `NotFound` as a possible error
- **THEN** the test file for that repository SHALL contain a test case that triggers `apperr.ErrNotFound`

#### Scenario: Documented AlreadyExists error is tested
- **WHEN** a repository method documents `AlreadyExists` as a possible error
- **THEN** the test file SHALL contain a test case that triggers `apperr.ErrAlreadyExists`

#### Scenario: Documented InvalidArgument error is tested
- **WHEN** a repository method documents `InvalidArgument` as a possible error
- **THEN** the test file SHALL contain a test case that triggers `apperr.ErrInvalidArgument`

#### Scenario: Documented FailedPrecondition error is tested
- **WHEN** a repository method documents `FailedPrecondition` as a possible error
- **THEN** the test file SHALL contain a test case that triggers `apperr.ErrFailedPrecondition`

### Requirement: All repository interfaces have test files
Every `entity.*Repository` interface implemented in the `rdb` package SHALL have a corresponding `_test.go` file with at least one test per interface method.

#### Scenario: PushSubscriptionRepository test file exists
- **WHEN** `push_subscription_repo.go` implements `entity.PushSubscriptionRepository`
- **THEN** `push_subscription_repo_test.go` SHALL exist with tests for Create, DeleteByEndpoint, ListByUserIDs, and DeleteByUserID

#### Scenario: TicketJourneyRepository test file exists
- **WHEN** `ticket_journey_repo.go` implements `entity.TicketJourneyRepository`
- **THEN** `ticket_journey_repo_test.go` SHALL exist with tests for Upsert, Delete, and ListByUser

### Requirement: Test files follow canonical structure
All `_test.go` files in the `rdb` package SHALL follow the go-tester skill's table-driven test pattern consistently.

#### Scenario: Loop variable naming
- **WHEN** iterating over test cases
- **THEN** the loop variable SHALL be named `tt` (not `tc` or other variants)

#### Scenario: Error assertion pattern
- **WHEN** asserting an expected error
- **THEN** the test SHALL use `assert.ErrorIs(t, err, tt.wantErr)` without a preceding `require.Error`

#### Scenario: Per-case database cleanup
- **WHEN** a test case requires a clean database state
- **THEN** `cleanDatabase()` SHALL be called within the case's `setup` function, not at the top-level of the test function

#### Scenario: No time.Sleep in tests
- **WHEN** a test needs to verify temporal ordering
- **THEN** the test SHALL NOT use `time.Sleep`; it SHALL use deterministic assertion or explicit timestamp injection

### Requirement: Shared seed helpers exist
The `setup_test.go` file SHALL provide reusable seed helpers for common entity creation, eliminating raw SQL INSERT duplication across test files.

#### Scenario: seedUser helper
- **WHEN** a test needs a user record
- **THEN** it SHALL call `seedUser(t, name, email, externalID)` which returns the user ID

#### Scenario: seedArtist helper
- **WHEN** a test needs an artist record
- **THEN** it SHALL call `seedArtist(t, name, mbid)` which returns the artist ID

#### Scenario: seedVenue helper
- **WHEN** a test needs a venue record
- **THEN** it SHALL call `seedVenue(t, name)` which returns the venue ID

#### Scenario: seedEvent helper
- **WHEN** a test needs an event record
- **THEN** it SHALL call `seedEvent(t, venueID, artistID, title, date)` which returns the event ID

### Requirement: cleanTables covers all tables
The `cleanTables()` function SHALL TRUNCATE all tables that have corresponding repository implementations, including `push_subscriptions`.

#### Scenario: push_subscriptions table is cleaned
- **WHEN** `cleanTables()` is called
- **THEN** the `push_subscriptions` table SHALL be truncated
