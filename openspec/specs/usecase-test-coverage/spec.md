# Usecase Test Coverage

## Purpose

This capability defines the test coverage requirements for use case layer implementations, ensuring that business logic, input validation, dependency orchestration, and error propagation are verified through unit tests with mocked dependencies.

## Requirements

### Requirement: TicketEmailUsecase Create Tests

The test suite SHALL verify that `TicketEmailUsecase.Create()` correctly validates input, invokes the Gemini parser, and persists records for each event ID.

#### Scenario: Create with valid lottery info email

- **WHEN** `Create()` is called with a valid `rawBody`, `emailType` = `LOTTERY_INFO`, and a list of `eventIDs`
- **THEN** the parser SHALL be invoked with the raw body and email type
- **AND** a `TicketEmail` record SHALL be created for each event ID
- **AND** the returned records SHALL contain the parsed data

#### Scenario: Create with valid lottery result email

- **WHEN** `Create()` is called with a valid `rawBody`, `emailType` = `LOTTERY_RESULT`, and a list of `eventIDs`
- **THEN** the parser SHALL be invoked with the raw body and email type
- **AND** a `TicketEmail` record SHALL be created for each event ID

#### Scenario: Create with invalid emailType

- **WHEN** `Create()` is called with an unrecognized or unspecified `emailType`
- **THEN** the system SHALL return an `InvalidArgument` error
- **AND** the parser SHALL NOT be invoked
- **AND** no records SHALL be persisted

#### Scenario: Create with empty rawBody

- **WHEN** `Create()` is called with an empty `rawBody`
- **THEN** the system SHALL return an `InvalidArgument` error
- **AND** the parser SHALL NOT be invoked

#### Scenario: Create when parser returns error

- **WHEN** `Create()` is called with valid input
- **AND** the Gemini parser returns an error
- **THEN** the system SHALL propagate the error
- **AND** no records SHALL be persisted

#### Scenario: Create when repository returns error

- **WHEN** `Create()` is called with valid input
- **AND** the repository `Create` call fails
- **THEN** the system SHALL propagate the error

### Requirement: TicketEmailUsecase Update Tests

The test suite SHALL verify that `TicketEmailUsecase.Update()` fetches the existing record, verifies ownership, updates the record, and triggers journey status upsert.

#### Scenario: Update with valid data

- **WHEN** `Update()` is called with a valid `ticketEmailID` owned by the calling user
- **THEN** the system SHALL fetch the existing record
- **AND** the system SHALL update the record with the provided fields
- **AND** the system SHALL trigger a journey status upsert

#### Scenario: Update with non-existent ID

- **WHEN** `Update()` is called with a `ticketEmailID` that does not exist in the repository
- **THEN** the system SHALL return a `NotFound` error

#### Scenario: Update with wrong userID (ownership check)

- **WHEN** `Update()` is called with a `ticketEmailID` that belongs to a different user
- **THEN** the system SHALL return a `NotFound` error
- **AND** no update SHALL be performed

#### Scenario: Update triggers journey status upsert

- **WHEN** `Update()` completes successfully
- **THEN** the system SHALL call the journey repository to upsert the ticket journey status
- **AND** the journey status SHALL be derived from the email type and parsed data

### Requirement: TicketEmailUsecase Helper Tests

The test suite SHALL verify the internal helper methods `buildNewTicketEmail()` and `determineJourneyStatus()`.

#### Scenario: buildNewTicketEmail constructs entity from parsed data

- **WHEN** `buildNewTicketEmail()` is called with parsed email data containing dates
- **THEN** the returned `NewTicketEmail` SHALL contain correctly parsed timestamps for `PaymentDeadline`, `LotteryStart`, `LotteryEnd`
- **AND** the `ApplicationURL` SHALL be set from the parsed data

#### Scenario: determineJourneyStatus with valid mapping

- **WHEN** `determineJourneyStatus()` is called with an email type and parsed data that map to a known status
- **THEN** the returned status SHALL match the expected `TicketJourneyStatus`

#### Scenario: determineJourneyStatus with no mapping (default)

- **WHEN** `determineJourneyStatus()` is called with data that does not map to a known status
- **THEN** the system SHALL return the default journey status

### Requirement: ArtistImageSyncUsecase SyncArtistImage Tests

The test suite SHALL verify that `ArtistImageSyncUsecase.SyncArtistImage()` correctly orchestrates artist fetch, image resolution, logo color analysis, and fanart update.

#### Scenario: Sync with valid MBID

