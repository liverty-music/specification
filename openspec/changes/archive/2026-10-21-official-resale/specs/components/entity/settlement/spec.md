## ADDED Requirements

### Requirement: Share of resold tickets

When k of the m Tickets of a Held Settlement's Order that are still Issued are resold, the Settlement SHALL give up the share of those tickets: its Organizer split falls by the split times k divided by m, rounded down to the yen, so rounding favours the Organizer. When k equals m, nothing is left to pay out for the Order and the Settlement SHALL become Reversed instead.

#### Scenario: One of two tickets resold
- **WHEN** a Held Settlement with a split of 9500 yen belongs to an Order with 2 Issued Tickets and 1 is resold
- **THEN** its split is 4750 yen

#### Scenario: One of three tickets resold
- **WHEN** a Held Settlement with a split of 9200 yen belongs to an Order with 3 Issued Tickets and 1 is resold
- **THEN** its split falls by 3066 yen to 6134 yen

#### Scenario: Last ticket resold
- **WHEN** a Held Settlement's Order has 1 Issued Ticket left and it is resold
- **THEN** the Settlement is Reversed
