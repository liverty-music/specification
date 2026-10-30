# Spec Delta

## Purpose

LotteryEntry.ListByTicketSaleAndUser lists a user's LotteryEntries for one TicketSale, at most one for each event it names.

## ADDED Requirements

### Requirement: Entries of one user for one sale

ListByTicketSaleAndUser SHALL take a TicketSale and a user and return the user's entries for the sale, at most one for each event the sale names, in any state, each with its Order, and no entry of another user or another sale. It SHALL return an empty list when there is none.

#### Scenario: Entry of the user
- **WHEN** the user has an Entered entry for the sale and another user has an entry for it
- **THEN** only the user's Entered entry is returned

#### Scenario: Never entered
- **WHEN** the user has no entry for the sale
- **THEN** an empty list is returned
