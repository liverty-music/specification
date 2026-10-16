# components/usecase/lottery-entry/start Specification

## Purpose
LotteryEntryUseCase.Start begins a fan's LotteryEntry for a TicketType of an open Lottery sale, or resumes it, after checking the ticket count, the sale's verification requirement and the per-account limit. It returns the Draft entry, and records the referral code it was started with; nothing is held on the card yet.

## Requirements

### Requirement: Start an entry while the window is open

Start SHALL take a TicketType, the calling fan as user and a ticket count. In this order it SHALL:
- read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition when the sale's method is not Lottery;
- fail with InvalidArgument when the count breaks the LotteryEntry count rule;
- fail with FailedPrecondition when the sale's window is not open at the current time;
- apply the verification gate;
- fail with FailedPrecondition when the count does not fit the TicketType's per-account limit, counting the fan's Issued Tickets for the TicketType's event from Ticket.ListByUserAndEvent;
- call LotteryEntry.GetOrCreateDraft and return the Draft it gives, failing with FailedPrecondition when it reports that the fan already has an Entered, Won or Lost entry for the TicketType.

Starting again with the same count SHALL resume the same Draft.

#### Scenario: Fan starts an entry within the window
- **WHEN** a fan with no entry and no ticket for the event starts an entry for 2 tickets of an open sale's TicketType
- **THEN** a Draft for 2 tickets is returned and nothing is held on the card

#### Scenario: Fan reloads mid-entry
- **WHEN** the fan starts again with the same count
- **THEN** the same Draft is returned

#### Scenario: Window closed
- **WHEN** the fan starts at or after the sale's end time
- **THEN** Start fails with FailedPrecondition and stores nothing

#### Scenario: Count over the limit
- **WHEN** the fan requests more tickets than the TicketType's per-account limit
- **THEN** Start fails with InvalidArgument

#### Scenario: Presale winner reaches the limit
- **WHEN** the fan holds 4 Issued Tickets for the event from a presale and starts an entry for 1 ticket of a general sale TicketType whose per-account limit is 4
- **THEN** Start fails with FailedPrecondition and stores nothing

#### Scenario: Second entry
- **WHEN** the fan already has an Entered, Won or Lost entry for the TicketType
- **THEN** Start fails with FailedPrecondition and stores nothing

#### Scenario: Re-entry after withdrawal
- **WHEN** the fan's only earlier entry for the TicketType is Withdrawn and the window is open
- **THEN** Start returns a new Draft

### Requirement: Verification gate

When the sale requires verification, Start SHALL require the fan to hold an IdentityVerification whose status is Active, read with IdentityVerification.GetByUserID, and SHALL fail with FailedPrecondition otherwise. When the sale's requirement is None, no IdentityVerification is needed.

#### Scenario: No IdentityVerification
- **WHEN** the sale requires JPKI-only and the fan has never verified
- **THEN** Start fails with FailedPrecondition and stores nothing

#### Scenario: Verification not active
- **WHEN** the sale requires verification and the fan's IdentityVerification needs re-verification
- **THEN** Start fails with FailedPrecondition

#### Scenario: Active verification
- **WHEN** the sale requires verification and the fan's IdentityVerification is Active
- **THEN** Start continues with the other checks

### Requirement: Record the referral code the entry started with

Start SHALL also take an optional ReferralCode. When a code is given and LotteryEntry.GetOrCreateDraft returns a Draft, Start SHALL call Referral.Record for that Draft with the code and the current time before it returns the Draft, and SHALL return a failure of Referral.Record unchanged; starting again resumes the same Draft and records the code again. When no code is given, Start SHALL record nothing and an existing Referral of the Draft stays as it is. When an earlier check fails, nothing is recorded. Start SHALL NOT check the code against any list or against the event's Series; any valid ReferralCode is recorded.

#### Scenario: Entry from a referral link
- **WHEN** a fan starts an entry for 2 tickets of an open sale's TicketType with the code `member-a`
- **THEN** the Draft is returned and its Referral has the code `member-a`

#### Scenario: Another link before confirming
- **WHEN** the fan's Draft has the code `member-a` and the fan starts again with the same count and the code `member-b`
- **THEN** the same Draft is returned and its Referral's code is `member-b`

#### Scenario: Started again without a code
- **WHEN** the fan's Draft has the code `member-a` and the fan starts again with the same count and no code
- **THEN** the same Draft is returned and its Referral keeps `member-a`

#### Scenario: Already entered with a code
- **WHEN** the fan already has an Entered entry for the TicketType whose Referral has the code `member-a`, and starts again with the code `member-b`
- **THEN** Start fails with FailedPrecondition and the Referral keeps `member-a`
