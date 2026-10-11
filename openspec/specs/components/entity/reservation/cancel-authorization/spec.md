# components/entity/reservation/cancel-authorization Specification

## Purpose
Releases a Reservation's card hold without charging, exactly once.

## Requirements

### Requirement: Release a hold

CancelAuthorization SHALL release the hold. Repeating it for the same hold, or calling it for a hold that has expired, SHALL succeed without a further effect. It SHALL fail with NotFound when no hold has the reference, with FailedPrecondition when the hold has already been charged, and with Unavailable when card payments cannot be reached.

#### Scenario: Hold released

- **WHEN** CancelAuthorization is called for an uncaptured hold
- **THEN** the hold is released and nothing is charged

#### Scenario: Repeated release

- **WHEN** CancelAuthorization is called again for the same hold
- **THEN** it succeeds and nothing changes

#### Scenario: Charged hold

- **WHEN** the hold has already been charged
- **THEN** CancelAuthorization fails with FailedPrecondition
