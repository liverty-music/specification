## ADDED Requirements

### Requirement: Search asks for the lower-priced service level

Search SHALL ask the external search model for its lower-priced service level, which may answer later and may refuse a request while it is busy, and SHALL wait up to 15 minutes for each answer. A refusal because the service is busy, and an answer not received within 15 minutes, SHALL count as transient failures. The service level SHALL be configurable per environment, so the standard level can be used without a release.

#### Scenario: Late answer
- **WHEN** the external service answers a request after 9 minutes
- **THEN** Search returns the concerts of that answer

#### Scenario: Busy on every attempt
- **WHEN** the external service refuses all 3 attempts because it is busy
- **THEN** Search fails with Unavailable

#### Scenario: No answer within 15 minutes
- **WHEN** the external service has not answered a request 15 minutes after it was sent
- **THEN** that attempt counts as a transient failure and the next attempt is sent

## MODIFIED Requirements

### Requirement: Each external call reports its usage

Every request Search sends to the external search model, including a retried or repeated one and one that fails, SHALL be reported once for product analytics as an LLM generation under the caller's trace, carrying: the model and its release, the service level the request asked for, the release version of the backend, the Artist, its official site, the pages listed in the request and the start date; the input, output, thinking, tool-use and cached token counts as separate numbers; the latency; the web search queries the model issued, the sources it cited, and each page read with its result; the finish reason, any block reason, and the numbers of series and events parsed; and, for a failure, the kind of failure. The prompt text and the response body SHALL NOT be reported. A failure to report SHALL NOT change what Search returns.

#### Scenario: Search with a retry
- **WHEN** the first request fails transiently and the second succeeds
- **THEN** two generations are reported under the same trace, the first marked as a transient failure

#### Scenario: Grounded search
- **WHEN** the model issues 3 web search queries and reads 2 pages
- **THEN** the generation lists the 3 queries and the 2 pages with their results

#### Scenario: Lower-priced service level
- **WHEN** Search sends a request at the lower-priced service level
- **THEN** its generation carries that service level
