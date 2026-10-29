## Purpose

Makes a Won LotteryEntry Lost, and its Pending Order Void, when its card authorization can no longer be charged, so its tickets stay unallocated.

## ADDED Requirements

### Requirement: Revert only an uncharged win

RevertWin SHALL make a Won entry whose Order is Pending Lost, keeping its draw position, and make its Order Void, in one indivisible step. It SHALL change nothing and succeed when the entry is already Lost. It SHALL fail with FailedPrecondition and change nothing when the entry's Order is Paid, Refunded or Failed, or when the entry is Entered, and with NotFound when no entry has the id.

#### Scenario: Win reverted
- **WHEN** RevertWin is called for a Won entry with draw position 3 whose Order is Pending
- **THEN** the entry is Lost with draw position 3 and its Order is Void

#### Scenario: Already reverted
- **WHEN** RevertWin is called again for the same entry
- **THEN** it succeeds and nothing changes

#### Scenario: Win already issued
- **WHEN** the Won entry's Order is Paid
- **THEN** RevertWin fails with FailedPrecondition and nothing changes

#### Scenario: Not drawn
- **WHEN** the entry is Entered
- **THEN** RevertWin fails with FailedPrecondition and nothing changes

#### Scenario: Unknown entry
- **WHEN** no entry has the id
- **THEN** RevertWin fails with NotFound
