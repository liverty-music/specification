# Spec Delta

## Purpose

Records that a Committed Checkout's card was charged, so a retry never charges again and the checkout can never be released.

## ADDED Requirements

### Requirement: Charge recorded once

RecordCapture SHALL take a Committed Checkout and a time, and store that time as its capture time. The charged payment is the Checkout's card hold, so its reference is the authorization reference. When the Checkout already has a capture time it SHALL change nothing. It SHALL fail with FailedPrecondition when the Checkout is not Committed, and with NotFound when no Checkout has the id.

#### Scenario: First charge
- **WHEN** a Committed Checkout's card is charged at 18:14
- **THEN** its capture time is 18:14

#### Scenario: Recorded twice
- **WHEN** the capture is recorded again
- **THEN** nothing changes
