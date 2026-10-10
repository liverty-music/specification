# Spec Delta

## Purpose

LotteryUseCase.GetMyEntry returns the calling fan's active LotteryEntry for a TicketType, in whatever state it is.

## ADDED Requirements

### Requirement: Caller's active entry

GetMyEntry SHALL return the calling fan's active entry for the TicketType with LotteryEntry.GetByTicketTypeAndUser, and SHALL fail with NotFound when the fan has none; a fan whose entries are all Withdrawn has none.

#### Scenario: Entered entry
- **WHEN** the fan has an Entered entry for the TicketType
- **THEN** it is returned

#### Scenario: Only withdrawn
- **WHEN** the fan's only entry for the TicketType is Withdrawn
- **THEN** GetMyEntry fails with NotFound
