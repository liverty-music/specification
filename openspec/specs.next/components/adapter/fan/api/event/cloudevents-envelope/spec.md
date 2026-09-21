# Cloudevents Envelope

## Purpose

This capability defines the test coverage requirements for use case layer implementations, ensuring that business logic, input validation, dependency orchestration, and error propagation are verified through unit tests with mocked dependencies.

## Requirements

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
