# User Created Consumer

## Purpose

This capability defines the test coverage requirements for use case layer implementations, ensuring that business logic, input validation, dependency orchestration, and error propagation are verified through unit tests with mocked dependencies.

## Requirements

### Requirement: User event consumer test coverage

The user-created event consumer SHALL have unit tests verifying event parsing and use case delegation.

#### Scenario: User created event handled

- **WHEN** a `USER.created` CloudEvent is received
- **THEN** the consumer SHALL parse the event data and invoke the appropriate use case method

#### Scenario: Malformed event payload rejected

- **WHEN** an event with invalid JSON payload is received
- **THEN** the consumer SHALL return an error
- **AND** the error SHALL be wrapped with event context
