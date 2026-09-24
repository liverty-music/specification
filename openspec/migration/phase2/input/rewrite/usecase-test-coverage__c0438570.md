<!-- spec: usecase-test-coverage | target: components/adapter/fan/api/event/user-created-consumer | flags: CLASSNAME | new_name: User event consumer test coverage -->

### Requirement: User event consumer test coverage

The `user_consumer.go` handler under `internal/adapter/event/` SHALL have unit tests verifying event parsing and use case delegation.

#### Scenario: User created event handled

- **WHEN** a `USER.created` CloudEvent is received
- **THEN** the consumer SHALL parse the event data and invoke the appropriate use case method

#### Scenario: Malformed event payload rejected

- **WHEN** an event with invalid JSON payload is received
- **THEN** the consumer SHALL return an error
- **AND** the error SHALL be wrapped with event context
