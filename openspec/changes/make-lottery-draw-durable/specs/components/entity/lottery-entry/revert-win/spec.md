## Purpose

Makes a Won LotteryEntry Lost when its card authorization can no longer be charged, so its tickets stay unallocated.

## ADDED Requirements

### Requirement: Revert only an uncharged win

RevertWin SHALL make a Won entry that has no Order Lost, keeping its draw position. It SHALL change nothing and succeed when the entry is already Lost. It SHALL fail with FailedPrecondition and change nothing when the entry has an Order or is Entered, and with NotFound when no entry has the id.

#### Scenario: Win reverted
- **WHEN** RevertWin is called for a Won entry with draw position 3 and no Order
- **THEN** the entry is Lost with draw position 3

#### Scenario: Already reverted
- **WHEN** RevertWin is called again for the same entry
- **THEN** it succeeds and nothing changes

#### Scenario: Win already issued
- **WHEN** the Won entry has an Order
- **THEN** RevertWin fails with FailedPrecondition and nothing changes

#### Scenario: Not drawn
- **WHEN** the entry is Entered
- **THEN** RevertWin fails with FailedPrecondition and nothing changes

#### Scenario: Unknown entry
- **WHEN** no entry has the id
- **THEN** RevertWin fails with NotFound
