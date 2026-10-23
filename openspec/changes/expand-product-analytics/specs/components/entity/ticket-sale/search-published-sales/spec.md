## ADDED Requirements

### Requirement: Each external call reports its usage

Every request SearchPublishedSales sends to the search service, including the second request after an invalid one and one that fails, SHALL be reported once for product analytics as an LLM generation under the caller's trace, with the same contents as for Concert.Search, except that it carries the series searched instead of a start date, and the numbers of sales returned and kept and the number discarded per reason instead of parsed series and events. The prompt text and the response body SHALL NOT be reported. A failure to report SHALL NOT change what SearchPublishedSales returns.

#### Scenario: Discarded sale
- **WHEN** the service returns 3 sales and 1 is discarded because it already opened
- **THEN** the generation reports 3 returned, 2 kept and 1 discarded for that reason
