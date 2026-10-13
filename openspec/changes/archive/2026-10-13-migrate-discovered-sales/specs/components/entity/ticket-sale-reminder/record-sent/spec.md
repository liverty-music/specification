# Spec Delta

## Purpose

RecordSent records that a reminder stage of a TicketSale has been sent to a user, at most once per user, sale and stage.

## ADDED Requirements

### Requirement: At most one record per user, ticket sale and stage

RecordSent SHALL create a ticket sale reminder for the given user, TicketSale and stage, with the current time as sent time. Recording the same user, TicketSale and stage again SHALL succeed and change nothing.

#### Scenario: First record
- **WHEN** RecordSent runs for a user, a sale and `APPLY_OPEN` with no earlier record
- **THEN** a ticket sale reminder is created for them

#### Scenario: Repeated record
- **WHEN** RecordSent runs again for the same user, sale and `APPLY_OPEN`
- **THEN** it succeeds and the existing record, with its sent time, is unchanged

### Requirement: RecordSent validates its input

RecordSent SHALL fail with InvalidArgument when the user or the TicketSale is not given, and with Internal on an unexpected failure.

#### Scenario: Missing user
- **WHEN** RecordSent is called without a user
- **THEN** it fails with InvalidArgument and records nothing
