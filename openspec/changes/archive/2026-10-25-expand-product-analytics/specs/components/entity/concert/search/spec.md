## ADDED Requirements

### Requirement: Each external call reports its usage

Every request Search sends to the external search model, including a retried or repeated one and one that fails, SHALL be reported once for product analytics as an LLM generation under the caller's trace, carrying: the model and its release, the release version of the backend, the Artist, its official site, the pages listed in the request and the start date; the input, output, thinking, tool-use and cached token counts as separate numbers; the latency; the web search queries the model issued, the sources it cited, and each page read with its result; the finish reason, any block reason, and the numbers of series and events parsed; and, for a failure, the kind of failure. The prompt text and the response body SHALL NOT be reported. A failure to report SHALL NOT change what Search returns.

#### Scenario: Search with a retry
- **WHEN** the first request fails transiently and the second succeeds
- **THEN** two generations are reported under the same trace, the first marked as a transient failure

#### Scenario: Grounded search
- **WHEN** the model issues 3 web search queries and reads 2 pages
- **THEN** the generation lists the 3 queries and the 2 pages with their results

## RENAMED Requirements

- FROM: `### Requirement: Transient failures degrade to no results`
- TO: `### Requirement: Transient failures are retried`

## MODIFIED Requirements

### Requirement: Transient failures are retried

Search SHALL retry a transient external failure — a timeout, rate limit, server error, temporary authorization failure or incomplete response — for up to 3 attempts in total. When every attempt fails transiently, Search SHALL fail with Unavailable, so the caller records a failed search rather than a search that found nothing. When the external service rejects the request as invalid, Search SHALL send it once more without the optional report of the external service's own tool calls, and SHALL fail with an error only if that request is rejected too. A permanent failure, a structurally broken response (including a response that ends normally with no text, since a result with no concerts is still a result), a response that carries no candidate result, a response stopped because the model made too many tool calls, or the caller's own deadline or cancellation SHALL fail Search with an error; a response with no candidate result or stopped for too many tool calls SHALL NOT be retried within the same Search.

#### Scenario: Recovered on retry
- **WHEN** the first attempt times out and the second succeeds
- **THEN** Search returns the second attempt's concerts

#### Scenario: All attempts transient
- **WHEN** all 3 attempts are rate-limited
- **THEN** Search fails with Unavailable after those 3 attempts

#### Scenario: Invalid request recovered without the tool report
- **WHEN** the external service rejects the request as invalid and accepts it without the tool-call report
- **THEN** Search returns the concerts of the second request

#### Scenario: Invalid request rejected twice
- **WHEN** the external service rejects the request as invalid with and without the tool-call report
- **THEN** Search fails with an error after those two requests

#### Scenario: Response without a candidate
- **WHEN** the external service answers successfully but with no candidate result
- **THEN** Search fails with an error after that one attempt

#### Scenario: Too many tool calls
- **WHEN** the external service stops the response because the model made too many tool calls
- **THEN** Search fails with an error after that one attempt

#### Scenario: Caller deadline expires
- **WHEN** the caller's deadline expires during Search
- **THEN** Search fails with an error

#### Scenario: Deadline passes during a call that then succeeds
- **WHEN** the caller's deadline passes while a call is in flight, and that call later returns concerts
- **THEN** Search fails with an error and returns no concerts

#### Scenario: Response without text
- **WHEN** the external service ends its response normally but with no text
- **THEN** Search fails with an error after that one attempt
