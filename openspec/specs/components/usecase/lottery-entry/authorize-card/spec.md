# components/usecase/lottery-entry/authorize-card Specification

## Purpose
LotteryEntryUseCase.AuthorizeCard records the fan's 本人確認 (identity check) details and opens a card authorization for a ticket count of one TicketStock of an event a Lottery TicketSale names, returning it with the card authorization secret the fan's browser uses to complete card authentication; it stores no entry.

## Requirements

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

### Requirement: Card authorized for a ticket count of a stock while the window is open

AuthorizeCard SHALL take a Lottery TicketSale, a TicketStock, the calling fan, a ticket count, a full name, a phone number and an optional ReferralCode. In this order it SHALL:
- read the sale with TicketSale.Get and the stock with TicketStock.Get, failing with NotFound when either does not exist, and fail with FailedPrecondition when the sale's method is not Lottery or the sale does not name the stock's event;
- fail with InvalidArgument when the count is below 1 or above the event's per-account limit, or the full name or phone number is missing or breaks the User's personal details rule;
- fail with FailedPrecondition when the sale's window is not open at the current time;
- apply the verification gate;
- read what the fan holds for the event with Order.GetHeldForEvent and fail with FailedPrecondition when the application does not fit the event;
- fail with FailedPrecondition when the fan already has an entry in the sale for the stock's event (LotteryEntry.ListByTicketTypeAndUser);
- store the full name and phone number on the fan's User with User.UpdatePersonalDetails;
- open a card authorization with CardAuthorization.Create for a lottery entry of the fan in the sale, for the stock, the count and the code, for the stock's SeatType amount for the count;
- return the card authorization's id and its card authorization secret, which SHALL NOT be stored.

It SHALL store no Order and no LotteryEntry, and failures of the operations it calls SHALL be returned unchanged. Any valid ReferralCode is passed on; it is not checked against any list or against the event's Series. Authorizing again, for another count or stock, opens a new card authorization; one whose card authentication was never completed holds nothing on the card.

#### Scenario: Fan authorizes their card
- **WHEN** a fan with no entry authorizes their card for 2 S席 tickets priced 8000 yen in an open lottery, giving a name and a phone number
- **THEN** a 16000 yen card authorization for the fan, the sale, the S席 stock and 2 tickets is opened, the fan's User carries the name and phone number, the card authorization's id and secret are returned, and no Order or entry exists yet

#### Scenario: Count changed before card authentication
- **WHEN** the fan authorizes their card for 2 tickets and then again for 3 tickets
- **THEN** a second card authorization of 24000 yen for 3 tickets is opened and no entry exists yet

#### Scenario: Entry from a referral link
- **WHEN** the fan authorizes their card with the code `member-a`
- **THEN** the card authorization carries the code `member-a`

#### Scenario: Window closed
- **WHEN** the fan authorizes their card at or after the sale's end time
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Stock of another event
- **WHEN** the stock's event is not named by the sale
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Count over the limit
- **WHEN** the fan requests more tickets than the event's per-account limit
- **THEN** AuthorizeCard fails with InvalidArgument

#### Scenario: Presale winner reaches the limit
- **WHEN** the event's per-account limit is 4, the fan won 4 S席 tickets in the presale, not yet issued, and authorizes their card for 1 S席 in the general sale
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Another seat type
- **WHEN** the fan holds 2 S席 tickets for the event and authorizes their card for 1 A席
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Already entered
- **WHEN** the fan already has an Entered, Won or Lost entry in the sale for the stock's event, for any stock of that event
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Missing identity details
- **WHEN** the full name or the phone number is empty
- **THEN** AuthorizeCard fails with InvalidArgument and no card authorization is opened

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Create fails with Unavailable
- **THEN** AuthorizeCard fails with Unavailable
