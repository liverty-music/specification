# components/usecase/lottery-entry/confirm Specification

## Purpose
LotteryEntryUseCase.Confirm turns a fan's Draft LotteryEntry into an Entered entry that takes part in the draw, after checking that its card authorization confirms it.

## Requirements

### Requirement: Confirm one's own draft once its card is authorized

Confirm SHALL take a LotteryEntry and the calling fan. It SHALL:
- read the entry with LotteryEntry.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another fan;
- fail with FailedPrecondition when the entry is not confirmable or its sale's window is not open at the current time;
- read the entry's card authorization with CardAuthorization.Get, returning its failure unchanged, and check that it confirms the entry for the TicketType's price times the ticket count: fail with FailedPrecondition when it is not Authorized or its card brand is not accepted, and with InvalidArgument when its amount differs;
- set the state to Entered with LotteryEntry.UpdateState and return the entry.

Confirming an Entered entry again SHALL return it unchanged. No money is captured at entry.

#### Scenario: Fan confirms
- **WHEN** a fan confirms their Draft whose Authorized 16000 yen card authorization matches 2 tickets at 8000 yen
- **THEN** the entry is Entered with that card authorization and nothing is charged

#### Scenario: Confirmed twice
- **WHEN** the fan confirms an entry that is already Entered
- **THEN** the entry is returned unchanged

#### Scenario: Card authentication not completed
- **WHEN** the entry's card authorization is still Pending
- **THEN** Confirm fails with FailedPrecondition and the entry stays a Draft

#### Scenario: American Express card
- **WHEN** the entry's Authorized card authorization is on an American Express card
- **THEN** Confirm fails with FailedPrecondition and the entry stays a Draft

#### Scenario: Amount differs
- **WHEN** the card authorization is for 8000 yen and the entry is for 16000 yen
- **THEN** Confirm fails with InvalidArgument and the entry stays a Draft

#### Scenario: Draft without a card authorization
- **WHEN** the Draft has no card authorization
- **THEN** Confirm fails with FailedPrecondition

#### Scenario: Window closed
- **WHEN** the fan confirms at or after the sale's end time
- **THEN** Confirm fails with FailedPrecondition and the entry stays a Draft

#### Scenario: Someone else's entry
- **WHEN** a fan confirms an entry of another fan
- **THEN** Confirm fails with PermissionDenied and nothing changes
