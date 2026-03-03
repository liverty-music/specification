## ADDED Requirements

### Requirement: Resilient External Search

The system SHALL retry transient failures from the external search API using exponential backoff before reporting an error. The `SearchNewConcerts` RPC SHALL have a dedicated timeout (≥15 seconds) independent of the global handler timeout to accommodate the latency of AI-grounded search.

#### Scenario: Transient Gemini timeout is retried

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** the API returns a transient error (504 Gateway Timeout, 503 Unavailable, 429 Too Many Requests, or 499 Client Cancelled)
- **THEN** the system MUST retry the call up to 2 additional times with exponential backoff
- **AND** return results if any retry succeeds

#### Scenario: All retries exhausted

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** all retry attempts fail with transient errors
- **THEN** the system MUST return an error to the caller
- **AND** log each failed attempt with the error details

#### Scenario: Non-transient error is not retried

- **WHEN** `SearchNewConcerts` calls the external search API
- **AND** the API returns a non-transient error (400 Bad Request, 401 Unauthorized)
- **THEN** the system MUST NOT retry the call
- **AND** return the error immediately
