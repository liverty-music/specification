## ADDED Requirements

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
