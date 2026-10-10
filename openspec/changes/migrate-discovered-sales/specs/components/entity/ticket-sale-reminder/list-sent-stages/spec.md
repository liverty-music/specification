# Spec Delta

## Purpose

ListSentStages returns, for one TicketSale and a set of users, the reminder stages already recorded as sent to each of those users.

## ADDED Requirements

### Requirement: ListSentStages returns the recorded stages per user

ListSentStages SHALL return, for each of the given users that has at least one ticket sale reminder for the given TicketSale, the set of stages recorded for that user. Users without a record, and records of users not given, SHALL be absent from the result. It SHALL fail with InvalidArgument when the TicketSale is not given, and with Internal on an unexpected failure.

#### Scenario: Some stages sent
- **WHEN** `APPLY_OPEN` and `APPLY_CLOSE_24H` of a sale were recorded for user A and nothing for user B, and ListSentStages runs for the sale with users A and B
- **THEN** the result maps user A to `APPLY_OPEN` and `APPLY_CLOSE_24H` and has no entry for user B

#### Scenario: No users given
- **WHEN** ListSentStages runs for a sale with no users
- **THEN** it returns an empty result without an error

#### Scenario: Missing ticket sale
- **WHEN** ListSentStages is called without a TicketSale
- **THEN** it fails with InvalidArgument
