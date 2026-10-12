# Spec Delta

## Purpose

Returns the Order created for a won LotteryEntry, which tells whether that entry has already been issued.

## ADDED Requirements

### Requirement: Order of a lottery entry

GetByLotteryEntryID SHALL return the Order created from the given entry and SHALL fail with NotFound when the entry has no Order.

#### Scenario: Issued entry
- **WHEN** an Order exists for the entry
- **THEN** that Order is returned

#### Scenario: Not yet issued
- **WHEN** no Order exists for the entry
- **THEN** GetByLotteryEntryID fails with NotFound
