# SalesPhaseReminder.AlreadySent

## Purpose

AlreadySent reports whether a reminder stage of a sales phase has already been recorded as sent to a user.

## Requirements

### Requirement: AlreadySent reports an existing record

AlreadySent SHALL return true when a sales phase reminder exists for the given user, sales phase and stage, and false otherwise. It SHALL fail with InvalidArgument when the user or the sales phase is not given, and with Internal on an unexpected failure.

#### Scenario: Recorded

- **WHEN** `APPLY_CLOSE_1H` of a phase was recorded as sent to a user
- **THEN** AlreadySent for that user, phase and stage returns true

#### Scenario: Not recorded

- **WHEN** no reminder of stage `RESULT_DAY` was recorded for a user and a phase
- **THEN** AlreadySent for that user, phase and stage returns false

#### Scenario: Missing sales phase

- **WHEN** AlreadySent is called without a sales phase
- **THEN** it fails with InvalidArgument
