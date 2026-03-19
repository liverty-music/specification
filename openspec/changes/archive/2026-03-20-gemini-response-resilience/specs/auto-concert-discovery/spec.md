## ADDED Requirements

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
