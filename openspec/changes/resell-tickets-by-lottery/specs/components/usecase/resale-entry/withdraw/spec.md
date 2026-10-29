# Spec Delta

## Purpose

ResaleEntryUseCase.Withdraw lets a fan cancel their own resale entry while it waits for a draw, so they are never charged for it and the hold on their card is given back.

## ADDED Requirements

### Requirement: A fan withdraws their own waiting entry

Withdraw SHALL take a User and a ResaleEntry. It SHALL read the entry with ResaleEntry.Get, failing with NotFound when it does not exist or its Order's user is not the given User. It SHALL withdraw it with ResaleEntry.Withdraw at the current time, returning FailedPrecondition unchanged when the entry is no longer Entered. The release of the Order's card authorization, as for a Lost entry, SHALL run from ResaleEntry.Withdraw's announcement, retrying while the payment provider cannot be reached, so Withdraw returns once the entry is Withdrawn. A failed release SHALL NOT undo the withdrawal. No email or push SHALL be sent, because the fan withdrew it themselves.

#### Scenario: Fan withdraws
- **WHEN** a fan withdraws their Entered entry for 2 tickets
- **THEN** the entry is Withdrawn, its Order Void, and its card authorization released without a charge

#### Scenario: Another fan's entry
- **WHEN** a fan withdraws an entry whose Order belongs to another user
- **THEN** it fails with NotFound and nothing changes

#### Scenario: Already drawn
- **WHEN** a fan withdraws an entry that won in the 12:00 draw
- **THEN** it fails with FailedPrecondition and the entry stays Won

#### Scenario: Payment provider unreachable
- **WHEN** the entry is withdrawn and the card authorization release cannot reach the payment provider
- **THEN** the entry stays Withdrawn and the release is tried again
