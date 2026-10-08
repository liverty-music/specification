# Spec Delta

## Purpose

Checks that a Reservation's card hold is authenticated and ready to capture for the right amount.

## ADDED Requirements

### Requirement: Verify a hold

VerifyAuthorization SHALL succeed only when the hold has completed card authentication and is waiting to be captured, its amount equals the Reservation's amount and its currency is yen. Every card brand that card payments accept, American Express included, SHALL be accepted. It SHALL fail with FailedPrecondition when the hold is not yet authenticated or not waiting to be captured, with InvalidArgument when the amount differs or the currency is not yen, with NotFound when no hold has the reference, and with Unavailable when card payments cannot be reached.

#### Scenario: Valid hold

- **WHEN** an authenticated 6000 yen hold is verified for a 6000 yen Reservation
- **THEN** VerifyAuthorization succeeds

#### Scenario: American Express card

- **WHEN** the authenticated hold is on an American Express card
- **THEN** VerifyAuthorization succeeds

#### Scenario: Not authenticated

- **WHEN** the fan has not completed card authentication
- **THEN** VerifyAuthorization fails with FailedPrecondition

#### Scenario: Amount mismatch

- **WHEN** the hold is for 3000 yen and the Reservation's amount is 6000 yen
- **THEN** VerifyAuthorization fails with InvalidArgument
