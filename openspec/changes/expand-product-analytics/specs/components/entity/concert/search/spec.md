## ADDED Requirements

### Requirement: Each external call reports its usage

Every request Search sends to the external search model, including a retried or repeated one and one that fails, SHALL be reported once for product analytics as an LLM generation under the caller's trace, carrying: the model and its release, the release version of the backend, the Artist, its official site, the pages listed in the request and the start date; the input, output, thinking, tool-use and cached token counts as separate numbers; the latency; the web search queries the model issued, the sources it cited, and each page read with its result; the finish reason, any block reason, and the numbers of series and events parsed; and, for a failure, the kind of failure. The prompt text and the response body SHALL NOT be reported. A failure to report SHALL NOT change what Search returns.

#### Scenario: Search with a retry
- **WHEN** the first request fails transiently and the second succeeds
- **THEN** two generations are reported under the same trace, the first marked as a transient failure

#### Scenario: Grounded search
- **WHEN** the model issues 3 web search queries and reads 2 pages
- **THEN** the generation lists the 3 queries and the 2 pages with their results
