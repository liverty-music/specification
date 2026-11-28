## ADDED Requirements

### Requirement: Search asks for the lower-priced service level

Search SHALL ask the external search model for its lower-priced service level, which may answer later and may refuse a request while it is busy, and SHALL wait up to 15 minutes for each answer. A refusal because the service is busy, and an answer not received within 15 minutes, SHALL count as transient failures. The service level SHALL be configurable per environment, so the standard level can be used without a release.

#### Scenario: Late answer
- **WHEN** the external service answers a request after 9 minutes
- **THEN** Search returns the concerts of that answer

#### Scenario: No answer within 15 minutes
- **WHEN** the external service has not answered a request 15 minutes after it was sent
- **THEN** Search fails with Unavailable after that one request

### Requirement: A failed request is classified, not retried

Search SHALL NOT send a request again because it failed; a caller that can wait searches again later. A transient failure — a timeout, a lost connection, a rate limit, a busy service, a server error or a temporary authorization failure — SHALL fail Search with Unavailable, so the caller records a failed search rather than a search that found nothing. When the external service rejects the request as invalid, Search SHALL send it once more without the optional report of the external service's own tool calls, and SHALL fail with an error only if that request is rejected too. A permanent failure (such as a refused account), a structurally broken response (including a response that ends normally with no text, since a result with no concerts is still a result), a response that carries no candidate result, a response not completed normally (stopped for too many tool calls, at the output limit or for any other reason) and the caller's own deadline or cancellation SHALL fail Search with an error; a response with no candidate result or not completed normally SHALL fail it with an error other than Unavailable and DeadlineExceeded.

#### Scenario: Rate limited
- **WHEN** the external service refuses the request because of a rate limit
- **THEN** Search fails with Unavailable after that one request

#### Scenario: Busy
- **WHEN** the external service refuses the request because it is busy
- **THEN** Search fails with Unavailable after that one request

#### Scenario: Server error
- **WHEN** the external service answers the request with a server error
- **THEN** Search fails with Unavailable after that one request

#### Scenario: Connection lost
- **WHEN** the connection ends before the external service has answered
- **THEN** Search fails with Unavailable after that one request

#### Scenario: Invalid request recovered without the tool report
- **WHEN** the external service rejects the request as invalid and accepts it without the tool-call report
- **THEN** Search returns the concerts of the second request

#### Scenario: Invalid request rejected twice
- **WHEN** the external service rejects the request as invalid with and without the tool-call report
- **THEN** Search fails with an error after those two requests

#### Scenario: Response without a candidate
- **WHEN** the external service answers successfully but with no candidate result
- **THEN** Search fails with an error other than Unavailable and DeadlineExceeded after that one request

#### Scenario: Too many tool calls
- **WHEN** the external service stops the response because the model made too many tool calls
- **THEN** Search fails with an error other than Unavailable and DeadlineExceeded after that one request

#### Scenario: Response not completed
- **WHEN** the external service stops the response at the output limit
- **THEN** Search fails with an error other than Unavailable and DeadlineExceeded after that one request

#### Scenario: Response without text
- **WHEN** the external service ends its response normally but with no text
- **THEN** Search fails with an error after that one request

#### Scenario: Caller deadline expires
- **WHEN** the caller's deadline expires during Search
- **THEN** Search fails with an error

#### Scenario: Deadline passes during a call that then succeeds
- **WHEN** the caller's deadline passes while a call is in flight, and that call later returns concerts
- **THEN** Search fails with an error and returns no concerts

## MODIFIED Requirements

### Requirement: Each external call reports its usage

Every request Search sends to the external search model, including a repeated one and one that fails, SHALL be reported once for product analytics as an LLM generation under the caller's trace, carrying: the model and its release, the service level the request asked for, the release version of the backend, the Artist, its official site, the pages listed in the request and the start date; the input, output, thinking, tool-use and cached token counts as separate numbers; the latency; the web search queries the model issued, the sources it cited, and each page read with its result; the finish reason, any block reason, and the numbers of series and events parsed; and, for a failure, the kind of failure. The prompt text and the response body SHALL NOT be reported. A failure to report SHALL NOT change what Search returns.

#### Scenario: Search with a retry
- **WHEN** the first request is rejected as invalid and the second succeeds
- **THEN** two generations are reported under the same trace, the first marked as an invalid request

#### Scenario: Grounded search
- **WHEN** the model issues 3 web search queries and reads 2 pages
- **THEN** the generation lists the 3 queries and the 2 pages with their results

#### Scenario: Lower-priced service level
- **WHEN** Search sends a request at the lower-priced service level
- **THEN** its generation carries that service level

## REMOVED Requirements

### Requirement: Transient failures are retried
**Reason**: The background search retries a transient failure for up to 20 hours; 3 tries a few seconds apart inside Search cannot outlast a busy service and held a calling place for up to 45 minutes. An incomplete response is no longer transient.
**Migration**: "A failed request is classified, not retried".
