# TicketApplication.CaptureAuthorization

## Purpose

Captures a hold, charging the fan's card the held amount.

## Requirements

### Requirement: Capture a hold

CaptureAuthorization SHALL charge the held amount; repeating it for the same hold SHALL succeed without charging again. It SHALL fail with NotFound when no hold has the reference, with FailedPrecondition when the hold can no longer be captured (released, expired, or the card was closed), and with Unavailable when card payments cannot be reached.

#### Scenario: Hold captured

- **WHEN** CaptureAuthorization is called for an authenticated hold
- **THEN** the held amount is charged

#### Scenario: Repeated capture

- **WHEN** CaptureAuthorization is called again for the same hold
- **THEN** it succeeds and the card is charged only once

#### Scenario: Hold no longer capturable

- **WHEN** the hold was released or the card was closed
- **THEN** CaptureAuthorization fails with FailedPrecondition and nothing is charged
