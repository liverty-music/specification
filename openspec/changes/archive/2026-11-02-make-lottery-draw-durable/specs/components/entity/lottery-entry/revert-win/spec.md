## Purpose

Makes a Won LotteryEntry Lost, and its Pending Order Void, when its card authorization can no longer be charged, so its tickets stay unallocated.

## ADDED Requirements

### Requirement: Revert only an uncharged win

RevertWin SHALL make a Won entry whose Order is Pending Lost with the lost reason "card could not be charged", keeping its draw position, and make its Order Void, in one indivisible step. It SHALL change nothing and succeed when the entry is already Lost. It SHALL fail with FailedPrecondition and change nothing when the entry's Order is Paid or Refunded, or when the entry is Entered, and with NotFound when no entry has the id.

#### Scenario: Win reverted
- **WHEN** RevertWin is called for a Won entry with draw position 3 whose Order is Pending
- **THEN** the entry is Lost with draw position 3 and the lost reason "card could not be charged", and its Order is Void

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

### Requirement: A reverted win is announced with the change

When RevertWin makes an entry Lost, it SHALL announce the entry, as it is after the change, together with the change: both are stored or neither is. When it changes nothing it SHALL announce nothing. When the announcement cannot be recorded, RevertWin SHALL fail with Unavailable and change nothing. The announcement is what product analytics records as the entry's "lottery result" signal for the lost win.

#### Scenario: Win reverted and announced
- **WHEN** RevertWin makes a Won entry Lost
- **THEN** one lottery result is announced, carrying the entry Lost with the lost reason "card could not be charged"

#### Scenario: Already reverted announces nothing
- **WHEN** RevertWin is called again for an entry it already made Lost
- **THEN** nothing is announced

#### Scenario: Announcement cannot be recorded
- **WHEN** the announcement of a reverted win cannot be recorded
- **THEN** RevertWin fails with Unavailable, the entry stays Won and its Order stays Pending
