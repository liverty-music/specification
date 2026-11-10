## MODIFIED Requirements

### Requirement: A stored status is announced with the change

When UpsertIfReplaceable stores a status, it SHALL announce the journey under its stored status (TicketJourney.Tracking, TicketJourney.Applied, TicketJourney.Lost, TicketJourney.Unpaid or TicketJourney.Paid), carrying the journey with its status and status set by, together with the change: both are stored or neither is. When it stores nothing or fails, it SHALL announce nothing. When the announcement cannot be recorded, it SHALL fail with Unavailable and leave the journey as it was.

#### Scenario: Status stored

- **WHEN** UpsertIfReplaceable stores Tracking set by inference
- **THEN** the journey is announced once as Tracking (TicketJourney.Tracking), carrying it at Tracking set by inference

#### Scenario: Nothing stored

- **WHEN** the fan's journey is not replaceable, or already has the given status and status set by, and UpsertIfReplaceable is called
- **THEN** nothing is announced
