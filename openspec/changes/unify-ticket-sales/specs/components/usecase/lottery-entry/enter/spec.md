# Spec Delta

## Purpose

LotteryUseCase.Enter records a fan's LotteryEntry for a TicketType of an open Lottery sale after checking the requested count, the fan's 本人確認 (identity check) details, the sale's verification requirement, the per-account limit, that the fan has no active entry, and that the fan's hold matches the amount.

## ADDED Requirements

### Requirement: Enter with an authenticated hold

Enter SHALL take a TicketType, the calling fan as user, a requested ticket count, the fan's full name and phone number, and the reference of a hold opened by CreateAuthorization. In this order it SHALL:
- read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition when the sale's method is not Lottery;
- fail with InvalidArgument when the count breaks the LotteryEntry count rule;
- fail with InvalidArgument when the full name or phone number is missing or breaks the User's personal details rule;
- fail with FailedPrecondition when the sale's window is not open at the current time;
- apply the verification gate;
- fail with FailedPrecondition when LotteryEntry.GetByTicketTypeAndUser finds an active entry of the fan for the TicketType;
- fail with FailedPrecondition when the count does not fit the TicketType's per-account limit, counting the fan's Issued Tickets for the TicketType's event from Ticket.ListByUserAndEvent;
- verify the hold with LotteryEntry.VerifyAuthorization for the TicketType's amount for the count, returning its failure unchanged.

It SHALL then store the full name and phone number on the fan's User with User.UpdatePersonalDetails, store the entry with LotteryEntry.Create and return the entry. No money is captured at entry.

#### Scenario: Fan enters within the window
- **WHEN** a fan with no active entry and no ticket for the event enters 2 tickets for an open sale's TicketType with an authenticated 16000 yen hold, giving a name and a phone number
- **THEN** a LotteryEntry is stored in state Entered with the hold's reference, the fan's User carries the name and phone number, and nothing is charged

#### Scenario: Window closed
- **WHEN** the fan enters at or after the sale's end time
- **THEN** Enter fails with FailedPrecondition and stores nothing

#### Scenario: Count over the limit
- **WHEN** the fan requests more tickets than the TicketType's per-account limit
- **THEN** Enter fails with InvalidArgument

#### Scenario: Presale winner reaches the limit
- **WHEN** the fan holds 4 Issued Tickets for the event from a presale and enters 1 ticket for a general sale TicketType whose per-account limit is 4
- **THEN** Enter fails with FailedPrecondition and stores nothing

#### Scenario: Missing identity details
- **WHEN** the full name or the phone number is empty
- **THEN** Enter fails with InvalidArgument

#### Scenario: Second entry
- **WHEN** the fan already has an Entered, Won or Lost entry for the TicketType
- **THEN** Enter fails with FailedPrecondition and stores nothing

#### Scenario: Hold does not verify
- **WHEN** LotteryEntry.VerifyAuthorization fails, for example because the card is American Express or the amount differs
- **THEN** Enter fails with the same error and stores nothing

#### Scenario: Re-entry after withdrawal
- **WHEN** the fan's only earlier entry for the TicketType is Withdrawn and the window is open
- **THEN** Enter stores a new entry

### Requirement: Verification gate

When the sale requires verification, Enter SHALL require the fan to hold a verified identity whose status is Active, read with VerifiedIdentity.GetByUserID, and SHALL fail with FailedPrecondition otherwise. When the sale's requirement is None, no verified identity is needed.

#### Scenario: No verified identity
- **WHEN** the sale requires JPKI-only and the fan has never verified
- **THEN** Enter fails with FailedPrecondition and stores nothing

#### Scenario: Verification not active
- **WHEN** the sale requires verification and the fan's verified identity needs re-verification
- **THEN** Enter fails with FailedPrecondition

#### Scenario: Active verification
- **WHEN** the sale requires verification and the fan's verified identity is Active
- **THEN** Enter continues with the other checks
