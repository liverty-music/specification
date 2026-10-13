# Spec Delta

## Purpose

AlreadySent reports whether a reminder stage of a TicketSale has already been recorded as sent to a user.

## ADDED Requirements

### Requirement: AlreadySent reports an existing record

AlreadySent SHALL return true when a ticket sale reminder exists for the given user, TicketSale and stage, and false otherwise. It SHALL fail with InvalidArgument when the user or the TicketSale is not given, and with Internal on an unexpected failure.

#### Scenario: Recorded
- **WHEN** `APPLY_CLOSE_24H` of a sale was recorded as sent to a user
- **THEN** AlreadySent for that user, sale and stage returns true

#### Scenario: Not recorded
- **WHEN** no reminder of stage `RESULT_DAY` was recorded for a user and a sale
- **THEN** AlreadySent for that user, sale and stage returns false

#### Scenario: Missing ticket sale
- **WHEN** AlreadySent is called without a TicketSale
- **THEN** it fails with InvalidArgument
