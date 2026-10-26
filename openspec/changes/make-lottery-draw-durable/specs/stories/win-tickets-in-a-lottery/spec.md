## ADDED Requirements

### Requirement: A draw that stops midway keeps its winners

When the platform stops while it draws a sale or charges its winners, the draw SHALL resume with the same winners: every Won fan SHALL be charged once and receive their Tickets, and no fan SHALL be charged without Tickets.

#### Scenario: Stopped after the first charge
- **WHEN** a sale's TicketType of 4 tickets closes with entries for 2, 2 and 3 tickets, the platform stops after charging one of the two winners, and starts again
- **THEN** the same two entries are Won, each winner is charged once and holds 2 Issued Tickets, and the 3-ticket entry is Lost and never charged
