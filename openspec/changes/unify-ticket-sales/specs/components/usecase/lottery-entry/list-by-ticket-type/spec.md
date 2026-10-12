# Spec Delta

## Purpose

LotteryEntryUseCase.ListByTicketType returns the calling fan's LotteryEntries for a TicketType, so the fan sees whether they have entered and, after the draw, whether they won.

## ADDED Requirements

### Requirement: Caller's entries for a ticket type

ListByTicketType SHALL take a TicketType and the calling fan and return the fan's entries for it from LotteryEntry.ListByTicketTypeAndUser, newest first. It SHALL return an empty list when the fan has none, and SHALL fail with NotFound when the TicketType does not exist (TicketType.Get).

#### Scenario: Entered entry
- **WHEN** the fan has an Entered entry for the TicketType
- **THEN** it is returned

#### Scenario: Fan won
- **WHEN** the draw has run and the fan's entry is Won
- **THEN** the returned entry is Won

#### Scenario: Fan lost
- **WHEN** the draw has run and the fan's entry is Lost
- **THEN** the returned entry is Lost

#### Scenario: Never entered
- **WHEN** the fan has no entry for the TicketType
- **THEN** an empty list is returned
