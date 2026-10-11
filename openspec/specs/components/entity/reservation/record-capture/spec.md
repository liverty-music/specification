# components/entity/reservation/record-capture Specification

## Purpose
Records that a Committed Reservation's card was charged, so a retry never charges again and the checkout can never be released.

## Requirements

### Requirement: Charge recorded once

RecordCapture SHALL take a Committed Reservation and a time, and store that time as its capture time. The charged payment is the Reservation's card hold, so its reference is the authorization reference. When the Reservation already has a capture time it SHALL change nothing. It SHALL fail with FailedPrecondition when the Reservation is not Committed, and with NotFound when no Reservation has the id.

#### Scenario: First charge

- **WHEN** a Committed Reservation's card is charged at 18:14
- **THEN** its capture time is 18:14

#### Scenario: Recorded twice

- **WHEN** the capture is recorded again
- **THEN** nothing changes
