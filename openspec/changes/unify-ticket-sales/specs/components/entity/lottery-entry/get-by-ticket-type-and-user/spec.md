# Spec Delta

## Purpose

Returns a user's active LotteryEntry for one TicketType.

## ADDED Requirements

### Requirement: Active entry of a user

GetByTicketTypeAndUser SHALL return the user's active entry for the TicketType and SHALL fail with NotFound when the user has none; Withdrawn entries are never returned.

#### Scenario: Active entry exists
- **WHEN** the user has an Entered, Won or Lost entry for the TicketType
- **THEN** that entry is returned

#### Scenario: Only withdrawn entries
- **WHEN** every entry of the user for the TicketType is Withdrawn
- **THEN** GetByTicketTypeAndUser fails with NotFound

#### Scenario: Never entered
- **WHEN** the user has no entry for the TicketType
- **THEN** GetByTicketTypeAndUser fails with NotFound
