# Spec Delta

## Purpose

LotteryEntryUseCase.AuthorizeCard records the fan's 本人確認 (identity check) details and opens the card authorization for their own Draft LotteryEntry, returning the card authorization secret the fan's browser uses to complete card authentication.

## ADDED Requirements

### Requirement: Details recorded and card authorization opened for one's own draft

AuthorizeCard SHALL take a LotteryEntry, the calling fan, a full name and a phone number. It SHALL:
- read the entry with LotteryEntry.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another fan;
- fail with FailedPrecondition when the entry is not a Draft or its sale's window is not open at the current time;
- fail with InvalidArgument when the full name or phone number is missing or breaks the User's personal details rule;
- store the full name and phone number on the fan's User with User.UpdatePersonalDetails;
- when the Draft has no card authorization, open one with CardAuthorization.Create for the entry, for the TicketType's price times the ticket count, and record it with LotteryEntry.SetCardAuthorization; when it has one, read it with CardAuthorization.Get;
- return the card authorization secret, which SHALL NOT be stored.

Their failures SHALL be returned unchanged. No money is captured.

#### Scenario: Fan authorizes their card
- **WHEN** a fan authorizes their card for their Draft for 2 tickets of a TicketType priced 8000 yen, giving a name and a phone number
- **THEN** a 16000 yen card authorization is opened and recorded on the Draft, the fan's User carries the name and phone number, and the card authorization secret is returned

#### Scenario: Card declined, fan retries
- **WHEN** the fan authorizes their card for the same Draft again after the card was declined
- **THEN** the secret of the same card authorization is returned for another attempt and no second one is opened

#### Scenario: Someone else's entry
- **WHEN** a fan authorizes their card for an entry of another fan
- **THEN** AuthorizeCard fails with PermissionDenied and nothing changes

#### Scenario: Missing identity details
- **WHEN** the full name or the phone number is empty
- **THEN** AuthorizeCard fails with InvalidArgument and no card authorization is opened

#### Scenario: Window closed
- **WHEN** the fan authorizes their card at or after the sale's end time
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Payment provider unavailable
- **WHEN** CardAuthorization.Create fails with Unavailable
- **THEN** AuthorizeCard fails with Unavailable and the Draft has no card authorization
