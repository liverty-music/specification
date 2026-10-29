# components/entity/order/list-lottery-entry-ids-awaiting-issuance Specification

## Purpose
Lists the Won LotteryEntries that have no Order yet.

## Requirements

### Requirement: Won entries without an order

ListLotteryEntryIDsAwaitingIssuance SHALL return the id of every Won entry whose Order is Pending, and no other id. It SHALL return an empty list when there is none.

#### Scenario: Won without order
- **WHEN** an entry is Won and its Order is Pending
- **THEN** its id is returned

#### Scenario: Already issued
- **WHEN** a Won entry's Order is Paid
- **THEN** its id is not returned

#### Scenario: Not won
- **WHEN** an entry is Entered or Lost
- **THEN** its id is not returned
