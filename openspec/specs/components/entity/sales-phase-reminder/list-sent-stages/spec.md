# SalesPhaseReminder.ListSentStages

## Purpose

ListSentStages returns, for one sales phase and a set of users, the reminder stages already recorded as sent to each of those users.

## Requirements

### Requirement: ListSentStages returns the recorded stages per user

ListSentStages SHALL return, for each of the given users that has at least one sales phase reminder for the given sales phase, the set of stages recorded for that user. Users without a record, and records of users not given, SHALL be absent from the result. It SHALL fail with InvalidArgument when the sales phase is not given, and with Internal on an unexpected failure.

#### Scenario: Some stages sent

- **WHEN** `APPLY_OPEN` and `APPLY_CLOSE_24H` of a phase were recorded for user A and nothing for user B, and ListSentStages runs for the phase with users A and B
- **THEN** the result maps user A to `APPLY_OPEN` and `APPLY_CLOSE_24H` and has no entry for user B

#### Scenario: No users given

- **WHEN** ListSentStages runs for a phase with no users
- **THEN** it returns an empty result without an error

#### Scenario: Missing sales phase

- **WHEN** ListSentStages is called without a sales phase
- **THEN** it fails with InvalidArgument
