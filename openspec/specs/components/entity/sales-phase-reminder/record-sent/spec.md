# SalesPhaseReminder.RecordSent

## Purpose

RecordSent records that a reminder stage of a sales phase has been sent to a user.

## Requirements

### Requirement: At most one record per user, sales phase and stage

RecordSent SHALL create a sales phase reminder for the given user, sales phase and stage, with the current time as sent time. Recording the same user, sales phase and stage again SHALL succeed and change nothing.

#### Scenario: First record

- **WHEN** RecordSent runs for a user, a phase and `APPLY_OPEN` with no earlier record
- **THEN** a sales phase reminder is created for them

#### Scenario: Repeated record

- **WHEN** RecordSent runs again for the same user, phase and `APPLY_OPEN`
- **THEN** it succeeds and the existing record, with its sent time, is unchanged

### Requirement: RecordSent validates its input

RecordSent SHALL fail with InvalidArgument when the user or the sales phase is not given, and with Internal on an unexpected failure.

#### Scenario: Missing user

- **WHEN** RecordSent is called without a user
- **THEN** it fails with InvalidArgument and records nothing
