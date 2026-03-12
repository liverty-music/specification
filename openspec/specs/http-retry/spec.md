## ADDED Requirements

### Requirement: HTTP retry on transient errors
The system SHALL automatically retry HTTP requests that fail with transient status codes (429 Too Many Requests, 503 Service Unavailable, 504 Gateway Timeout) using exponential backoff with jitter.

#### Scenario: Retry on 429 rate limit
- **WHEN** an external HTTP API returns 429 Too Many Requests
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 503 service unavailable
- **WHEN** an external HTTP API returns 503 Service Unavailable
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: Retry on 504 gateway timeout
- **WHEN** an external HTTP API returns 504 Gateway Timeout
- **THEN** the system SHALL wait with exponential backoff and retry the request up to 3 times

#### Scenario: No retry on client errors
- **WHEN** an external HTTP API returns a 4xx status code other than 429
- **THEN** the system SHALL NOT retry and SHALL return the error immediately

#### Scenario: All retries exhausted
- **WHEN** all retry attempts are exhausted
- **THEN** the system SHALL return the last error to the caller

### Requirement: Retry-After header respect
The system SHALL parse and respect the `Retry-After` HTTP header when present in a response, using the specified delay as the minimum backoff for that retry attempt.

#### Scenario: Retry-After with delta-seconds
- **WHEN** a 429 response includes a `Retry-After: 5` header
- **THEN** the system SHALL wait at least 5 seconds before retrying

#### Scenario: Retry-After with HTTP-date
- **WHEN** a 429 response includes a `Retry-After` header with an HTTP-date value
- **THEN** the system SHALL wait until the specified time before retrying

### Requirement: Context cancellation during retry
The system SHALL respect context cancellation during retry backoff waits, stopping the retry loop immediately when the context is canceled or its deadline is exceeded.

#### Scenario: Context canceled during backoff
- **WHEN** the context is canceled while waiting for a retry backoff
- **THEN** the system SHALL stop retrying and return the context error

### Requirement: Request body replay for retried POST requests
The system SHALL correctly replay the request body for POST requests across retry attempts.

#### Scenario: POST request retried after 503
- **WHEN** a POST request to an external API receives 503 and is retried
- **THEN** the retried request SHALL contain the same body as the original request
