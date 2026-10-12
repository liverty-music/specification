# Spec Delta

## Purpose

Lists the Won LotteryEntries that have no Order yet.

## ADDED Requirements

### Requirement: Won entries without an order

ListLotteryEntryIDsAwaitingIssuance SHALL return the id of every Won entry that has no Order, and no other id. It SHALL return an empty list when there is none.

#### Scenario: Won without order
- **WHEN** an entry is Won and has no Order
- **THEN** its id is returned

#### Scenario: Already issued
- **WHEN** a Won entry already has an Order
- **THEN** its id is not returned

#### Scenario: Not won
- **WHEN** an entry is Entered, Lost or Withdrawn
- **THEN** its id is not returned
