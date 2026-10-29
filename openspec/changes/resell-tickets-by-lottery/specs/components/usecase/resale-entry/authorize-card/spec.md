# Spec Delta

## Purpose

ResaleEntryUseCase.AuthorizeCard opens the card authorization a fan's official resale (公式リセール) application is paid with, for a ticket count of one sold-out TicketStock.

## ADDED Requirements

### Requirement: Card authorized for an application while resale is open

AuthorizeCard SHALL take the signed-in fan, a TicketStock, a ticket count, the fan's full name and phone number for 本人確認 (identity check), and an optional referral code. It SHALL:
- read the stock with TicketStock.Get, failing with NotFound when it does not exist, and fail with FailedPrecondition when its resale is not open at the current time or Event.IsEventPublished reports false for its event, as for a 中止 (cancelled) concert;
- read the tickets the fan holds for the event with Order.GetHeldForEvent and fail with FailedPrecondition when the application does not fit the event (the per-account limit or the seat type rule), so the fan is not asked to authenticate a card for an entry that would be refused;
- fail with FailedPrecondition when the fan does not hold an Active IdentityVerification and any sale of the event requires verification;
- open a CardAuthorization with CardAuthorization.Create for the seat type's amount for the count, carrying the TicketStock, the count and the referral code, and return it.

#### Scenario: Card authorized
- **WHEN** a fan holding no ticket for the event asks to apply for 2 tickets of a sold-out stock priced 5000 yen
- **THEN** a card authorization for 10000 yen carrying the stock and the count is returned

#### Scenario: Not sold out
- **WHEN** the stock is not sold out
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Another seat type held
- **WHEN** the fan holds S席 tickets for the event and asks for A席
- **THEN** AuthorizeCard fails with FailedPrecondition and no card authorization is opened

#### Scenario: Verification required
- **WHEN** a sale of the event requires verification and the fan holds none
- **THEN** AuthorizeCard fails with FailedPrecondition
