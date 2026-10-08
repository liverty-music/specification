# Spec Delta

## Purpose

Charges a Reservation's held amount, exactly once, however often and however late it is repeated.

## ADDED Requirements

### Requirement: Capture a hold

CaptureAuthorization SHALL charge the held amount and return the charged payment's reference, card brand and last four digits. The outcome SHALL follow the state of the hold, not the outcome of an earlier request:
- When the hold was already charged, by this call or any earlier one however long ago, it SHALL succeed and return the charged payment without charging again.
- When the hold was released or has expired, or the card can no longer be charged, it SHALL fail with FailedPrecondition and nothing is charged.
- When the outcome cannot be known yet — the payment service is unreachable, or another capture of the same hold is still in progress — it SHALL fail with Unavailable.

It SHALL fail with NotFound when no hold has the reference.

#### Scenario: Hold captured

- **WHEN** CaptureAuthorization is called for an authenticated hold
- **THEN** the held amount is charged

#### Scenario: Repeated capture

- **WHEN** CaptureAuthorization is called again for the same hold
- **THEN** it succeeds, returns the same payment and the card is charged only once

#### Scenario: Repeated a day later

- **WHEN** CaptureAuthorization is called for a hold that was charged 2 days earlier
- **THEN** it succeeds and returns that payment without charging again

#### Scenario: Hold no longer capturable

- **WHEN** the hold was released
- **THEN** CaptureAuthorization fails with FailedPrecondition and nothing is charged

#### Scenario: Capture already in progress

- **WHEN** another capture of the same hold has not finished
- **THEN** CaptureAuthorization fails with Unavailable
