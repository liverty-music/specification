# Spec Delta

## MODIFIED Requirements

### Requirement: At most one record per user, ticket sale and stage

RecordSent SHALL create a ticket sale reminder for the given user, TicketSale and stage, with the current time as send time. Recording the same user, TicketSale and stage again SHALL succeed and change nothing.

#### Scenario: First record
- **WHEN** RecordSent runs for a user, a sale and `APPLY_OPEN` with no earlier record
- **THEN** a ticket sale reminder is created for them

#### Scenario: Repeated record
- **WHEN** RecordSent runs again for the same user, sale and `APPLY_OPEN`
- **THEN** it succeeds and the existing record, with its send time, is unchanged
