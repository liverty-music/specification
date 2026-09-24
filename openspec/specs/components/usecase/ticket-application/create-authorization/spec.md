# LotteryUseCase.CreateAuthorization

## Purpose

LotteryUseCase.CreateAuthorization opens the hold a fan needs before applying: an authorization on the fan's card for the phase's price times the requested ticket count, while the window is open. No application is stored.

## Requirements

### Requirement: Open a hold for an intended application

CreateAuthorization SHALL take a phase and a requested ticket count. It SHALL read the phase with LotterySalesPhase.Get, failing with NotFound when it does not exist; fail with InvalidArgument when the count breaks the TicketApplication count rule for the phase; and fail with FailedPrecondition when the window is not open at the current time. It SHALL then call TicketApplication.CreateAuthorization for the phase's amount for that count and return the hold's reference and confirmation secret, which the fan's browser uses to complete card authentication; the confirmation secret SHALL NOT be stored.

#### Scenario: Hold opened in an open window

- **WHEN** a fan asks for a hold for 2 tickets on an open phase priced 8000 yen
- **THEN** a 16000 yen hold is opened and its reference and confirmation secret are returned, and no application exists yet

#### Scenario: Window not open

- **WHEN** the phase's window has not opened yet or has closed
- **THEN** CreateAuthorization fails with FailedPrecondition and no hold is opened

#### Scenario: Count over the limit

- **WHEN** more tickets are requested than the phase allows per application
- **THEN** CreateAuthorization fails with InvalidArgument and no hold is opened

#### Scenario: Card payments unavailable

- **WHEN** TicketApplication.CreateAuthorization fails with Unavailable
- **THEN** CreateAuthorization fails with Unavailable
