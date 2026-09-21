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

