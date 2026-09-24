# TicketApplication.CreateAuthorization

## Purpose

Opens an authorization (hold) in yen for an application's amount and returns its reference plus a short-lived confirmation secret that the fan's browser uses to complete card authentication; no money is captured and no application is stored.

## Requirements

### Requirement: Holding an amount

CreateAuthorization SHALL open a hold in Japanese yen for the given amount that captures nothing until CaptureAuthorization runs, and SHALL return the hold's reference and a confirmation secret. It SHALL fail with InvalidArgument when the amount is zero or negative, and with Unavailable when card payments cannot be reached.

#### Scenario: Hold opened

- **WHEN** CreateAuthorization is called with a positive amount
- **THEN** a hold for that amount in yen is opened, its reference and a confirmation secret are returned, and nothing is charged

#### Scenario: Non-positive amount

- **WHEN** CreateAuthorization is called with an amount of zero or less
- **THEN** it fails with InvalidArgument and no hold is opened

#### Scenario: Card payments unavailable

- **WHEN** card payments cannot be reached
- **THEN** CreateAuthorization fails with Unavailable
