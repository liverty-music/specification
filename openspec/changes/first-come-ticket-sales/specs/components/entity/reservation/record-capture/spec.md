# Spec Delta

## Purpose

Records that a Committed Reservation's card was charged, so a retry never charges again and the checkout can never be released.

## ADDED Requirements

### Requirement: Charge recorded once

RecordCapture SHALL take a Committed Reservation, a time, the captured payment's reference, card brand and last four digits, and store them with that capture time. When the Reservation already has a capture time it SHALL change nothing. It SHALL fail with FailedPrecondition when the Reservation is not Committed, and with NotFound when no Reservation has the id.

#### Scenario: First charge

- **WHEN** a Committed Reservation's card is charged at 18:14
- **THEN** its capture time is 18:14 with the payment reference and card facets

#### Scenario: Recorded twice

- **WHEN** the capture is recorded again
- **THEN** nothing changes
