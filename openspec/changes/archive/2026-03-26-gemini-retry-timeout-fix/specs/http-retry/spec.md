## MODIFIED Requirements

### Requirement: HTTP retry on transient errors
The system SHALL automatically retry HTTP requests that fail with transient status codes (408 Request Timeout, 429 Too Many Requests, 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout) using exponential backoff with jitter.

#### Scenario: Retry on 408 request timeout
- **WHEN** an external HTTP API returns 408 Request Timeout
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 429 rate limit
- **WHEN** an external HTTP API returns 429 Too Many Requests
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 500 internal server error
- **WHEN** an external HTTP API returns 500 Internal Server Error
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 502 bad gateway
- **WHEN** an external HTTP API returns 502 Bad Gateway
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 503 service unavailable
- **WHEN** an external HTTP API returns 503 Service Unavailable
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 504 gateway timeout
- **WHEN** an external HTTP API returns 504 Gateway Timeout
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: No retry on client errors
- **WHEN** an external HTTP API returns a 4xx status code other than 408 or 429
- **THEN** the system SHALL NOT retry and SHALL return the error immediately

#### Scenario: All retries exhausted
- **WHEN** all retry attempts are exhausted
- **THEN** the system SHALL return the last error to the caller

#### Scenario: All retries exhausted with transient errors only (graceful degradation)
- **WHEN** all retry attempts are exhausted
- **AND** all failures were transient errors (not permanent)
- **THEN** the Gemini concert searcher SHALL log a warning and return empty results instead of an error
- **AND** the CronJob batch process SHALL eventually discover the concerts on a subsequent run

## ADDED Requirements

### Requirement: Independent context per Gemini API retry
The Gemini API caller SHALL create a new context for each API call attempt using `context.WithoutCancel` from the parent context, with a fixed 120-second timeout. This ensures each retry has a fresh deadline independent of the parent RPC deadline, and preserves trace propagation.

#### Scenario: First attempt uses independent context
- **WHEN** the Gemini API is called for the first time in a request
- **THEN** the system SHALL create a new context derived from `context.WithoutCancel(parentCtx)` with a 120-second timeout
- **AND** the parent context's trace_id and span_id SHALL be preserved in the new context

#### Scenario: Retry uses fresh context
- **WHEN** a retryable error occurs and a retry is attempted
- **THEN** the system SHALL create a new context with a fresh 120-second timeout
- **AND** the new context SHALL NOT share the deadline of the previous attempt

#### Scenario: Client cancellation does not abort Gemini call
- **WHEN** the parent RPC context is canceled (e.g., client navigates away)
- **THEN** the in-progress Gemini API call SHALL continue to completion
- **AND** the backoff retry loop SHALL stop (no further retry attempts)

### Requirement: Backoff max interval aligned with Google recommendation
The exponential backoff `MaxInterval` SHALL be set to 60 seconds, aligned with the Google Vertex AI retry strategy documentation.

#### Scenario: Backoff interval capped at 60 seconds
- **WHEN** the calculated exponential backoff exceeds 60 seconds
- **THEN** the actual wait time SHALL be capped at 60 seconds
