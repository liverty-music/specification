## REMOVED Requirements

### Requirement: Import ticket email route has component integration tests
**Reason**: The `ImportTicketEmailRoute` component and its route are removed with the ticket-email import capability, so there is nothing left to test.
**Migration**: None. The route component and its `import-ticket-email-route.spec.ts` test file are deleted.

The `ImportTicketEmailRoute` component SHALL have integration tests verifying multi-step wizard rendering and state transitions.

#### Scenario: Initial step renders input form
- **WHEN** the route is rendered in the initial step
- **THEN** the DOM SHALL contain the email input form

#### Scenario: Step advancement renders next step content
- **WHEN** the user completes the current step
- **THEN** the DOM SHALL transition to show the next step's content
