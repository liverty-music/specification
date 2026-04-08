## Purpose

This capability automates concert discovery by running a scheduled batch job that invokes `SearchNewConcerts` for all followed artists, ensuring the concert database stays up-to-date without manual user intervention.

## Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist sequentially

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

### Requirement: Circuit Breaker on Consecutive Failures

The job SHALL stop processing further artists after 3 consecutive errors from `SearchNewConcerts`, treating this as a systemic failure indicator.

#### Scenario: 3 consecutive errors triggers stop

- **WHEN** `SearchNewConcerts` returns an error for 3 consecutive artists
- **THEN** the job SHALL log a warning indicating circuit break activation
- **AND** stop processing remaining artists
- **AND** exit with status code 0

#### Scenario: Successful search resets error counter

- **WHEN** `SearchNewConcerts` succeeds after 1 or 2 consecutive errors
- **THEN** the consecutive error counter SHALL reset to 0
- **AND** processing continues normally

#### Scenario: Individual artist failure is non-fatal

- **WHEN** `SearchNewConcerts` returns an error for a single artist (fewer than 3 consecutive)
- **THEN** the job SHALL log the error with the artist ID
- **AND** continue processing the next artist

### Requirement: Job Always Exits Successfully

The CronJob SHALL always exit with status code 0 regardless of individual or total artist processing outcomes.

#### Scenario: All artists fail

- **WHEN** every artist search results in an error (including circuit break)
- **THEN** the job SHALL exit with status code 0

#### Scenario: Partial success

- **WHEN** some artists succeed and some fail
- **THEN** the job SHALL exit with status code 0
- **AND** log the total count of discovered concerts and failed artists

### Requirement: Job-Specific Dependency Injection

The CronJob SHALL use a lightweight DI initializer that provisions only the dependencies required for batch processing, without starting an HTTP server.

#### Scenario: Job initialization

- **WHEN** the concert discovery job starts
- **THEN** it SHALL initialize config, logger, database, repositories, Gemini searcher, and ConcertUseCase
- **AND** the Gemini searcher SHALL be initialized with `HTTPClient: nil` to use SDK-managed ADC authentication
- **AND** it SHALL NOT initialize HTTP server, RPC handlers, auth interceptors, or in-memory caches

#### Scenario: Graceful resource cleanup

- **WHEN** the job completes (success or circuit break)
- **THEN** it SHALL close all initialized resources (database connections, telemetry)

### Requirement: Gemini Response Resilience

The concert search SHALL gracefully handle incomplete or invalid responses from the Gemini API by validating response completeness before JSON parsing, retrying transient failures, and classifying errors by severity.

#### Scenario: FinishReason is not STOP

- **WHEN** the Gemini API returns a response with a `FinishReason` other than `STOP` or empty string
- **THEN** the system SHALL treat this as a retryable transient error
- **AND** retry the API call within the existing backoff loop (up to max retries)
- **AND** if all retries are exhausted, log a WARN with the `FinishReason` value and response metadata
- **AND** return empty results (no error propagated to caller)

#### Scenario: Gemini returns invalid JSON with FinishReason STOP

- **WHEN** the Gemini API returns `FinishReason: STOP` but the response text is not valid JSON
- **THEN** the system SHALL treat this as a retryable transient error
- **AND** log a WARN with the first 1000 characters of the raw response text and total response length
- **AND** retry the API call within the existing backoff loop
- **AND** if all retries are exhausted, return empty results (no error propagated to caller)

#### Scenario: Valid JSON with unexpected structure

- **WHEN** the Gemini API returns valid JSON that does not match the expected `EventsResponse` schema
- **THEN** the system SHALL treat this as a permanent (non-retryable) ERROR
- **AND** log an ERROR with the response text

#### Scenario: Successful response after transient retry

- **WHEN** the Gemini API returns an invalid response on the first attempt but a valid response on a subsequent retry
- **THEN** the system SHALL parse the valid response normally
- **AND** return the discovered concerts

### Requirement: Consumer JetStream Delivery Policy

The NATS JetStream consumer SHALL use `DeliverNew` delivery policy so that a newly created durable consumer only receives messages published after its creation time, preventing historical message redelivery when consumer state is lost due to infrastructure events (e.g., cluster migration, PVC recreation).

#### Scenario: First consumer creation after state loss

- **WHEN** the durable JetStream consumer is created for the first time (no prior consumer state exists)
- **THEN** the consumer SHALL only receive messages published from that point forward
- **AND** messages published before consumer creation SHALL NOT be redelivered

#### Scenario: Consumer reconnects to existing durable

- **WHEN** a consumer pod restarts and reconnects to an existing durable consumer
- **THEN** the consumer SHALL resume from the last acknowledged message sequence
- **AND** the delivery policy SHALL have no effect on reconnection behavior

### Requirement: Consumer JetStream Acknowledgement Policy

The NATS JetStream consumer SHALL use synchronous acknowledgement (`AckSync`) to guarantee that a message's Ack is confirmed by the NATS server before the handler is considered complete, preventing message redelivery due to lost Acks during pod shutdown.

#### Scenario: Successful message processing

- **WHEN** a message handler completes successfully
- **THEN** the consumer SHALL wait for NATS server confirmation of the Ack before marking the handler as done
- **AND** the NATS JetStream consumer lag SHALL reflect the acknowledged message as processed

#### Scenario: Simultaneous pod scale-down

- **WHEN** KEDA scales down multiple consumer pods simultaneously
- **THEN** all in-flight Acks SHALL be confirmed by the NATS server before pod shutdown completes
- **AND** KEDA SHALL observe consumer lag = 0 after scale-down
- **AND** KEDA SHALL NOT re-activate the consumer deployment within the cooldown period