- **WHEN** `SyncArtistImage()` is called for an artist with a valid MusicBrainz ID
- **THEN** the image resolver SHALL be called to resolve the image URL
- **AND** the logo image fetcher SHALL be called to download and analyze the logo
- **AND** the fanart record SHALL be updated with the resolved image URL and logo color

#### Scenario: Sync with empty MBID

- **WHEN** `SyncArtistImage()` is called for an artist with an empty MusicBrainz ID
- **THEN** the system SHALL return early without error
- **AND** the image resolver SHALL NOT be called

#### Scenario: Sync when image resolver returns NotFound

- **WHEN** `SyncArtistImage()` is called for a valid artist
- **AND** the image resolver returns a `NotFound` error
- **THEN** the fanart record SHALL be updated with nil image URL (marking the artist as synced)
- **AND** the system SHALL NOT return an error

#### Scenario: Sync when logo fetch fails

- **WHEN** `SyncArtistImage()` is called for a valid artist
- **AND** the image is resolved successfully
- **AND** the logo image fetcher returns an error
- **THEN** the fanart record SHALL be updated with the resolved image URL but without logo color data
- **AND** the system SHALL NOT return an error

#### Scenario: Sync when artist repository returns error

- **WHEN** `SyncArtistImage()` is called
- **AND** the artist repository returns an error when fetching the artist
- **THEN** the system SHALL propagate the error
- **AND** no fanart update SHALL occur

### Requirement: Adapter mapper test coverage

All adapter mapper files under `internal/adapter/rpc/mapper/` SHALL have corresponding test files verifying Proto-to-Entity and Entity-to-Proto conversions.

#### Scenario: Concert mapper tested

- **WHEN** a Concert entity is converted to Proto and back
- **THEN** all fields (event ID, artist, venue, dates, title) SHALL round-trip correctly
- **AND** nil/zero-value fields SHALL be handled without panic

#### Scenario: Follow mapper tested

- **WHEN** a FollowedArtist entity is converted to Proto
- **THEN** hype level, artist details, and follow metadata SHALL map correctly

#### Scenario: Ticket mapper tested

- **WHEN** a Ticket entity is converted to Proto
- **THEN** token ID, tx hash, event ID, and minted timestamp SHALL map correctly

#### Scenario: TicketEmail mapper tested

- **WHEN** a TicketEmail entity is converted to Proto
- **THEN** email type, parsed data fields, and optional timestamps SHALL map correctly

#### Scenario: TicketJourney mapper tested

- **WHEN** a TicketJourney entity is converted to Proto
- **THEN** journey status enum and event reference SHALL map correctly

### Requirement: Messaging layer test coverage

The messaging infrastructure under `internal/infrastructure/messaging/` SHALL have unit tests for event publishing, CloudEvents formatting, and stream configuration.

#### Scenario: CloudEvents message construction tested

- **WHEN** a domain event is published via EventPublisher
- **THEN** the CloudEvents envelope SHALL contain correct `id`, `source`, `type`, `time`, and `datacontenttype` fields
- **AND** the payload SHALL be valid JSON

#### Scenario: Publisher fallback to GoChannel tested

- **WHEN** NATS URL is empty (local development)
- **THEN** the publisher SHALL use GoChannel (in-memory) without error

#### Scenario: Subscriber durable name generation tested

- **WHEN** a subscriber is created for topic `concert.discovered`
- **THEN** the durable consumer name SHALL be `concert_discovered` (dots replaced with underscores)

### Requirement: User event consumer test coverage

The `user_consumer.go` handler under `internal/adapter/event/` SHALL have unit tests verifying event parsing and use case delegation.

#### Scenario: User created event handled

- **WHEN** a `USER.created` CloudEvent is received
- **THEN** the consumer SHALL parse the event data and invoke the appropriate use case method

#### Scenario: Malformed event payload rejected

- **WHEN** an event with invalid JSON payload is received
- **THEN** the consumer SHALL return an error
- **AND** the error SHALL be wrapped with event context

### Requirement: Package utility test coverage

Utility packages `pkg/geo/` and `pkg/api/` SHALL have unit tests.

#### Scenario: Haversine distance calculation tested

- **WHEN** two coordinate pairs are provided
- **THEN** the Haversine function SHALL return the correct great-circle distance in kilometers
- **AND** edge cases (same point, antipodal points) SHALL be handled

#### Scenario: API error mapping tested

- **WHEN** an `apperr.Error` with a known code is passed to the error mapper
- **THEN** the corresponding HTTP status code SHALL be returned
