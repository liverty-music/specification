# Spec Delta

## Purpose

LotteryEntryUseCase.Withdraw lets a fan give up their own LotteryEntry before the draw, releasing its card authorization.

## ADDED Requirements

### Requirement: Withdraw before the draw

Withdraw SHALL take an entry and the calling fan. It SHALL read the entry with LotteryEntry.Get, failing with NotFound when it does not exist; fail with PermissionDenied when the entry belongs to another fan; and fail with FailedPrecondition when the entry is not withdrawable. It SHALL then release the entry's card authorization with CardAuthorization.Release, when the entry has one, and only after that set the state to Withdrawn with LotteryEntry.UpdateState. When the release fails, its error SHALL be returned and the entry keeps its state. Withdrawal is possible until the draw runs, also after the window has closed.

#### Scenario: Withdraw before the draw
- **WHEN** a fan withdraws their Entered entry
- **THEN** its card authorization is released and its state is Withdrawn, and the fan may enter again while the window is open

#### Scenario: Withdraw a draft
- **WHEN** a fan withdraws their Draft that has no card authorization
- **THEN** its state is Withdrawn and no card authorization is released

#### Scenario: Window closed but not drawn
- **WHEN** a fan withdraws an Entered entry after the end time and before the draw
- **THEN** the card authorization is released and the entry is Withdrawn

#### Scenario: Already drawn
- **WHEN** the entry is Won or Lost
- **THEN** Withdraw fails with FailedPrecondition and nothing changes

#### Scenario: Another fan's entry
- **WHEN** a fan withdraws an entry of another fan
- **THEN** Withdraw fails with PermissionDenied and nothing changes

#### Scenario: Release fails
- **WHEN** CardAuthorization.Release fails with Unavailable
- **THEN** Withdraw fails with Unavailable and the entry stays Entered
