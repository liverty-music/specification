## Purpose

This capability automates concert discovery by running a scheduled batch job that invokes `SearchNewConcerts` for all followed artists, ensuring the concert database stays up-to-date without manual user intervention.

## Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist, **except artists associated with an active organizer**. An artist associated with an active organizer SHALL be excluded from the discovery run — filtered out of the artist list **before** `SearchNewConcerts` is called (so the Gemini/search call is skipped entirely, not merely dropped downstream). Disassociating the artist (or deactivating the organizer) SHALL return it to the discovery run.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist not associated with an active organizer, sequentially

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

#### Scenario: Organizer-represented artist is skipped before search

- **WHEN** the discovery job builds its artist list and an artist is associated with an active organizer
- **THEN** the job SHALL NOT call `SearchNewConcerts` for that artist (the search/Gemini call is skipped)
- **AND** when that artist is later disassociated (or its organizer deactivated), the job SHALL call `SearchNewConcerts` for it again

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
