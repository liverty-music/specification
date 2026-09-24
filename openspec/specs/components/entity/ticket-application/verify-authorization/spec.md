# TicketApplication.VerifyAuthorization

## Purpose

Confirms that a hold is authenticated and held for exactly an expected yen amount on an accepted card.

## Requirements

### Requirement: Verify a hold

VerifyAuthorization SHALL succeed only when the hold has completed card authentication and is waiting to be captured, its amount equals the expected amount, its currency is yen, and its card brand is accepted. It SHALL fail with FailedPrecondition when the hold is not yet authenticated or not waiting to be captured, with InvalidArgument when the amount differs or the currency is not yen, with FailedPrecondition when the card is American Express, with NotFound when no hold has the reference, and with Unavailable when card payments cannot be reached.

#### Scenario: Valid hold

- **WHEN** an authenticated yen hold of 16000 on a Visa card is verified against 16000
- **THEN** VerifyAuthorization succeeds

#### Scenario: Not authenticated

- **WHEN** the fan has not completed card authentication for the hold
- **THEN** VerifyAuthorization fails with FailedPrecondition

#### Scenario: Amount mismatch

- **WHEN** the hold is for 8000 and 16000 is expected
- **THEN** VerifyAuthorization fails with InvalidArgument

#### Scenario: Foreign currency

- **WHEN** the hold is not in yen
- **THEN** VerifyAuthorization fails with InvalidArgument

#### Scenario: American Express card

- **WHEN** the hold is on an American Express card
- **THEN** VerifyAuthorization fails with FailedPrecondition

#### Scenario: Unknown reference

- **WHEN** no hold has the reference
- **THEN** VerifyAuthorization fails with NotFound
