# components/usecase/lottery-entry/authorize-card Specification

## Purpose
LotteryEntryUseCase.AuthorizeCard records the fan's 本人確認 (identity check) details and opens a card authorization for a ticket count of one TicketType, returning it with the card authorization secret the fan's browser uses to complete card authentication; it stores no entry.

## Requirements

### Requirement: Card authorized for a ticket count while the window is open

AuthorizeCard SHALL take a TicketType, the calling fan, a ticket count, a full name, a phone number and an optional ReferralCode. In this order it SHALL:
- read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition when the sale's method is not Lottery;
- fail with InvalidArgument when the count breaks the LotteryEntry count rule, or the full name or phone number is missing or breaks the User's personal details rule;
- fail with FailedPrecondition when the sale's window is not open at the current time;
- apply the verification gate;
- fail with FailedPrecondition when the count does not fit the TicketType's per-account limit, counting the fan's Issued Tickets for the TicketType's event from Ticket.ListByUserAndEvent;
- fail with FailedPrecondition when the fan already has an entry for the TicketType (LotteryEntry.ListByTicketTypeAndUser);
- store the full name and phone number on the fan's User with User.UpdatePersonalDetails;
- open a card authorization with CardAuthorization.Create for a lottery entry of the fan, the TicketType, the count and the code, for the TicketType's price times the count;
- return the card authorization's id and its card authorization secret, which SHALL NOT be stored.

It SHALL store no LotteryEntry, and failures of the operations it calls SHALL be returned unchanged. Any valid ReferralCode is passed on; it is not checked against any list or against the event's Series. Authorizing again, for another count, opens a new card authorization; one whose card authentication was never completed holds nothing on the card.

#### Scenario: Fan authorizes their card
- **WHEN** a fan with no entry authorizes their card for 2 tickets of an open sale's TicketType priced 8000 yen, giving a name and a phone number
- **THEN** a 16000 yen card authorization for the fan, the TicketType and 2 tickets is opened, the fan's User carries the name and phone number, the card authorization's id and secret are returned, and no entry exists yet

#### Scenario: Count changed before card authentication
- **WHEN** the fan authorizes their card for 2 tickets and then again for 3 tickets
- **THEN** a second card authorization of 24000 yen for 3 tickets is opened and no entry exists yet

#### Scenario: Entry from a referral link
- **WHEN** the fan authorizes their card with the code `member-a`
- **THEN** the card authorization carries the code `member-a`

#### Scenario: Window closed
- **WHEN** the fan authorizes their card at or after the sale's end time
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Count over the limit
- **WHEN** the fan requests more tickets than the TicketType's per-account limit
- **THEN** AuthorizeCard fails with InvalidArgument

#### Scenario: Presale winner reaches the limit
- **WHEN** the fan holds 4 Issued Tickets for the event from a presale and authorizes their card for 1 ticket of a general sale TicketType whose per-account limit is 4
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Already entered
- **WHEN** the fan already has an Entered, Won or Lost entry for the TicketType
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Missing identity details
- **WHEN** the full name or the phone number is empty
- **THEN** AuthorizeCard fails with InvalidArgument and no card authorization is opened

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Create fails with Unavailable
- **THEN** AuthorizeCard fails with Unavailable

### Requirement: Verification gate

When the sale requires verification, AuthorizeCard SHALL require the fan to hold an IdentityVerification whose status is Active, read with IdentityVerification.GetByUserID, and SHALL fail with FailedPrecondition otherwise. When the sale's requirement is None, no IdentityVerification is needed.

#### Scenario: No IdentityVerification
- **WHEN** the sale requires JPKI-only and the fan has never verified
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Verification not active
- **WHEN** the sale requires verification and the fan's IdentityVerification needs re-verification
- **THEN** AuthorizeCard fails with FailedPrecondition

#### Scenario: Active verification
- **WHEN** the sale requires verification and the fan's IdentityVerification is Active
- **THEN** AuthorizeCard continues with the other checks
