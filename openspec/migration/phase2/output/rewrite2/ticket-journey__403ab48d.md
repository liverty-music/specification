<!-- spec: ticket-journey | target: components/infrastructure/fan/web/global/event-detail-sheet | flags: CLASSNAME | new_name: Ticket Status UI visibility -->

### Requirement: Ticket Status UI visibility

The Ticket Status UI in the event detail sheet SHALL only be rendered when the user is authenticated. Unauthenticated (guest) users SHALL NOT see the Ticket Status section.

#### Scenario: Authenticated user sees Ticket Status section

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the Ticket Status section SHALL be visible
- **AND** the user SHALL be able to select a status (TRACKING, APPLIED, LOST, UNPAID, PAID)

#### Scenario: Unauthenticated user does not see Ticket Status section

- **WHEN** an unauthenticated (guest) user opens the concert detail sheet
- **THEN** the Ticket Status section SHALL NOT be rendered
- **AND** no RPC call to `TicketJourneyService/SetStatus` SHALL be made
