## ADDED Requirements

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
