## ADDED Requirements

### Requirement: Graceful shutdown ordering for event consumer

The event consumer process SHALL complete all in-flight message handlers before closing downstream resources (publisher, database). The shutdown sequence SHALL follow the order: stop accepting new messages → drain in-flight handlers → flush publisher → close external clients → flush telemetry → close datastore.

#### Scenario: SIGTERM during message processing
- **WHEN** the consumer receives SIGTERM while handlers are processing messages
- **THEN** the consumer SHALL wait for all in-flight handlers to complete before closing the publisher or database connection
- **AND** successfully processed messages SHALL be acknowledged to the message broker

#### Scenario: SIGTERM with no in-flight messages
- **WHEN** the consumer receives SIGTERM with no messages being processed
- **THEN** the consumer SHALL proceed through all shutdown phases and exit with code 0

### Requirement: Consumer health server lifecycle independence

The consumer health server SHALL be cleaned up on all exit paths, including DI initialization failure.

#### Scenario: DI initialization failure
- **WHEN** the consumer health server starts but DI initialization subsequently fails
- **THEN** the health server SHALL be gracefully shut down before the process exits
- **AND** the health server port SHALL be released

### Requirement: Nil-safe shutdown on initialization failure

All entry points (API server, event consumer, CronJobs) SHALL execute the shutdown sequence without panicking, even when application initialization fails partway through.

#### Scenario: DI failure with partial resource initialization
- **WHEN** DI initialization fails after some resources (e.g., database connection) have been created
- **THEN** the shutdown sequence SHALL execute with a fallback timeout
- **AND** the process SHALL NOT panic due to nil application references
- **AND** any partially-initialized resources registered in the shutdown manager SHALL be closed
