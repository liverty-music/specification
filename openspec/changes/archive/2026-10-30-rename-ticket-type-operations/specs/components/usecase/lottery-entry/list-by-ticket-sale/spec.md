# Spec Delta

## Purpose

LotteryEntryUseCase.ListByTicketSale returns the calling fan's LotteryEntries in a Lottery TicketSale, so the fan sees whether they have entered and, after the draw, whether they won.

## ADDED Requirements

### Requirement: Caller's entries in a sale

ListByTicketSale SHALL take a Lottery TicketSale and the calling fan and return the fan's entries in it, each with its Order's TicketStock and ticket count, from LotteryEntry.ListByTicketSaleAndUser; a fan has at most one for each event the sale names. It SHALL return an empty list when the fan has none, and SHALL fail with NotFound when the sale does not exist (TicketSale.Get).

#### Scenario: Entered entry
- **WHEN** the fan has an Entered entry in the sale for 2 S席 tickets
- **THEN** it is returned with the S席 stock and 2 tickets

#### Scenario: Fan won
- **WHEN** the draw has run and the fan's entry is Won
- **THEN** the returned entry is Won

#### Scenario: Fan lost
- **WHEN** the draw has run and the fan's entry is Lost
- **THEN** the returned entry is Lost

#### Scenario: Never entered
- **WHEN** the fan has no entry in the sale
- **THEN** an empty list is returned
