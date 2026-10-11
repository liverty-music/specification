# Spec Delta

## Purpose

LotteryUseCase.Confirm turns a fan's authorized Draft LotteryEntry into an Entered entry that takes part in the draw, after checking that the hold matches the amount.

## ADDED Requirements

### Requirement: Confirm one's own authorized draft

Confirm SHALL take a LotteryEntry and the calling fan. It SHALL:
- read the entry with LotteryEntry.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another fan;
- fail with FailedPrecondition when the entry is not confirmable or its sale's window is not open at the current time;
- verify the hold with LotteryEntry.VerifyAuthorization for the TicketType's amount for the requested count, returning its failure unchanged;
- set the state to Entered with LotteryEntry.UpdateState and return the entry.

Confirming an Entered entry again SHALL return it unchanged. No money is captured at entry.

#### Scenario: Fan confirms
- **WHEN** a fan confirms their Draft whose authenticated 16000 yen hold matches 2 tickets at 8000 yen
- **THEN** the entry is Entered with the hold's reference and nothing is charged

#### Scenario: Confirmed twice
- **WHEN** the fan confirms an entry that is already Entered
- **THEN** the entry is returned unchanged

#### Scenario: Hold does not verify
- **WHEN** LotteryEntry.VerifyAuthorization fails, for example because the card is American Express or card authentication is not complete
- **THEN** Confirm fails with the same error and the entry stays a Draft

#### Scenario: Draft without a hold
- **WHEN** the Draft has no authorization
- **THEN** Confirm fails with FailedPrecondition

#### Scenario: Window closed
- **WHEN** the fan confirms at or after the sale's end time
- **THEN** Confirm fails with FailedPrecondition and the entry stays a Draft

#### Scenario: Someone else's entry
- **WHEN** a fan confirms an entry of another fan
- **THEN** Confirm fails with PermissionDenied and nothing changes
