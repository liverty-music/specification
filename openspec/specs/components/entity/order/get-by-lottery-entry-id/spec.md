# components/entity/order/get-by-lottery-entry-id Specification

## Purpose
Returns the Order created for a won LotteryEntry, which tells whether that entry has already been issued.

## Requirements

### Requirement: Order of a lottery entry

GetByLotteryEntryID SHALL return the Order the given entry names, in any status; a Paid Order tells that the entry has been issued. It SHALL fail with NotFound when no LotteryEntry has the id.

#### Scenario: Issued entry
- **WHEN** the entry's Order is Paid
- **THEN** that Order is returned, Paid

#### Scenario: Not yet issued
- **WHEN** a Won entry's Order is Pending
- **THEN** that Order is returned, Pending

#### Scenario: Unknown entry
- **WHEN** no LotteryEntry has the id
- **THEN** GetByLotteryEntryID fails with NotFound
