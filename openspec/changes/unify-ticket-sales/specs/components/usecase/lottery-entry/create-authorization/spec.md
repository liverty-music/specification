# Spec Delta

## Purpose

LotteryUseCase.CreateAuthorization opens the hold a fan needs before entering: an authorization on the fan's card for the TicketType's price times the requested ticket count, while the sale's window is open. No entry is stored.

## ADDED Requirements

### Requirement: Open a hold for an intended entry

CreateAuthorization SHALL take a TicketType and a requested ticket count. It SHALL read the TicketType and its sale with TicketType.Get, failing with NotFound when it does not exist; fail with FailedPrecondition when the sale's method is not Lottery; fail with InvalidArgument when the count breaks the LotteryEntry count rule for the TicketType; and fail with FailedPrecondition when the sale's window is not open at the current time. It SHALL then call LotteryEntry.CreateAuthorization for the TicketType's amount for that count and return the hold's reference and confirmation secret, which the fan's browser uses to complete card authentication; the confirmation secret SHALL NOT be stored.

#### Scenario: Hold opened in an open window
- **WHEN** a fan asks for a hold for 2 tickets of an open sale's TicketType priced 8000 yen
- **THEN** a 16000 yen hold is opened and its reference and confirmation secret are returned, and no entry exists yet

#### Scenario: Window not open
- **WHEN** the sale's window has not opened yet or has closed
- **THEN** CreateAuthorization fails with FailedPrecondition and no hold is opened

#### Scenario: Count over the limit
- **WHEN** more tickets are requested than the TicketType's per-account limit
- **THEN** CreateAuthorization fails with InvalidArgument and no hold is opened

#### Scenario: Card payments unavailable
- **WHEN** LotteryEntry.CreateAuthorization fails with Unavailable
- **THEN** CreateAuthorization fails with Unavailable
