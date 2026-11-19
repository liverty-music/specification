# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Record sets the searched time of every given series`
- TO: `### Requirement: Record sets the search time of every given series`

## MODIFIED Requirements

### Requirement: Record sets the search time of every given series

Record SHALL set the search time of each given series to the given time, creating the series' TicketSaleSearch when it has none and replacing the earlier search time otherwise. Either every given series is recorded or none is. An empty input SHALL record nothing without an error.

#### Scenario: Series searched again
- **WHEN** series A was last searched on 1 September and Record is called for series A at 1 October
- **THEN** series A's search time becomes 1 October

#### Scenario: Series searched for the first time
- **WHEN** Record is called for a series that has no TicketSaleSearch
- **THEN** a TicketSaleSearch is created for it with the given time
