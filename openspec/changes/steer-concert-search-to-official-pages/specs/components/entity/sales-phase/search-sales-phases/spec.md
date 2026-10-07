## MODIFIED Requirements

### Requirement: A failed search fails

SearchSalesPhases SHALL call the search service once per search. When the service rejects that request as invalid, SearchSalesPhases SHALL send it once more without the optional report of the search service's own tool calls. SearchSalesPhases SHALL fail with an error, and return no phases, in these cases:

- The service is unreachable or overloaded: Unavailable.
- The service rejects the request: the matching error (InvalidArgument when the request without the tool-call report is rejected as invalid too, Unauthenticated, ResourceExhausted including a spend cap, or DeadlineExceeded).
- The service returns no result, or a result that cannot be read: Internal.

A readable result that lists no sale SHALL return no phases without an error.

#### Scenario: Spend cap reached

- **WHEN** the search service rejects the request because the monthly spend cap is reached
- **THEN** SearchSalesPhases fails with ResourceExhausted

#### Scenario: No result

- **WHEN** the search service answers without a result
- **THEN** SearchSalesPhases fails with Internal

#### Scenario: Service unreachable

- **WHEN** the search service is unreachable
- **THEN** SearchSalesPhases fails with Unavailable

#### Scenario: Invalid request recovered without the tool report

- **WHEN** the search service rejects the request as invalid and accepts it without the tool-call report
- **THEN** SearchSalesPhases returns the phases of the second request

#### Scenario: Invalid request rejected twice

- **WHEN** the search service rejects the request as invalid with and without the tool-call report
- **THEN** SearchSalesPhases fails with InvalidArgument after those two requests
