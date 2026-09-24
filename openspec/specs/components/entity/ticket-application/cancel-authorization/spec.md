# TicketApplication.CancelAuthorization

## Purpose

Releases a hold so the fan is never charged for it.

## Requirements

### Requirement: Release a hold

CancelAuthorization SHALL release the hold; repeating it for the same hold SHALL succeed without a second effect. It SHALL fail with NotFound when no hold has the reference, with FailedPrecondition when the hold has already been captured, and with Unavailable when card payments cannot be reached.

#### Scenario: Hold released

- **WHEN** CancelAuthorization is called for an uncaptured hold
- **THEN** the hold is released and nothing is charged

#### Scenario: Repeated release

- **WHEN** CancelAuthorization is called again for the same hold
- **THEN** it succeeds and nothing changes

#### Scenario: Captured hold

- **WHEN** the hold has already been captured
- **THEN** CancelAuthorization fails with FailedPrecondition

#### Scenario: Unknown reference

- **WHEN** no hold has the reference
- **THEN** CancelAuthorization fails with NotFound
