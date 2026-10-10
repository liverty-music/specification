# Spec Delta

## Purpose

LotteryUseCase.WithdrawEntry lets a fan give up their own LotteryEntry before the draw, releasing its hold.

## ADDED Requirements

### Requirement: Withdraw before the draw

WithdrawEntry SHALL take an entry and the calling fan. It SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist; fail with PermissionDenied when the entry belongs to another fan; and fail with FailedPrecondition when the entry is not withdrawable. It SHALL then release the hold with LotteryEntry.CancelAuthorization and only after that set the state to Withdrawn with LotteryEntry.UpdateState. When the release fails, its error SHALL be returned and the entry stays Entered. Withdrawal is possible until the draw runs, also after the window has closed.

#### Scenario: Withdraw before the draw
- **WHEN** a fan withdraws their Entered entry
- **THEN** its hold is released and its state is Withdrawn, and the fan may enter again while the window is open

#### Scenario: Window closed but not drawn
- **WHEN** a fan withdraws an Entered entry after the end time and before the draw
- **THEN** the hold is released and the entry is Withdrawn

#### Scenario: Already drawn
- **WHEN** the entry is Won or Lost
- **THEN** WithdrawEntry fails with FailedPrecondition and nothing changes

#### Scenario: Another fan's entry
- **WHEN** a fan withdraws an entry of another fan
- **THEN** WithdrawEntry fails with PermissionDenied and nothing changes

#### Scenario: Release fails
- **WHEN** LotteryEntry.CancelAuthorization fails with Unavailable
- **THEN** WithdrawEntry fails with Unavailable and the entry stays Entered
