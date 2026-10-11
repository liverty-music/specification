# Spec Delta

## Purpose

LotteryUseCase.Authorize records the fan's 本人確認 (identity check) details and opens the hold on the fan's card for their own Draft LotteryEntry, returning the secret the fan's browser uses to complete card authentication.

## ADDED Requirements

### Requirement: Details recorded and hold opened for one's own draft

Authorize SHALL take a LotteryEntry, the calling fan, a full name and a phone number. It SHALL:
- read the entry with LotteryEntry.Get and fail with PermissionDenied, without revealing whether it exists, when it does not exist or belongs to another fan;
- fail with FailedPrecondition when the entry is not a Draft or its sale's window is not open at the current time;
- fail with InvalidArgument when the full name or phone number is missing or breaks the User's personal details rule;
- store the full name and phone number on the fan's User with User.UpdatePersonalDetails;
- when the Draft has no authorization, open a hold with LotteryEntry.CreateAuthorization for the TicketType's amount for the requested count and record it with LotteryEntry.SetAuthorization; when it has one, use that hold;
- return the hold's confirmation secret, which SHALL NOT be stored.

Their failures SHALL be returned unchanged. No money is captured.

#### Scenario: Fan authorizes
- **WHEN** a fan authorizes their Draft for 2 tickets of a TicketType priced 8000 yen, giving a name and a phone number
- **THEN** a 16000 yen hold is opened and recorded on the Draft, the fan's User carries the name and phone number, and the confirmation secret is returned

#### Scenario: Card declined, fan retries
- **WHEN** the fan authorizes the same Draft again after the card was declined
- **THEN** the same hold is returned for another attempt

#### Scenario: Someone else's entry
- **WHEN** a fan authorizes an entry of another fan
- **THEN** Authorize fails with PermissionDenied and nothing changes

#### Scenario: Missing identity details
- **WHEN** the full name or the phone number is empty
- **THEN** Authorize fails with InvalidArgument and no hold is opened

#### Scenario: Window closed
- **WHEN** the fan authorizes at or after the sale's end time
- **THEN** Authorize fails with FailedPrecondition and no hold is opened

#### Scenario: Card payments unavailable
- **WHEN** LotteryEntry.CreateAuthorization fails with Unavailable
- **THEN** Authorize fails with Unavailable and the Draft has no authorization
